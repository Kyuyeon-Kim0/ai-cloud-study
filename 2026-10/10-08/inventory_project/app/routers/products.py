from typing import Annotated

from fastapi import APIRouter, Path, Query, Response

from app.schemas import Movement, Product, ProductCreate, ProductInput, StockInput
from app.services import product_service as service

router = APIRouter(prefix="/api", tags=["Inventory"])
ProductId = Annotated[int, Path(gt=0)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]


@router.get("/products", response_model=list[Product])
def read_products(q: Annotated[str, Query(max_length=100)] = "", low_stock: bool = False,
                  limit: Limit = 100, offset: Offset = 0):
    return service.get_products(q.strip(), low_stock, limit, offset)


@router.post("/products", response_model=Product, status_code=201)
def create_product(data: ProductCreate):
    return service.create_product(data)


@router.get("/products/{product_id}", response_model=Product)
def read_product(product_id: ProductId):
    return service.get_product(product_id)


@router.put("/products/{product_id}", response_model=Product)
def update_product(product_id: ProductId, data: ProductInput):
    return service.update_product(product_id, data)


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: ProductId):
    service.delete_product(product_id)
    return Response(status_code=204)


@router.post("/products/{product_id}/stock", response_model=Product)
def change_stock(product_id: ProductId, data: StockInput):
    return service.change_stock(product_id, data)


@router.get("/movements", response_model=list[Movement])
def read_movements(product_id: Annotated[int | None, Query(gt=0)] = None,
                   limit: Limit = 100, offset: Offset = 0):
    return service.get_movements(product_id, limit, offset)


@router.get("/summary")
def read_summary():
    return service.get_summary()
