import unittest
from unittest.mock import MagicMock, patch

from mysql.connector import Error

from app.models.product import ProductCreate
from app.repositories.product import ProductInputError, ProductRepository, ProductStorageError
from tests.helpers import test_settings


class ProductRegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.product = ProductCreate(name="상품", price=100, description="설명", manager_code="A")

    @patch("app.database.mysql.connector.connect")
    def test_insert_is_parameterized_and_committed(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        ProductRepository(test_settings()).save_product(self.product)
        query, parameters = cursor.execute.call_args.args
        self.assertIn("INSERT INTO products", query)
        self.assertEqual(parameters, ("상품", 100, "설명", "A"))
        connect.return_value.commit.assert_called_once_with()
        connect.return_value.rollback.assert_not_called()
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_insert_failure_rolls_back_and_closes(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.execute.side_effect = Error("insert failed", errno=1054)
        with self.assertRaises(ProductStorageError):
            ProductRepository(test_settings()).save_product(self.product)
        connect.return_value.commit.assert_not_called()
        connect.return_value.rollback.assert_called_once_with()
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_foreign_key_error_is_reported_as_invalid_manager(self, connect: MagicMock) -> None:
        connect.return_value.cursor.return_value.execute.side_effect = Error("unknown manager", errno=1452)
        with self.assertRaises(ProductInputError):
            ProductRepository(test_settings()).save_product(self.product)
        connect.return_value.rollback.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_commit_failure_rolls_back(self, connect: MagicMock) -> None:
        connect.return_value.commit.side_effect = Error("commit failed")
        with self.assertRaises(ProductStorageError):
            ProductRepository(test_settings()).save_product(self.product)
        connect.return_value.rollback.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()
