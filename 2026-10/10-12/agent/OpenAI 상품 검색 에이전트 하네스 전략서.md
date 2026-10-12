# OpenAI 상품 안내 에이전트 하네스(Harness) 설계 전략서

- 버전: 1.0
- 작성일: 2026-10-12
- 기술 스택: Python, OpenAI Agents SDK

## 1. 프로젝트 개요

상품 검색, 가격 조회, 재고 확인, 구매 금액 계산, 상품 추천을 수행하는 AI 에이전트의 실행 환경을 설계한다.

**하네스(Harness)**는 에이전트가 안정적으로 작동하도록 실행 흐름, 도구 호출, 상태 관리, 검증, 오류 복구, 비용 통제 및 모니터링을 담당하는 구조다.

**목표:** 답변 정확성과 응답 속도를 유지하면서 API 토큰 비용을 최소화한다.

## 2. 핵심 설계 원칙

| 원칙 | 적용 전략 |
|---|---|
| 비용 최소화 | 단순 작업은 Python에서 직접 처리 |
| 속도 최적화 | 캐시, 경량 모델, API 호출 최소화 |
| 정확성 | 상품 데이터 기반 답변, Python 계산 검증 |
| 안정성 | 타임아웃, 제한된 재시도, 오류 처리 |
| 확장성 | 함수별 모듈화, 도구 등록 체계 |
| 관측성 | 실행 로그, 토큰, 지연시간 추적 |
| 안전성 | 입력·출력 검증, 주문 직전 재고 재확인 |

## 3. 하네스 아키텍처

```text
사용자 질문
    |
    v
입력 검증 및 세션 관리
    |
    v
Harness Controller
(캐시 확인 / 실행 경로 결정 / 비용 제한)
    |
    +------------------------+
    |                        |
    v                        v
Python 직접 처리          OpenAI Agent
(가격·재고·계산)          (모호한 질문·추천·복합 의도)
    |                        |
    +-----------+------------+
                |
                v
출력 검증 및 응답 생성
                |
                v
최종 답변 + 로그 기록
```

## 4. 하네스 구성요소

| 모듈 | 역할 | 구현 기술 |
|---|---|---|
| Input Validator | 사용자 입력 검증 | Pydantic |
| Router | 질문 처리 경로 결정 | Python / Agent |
| Cache Manager | 응답 및 데이터 캐싱 | Dictionary → Redis |
| Tool Registry | 함수 등록 및 관리 | `@function_tool` |
| Agent Runner | 에이전트 실행 제어 | OpenAI Agents SDK |
| Context Manager | 대화 문맥 관리 | Session |
| Guardrails | 입출력 및 도구 검증 | Pydantic / SDK 및 별도 검증 |
| Error Handler | 실패 처리 및 복구 | Python |
| Observability | 토큰·비용·시간 측정 | Tracing / 로그 |
| Evaluation | 정확도 및 성능 평가 | 테스트 데이터셋 |

## 5. 비용 및 속도 최적화 전략

| 전략 | 적용 방법 | 우선순위 |
|---|---|---|
| 조건부 GPT 호출 | Python으로 해결 가능한 질문은 직접 처리 | P0 |
| API 호출 최소화 | 별도 의도 분류용 모델 호출 제거 | P0 |
| 캐시 | 동일 요청의 유효한 결과 재사용 | P0 |
| 모델 라우팅 | 질문 난이도에 따라 모델 선택 | P1 |
| 프롬프트 최적화 | 정적 지침 재사용, 동적 데이터 최소화 | P1 |
| 도구 결과 즉시 반환 | 불필요한 후속 모델 응답 생략 | P1 |
| 컨텍스트 축소 | 필요한 대화 이력만 전달 | P1 |
| 병렬 처리 | 독립적인 조회를 동시에 실행 | P2 |
| 임베딩 라우팅 | 도구가 많아질 때 의미 기반 검색 | P2 |
| 스트리밍 | 첫 응답까지 체감 대기시간 감소 | P2 |

### 5.1 캐시 정책 예시

| 데이터 | TTL 예시 | 주의사항 |
|---|---|---|
| 상품 설명 | 24시간 | 상품 수정 시 무효화 |
| 가격 | 5~10분 | 가격 변경 시 무효화 |
| 재고 | 5~30초 | 주문 직전 원본 데이터로 재검증 |
| 추천 결과 | 1시간 | 상품 정보 변경 시 무효화 |
| 함수 Docstring 임베딩 | 설명 변경 전까지 | 함수 변경 시 재생성 |

TTL은 초기 예시이며 실제 변경 빈도에 맞춰 조정한다.

## 6. 도구 선택 전략

