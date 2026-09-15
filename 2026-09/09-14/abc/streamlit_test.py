# streamlit test: 이미지 성능 분석기
#   실행: streamlit run streamlit_test.py

import streamlit as st
from PIL import Image
import psutil
import time
import os

st.title("🖼️ 이미지 성능 분석기")
st.write("이미지 크기와 모드를 변경하면서 RAM과 처리시간을 비교합니다.")

# 현재 Python 프로세스
process = psutil.Process(os.getpid())

# 이미지 업로드
file = st.file_uploader(
    "이미지를 업로드하세요",
    type=["jpg", "jpeg", "png"]
)

if file:
    # PIL로 이미지 열기
    img = Image.open(file)

    st.subheader("원본 이미지")
    st.image(img)

    st.write("크기:", img.size)
    st.write("모드:", img.mode)

    # -------------------------
    # 성능 측정 함수
    # -------------------------
    def test_image(image, scale, mode):
        ram_before = process.memory_info().rss

        start = time.perf_counter()

        # 크기 변경
        new_width = max(1, int(image.width * scale))
        new_height = max(1, int(image.height * scale))

        result = image.resize((new_width, new_height))

        # 이미지 모드 변경
        result = result.convert(mode)

        end = time.perf_counter()

        ram_after = process.memory_info().rss

        time_ms = (end - start) * 1000
        ram_change = (ram_after - ram_before) / 1024 / 1024

        return result, time_ms, ram_change

    # -------------------------
    # 테스트
    # -------------------------

    results = []

    tests = [
        ("원본 크기 RGB", 1, "RGB"),
        ("1/2 크기 RGB", 0.5, "RGB"),
        ("1/5 크기 RGB", 0.2, "RGB"),
        ("원본 크기 L", 1, "L"),
        ("1/2 크기 L", 0.5, "L"),
        ("1/5 크기 L", 0.2, "L"),
    ]

    for name, scale, mode in tests:

        result_img, time_ms, ram = test_image(
            img,
            scale,
            mode
        )

        results.append({
            "테스트": name,
            "크기": f"{result_img.width} x {result_img.height}",
            "모드": result_img.mode,
            "처리시간(ms)": round(time_ms, 3),
            "RAM 변화(MB)": round(ram, 3)
        })

    # -------------------------
    # 결과 출력
    # -------------------------

    st.subheader("📊 성능 비교")

    st.dataframe(
        results,
        use_container_width=True
    )