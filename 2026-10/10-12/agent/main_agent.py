"""OpenAI Agents SDK 기반 상품 검색/재고/가격 안내 예제.

설치: pip install openai-agents
환경변수: OPENAI_API_KEY
실행: python main_agent.py
"""

import asyncio

from agents import Agent, Runner, function_tool


PRODUCTS: dict[str, dict[str, int | str]] = {
    "무선 블루투스 이어폰": {
        "price": 39000,
        "stock": 15,
        "description": "가볍고 휴대하기 좋은 무선 이어폰",
    },
    "노이즈 캔슬링 헤드폰": {
        "price": 159000,
        "stock": 8,
        "description": "외부 소음을 줄여주는 오버이어 헤드폰",
    },
    "휴대용 보조배터리": {
        "price": 29000,
        "stock": 20,
        "description": "스마트폰 충전을 위한 10000mAh 보조배터리",
    },
    "게이밍 기계식 키보드": {
        "price": 89000,
        "stock": 10,
        "description": "게임과 문서 작업에 적합한 기계식 키보드",
    },
}


def find_product(keyword: str) -> dict[str, dict[str, int | str]]:
    """상품명에 포함된 키워드로 상품을 찾는다."""
    terms = keyword.strip().lower().split()
    if not terms:
        return {}
    return {
        name: info
        for name, info in PRODUCTS.items()
        if all(term in name.lower() for term in terms)
    }


@function_tool
def search_product(keyword: str) -> dict:
    """상품의 존재 여부, 이름, 특징과 설명을 조회한다. '키보드 있어?', '이어폰 종류 알려줘'에 사용한다.

    Args:
        keyword: 찾을 상품명이나 상품명 일부.
    """
    return find_product(keyword)


@function_tool
def search_price(keyword: str) -> dict:
    """상품 가격과 단가를 조회한다. '헤드폰 얼마야?', '키보드 가격은?'에 사용한다.

    Args:
        keyword: 가격을 조회할 상품명이나 상품명 일부.
    """
    return {name: info["price"] for name, info in find_product(keyword).items()}


@function_tool
def search_stock(keyword: str) -> dict:
    """상품 재고 수량과 품절 여부를 확인한다. '몇 개 남았어?', '지금 살 수 있어?'에 사용한다.

    Args:
        keyword: 재고를 확인할 상품명이나 상품명 일부.
    """
    return {name: info["stock"] for name, info in find_product(keyword).items()}


@function_tool
def calculate_total(keyword: str, quantity: int) -> dict:
    """상품 구매 수량에 대한 재고 충족 여부와 총금액을 계산한다. '키보드 3개 사면 얼마야?'에 사용한다.

    Args:
        keyword: 구매할 상품명이나 상품명 일부.
        quantity: 구매하려는 개수(1 이상).
    """
    if quantity < 1:
        return {"error": "구매 수량은 1개 이상이어야 합니다."}
    matches = find_product(keyword)
    if not matches:
        return {"error": "일치하는 상품이 없습니다."}
    return {
        name: {
            "unit_price": info["price"],
            "stock": info["stock"],
            "quantity": quantity,
            "available": info["stock"] >= quantity,
            "total_price": info["price"] * quantity,
        }
        for name, info in matches.items()
    }


@function_tool
def recommend_product(purpose: str) -> dict:
    """사용 목적이나 조건에 맞는 상품을 추천할 때 상품 후보와 설명을 조회한다. '게임용 추천해줘'에 사용한다.

    Args:
        purpose: 사용 목적 또는 원하는 특징.
    """
    return PRODUCTS


product_agent = Agent(
    name="상품 안내 에이전트",
    model="gpt-4.1-mini",
    instructions=(
        "너는 쇼핑몰 상품 안내 에이전트다. 사용자 의도에 맞는 도구를 호출한다. "
        "상품 정보와 가격, 재고는 반드시 도구 결과만 근거로 답한다. "
        "복합 질문은 필요한 도구를 여러 개 사용할 수 있다. "
        "상품명 검색에 쓸 키워드는 짧고 명확하게 추출한다. "
        "검색 결과가 여러 개여서 특정할 수 없으면 되묻는다. "
        "검색 결과가 없으면 상품이 없다고 안내하고 지어내지 않는다. "
        "재고가 부족하면 구매 불가능하다고 알린다. "
        "총금액은 calculate_total의 계산 결과를 사용한다. "
        "사용자에게 간결한 한국어로 답한다."
    ),
    tools=[
        search_product,
        search_price,
        search_stock,
        calculate_total,
        recommend_product,
    ],
)


async def ask_agent(question: str) -> str:
    """에이전트에게 질문하고 최종 답변을 반환한다."""
    result = await Runner.run(product_agent, question)
    return str(result.final_output)


async def main() -> None:
    """사용자 질문을 반복적으로 입력받는다."""
    print("=== 상품 안내 AI 에이전트 ===")
    print("종료하려면 q를 입력하세요.")
    while True:
        question = input("\n질문: ").strip()
        if question.lower() == "q":
            break
        if not question:
            continue
        try:
            print("\nGPT:", await ask_agent(question))
        except Exception as exc:
            print(f"오류: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
