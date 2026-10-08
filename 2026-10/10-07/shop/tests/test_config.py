import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from pydantic import ValidationError

from app.config import Settings, get_settings
from tests.helpers import test_settings


class SettingsTests(unittest.TestCase):
    def test_invalid_values_are_rejected(self) -> None:
        defaults = test_settings().model_dump()
        invalid = [
            ("mysql_host", "   "),
            ("mysql_user", ""),
            ("mysql_database", "\t"),
            ("mysql_password", "   "),
            ("mysql_port", 0),
            ("mysql_port", 65536),
            ("mysql_connection_timeout", 0),
            ("mysql_connection_timeout", 61),
        ]
        for field, value in invalid:
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                Settings.model_validate({**defaults, field: value})

    def test_missing_settings_fail_without_exposing_password(self) -> None:
        secret = "do-not-expose-this-password"
        with self.assertRaises(ValidationError) as result:
            Settings.model_validate({"mysql_password": secret})
        self.assertNotIn(secret, str(result.exception))
        self.assertNotIn("test-only-password", repr(test_settings()))

    def test_environment_configuration(self) -> None:
        env = {
            "MYSQL_HOST": " test-host ",
            "MYSQL_PORT": "3307",
            "MYSQL_USER": "test-user",
            "MYSQL_PASSWORD": "test-password",
            "MYSQL_DATABASE": "test-database",
        }
        get_settings.cache_clear()
        try:
            with patch.dict(os.environ, env, clear=True), patch("app.config.load_dotenv") as load:
                settings = get_settings()
                self.assertEqual(settings.mysql_host, "test-host")
                self.assertEqual(settings.mysql_port, 3307)
                self.assertEqual(settings.mysql_connection_timeout, 5)
                self.assertIs(get_settings(), settings)
                self.assertFalse(load.call_args.kwargs["override"])
        finally:
            get_settings.cache_clear()

    def test_dotenv_fills_missing_values_without_overriding_environment(self) -> None:
        get_settings.cache_clear()
        try:
            with TemporaryDirectory() as directory:
                root = Path(directory)
                (root / ".env").write_text(
                    "MYSQL_HOST=file-host\nMYSQL_USER=file-user\n"
                    "MYSQL_PASSWORD=file-password\nMYSQL_DATABASE=file-database\n",
                    encoding="utf-8",
                )
                with patch.dict(os.environ, {"MYSQL_HOST": "environment-host"}, clear=True):
                    with patch("app.config.BASE_DIR", root):
                        settings = get_settings()
                self.assertEqual(settings.mysql_host, "environment-host")
                self.assertEqual(settings.mysql_user, "file-user")
                self.assertEqual(settings.mysql_database, "file-database")
        finally:
            get_settings.cache_clear()
