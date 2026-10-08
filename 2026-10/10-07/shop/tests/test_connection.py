import os
import unittest
from unittest.mock import MagicMock, patch

from mysql.connector import Error

from app.config import get_settings
from app.database import get_connection
from app.repositories.product import ProductRepository, ProductStorageError
from tests.helpers import test_settings


class ConnectionTests(unittest.TestCase):
    @patch("app.database.mysql.connector.connect")
    def test_cleanup_failure_preserves_initial_error(self, connect: MagicMock) -> None:
        connect.return_value.close.side_effect = Error("cleanup failed")
        with self.assertRaisesRegex(RuntimeError, "initial failure"):
            with get_connection(test_settings()):
                raise RuntimeError("initial failure")

    @patch("app.database.mysql.connector.connect")
    def test_connection_closes_after_failure(self, connect: MagicMock) -> None:
        with self.assertRaisesRegex(RuntimeError, "operation failed"):
            with get_connection(test_settings()):
                raise RuntimeError("operation failed")
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_cursor_creation_failure_still_closes_connection(self, connect: MagicMock) -> None:
        connect.return_value.cursor.side_effect = Error("cursor unavailable")
        with self.assertRaises(ProductStorageError):
            ProductRepository(test_settings()).list_products()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_query_failure_closes_cursor_and_connection(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.execute.side_effect = Error("query unavailable")
        with self.assertRaises(ProductStorageError):
            ProductRepository(test_settings()).list_products()
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect", side_effect=Error("connection unavailable"))
    def test_connection_failure_becomes_storage_error(self, connect: MagicMock) -> None:
        with self.assertRaises(ProductStorageError):
            ProductRepository(test_settings()).list_products()


@unittest.skipUnless(
    os.getenv("RUN_MYSQL_INTEGRATION_TESTS") == "1",
    "Set RUN_MYSQL_INTEGRATION_TESTS=1 to use the configured MySQL database.",
)
class MySQLIntegrationTests(unittest.TestCase):
    def test_real_connection(self) -> None:
        with get_connection(get_settings()) as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT 1")
                self.assertEqual(cursor.fetchone(), (1,))
            finally:
                cursor.close()

    def test_real_product_query(self) -> None:
        repository = ProductRepository(get_settings())
        products = repository.list_products()
        ids = [product.id for product in products]
        self.assertEqual(ids, sorted(ids))
        if products:
            self.assertEqual(repository.get_by_id(products[0].id), products[0])
