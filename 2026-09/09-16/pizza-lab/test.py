import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 불러오기
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

# OpenAI 연결
client = OpenAI(api_key=api_key)

# 사용자 입력값
topic = "클라우드 컴퓨팅"
level = "초보자"
length = "3줄"

# Query 템플릿 + Few-shot
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

# 테스트 질문
response = client.responses.create(
    model=model,

    # 역할/규칙 설정
    instructions="할머니에게 설명하듯.",

    # 실제 질문
    input=query,

    # 최대 출력 토큰
    max_output_tokens=500,

    # 출력 다양성 조절 (0~2), default=0.7, 낮을수록 결정적, 높을수록 창의적
    #temperature=0 
)

# 웹은 0.7 정도의 temp가 설정되어 있는 듯함. 조정 못함.
print(response.output_text)