| 함수 | 호출 조건 | 처리 |
|---|---|---|
| `search_product` | 상품 존재·설명 질문 | 상품 검색 |
| `search_price` | 가격 관련 질문 | 단가 조회 |
| `search_stock` | 재고 관련 질문 | 재고 조회 |
| `calculate_total` | 구매 수량·총액 질문 | 재고 확인 및 금액 계산 |
| `recommend_product` | 추천·비교 질문 | 조건 기반 추천 |

각 도구의 Docstring에는 기능, 호출 조건, 매개변수, 모호한 표현의 예시를 포함한다. 여러 기능이 필요한 질문은 복수의 도구로 처리할 수 있도록 한다.

### 6.1 질문 라우팅 예시

- `키보드 가격?` → Python에서 직접 상품 가격 조회
- `키보드 3개 사면 얼마야?` → Python에서 재고 검증 및 `89,000 × 3 = 267,000원` 계산
- `게임과 문서 작업에 좋은 제품 추천해줘` → 에이전트가 상품 설명을 참고하여 추천
- `그거 2개는?` → 세션 문맥에서 이전 상품을 확인한 뒤 계산
- `좋은 거 있어?` → 의도가 충분히 명확하지 않으면 추가 질문

## 7. 오류 처리 및 안전 전략

| 상황 | 대응 방법 |
|---|---|
| 상품 없음 | 검색 실패 안내 |
| 질문 불명확 | 추가 질문 |
| 재고 부족 | 구매 불가 안내 |
| 수량 오류 | 양의 정수인지 검증 |
| API 타임아웃 | 제한된 재시도와 백오프 |
| API 사용량 초과 | 대기 또는 Python 대체 경로 |
| 금액 계산 오류 | Python에서 재계산 |
| 도구 호출 반복 | 최대 실행 횟수 제한 |
| 오래된 재고 | 주문 직전 최신 데이터 재조회 |

**중요:** 실제 주문 가능 여부와 금액은 GPT의 자연어 추론이 아니라 검증된 Python 로직과 최신 원본 데이터로 최종 판단한다.

## 8. 모니터링 및 평가 전략

| KPI | 초기 목표 예시 |
|---|---|
| 도구 선택 정확도 | 95% 이상 |
| 상품 가격 계산 정확도 | 100% |
| 재고 판단 정확도 | 최신 데이터 기준 100% |
| 단순 질문 GPT 호출 횟수 | 0회 |
| 응답시간 p95 | 3초 이내 |
| 요청당 토큰 비용 | 기준 버전 대비 30% 절감 |
| 오류율 | 1% 미만 |

위 수치는 **측정 결과가 아닌 설계 목표**다. 테스트 데이터와 실제 운영 환경에서 검증한다.

추가로 `input_tokens`, `output_tokens`, `cached_tokens`, API 호출 횟수, 도구 호출 성공률, 캐시 적중률, p50/p95 지연시간, 요청당 비용을 기록한다.

## 9. 권장 프로젝트 디렉터리

```text
product_agent/
├── main.py
├── .env
├── config.py
├── data/
│   └── products.py
├── tools/
│   ├── product.py
│   ├── price.py
│   ├── stock.py
│   ├── calculate.py
│   └── recommend.py
├── agent/
│   ├── product_agent.py
│   └── instructions.py
├── harness/
│   ├── router.py
│   ├── cache.py
│   ├── context.py
│   ├── guardrails.py
│   ├── retry.py
│   └── monitor.py
├── tests/
│   ├── test_tools.py
│   ├── test_routing.py
│   └── test_agent.py
└── requirements.txt
```

## 10. 단계별 구현 로드맵

- [ ] **1단계:** 상품 기능 분리 및 Docstring 작성
- [ ] **2단계:** OpenAI Agent와 Tool Registry 구현
- [ ] **3단계:** Python 직접 처리 Router 추가
- [ ] **4단계:** 캐시 및 세션 관리 구현
- [ ] **5단계:** Guardrails·재시도·실행 제한
- [ ] **6단계:** Tracing 및 토큰 비용 측정
- [ ] **7단계:** 평가 데이터셋 기반 성능 최적화

## 11. 최종 설계 결론

**하이브리드 하네스 아키텍처**를 채택한다. 단순 상품 조회와 계산은 Python이 처리하고, 모호한 질문과 복합 추천은 OpenAI Agent가 담당한다. Harness Controller는 캐시, 실행 경로, 오류 처리, 검증, 비용과 성능을 통합 관리한다.

향후 MySQL, FastAPI, Docker, Redis 기반 서비스로 확장할 수 있도록 구성한다.

## 12. 참고 자료

- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [OpenAI API 문서](https://platform.openai.com/docs/overview)
- [OpenAI Latency Optimization](https://platform.openai.com/docs/guides/latency-optimization)
