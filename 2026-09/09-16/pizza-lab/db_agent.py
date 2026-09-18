import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL")

conn = sqlite3.connect("shop.db")

def schema_check():
    return conn.execute(
        "PRAGMA table_info(orders)"
    ).fetchall()

def null_check():
    return conn.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE amount IS NULL
    """).fetchall()

def sales_check():
    return conn.execute("""
        SELECT COUNT(*), SUM(amount), AVG(amount)
        FROM orders
    """).fetchall()


question = input("무엇을 확인할까요? ")

prompt = f"""
너는 DB 관리 Agent다.

사용자의 의도를 파악하여
다음 함수 중 가장 적절한 함수 하나를 선택하라.

schema_check
- DB 필드와 구조 확인

null_check
- 매출 데이터의 결측값 확인

sales_check
- 주문수, 총매출, 평균매출 확인

사용자 요청:
{question}

함수 이름만 출력하라.
"""

response = client.responses.create(
    model=model,
    input=prompt
)

action = response.output_text.strip()

print("Agent 선택:", action)

if action == "schema_check":
    result = schema_check()

elif action == "null_check":
    result = null_check()

elif action == "sales_check":
    result = sales_check()

else:
    result = "실행 가능한 작업이 없습니다."

print("실행 결과:", result)

report_prompt = f"""
당신은 DB 관리 Agent다.

사용자 요청:
{question}

실행한 작업:
{action}

실행 결과:
{result}

이 결과가 무엇을 의미하는지
초보자가 이해할 수 있도록 3줄 이내로 설명하라.

확인하지 않은 내용은 추측하지 마라.
"""

report = client.responses.create(
    model=model,
    input=report_prompt
)

print("\nAgent 분석:")
print(report.output_text)

conn.close()