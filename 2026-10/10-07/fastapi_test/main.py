from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# 메인 페이지
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# 상품 페이지
@app.get("/sub")
def sub(request: Request):

    # Python 딕셔너리 구조의 샘플 데이터
    products = [
        {"name": "노트북", "price": 1200000},
        {"name": "키보드", "price": 50000},
        {"name": "마우스", "price": 30000}
    ]

    return templates.TemplateResponse(
        request=request,
        name="sub.html",
        context={"products": products}
    )