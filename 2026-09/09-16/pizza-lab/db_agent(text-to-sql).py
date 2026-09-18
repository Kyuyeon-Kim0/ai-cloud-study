import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL")

conn = sqlite3.connect("shop.db")


# --------------------------------------------------
# 1. 기존 DB 관리 함수
# --------------------------------------------------

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


# --------------------------------------------------
# 2. DB 스키마 가져오기
# --------------------------------------------------

def get_schema():
    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """).fetchall()

    schema = []

    for table in tables:
        table_name = table[0]

        columns = conn.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()

        column_info = [
            f"{col[1]} ({col[2]})"
            for col in columns
        ]

        schema.append(
            f"{table_name}: {', '.join(column_info)}"
        )

    return "\n".join(schema)


# --------------------------------------------------
# 3. Text-to-SQL
# --------------------------------------------------

def text_to_sql(question):

    schema = get_schema()

    sql_prompt = f"""
너는 SQLite 전문 Text-to-SQL Agent다.

사용자의 자연어 질문을
SQLite SELECT SQL문으로 변환하라.

[DB 스키마]
{schema}

[사용자 질문]
{question}

규칙:
- SELECT 조회만 허용한다.
- INSERT, UPDATE, DELETE, DROP, ALTER는 사용하지 않는다.
- 존재하는 테이블과 컬럼만 사용한다.
- 설명하지 말고 SQL문만 출력한다.
- ```sql 같은 Markdown은 사용하지 않는다.
"""

    response = client.responses.create(
        model=model,
        input=sql_prompt
    )

    sql = response.output_text.strip()

    print("\n생성 SQL:")
    print(sql)

    # 안전 검사
    sql_upper = sql.upper().strip()

    if not sql_upper.startswith("SELECT"):
        return {
            "sql": sql,
            "result": "SELECT 문만 실행할 수 있습니다."
        }

    forbidden = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "REPLACE",
        "TRUNCATE"
    ]

    if any(keyword in sql_upper for keyword in forbidden):
        return {
            "sql": sql,
            "result": "허용되지 않는 SQL이 포함되어 있습니다."
        }

    try:
        result = conn.execute(sql).fetchall()

        return {
            "sql": sql,
            "result": result
        }

    except sqlite3.Error as e:

        return {
            "sql": sql,
            "result": f"SQL 오류: {e}"
        }


# --------------------------------------------------
# 4. 사용자 질문
# --------------------------------------------------

question = input("무엇을 확인할까요? ")


# --------------------------------------------------
# 5. Router Agent
# --------------------------------------------------

prompt = f"""
너는 DB 관리 Router Agent다.

사용자의 질문을 분석하여
다음 네 가지 작업 중 하나만 선택하라.


schema_check
- DB 필드 확인
- 테이블 구조 확인
- 컬럼 확인
- 스키마 확인


null_check
- amount 컬럼의 NULL 확인
- 매출 결측값 확인


sales_check
- 전체 주문 수 확인
- 전체 매출 확인
- 평균 매출 확인


text_to_sql
- 위 세 함수로 처리할 수 없는 DB 조회
- 특정 상품 조회
- 특정 고객 조회
- 조건 검색
- 기간별 조회
- 정렬
- 그룹 집계
- 자연어를 SQL로 변환해야 하는 질문


사용자 질문:
{question}

함수 이름 하나만 출력하라.
"""

response = client.responses.create(
    model=model,
    input=prompt
)

action = response.output_text.strip()

print("\nAgent 선택:", action)


# --------------------------------------------------
# 6. Agent 실행
# --------------------------------------------------

if action == "schema_check":

    result = schema_check()


elif action == "null_check":

    result = null_check()


elif action == "sales_check":

    result = sales_check()


elif action == "text_to_sql":

    sql_result = text_to_sql(question)

    result = sql_result["result"]


else:

    result = "실행 가능한 작업이 없습니다."


print("\n실행 결과:")
print(result)


# --------------------------------------------------
# 7. 결과 설명 Agent
# --------------------------------------------------

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

숫자와 조회 결과를 기반으로 설명하라.
확인하지 않은 내용은 추측하지 마라.
"""

report = client.responses.create(
    model=model,
    input=report_prompt
)

print("\nAgent 분석:")
print(report.output_text)


conn.close()