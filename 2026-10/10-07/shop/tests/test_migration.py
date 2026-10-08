import unittest
from unittest.mock import MagicMock, patch

from mysql.connector import Error

from migrate_shop_db import ColumnInfo, foreign_key_exists, migrate
from tests.helpers import test_settings


class MigrationTests(unittest.TestCase):
    def run_migration(self, complete: bool) -> tuple[MagicMock, MagicMock]:
        connection = MagicMock()
        cursor = connection.cursor.return_value
        cursor.fetchone.return_value = (0,)
        code = ColumnInfo("varchar", False, 20, "utf8mb4", "utf8mb4_unicode_ci")
        with (
            patch("app.database.mysql.connector.connect", return_value=connection),
            patch("migrate_shop_db.table_info", side_effect=[
                ("InnoDB", "utf8mb4_unicode_ci"),
                ("InnoDB", "utf8mb4_unicode_ci") if complete else None,
            ]),
            patch("migrate_shop_db.column_info", side_effect=[
                ColumnInfo("text", False, 65535, "utf8mb4", "utf8mb4_unicode_ci"), code, code,
            ] if complete else [None, None]),
            patch("migrate_shop_db.foreign_key_exists", return_value=complete),
            patch("builtins.print"),
        ):
            migrate(test_settings())
        return connection, cursor

    def test_first_run_adds_missing_schema_and_cleans_up(self) -> None:
        connection, cursor = self.run_migration(complete=False)
        statements = [call.args[0] for call in cursor.execute.call_args_list]
        self.assertTrue(any(sql.startswith("CREATE TABLE managers") for sql in statements))
        self.assertEqual(sum("ADD COLUMN" in sql for sql in statements), 2)
        self.assertTrue(any("ADD CONSTRAINT" in sql for sql in statements))
        self.assertFalse(any("ENGINE=InnoDB" in sql and sql.startswith("ALTER") for sql in statements))
        connection.commit.assert_called_once_with()
        cursor.close.assert_called_once_with()
        connection.close.assert_called_once_with()

    def test_complete_schema_skips_all_ddl_and_backfills(self) -> None:
        connection, cursor = self.run_migration(complete=True)
        self.assertEqual(cursor.execute.call_count, 3)
        for call in cursor.execute.call_args_list:
            self.assertTrue(call.args[0].startswith("INSERT INTO managers"))
            code, name, phone, update_name, update_phone = call.args[1]
            self.assertEqual(name, update_name)
            self.assertEqual(phone, update_phone)
            self.assertIn(code, ("A", "B", "C"))
        cursor.executemany.assert_not_called()
        connection.commit.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_missing_product_table_fails_before_writes(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        cursor.fetchone.return_value = None
        with self.assertRaisesRegex(RuntimeError, "products"):
            migrate(test_settings())
        self.assertEqual(cursor.execute.call_count, 1)
        cursor.executemany.assert_not_called()
        connect.return_value.rollback.assert_called_once_with()
        cursor.close.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_cursor_creation_failure_rolls_back_and_closes(self, connect: MagicMock) -> None:
        connect.return_value.cursor.side_effect = Error("simulated cursor failure")
        with self.assertRaises(Error):
            migrate(test_settings())
        connect.return_value.rollback.assert_called_once_with()
        connect.return_value.close.assert_called_once_with()

    @patch("app.database.mysql.connector.connect")
    def test_orphan_manager_prevents_foreign_key_creation(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        code = ColumnInfo("varchar", False, 20, "utf8mb4", "utf8mb4_unicode_ci")
        cursor.fetchone.return_value = (1,)
        with (
            patch("migrate_shop_db.table_info", return_value=("InnoDB", "utf8mb4_unicode_ci")),
            patch("migrate_shop_db.column_info", side_effect=[
                ColumnInfo("text", False, 65535, "utf8mb4", "utf8mb4_unicode_ci"), code, code,
            ]),
            patch("migrate_shop_db.foreign_key_exists", return_value=False),
            self.assertRaisesRegex(RuntimeError, "담당자"),
        ):
            migrate(test_settings())
        self.assertFalse(any("ADD CONSTRAINT" in call.args[0] for call in cursor.execute.call_args_list))
        connect.return_value.commit.assert_not_called()
        connect.return_value.rollback.assert_called_once_with()

    def test_conflicting_foreign_key_definition_is_rejected(self) -> None:
        cursor = MagicMock()
        cursor.fetchall.return_value = [("manager_code", "managers", "manager_code", "CASCADE", "CASCADE")]
        with self.assertRaisesRegex(RuntimeError, "외래키"):
            foreign_key_exists(cursor, "fk_products_manager")

    @patch("app.database.mysql.connector.connect")
    def test_incompatible_column_stops_before_writes(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        with (
            patch("migrate_shop_db.table_info", side_effect=[("InnoDB", "utf8mb4_unicode_ci"), None]),
            patch("migrate_shop_db.column_info", side_effect=[
                ColumnInfo("varchar", True, 100, "utf8mb4", "utf8mb4_unicode_ci"), None,
            ]),
            patch("migrate_shop_db.foreign_key_exists", return_value=False),
            self.assertRaisesRegex(RuntimeError, "TEXT"),
        ):
            migrate(test_settings())
        cursor.execute.assert_not_called()
        cursor.executemany.assert_not_called()
        connect.return_value.commit.assert_not_called()

    @patch("app.database.mysql.connector.connect")
    def test_collation_mismatch_stops_before_writes(self, connect: MagicMock) -> None:
        cursor = connect.return_value.cursor.return_value
        with (
            patch("migrate_shop_db.table_info", return_value=("InnoDB", "utf8mb4_unicode_ci")),
            patch("migrate_shop_db.column_info", side_effect=[
                None,
                ColumnInfo("varchar", True, 20, "utf8mb4", "utf8mb4_bin"),
                ColumnInfo("varchar", False, 20, "utf8mb4", "utf8mb4_unicode_ci"),
            ]),
            patch("migrate_shop_db.foreign_key_exists", return_value=False),
            self.assertRaisesRegex(RuntimeError, "콜레이션"),
        ):
            migrate(test_settings())
        cursor.execute.assert_not_called()
        cursor.executemany.assert_not_called()
