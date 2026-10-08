from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProductInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    product_name: str = Field(min_length=1, max_length=100)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    min_stock: int = Field(default=0, ge=0, le=2_147_483_647, strict=True)


class ProductCreate(ProductInput):
    quantity: int = Field(default=0, ge=0, le=2_147_483_647, strict=True)


class Product(ProductInput):
    product_id: int
    quantity: int
    created_at: datetime


class StockInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    direction: Literal["in", "out"]
    quantity: int = Field(gt=0, le=2_147_483_647, strict=True)
    reason: str = Field(min_length=1, max_length=200)


class Movement(BaseModel):
    movement_id: int
    product_id: int
    product_name: str
    change_amount: int
    resulting_quantity: int
    reason: str
    created_at: datetime
