from mysql.connector import MySQLConnection
from mysql.connector.errors import Error

from app.database import get_connection


def main() -> None:
    connection: MySQLConnection | None = None

    try:
        connection = get_connection()

        if connection.is_connected():
            print("MySQL 연결 성공")

    except Error as exc:
        print(f"MySQL 연결 실패 (오류 코드: {exc.errno}). 환경 설정과 서버 상태를 확인하세요.")

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("MySQL 연결 종료")


if __name__ == "__main__":
    main()
