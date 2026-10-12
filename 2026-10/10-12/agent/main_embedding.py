import inspect
import os
from collections.abc import Callable
from typing import Any

import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
EMBEDDING_MODEL = 'text-embedding-3-small'

PRODUCTS: dict[str, dict[str, Any]] = {
    '무선 블루투스 이어폰': {'price': 39000, 'stock': 15, 'description': '가볍고 휴대하기 좋은 무선 이어폰'},
    '노이즈 캔슬링 헤드폰': {'price': 159000, 'stock': 8, 'description': '외부 소음을 줄여주는 오버이어 헤드폰'},
    '휴대용 보조배터리': {'price': 29000, 'stock': 20, 'description': '스마트폰 충전을 위한 10000mAh 보조배터리'},
    '게이밍 기계식 키보드': {'price': 89000, 'stock': 10, 'description': '게임과 문서 작업에 적합한 기계식 키보드'},
}


def answer_with_gpt(question: str, instruction: str) -> str:
    """상품 데이터에 근거하여 한국어로 답변한다."""
    import json
    response = client.responses.create(
        model='gpt-4.1-mini',
        instructions=instruction + ' 제공된 데이터만 사용하고 없는 정보는 추측하지 마. 가격과 재고를 정확히 확인해.',
        input=f'상품 데이터: {json.dumps(PRODUCTS, ensure_ascii=False)}\n질문: {question}',
    )
    return response.output_text


def search_product(question: str) -> str:
    """상품 검색, 상품 종류, 특징, 설명, 용도, 판매 여부를 확인한다. 예: 키보드 있어? 어떤 제품 팔아? 이어폰 특징 알려줘."""
    return answer_with_gpt(question, '관련 상품명과 특징을 설명해.')


def search_price(question: str) -> str:
    """상품 가격, 단가, 판매 금액, 저렴한 상품, 비싼 상품을 조회한다. 예: 키보드 얼마야? 가장 싼 제품은? 헤드폰 가격 알려줘."""
    return answer_with_gpt(question, '상품 가격을 안내해.')


def search_stock(question: str) -> str:
    """상품 재고, 남은 수량, 품절, 현재 구매 가능 여부를 확인한다. 예: 키보드 남아 있어? 이어폰 재고 몇 개야? 키보드 3개 있어?"""
    return answer_with_gpt(question, '상품 재고 수량과 요청 수량의 구매 가능 여부를 안내해.')


def calculate_total(question: str) -> str:
    """여러 개 구매할 때 총금액, 합계, 결제 예상액을 계산하고 재고를 확인한다. 예: 키보드 3개 사면 얼마야? 이어폰 두 개 총 얼마?"""
    return answer_with_gpt(question, '구매 수량을 파악하고 재고 확인 후 단가 곱하기 수량으로 총금액을 계산해.')


def recommend_product(question: str) -> str:
    """사용 목적, 조건, 취향, 상황에 맞는 상품을 추천하거나 비교한다. 예: 게임용으로 추천해줘. 휴대하기 좋은 제품 뭐야?"""
    return answer_with_gpt(question, '사용자의 요구에 적합한 상품을 추천하고 이유를 설명해.')


FUNCTIONS: dict[str, Callable[[str], str]] = {
    func.__name__: func
    for func in (search_product, search_price, search_stock, calculate_total, recommend_product)
}


def collect_descriptions(functions: dict[str, Callable[[str], str]]) -> dict[str, str]:
    """등록 함수의 Docstring을 함수 이름과 설명의 딕셔너리로 수집한다."""
    return {name: inspect.getdoc(func) or '' for name, func in functions.items()}


def embed_texts(texts: list[str]) -> np.ndarray:
    """텍스트를 한 번의 API 요청으로 임베딩한다."""
    result = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return np.asarray([item.embedding for item in sorted(result.data, key=lambda x: x.index)], dtype=float)


def cosine_similarities(query_vector: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """질문 벡터와 각 함수 설명 벡터 사이의 코사인 유사도를 계산한다."""
    numerator = vectors @ query_vector
    denominator = np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vector)
    return numerator / np.maximum(denominator, 1e-12)


def main() -> None:
    descriptions = collect_descriptions(FUNCTIONS)
    keys = list(descriptions.keys())
    values = list(descriptions.values())
    description_vectors = embed_texts(values)  # 최초 한 번만 임베딩

    print('상품 안내 챗봇 (종료: q)')
    while True:
        question = input('\n질문: ').strip()
        if question.lower() == 'q':
            break
        if not question:
            continue
        try:
            question_vector = embed_texts([question])[0]
            scores = cosine_similarities(question_vector, description_vectors)
            index = int(np.argmax(scores))
            function_name = keys[index]
            print(f'[선택 함수] {function_name} / 유사도: {scores[index]:.4f}')
            print('답변:', FUNCTIONS[function_name](question))
        except Exception as error:
            print('오류:', error)


if __name__ == '__main__':
    main()
