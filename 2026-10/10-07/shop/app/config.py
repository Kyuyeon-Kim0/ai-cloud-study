"""환경설정과 작업 디렉터리에 독립적인 경로."""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, hide_input_in_errors=True)

    mysql_host: str = Field(min_length=1)
    mysql_port: int = Field(default=3306, ge=1, le=65535)
    mysql_user: str = Field(min_length=1)
    mysql_password: SecretStr
    mysql_database: str = Field(min_length=1)
    mysql_connection_timeout: int = Field(default=5, ge=1, le=60)

    @field_validator("mysql_host", "mysql_user", "mysql_database", mode="before")
    @classmethod
    def strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("mysql_password")
    @classmethod
    def require_password(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("MYSQL_PASSWORD must not be blank")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """프로세스 환경변수를 우선하고 shop/.env로 누락된 값을 채운다."""
    load_dotenv(BASE_DIR / ".env", override=False)
    names = {
        "mysql_host": "MYSQL_HOST",
        "mysql_port": "MYSQL_PORT",
        "mysql_user": "MYSQL_USER",
        "mysql_password": "MYSQL_PASSWORD",
        "mysql_database": "MYSQL_DATABASE",
        "mysql_connection_timeout": "MYSQL_CONNECTION_TIMEOUT",
    }
    values = {field: os.environ[key] for field, key in names.items() if key in os.environ}
    return Settings.model_validate(values)
