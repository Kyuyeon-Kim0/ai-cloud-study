import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="AI 개념 설명기",
    page_icon="☁️",
    layout="wide"
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

client = OpenAI(api_key=api_key)


# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>

.block-container {
    max-width: 1000px;
    padding-top: 3rem;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.sub-title {
    font-size: 18px;
    color: #777;
    margin-bottom: 35px;
}

.result-box {
    padding: 28px;
    border-radius: 18px;
    background: rgba(128, 128, 128, 0.08);
    border: 1px solid rgba(128, 128, 128, 0.2);
    font-size: 18px;
    line-height: 1.8;
}

</style>
""", unsafe_allow_html=True)


# -------------------------
# 왼쪽 사이드바
# -------------------------
with st.sidebar:

    st.title("⚙️ 설정")

    st.caption(f"현재 모델: {model}")

    st.divider()

    topic = st.text_input(
        "📌 주제",
        value="클라우드 컴퓨팅"
    )

    level = st.selectbox(
        "👤 대상",
        [
            "초보자",
            "중급자",
            "전문가"
        ]
    )

    length = st.selectbox(
        "📏 분량",
        [
            "3줄",
            "5줄",
            "10줄"
        ]
    )

    st.divider()

    max_tokens = st.slider(
        "🧮 Max Tokens",
        min_value=100,
        max_value=2000,
        value=500,
        step=100
    )

    temperature = st.slider(
        "🌡️ Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )

    st.caption("낮음 → 일정한 답변")
    st.caption("높음 → 다양한 답변")

    if "gpt-5.6" in model:
        st.warning(
            "현재 모델은 temperature를 지원하지 않아 "
            "실제 API 요청에서는 제외됩니다."
        )

    st.divider()

    run_button = st.button(
        "✨ 설명 생성",
        use_container_width=True,
        type="primary"
    )


# -------------------------
# 메인 화면
# -------------------------
st.markdown(
    '<div class="main-title">☁️ AI 개념 설명기</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '왼쪽에서 조건을 설정하고 AI 설명을 생성해보세요.'
    '</div>',
    unsafe_allow_html=True
)


# 현재 설정 간단 표시
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("주제", topic)

with col2:
    st.metric("대상", level)

with col3:
    st.metric("분량", length)


# -------------------------
# 버튼 실행
# -------------------------
if run_button:

    query = f"""
아래 예시의 설명 방식과 형식을 참고해서 답변해줘.

[예시 1]

주제: 데이터베이스
대상: 초보자
분량: 3줄

답변:
데이터베이스는 정보를 차곡차곡 보관하는 디지털 서랍장입니다.
필요한 정보를 빠르게 찾아보고 수정할 수 있습니다.
예를 들어 쇼핑몰은 상품과 회원 정보를 데이터베이스에 저장합니다.


[예시 2]

주제: API
대상: 초보자
분량: 3줄

답변:
API는 프로그램끼리 대화할 수 있게 해주는 창구입니다.
한 프로그램이 필요한 정보를 요청하면 다른 프로그램이 결과를 보내줍니다.
예를 들어 날씨 앱은 API를 통해 서버에서 날씨 정보를 받아옵니다.


[실제 질문]

주제: {topic}
대상: {level}
분량: {length}

위 예시와 같은 형식으로 설명해줘.
"""

    try:

        with st.spinner("AI가 설명을 만들고 있습니다..."):

            # 기본 API 옵션
            options = {
                "model": model,
                "instructions": "할머니에게 설명하듯 아주 쉽게 설명해.",
                "input": query,
                "max_output_tokens": max_tokens
            }

            # temperature 지원 모델에서만 추가
            if "gpt-5.6" not in model:
                options["temperature"] = temperature

            response = client.responses.create(**options)

        st.success("생성이 완료되었습니다.")

        st.subheader("🤖 AI 설명")

        st.markdown(
            f"""
            <div class="result-box">
            {response.output_text}
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:

        st.error("API 요청 중 오류가 발생했습니다.")

        st.code(str(e))