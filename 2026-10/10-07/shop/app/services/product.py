from typing import Protocol

from app.models.product import Product, ProductCreate


class ProductStore(Protocol):
    """서비스에 필요한 최소 저장소 계약."""

    def list_products(self, keyword: str = "") -> list[Product]: ...

    def get_by_id(self, product_id: int) -> Product | None: ...

    def save_product(self, product: ProductCreate) -> None: ...


class ProductService:
    def __init__(self, repository: ProductStore) -> None:
        self._repository = repository

    def search_products(self, query: str = "") -> list[Product]:
        """기존 동작대로 앞뒤 공백과 대소문자를 무시해 부분 검색한다."""
        keyword = query.strip().lower()
        candidates = self._repository.list_products(keyword)
        if not keyword:
            return candidates
        return [product for product in candidates if keyword in product.name.lower()]

    def get_product(self, product_id: int) -> Product | None:
        """없는 상품은 None으로 반환하고 HTTP 상태는 라우터가 결정한다."""
        return self._repository.get_by_id(product_id)
    def register_product(self, product: ProductCreate) -> None:
        self._repository.save_product(product)
