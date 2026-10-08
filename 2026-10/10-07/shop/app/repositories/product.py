from collections.abc import Iterator
from contextlib import contextmanager, suppress

from mysql.connector import Error
from mysql.connector.errorcode import ER_NO_REFERENCED_ROW_2
from mysql.connector.abstracts import MySQLCursorAbstract
from pydantic import ValidationError

from app.config import Settings
from app.database import get_connection, get_cursor
from app.models.product import Product, ProductCreate


class ProductStorageError(RuntimeError):
    """DB 연결 또는 조회 실패."""


class ProductDataError(RuntimeError):
    """저장된 상품 데이터가 상품 규칙을 위반함."""


class ProductInputError(ValueError):
    """상품 등록 시 저장소 제약을 위반한 입력."""


class ProductRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @contextmanager
    def _cursor(self) -> Iterator[MySQLCursorAbstract]:
        """조회 종류와 관계없이 자원 정리와 오류 변환을 적용한다."""
        try:
            with get_connection(self._settings) as connection:
                with get_cursor(connection, dictionary=True) as cursor:
                    yield cursor
        except Error as exc:
            raise ProductStorageError("상품 저장소에 접근할 수 없습니다.") from exc
        except ValidationError as exc:
            raise ProductDataError("상품 데이터가 올바르지 않습니다.") from exc

    def list_products(self, keyword: str = "") -> list[Product]:
        """검색 후보를 반환한다. Unicode의 최종 일치 판정은 서비스가 한다."""
        with self._cursor() as cursor:
            query = "SELECT id, name, price FROM products"
            # MySQL과 Python의 Unicode 소문자 규칙이 다른 문자는 전체 후보 조회.
            sql_search = bool(keyword) and all(
                char.isascii() or "\uac00" <= char <= "\ud7a3" for char in keyword
            )
            if sql_search:
                # LIKE의 %와 _를 와일드카드로 해석하지 않는 부분 검색.
                query += " WHERE LOCATE(CAST(%s AS BINARY), CAST(LOWER(name) AS BINARY)) > 0"
                cursor.execute(query + " ORDER BY id", (keyword,))
            else:
                cursor.execute(query + " ORDER BY id")
            return [Product.model_validate(row) for row in cursor.fetchall()]

    def get_by_id(self, product_id: int) -> Product | None:
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT id, name, price FROM products WHERE id = %s",
                (product_id,),
            )
            row = cursor.fetchone()
            return Product.model_validate(row) if row is not None else None

    def save_product(self, product: ProductCreate) -> None:
        try:
            with get_connection(self._settings) as connection:
                try:
                    with get_cursor(connection) as cursor:
                        cursor.execute(
                            "INSERT INTO products (name, price, description, manager_code) "
                            "VALUES (%s, %s, %s, %s)",
                            (product.name, product.price, product.description, product.manager_code),
                        )
                    connection.commit()
                except BaseException:
                    with suppress(Error):
                        connection.rollback()
                    raise
        except Error as exc:
            if exc.errno == ER_NO_REFERENCED_ROW_2:
                raise ProductInputError("등록되지 않은 담당자 코드입니다.") from exc
            raise ProductStorageError("상품을 저장할 수 없습니다.") from exc
