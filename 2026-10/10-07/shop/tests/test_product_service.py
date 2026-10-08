import unittest
from decimal import Decimal
from unittest.mock import MagicMock

from pydantic import ValidationError

from app.models.product import Product
from app.services.product import ProductService
from tests.helpers import MemoryProductReader


class ProductServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.products = [
            Product(id=1, name="노트북", price=1200000),
            Product(id=2, name="USB Mouse", price=30000),
            Product(id=3, name="키보드", price=50000),
        ]
        self.service = ProductService(MemoryProductReader(self.products))

    def test_empty_or_whitespace_query_returns_all_products(self) -> None:
        for query in ("", "   ", "\t\n"):
            with self.subTest(query=query):
                self.assertEqual(self.service.search_products(query), self.products)

    def test_partial_search_ignores_case_and_surrounding_whitespace(self) -> None:
        self.assertEqual(self.service.search_products("  mOuSe  "), [self.products[1]])
        self.assertEqual(self.service.search_products("노트"), [self.products[0]])

    def test_no_match_and_empty_repository(self) -> None:
        self.assertEqual(self.service.search_products("없는상품"), [])
        self.assertEqual(ProductService(MemoryProductReader([])).search_products(), [])

    def test_detail_returns_matching_product_or_none(self) -> None:
        self.assertEqual(self.service.get_product(2), self.products[1])
        self.assertIsNone(self.service.get_product(999))

    def test_search_normalizes_keyword_before_repository_call(self) -> None:
        repository = MagicMock()
        repository.list_products.return_value = []
        ProductService(repository).search_products("  mOuSe  ")
        repository.list_products.assert_called_once_with("mouse")

    def test_unicode_final_sigma_keeps_python_search_behavior(self) -> None:
        repository = MagicMock()
        greek = Product(id=1, name="ΟΣ", price=100)
        repository.list_products.return_value = [greek, self.products[0]]
        self.assertEqual(ProductService(repository).search_products("ΟΣ"), [greek])

    def test_final_filter_removes_sql_lowercase_false_positive(self) -> None:
        repository = MagicMock()
        repository.list_products.return_value = [Product(id=1, name="İX", price=100)]
        self.assertEqual(ProductService(repository).search_products("ix"), [])


class ProductValidationTests(unittest.TestCase):
    def test_invalid_product_data(self) -> None:
        defaults = {"id": 1, "name": "상품", "price": 100}
        for field, value in (
            ("id", 0), ("id", True), ("id", "1"),
            ("name", " "), ("name", None),
            ("price", -1), ("price", "NaN"), ("price", "Infinity"),
        ):
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                Product.model_validate({**defaults, field: value})

    def test_decimal_price_is_preserved_and_free_products_are_allowed(self) -> None:
        self.assertEqual(Product(id=1, name="상품", price="1234.50").price, Decimal("1234.50"))
        self.assertEqual(Product(id=2, name="무료", price=0).price, Decimal(0))
