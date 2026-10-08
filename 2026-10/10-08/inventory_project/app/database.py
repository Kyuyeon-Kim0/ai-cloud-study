import mysql.connector
from mysql.connector import MySQLConnection

from app.config import get_settings


def get_connection() -> MySQLConnection:
    settings = get_settings()
    connection: MySQLConnection = mysql.connector.connect(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        database=settings.mysql_database,
        connection_timeout=5,
        charset="utf8mb4",
    )

    return connection
