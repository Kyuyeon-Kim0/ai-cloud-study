from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Path, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, Settings, get_settings
from app.models.product import ProductCreate
from app.repositories.product import ProductInputError, ProductRepository
from app.services.product import ProductService


router = APIRouter()
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_product_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> ProductService:
    return ProductService(ProductRepository(settings))


@router.get("/", response_class=HTMLResponse, name="product_list")
def home(
    request: Request,
    service: Annotated[ProductService, Depends(get_product_service)],
    q: Annotated[str, Query(max_length=200)] = "",
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="products/list.html",
        context={"products": service.search_products(q), "keyword": q},
    )


@router.get("/products/{product_id}", response_class=HTMLResponse, name="product_detail")
def product_detail(
    request: Request,
    product_id: Annotated[int, Path(gt=0)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> HTMLResponse:
    item = service.get_product(product_id)
    if item is None:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return templates.TemplateResponse(
        request=request,
        name="products/detail.html",
        context={"product": item},
    )


@router.get("/product", response_class=HTMLResponse, name="product_form")
def product_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="product.html", context={})


@router.post("/product", name="product_create", response_class=RedirectResponse, status_code=303)
def product_create(
    request: Request,
    product: Annotated[ProductCreate, Form()],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> RedirectResponse:
    try:
        service.register_product(product)
    except ProductInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse(url=str(request.url_for("product_form")), status_code=303)
