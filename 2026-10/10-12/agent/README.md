# AI 에이전트 학습 자료

같은 상품 검색·안내 과제를 **임베딩 기반 방식**과 **AI 에이전트 방식**으로 각각 구현해 비교하는 실습 자료입니다. 두 Python 파일은 비교 대상이며, HTML 학습 자료와 설계 전략 문서도 함께 포함합니다.

## 파일 안내

| 파일 | 설명 |
|---|---|
| `main_embedding.py` | 임베딩 방식입니다. 함수 설명을 벡터화하고 질문과의 유사도를 기준으로 관련 기능을 찾아 상품 안내를 수행합니다. |
| `main_agent.py` | 에이전트 방식입니다. OpenAI Agents SDK가 질문에 따라 상품 검색, 가격·재고 조회, 구매 금액 계산, 상품 추천 도구를 선택해 사용합니다. |
| `쇼핑몰 에이전트.html` | 쇼핑몰 에이전트 구현을 단계별로 설명하는 브라우저용 학습 자료입니다. |
| `LLM API · LangChain · AI 에이전트 학습 정리.html` | LLM API, LangChain, AI 에이전트 관련 학습 내용을 정리한 HTML 자료입니다. |
| `LLM 플랫폼 및 API 활용 정리.html` | LLM 플랫폼과 API 활용을 정리한 HTML 자료입니다. |
| `OpenAI 상품 검색 에이전트 하네스 전략서.md` | 상품 검색 에이전트의 하네스 구성, 도구 선택, 오류 처리 및 단계별 구현 전략을 정리한 문서입니다. |

## 실행 준비

Python 환경에서 필요한 패키지를 설치하고 OpenAI API 키를 환경 변수로 설정합니다.

```powershell
python -m pip install openai openai-agents numpy
$env:OPENAI_API_KEY = "발급받은_API_키"
```

## 비교 실습 실행

두 프로그램에 같은 질문을 입력해 응답과 처리 방식을 비교해 보세요. 예를 들어 상품 가격, 재고 확인, 여러 개 구매 금액 계산, 조건에 맞는 상품 추천 질문을 각각 입력할 수 있습니다.

임베딩 방식:

```powershell
python main_embedding.py
```

에이전트 방식:

```powershell
python main_agent.py
```

대화형 예제는 `q`를 입력하면 종료됩니다. 두 스크립트 모두 OpenAI API를 호출하므로 실행 시 API 키와 사용량에 따른 비용이 발생할 수 있습니다.

HTML 학습 자료는 파일을 브라우저에서 열어 확인할 수 있습니다. 설계 문서는 Markdown을 지원하는 편집기에서 열면 됩니다.
