"""Streamlit 기반 실시간 인물 분할 및 이미지 히스토그램 분석 앱."""

import json
import os
import threading
from datetime import datetime
from pathlib import Path

import av
import cv2
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import torch
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from st_keyup import st_keyup
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer
from torchvision.models.segmentation import DeepLabV3_ResNet50_Weights, deeplabv3_resnet50

BASE_DIR = Path(__file__).resolve().parent
CAPTURE_DIR = BASE_DIR / "captures"
CAPTURE_DIR.mkdir(exist_ok=True)
load_dotenv(BASE_DIR / ".env")

st.set_page_config(page_title="실시간 인물 분할 분석", layout="wide")


@st.cache_resource(show_spinner="PyTorch 모델을 불러오는 중...")
def load_segmentation_model():
    """사전 학습된 DeepLabV3 모델을 불러오고 입력 변환을 준비합니다."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    weights = DeepLabV3_ResNet50_Weights.DEFAULT
    model = deeplabv3_resnet50(weights=weights).to(device).eval()
    return model, weights.transforms(), device


class SegmentationProcessor(VideoProcessorBase):
    """웹캠 프레임에서 사람을 분할하고 배경을 합성합니다."""

    def __init__(self):
        self.lock = threading.Lock()
        self.last_frame_rgb = None
        self.background_path = BASE_DIR / "back.jpg"
        self.model, self.preprocess, self.device = load_segmentation_model()

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        bgr = frame.to_ndarray(format="bgr24")
        height, width = bgr.shape[:2]
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        tensor = self.preprocess(Image.fromarray(rgb)).unsqueeze(0).to(self.device)
        with torch.inference_mode():
            logits = self.model(tensor)["out"]

        # Pascal VOC 클래스 인덱스 15는 사람입니다.
        mask = (logits.argmax(dim=1)[0] == 15).byte().cpu().numpy()
        mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)
        alpha = cv2.GaussianBlur(mask.astype(np.float32), (7, 7), 0)[:, :, None]

        background_bgr = cv2.imread(str(self.background_path))
        if background_bgr is None:
            result_rgb = rgb
        else:
            background_rgb = cv2.cvtColor(
                cv2.resize(background_bgr, (width, height)), cv2.COLOR_BGR2RGB
            )
            result_rgb = np.clip(
                rgb * alpha + background_rgb * (1 - alpha), 0, 255
            ).astype(np.uint8)

        with self.lock:
            self.last_frame_rgb = result_rgb.copy()

        return av.VideoFrame.from_ndarray(result_rgb, format="rgb24")


def get_histogram_statistics(image_rgb: np.ndarray) -> dict:
    """RGB와 밝기 히스토그램 및 GPT에 전달할 요약 통계를 계산합니다."""
    channels = {
        "R": image_rgb[:, :, 0],
        "G": image_rgb[:, :, 1],
        "B": image_rgb[:, :, 2],
    }
    gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    counts = {
        name: np.histogram(values, bins=256, range=(0, 256))[0]
        for name, values in channels.items()
    }
    counts["밝기"] = np.histogram(gray, bins=256, range=(0, 256))[0]
    stats = {
        "width": int(image_rgb.shape[1]),
        "height": int(image_rgb.shape[0]),
        "mean_rgb": {
            name: round(float(values.mean()), 2)
            for name, values in channels.items()
        },
        "mean_brightness": round(float(gray.mean()), 2),
        "brightness_std": round(float(gray.std()), 2),
        "dark_pixel_ratio_percent": round(float((gray < 64).mean() * 100), 2),
        "bright_pixel_ratio_percent": round(float((gray >= 192).mean() * 100), 2),
        "brightness_percentiles": {
            str(percentile): float(np.percentile(gray, percentile))
            for percentile in (10, 50, 90)
        },
        "histogram_16bins": {
            name: np.histogram(values, bins=16, range=(0, 256))[0]
            .astype(int)
            .tolist()
            for name, values in {**channels, "밝기": gray}.items()
        },
    }
    return {"counts": counts, "stats": stats}


def make_histogram(counts: dict, selected: list[str]) -> go.Figure:
    """선택한 채널의 히스토그램 그래프를 만듭니다."""
    fig = go.Figure()
    colors = {"R": "red", "G": "green", "B": "blue", "밝기": "gray"}
    for channel in selected:
        fig.add_trace(
            go.Scatter(
                x=list(range(256)),
                y=counts[channel],
                name=channel,
                mode="lines",
                line={"color": colors[channel]},
            )
        )
    fig.update_layout(
        xaxis_title="픽셀 값 (0~255)",
        yaxis_title="픽셀 수",
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h"),
    )
    return fig


def ask_gpt(question: str, stats: dict) -> str:
    """이미지 자체가 아닌 계산된 통계만 GPT에 전달합니다."""
    api_key = os.getenv("GPT_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(".env 파일에 GPT_API_KEY 또는 OPENAI_API_KEY를 설정하세요.")

    client = OpenAI(api_key=api_key)
    model_name = os.getenv("GPT_MODEL", "gpt-4.1-mini")
    response = client.responses.create(
        model=model_name,
        instructions=(
            "당신은 이미지 히스토그램 통계 분석 도우미입니다. 한국어로 쉽고 정확하게 답하세요. "
            "전달된 수치만으로 판단하고 사진 속 인물의 신원, 감정, 행동, 사물 등을 추정하지 마세요. "
            "히스토그램은 색상과 밝기 분포만 설명할 수 있음을 명시하세요. "
            "밝기 평균과 표준편차, 채널별 평균, 어둡거나 밝은 픽셀 비율을 활용하세요."
        ),
        input=(
            f"히스토그램 통계(JSON):\n{json.dumps(stats, ensure_ascii=False)}"
            f"\n\n사용자 질문: {question}"
        ),
    )
    return response.output_text


# 세션 상태에 현재 캡처 이미지와 대화 내역을 보관합니다.
if "saved_image" not in st.session_state:
    st.session_state.saved_image = None
if "saved_path" not in st.session_state:
    st.session_state.saved_path = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "key_version" not in st.session_state:
    st.session_state.key_version = 0

st.title("실시간 인물 분할 · 히스토그램 · GPT 분석")
st.caption("카메라를 켜고 S 키 또는 캡처 버튼을 누르면 프레임을 저장해 색상과 밝기를 분석합니다.")

left, right = st.columns(2, gap="large")
with left:
    st.subheader("1. 실시간 웹캠")
    ctx = webrtc_streamer(
        key="person-segmentation",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=SegmentationProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    st.caption("브라우저에서 카메라 사용을 허용하세요. CPU 환경에서는 처리 속도가 느릴 수 있습니다.")

    key_text = st_keyup(
        "S 키 입력 (입력 칸을 클릭한 뒤 S 누르기)",
        key=f"save_key_{st.session_state.key_version}",
        debounce=0,
    )
    clicked = st.button("현재 프레임 저장", type="primary", use_container_width=True)

    if clicked or (key_text and key_text.lower().strip() == "s"):
        processor = ctx.video_processor if ctx else None
        if processor is None:
            st.warning("먼저 웹캠을 시작해 주세요.")
        else:
            with processor.lock:
                latest = (
                    None
                    if processor.last_frame_rgb is None
                    else processor.last_frame_rgb.copy()
                )
            if latest is None:
                st.warning("아직 수신된 프레임이 없습니다. 잠시 후 다시 시도하세요.")
            else:
                filename = f"capture_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
                path = CAPTURE_DIR / filename
                Image.fromarray(latest).save(path)
                st.session_state.saved_image = latest
                st.session_state.saved_path = str(path)
                st.session_state.messages = []
                st.session_state.key_version += 1
                st.rerun()

with right:
    st.subheader("2. 저장된 프레임")
    if st.session_state.saved_image is None:
        st.info("왼쪽에서 웹캠을 시작하고 S 키 또는 저장 버튼을 눌러 주세요.")
    else:
        st.image(
            st.session_state.saved_image,
            caption=Path(st.session_state.saved_path).name,
            use_container_width=True,
        )
        st.success(f"저장 완료: {st.session_state.saved_path}")

if st.session_state.saved_image is not None:
    st.divider()
    st.subheader("3. 히스토그램 분석")
    data = get_histogram_statistics(st.session_state.saved_image)
    selected = st.multiselect(
        "표시할 채널",
        ["R", "G", "B", "밝기"],
        default=["R", "G", "B", "밝기"],
    )
    if selected:
        st.plotly_chart(
            make_histogram(data["counts"], selected), use_container_width=True
        )
    stats = data["stats"]
    a, b, c, d = st.columns(4)
    a.metric("평균 밝기", stats["mean_brightness"])
    b.metric("밝기 표준편차", stats["brightness_std"])
    c.metric("어두운 픽셀 (%)", stats["dark_pixel_ratio_percent"])
    d.metric("밝은 픽셀 (%)", stats["bright_pixel_ratio_percent"])
    st.dataframe(
        pd.DataFrame([stats["mean_rgb"]]), hide_index=True, use_container_width=True
    )

    st.divider()
    st.subheader("4. GPT 히스토그램 요약 및 질의응답")
    if st.button("GPT로 히스토그램 요약하기"):
        try:
            with st.spinner("히스토그램을 분석하는 중..."):
                answer = ask_gpt(
                    "이 히스토그램을 초보자도 이해할 수 있도록 요약해 줘.", stats
                )
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        except Exception as exc:
            st.error(f"GPT 호출 오류: {exc}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("사진의 색상이나 밝기 분포에 대해 질문하세요.")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        try:
            with st.spinner("답변을 만드는 중..."):
                answer = ask_gpt(question, stats)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
            with st.chat_message("assistant"):
                st.markdown(answer)
        except Exception as exc:
            st.error(f"GPT 호출 오류: {exc}")
