"""요청마다 생성한 MySQL 연결을 반드시 반환한다."""

from collections.abc import Iterator
from contextlib import contextmanager, suppress
from typing import cast

import mysql.connector
from mysql.connector import Error
from mysql.connector.abstracts import MySQLConnectionAbstract, MySQLCursorAbstract

from app.config import Settings


@contextmanager
def get_connection(settings: Settings) -> Iterator[MySQLConnectionAbstract]:
    connection = cast(
        MySQLConnectionAbstract,
        mysql.connector.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password.get_secret_value(),
            database=settings.mysql_database,
            connection_timeout=settings.mysql_connection_timeout,
        ),
    )
    try:
        yield connection
    except BaseException:
        # 정리 실패가 최초 연결 사용 오류를 덮어쓰지 않도록 한다.
        with suppress(Error):
            connection.close()
        raise
    else:
        connection.close()


@contextmanager
def get_cursor(
    connection: MySQLConnectionAbstract, *, dictionary: bool = False,
) -> Iterator[MySQLCursorAbstract]:
    """저장소와 마이그레이션이 동일한 커서 수명 관리를 사용한다."""
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
    except BaseException:
        with suppress(Error):
            cursor.close()
        raise
    else:
        cursor.close()
