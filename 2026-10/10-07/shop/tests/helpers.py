from app.config import Settings
from app.models.product import Product, ProductCreate


def test_settings() -> Settings:
    return Settings(
        mysql_host="localhost",
        mysql_user="test_user",
        mysql_password="test-only-password",
        mysql_database="test_shop",
    )


class MemoryProductReader:
    def __init__(self, products: list[Product]) -> None:
        self.products = products
        self.saved: list[ProductCreate] = []

    def list_products(self, keyword: str = "") -> list[Product]:
        return [product for product in self.products if keyword in product.name.lower()]

    def get_by_id(self, product_id: int) -> Product | None:
        return next((product for product in self.products if product.id == product_id), None)

    def save_product(self, product: ProductCreate) -> None:
        self.saved.append(product)
