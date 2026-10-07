# Python 비동기 웹 프레임워크 정리

## 1. Python 웹 프레임워크 종류

| 프레임워크 | 특징 | 장점 | 주요 용도 |
|---|---|---|---|
| FastAPI | 현대적인 ASGI 기반 프레임워크 | 비동기, 타입 힌트, 자동 API 문서 | REST API, AI API |
| Flask | 가벼운 웹 프레임워크 | 단순하고 배우기 쉬움 | 소규모 웹/API |
| Django | 종합 웹 프레임워크 | ORM, 관리자, 인증 등 기본 제공 | 대규모 웹서비스 |
| Streamlit | 데이터 앱 중심 | Python만으로 UI 제작 | 데이터 분석 |
| Gradio | AI UI 중심 | AI 모델 UI를 빠르게 제작 | AI/ML 데모 |
| Litestar | ASGI 기반 API 프레임워크 | DI, ORM 통합, Cache 등 | 구조화된 API |
| Sanic | Async-first 프레임워크 | 비동기 처리와 자체 서버 | 비동기 웹서비스 |
| Robyn | Rust + Python | 고성능 런타임 지향 | 고성능 API |

---

# 2. FastAPI

FastAPI는 Python으로 REST API와 웹 백엔드를 개발할 때 사용하는 웹 프레임워크이다.

특히 Python의 타입 힌트와 비동기 처리를 적극적으로 활용한다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
async def hello():
    return {"message": "Hello"}
```

주요 특징:

- ASGI 기반
- `async / await` 지원
- Python Type Hint 적극 활용
- Pydantic을 이용한 데이터 검증
- OpenAPI 기반 API 문서 자동 생성
- REST API 개발에 적합

---

# 3. Uvicorn

## Uvicorn의 역할

Uvicorn은 Python의 **ASGI 서버**이다.

FastAPI는 웹 애플리케이션의 기능을 정의하고, Uvicorn은 실제 네트워크 요청을 받아 FastAPI에 전달한다.

```text
사용자
  │
  │ HTTP
  ▼
Uvicorn
  │
  │ ASGI
  ▼
FastAPI
  │
  ▼
Python 함수
```

실행 예:

```bash
uvicorn main:app --reload
```

의미:

```text
uvicorn main:app --reload
│       │    │      │
│       │    │      └─ 코드 변경 시 자동 재시작
│       │    └──────── main.py의 app 객체
│       └───────────── main.py
└───────────────────── Uvicorn 서버 실행
```

## Uvicorn이 사용되는 경우

Uvicorn은 FastAPI 전용 서버가 아니다.

ASGI 규격을 지원하는 Python 애플리케이션을 실행할 수 있다.

대표적으로:

- FastAPI
- Starlette
- Django ASGI
- WebSocket 애플리케이션
- 직접 작성한 ASGI 애플리케이션

등에서 사용할 수 있다.

---

# 4. ASGI

## ASGI란?

**ASGI = Asynchronous Server Gateway Interface**

Python 웹 서버와 웹 애플리케이션이 서로 통신하기 위한 표준 인터페이스이다.

쉽게 말하면:

> 웹 서버와 Python 웹 프레임워크 사이의 통신 규칙

이라고 이해할 수 있다.

```text
Uvicorn
   │
   │ ASGI
   ▼
FastAPI
```

ASGI의 주요 특징:

- 비동기 처리 지원
- `async / await` 지원
- HTTP 지원
- WebSocket 지원
- 실시간 통신 지원
- 동시 요청 처리에 적합

---

# 5. WSGI vs ASGI

둘 다 Python 웹 서버와 웹 애플리케이션을 연결하기 위한 표준 인터페이스이다.

| 구분 | WSGI | ASGI |
|---|---|---|
| 전체 이름 | Web Server Gateway Interface | Asynchronous Server Gateway Interface |
| 처리 방식 | 동기 중심 | 동기 + 비동기 |
| async / await | 기본 지원 X | 지원 O |
| HTTP | O | O |
| WebSocket | 기본 지원 X | O |
| 실시간 통신 | 부적합 | 적합 |
| 대표 프레임워크 | Flask, 전통적 Django | FastAPI, Starlette |
| 대표 서버 | Gunicorn, uWSGI | Uvicorn, Daphne, Hypercorn |

구조 비교:

```text
WSGI

사용자
  ↓
WSGI Server
  ↓
WSGI
  ↓
Flask / Django
```

```text
ASGI

사용자
  ↓
Uvicorn
  ↓
ASGI
  ↓
FastAPI / Starlette
  ↓
async 함수
```

핵심:

> WSGI = 전통적인 동기 Python 웹 표준  
> ASGI = 비동기와 실시간 통신까지 지원하는 Python 웹 표준

---

# 6. FastAPI 이후 주목할 프레임워크

## Litestar

FastAPI와 비슷한 현대적인 ASGI 기반 프레임워크이다.

```python
from litestar import Litestar, get

