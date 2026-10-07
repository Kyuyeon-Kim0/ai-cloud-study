# FastAPI 상품 목록 실습

학습 날짜: 2026-10-07 (수요일)

FastAPI와 Jinja2 템플릿으로 메인 페이지와 상품 목록 페이지를 만드는 실습입니다. Python의 리스트·딕셔너리 데이터를 HTML 템플릿에 전달하고, 반복문으로 화면에 표시하는 방법을 연습합니다.

## 주요 기능

- 메인 페이지에서 `Hello` 문구와 상품 목록 링크 표시
- 상품 목록 페이지에서 상품명과 가격 표시
- 링크를 통한 메인 페이지와 상품 목록 페이지 이동

상품 데이터는 `main.py`의 `products` 리스트에 정의되어 있습니다. 데이터베이스 연결이나 상품 추가·수정·삭제 기능은 구현되어 있지 않습니다.

## 준비 사항

- Windows 및 PowerShell
- Python 3와 `pip`
- 패키지 설치를 위한 인터넷 연결

필요한 패키지는 `fastapi`, `uvicorn`, `jinja2`입니다. 이 프로젝트에는 패키지 버전을 고정한 파일이 없습니다.

## 파일 구성

| 파일 또는 폴더 | 역할 |
| --- | --- |
| `main.py` | FastAPI 앱, URL 경로, 상품 데이터 및 템플릿 렌더링 |
| `templates/index.html` | 메인 페이지와 상품 목록 링크 |
| `templates/sub.html` | 상품 목록을 반복해서 표시하는 템플릿 |
| `README.md` | 프로젝트 설명 및 설치·실행 안내 |

## 설치 및 실행

PowerShell에서 프로젝트 폴더로 이동한 뒤 실행합니다. 템플릿 경로가 `templates`라는 상대 경로이므로 반드시 이 폴더에서 서버를 시작하세요.

```powershell
cd C:\ai-starter\2026-10\10-07\fastapi_test
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install fastapi uvicorn jinja2
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

가상환경의 Python을 직접 실행하므로 별도의 가상환경 활성화는 필요하지 않습니다. `main:app`은 `main.py`에 정의된 `app` 객체를 뜻하며, `--reload`는 코드 변경 시 서버를 자동으로 다시 불러옵니다.

서버를 실행한 뒤 브라우저에서 <http://127.0.0.1:8000>에 접속합니다. 서버를 종료하려면 실행 중인 터미널에서 `Ctrl+C`를 누릅니다.

## 사용 방법

| 주소 | 내용 |
| --- | --- |
| <http://127.0.0.1:8000/> | 메인 페이지 |
| <http://127.0.0.1:8000/sub> | 상품 목록 페이지 |
| <http://127.0.0.1:8000/docs> | FastAPI 자동 API 문서 |

1. 메인 페이지에서 **상품 목록 보기**를 클릭합니다.
2. 상품 목록 페이지에서 상품명과 가격을 확인합니다.
3. **메인으로**를 클릭해 처음 화면으로 돌아갑니다.

`/`와 `/sub`는 HTML 페이지를 반환합니다. `/docs`에서 경로를 확인할 수 있지만, 상품 목록을 JSON으로 반환하는 별도 API는 없습니다.

## 동작 흐름

1. `/` 요청을 받으면 `index()`가 `templates/index.html`을 렌더링합니다.
2. `/sub` 요청을 받으면 `sub()`가 상품 리스트를 생성합니다.
3. `context={"products": products}`로 리스트를 `templates/sub.html`에 전달합니다.
4. 템플릿의 `{% for product in products %}` 반복문이 각 상품의 `name`과 `price`를 표시합니다.

상품 데이터를 바꾸려면 `main.py`의 `products` 리스트를 수정하고 상품 목록 페이지를 새로고침합니다.

## 문제 해결

| 증상 | 확인할 내용 |
| --- | --- |
| `No module named fastapi`, `uvicorn`, `jinja2` | 설치 명령을 다시 실행하고 `.venv`의 Python으로 서버를 시작했는지 확인 |
| `Could not import module "main"` | 현재 위치가 `main.py`가 있는 `fastapi_test` 폴더인지 확인 |
| `TemplateNotFound` | 프로젝트 폴더에서 실행했는지, `templates/index.html`과 `templates/sub.html`이 있는지 확인 |
| 8000 포트를 사용할 수 없음 | 실행 명령 끝에 `--port 8001`을 추가하고 `http://127.0.0.1:8001`로 접속 |
| 브라우저에서 접속되지 않음 | 터미널에서 서버가 실행 중인지, 오류 메시지가 있는지 확인 |
