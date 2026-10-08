from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Product(BaseModel):
    """DB에서 읽은 상품을 검증한다. 가격은 부동소수점 오차를 피한다."""

    model_config = ConfigDict(frozen=True, allow_inf_nan=False)

    id: int = Field(gt=0, strict=True)
    name: str = Field(min_length=1, strict=True)
    price: Decimal = Field(ge=0)

    @field_validator("name")
    @classmethod
    def require_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Product name must not be blank")
        return value


class ProductCreate(BaseModel):
    """현재 MySQL VARCHAR(255), INT, TEXT, VARCHAR(20) 스키마에 맞춘 입력."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=255)
    price: int = Field(ge=0, le=2147483647)
    description: str = Field(min_length=1, max_length=65535)
    manager_code: str = Field(min_length=1, max_length=20)

    @field_validator("name", "description", "manager_code", mode="before")
    @classmethod
    def validate_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("문자열 값은 비어 있을 수 없습니다.")
        return value

    @field_validator("description")
    @classmethod
    def validate_description_size(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 65535:
            raise ValueError("상세설명은 UTF-8 기준 65535바이트 이하여야 합니다.")
        return value