@get("/")
async def hello() -> dict:
    return {"message": "Hello"}

app = Litestar([hello])
```

주요 특징:

- ASGI 기반
- Dependency Injection
- OpenAPI
- ORM 통합
- Cache
- Session
- Controller
- OpenTelemetry 지원

FastAPI보다 애플리케이션 구조와 여러 부가 기능을 프레임워크 차원에서 폭넓게 제공하려는 방향을 가지고 있다.

---

# 7. Robyn

Robyn은 **Python + Rust** 구조를 사용하는 웹 프레임워크이다.

```python
from robyn import Robyn

app = Robyn(__file__)

@app.get("/")
async def hello(request):
    return "Hello"

app.start(port=8080)
```

구조:

```text
Python 코드
    ↓
Robyn
    ↓
Rust 기반 Runtime
    ↓
HTTP 처리
```

주요 특징:

- Python으로 개발
- Rust 기반 런타임
- 비동기 처리
- 높은 성능을 지향
- Python 개발 편의성과 Rust 성능을 결합

---

# 8. Sanic

Sanic은 처음부터 비동기 처리를 중요하게 설계한 Python 웹 프레임워크이다.

```python
from sanic import Sanic
from sanic.response import text

app = Sanic("app")

@app.get("/")
async def hello(request):
    return text("Hello")
```

FastAPI에서는 일반적으로:

```text
FastAPI
   +
Uvicorn
   ↓
서버 실행
```

Sanic은 자체 서버 기능을 제공한다.

```text
Sanic
 ├─ Web Framework
 └─ Web Server
```

비동기 웹 애플리케이션이나 높은 동시성을 요구하는 서비스에 사용할 수 있다.

---

# 9. Python 웹 프레임워크의 발전 방향

현재는 단순히 FastAPI를 새로운 프레임워크 하나가 대체하는 형태라기보다 목적에 따라 전문화되는 방향으로 발전하고 있다.

```text
                Python Web
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
     API 개발      고성능      Full-stack
        │           │           │
    FastAPI       Robyn       Django
    Litestar    Rust Core
        │
        ↓
 DI / ORM / Cache
 OpenAPI
 Observability
```

주요 흐름은 다음과 같다.

### 개발 생산성

FastAPI와 Litestar처럼 타입 힌트, 데이터 검증, 자동 문서화 등을 적극적으로 활용한다.

### 비동기 처리

ASGI를 기반으로 `async / await`, WebSocket 등의 기능을 활용한다.

### Python + Rust

Python의 편리한 개발 환경을 유지하면서 성능이 중요한 부분을 Rust 등으로 구현하는 방식도 등장하고 있다.

### 프레임워크 통합 기능 증가

단순 HTTP 처리뿐만 아니라 다음 기능들이 중요해지고 있다.

```text
Dependency Injection
ORM
Cache
Session
OpenAPI
Authentication
Observability
WebSocket
```

---

# 10. 추천 학습 순서

현재 Python 백엔드를 공부한다면 다음 순서로 학습할 수 있다.

```text
1. Python
   ↓
2. Type Hint
   ↓
3. async / await
   ↓
4. HTTP / REST API
   ↓
5. FastAPI
   ↓
6. Pydantic
   ↓
7. ASGI / Uvicorn
   ↓
8. SQLAlchemy / Database
   ↓
9. Docker
   ↓
10. Litestar 비교
   ↓
11. Robyn 등 고성능 프레임워크 탐색
```

FastAPI를 먼저 학습하면 Python의 현대적인 백엔드 구조를 이해하는 데 도움이 된다.

그 후 Litestar와 비교하면서 프레임워크 구조를 공부하고, Robyn을 통해 Python과 Rust를 결합한 고성능 웹 서버 구조까지 확장해서 살펴볼 수 있다.

---

# 핵심 요약

```text
FastAPI
= Python API 개발 프레임워크

Uvicorn
= FastAPI 등의 ASGI 앱을 실행하는 서버

ASGI
= 웹 서버 ↔ Python 웹 앱 연결 규칙
  + 비동기 지원

WSGI
= 전통적인 동기 중심 Python 웹 인터페이스

Litestar
= FastAPI와 경쟁하는 기능이 풍부한 ASGI 프레임워크

Robyn
= Python + Rust 기반 고성능 웹 프레임워크

Sanic
= Async-first Python 웹 프레임워크
```

가장 중요한 관계는 다음과 같이 기억한다.

```text
Client
   ↓ HTTP
Uvicorn
   ↓ ASGI
FastAPI
   ↓
Python Application
   ↓
Database / AI / External API
```