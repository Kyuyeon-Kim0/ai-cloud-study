import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from mysql.connector import Error

from app.repositories.product import ProductDataError, ProductRepository, ProductStorageError
from tests.helpers import test_settings


class ProductRepositoryTests(unittest.TestCase):
    @patch("app.database.mysql.connector.connect")
    def test_cursor_cleanup_does_not_replace_query_error(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        original = Error("query failed", errno=1064)
        cursor.execute.side_effect = original
        cursor.close.side_effect = Error("close failed")
        with self.assertRaises(ProductStorageError) as result:
            ProductRepository(test_settings()).list_products()
        self.assertIs(result.exception.__cause__, original)
        connect.return_value.close.assert_called_once_with()
    @patch("app.database.mysql.connector.connect")
    def test_unicode_keyword_leaves_final_filtering_to_service(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchall.return_value = []
        ProductRepository(test_settings()).list_products("ος")
        cursor.execute.assert_called_once_with("SELECT id, name, price FROM products ORDER BY id")

    @patch("app.database.mysql.connector.connect")
    def test_search_binds_literal_keyword(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchall.return_value = []
        keyword = "%_'; DROP TABLE products; --"
        self.assertEqual(ProductRepository(test_settings()).list_products(keyword), [])
        query, parameters = cursor.execute.call_args.args
        self.assertIn("LOCATE", query)
        self.assertNotIn(keyword, query)
        self.assertEqual(parameters, (keyword,))
        self.assertTrue(query.endswith("ORDER BY id"))

    @patch("app.database.mysql.connector.connect")
    def test_rows_are_validated_and_resources_are_closed(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchall.return_value = [{"id": 1, "name": "노트북", "price": 1200000}]
        products = ProductRepository(test_settings()).list_products()
        self.assertEqual(products[0].price, Decimal(1200000))
        self.assertEqual(products[0].name, "노트북")
        cursor.execute.assert_called_once_with("SELECT id, name, price FROM products ORDER BY id")
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_detail_uses_parameterized_query_and_closes_resources(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchone.return_value = {"id": 2, "name": "마우스", "price": 30000}
        product = ProductRepository(test_settings()).get_by_id(2)
        self.assertIsNotNone(product)
        assert product is not None
        self.assertEqual(product.id, 2)
        cursor.execute.assert_called_once_with(
            "SELECT id, name, price FROM products WHERE id = %s", (2,),
        )
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_detail_missing_product_returns_none(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchone.return_value = None
        self.assertIsNone(ProductRepository(test_settings()).get_by_id(999))
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_detail_invalid_data_closes_resources(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchone.return_value = {"id": 1, "name": "상품", "price": -1}
        with self.assertRaises(ProductDataError):
            ProductRepository(test_settings()).get_by_id(1)
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_detail_query_failure_closes_resources(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.execute.side_effect = Error("query failed")
        with self.assertRaises(ProductStorageError):
            ProductRepository(test_settings()).get_by_id(1)
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_invalid_rows_close_resources(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchall.return_value = [{"id": 1, "name": "상품", "price": -100}]
        with self.assertRaises(ProductDataError):
            ProductRepository(test_settings()).list_products()
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()
