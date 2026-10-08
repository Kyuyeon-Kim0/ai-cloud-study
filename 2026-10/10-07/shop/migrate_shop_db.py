"""환경설정의 DB를 대상으로 수동 실행하는 상품 담당자 마이그레이션.

실행: shop 디렉터리에서 python migrate_shop_db.py
이미 적용된 컬럼·엔진·외래키 변경은 건너뛴다.
MySQL DDL은 암묵적으로 커밋되어 rollback으로 전체 구조를 되돌릴 수 없다.
"""

import re
from dataclasses import dataclass
from typing import cast

from mysql.connector.abstracts import MySQLCursorAbstract

from app.config import Settings, get_settings
from app.database import get_connection, get_cursor


MANAGERS: tuple[tuple[str, str, str], ...] = (
    ("A", "김철수", "010-1111-1111"),
    ("B", "이영희", "010-2222-2222"),
    ("C", "박민수", "010-3333-3333"),
)


@dataclass(frozen=True)
class ColumnInfo:
    data_type: str
    nullable: bool
    length: int | None
    charset: str | None
    collation: str | None


def table_info(cursor: MySQLCursorAbstract, table_name: str) -> tuple[str, str] | None:
    cursor.execute(
        "SELECT ENGINE, TABLE_COLLATION FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s",
        (table_name,),
    )
    return cast(tuple[str, str] | None, cursor.fetchone())


def column_info(
    cursor: MySQLCursorAbstract, table_name: str, column_name: str,
) -> ColumnInfo | None:
    cursor.execute(
        "SELECT DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH, "
        "CHARACTER_SET_NAME, COLLATION_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
        (table_name, column_name),
    )
    row = cast(tuple[str, str, int | None, str | None, str | None] | None, cursor.fetchone())
    if row is None:
        return None
    return ColumnInfo(row[0], row[1] == "YES", row[2], row[3], row[4])


def foreign_key_exists(cursor: MySQLCursorAbstract, constraint_name: str) -> bool:
    cursor.execute(
        """
        SELECT k.COLUMN_NAME, k.REFERENCED_TABLE_NAME, k.REFERENCED_COLUMN_NAME,
               r.UPDATE_RULE, r.DELETE_RULE
        FROM information_schema.KEY_COLUMN_USAGE AS k
        JOIN information_schema.REFERENTIAL_CONSTRAINTS AS r
          ON r.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA
         AND r.TABLE_NAME = k.TABLE_NAME
         AND r.CONSTRAINT_NAME = k.CONSTRAINT_NAME
        WHERE k.CONSTRAINT_SCHEMA = DATABASE()
          AND k.TABLE_NAME = 'products' AND k.CONSTRAINT_NAME = %s
        ORDER BY k.ORDINAL_POSITION
        """,
        (constraint_name,),
    )
    rows = cursor.fetchall()
    if not rows:
        return False
    expected = [("manager_code", "managers", "manager_code", "CASCADE", "RESTRICT")]
    if rows != expected:
        raise RuntimeError("기존 fk_products_manager 정의가 목표 외래키와 다릅니다.")
    return True


def _identifier(value: str) -> str:
    """메타데이터의 문자셋·콜레이션만 검증하여 SQL 정의에 사용한다."""
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise RuntimeError("지원하지 않는 문자셋 또는 콜레이션 이름입니다.")
    return value


def _seed_managers(cursor: MySQLCursorAbstract) -> None:
    # executemany의 INSERT 일괄 변환은 UPDATE 절의 추가 매개변수를 처리하지 못한다.
    # 담당자 3명은 execute로 저장하여 INSERT와 UPDATE의 5개 값을 모두 바인딩한다.
    for code, name, phone in MANAGERS:
        cursor.execute(
            "INSERT INTO managers (manager_code, name, phone) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE name = %s, phone = %s",
            (code, name, phone, name, phone),
        )


def _migrate_schema(cursor: MySQLCursorAbstract) -> None:
    products_table = table_info(cursor, "products")
    if products_table is None:
        raise RuntimeError("products 테이블이 먼저 준비되어 있어야 합니다.")
    managers_table = table_info(cursor, "managers")
    description = column_info(cursor, "products", "description")
    manager_code = column_info(cursor, "products", "manager_code")
    manager_key = column_info(cursor, "managers", "manager_code") if managers_table else None
    has_foreign_key = foreign_key_exists(cursor, "fk_products_manager")

    if description is not None and description.data_type != "text":
        raise RuntimeError("기존 products.description은 TEXT 타입이어야 합니다.")
    for column in (manager_code, manager_key):
        if column is not None and (column.data_type != "varchar" or column.length != 20):
            raise RuntimeError("기존 manager_code는 VARCHAR(20) 타입이어야 합니다.")
    if managers_table and manager_key is None:
        raise RuntimeError("기존 managers 테이블에 manager_code가 없습니다.")

    collation = _identifier(
        manager_key.collation if manager_key and manager_key.collation else products_table[1]
    )
    charset = _identifier(
        manager_key.charset if manager_key and manager_key.charset else collation.split("_", 1)[0]
    )
    if manager_code and (manager_code.charset != charset or manager_code.collation != collation):
        raise RuntimeError("상품과 담당자 manager_code의 문자셋·콜레이션이 다릅니다.")
    code_definition = f"VARCHAR(20) CHARACTER SET {charset} COLLATE {collation}"

    if managers_table is None:
        cursor.execute(
            "CREATE TABLE managers (manager_code VARCHAR(20) PRIMARY KEY, "
            "name VARCHAR(100) NOT NULL, phone VARCHAR(30) NOT NULL) "
            f"ENGINE=InnoDB DEFAULT CHARACTER SET {charset} COLLATE {collation}"
        )
    elif managers_table[0].lower() != "innodb":
        cursor.execute("ALTER TABLE managers ENGINE=InnoDB")
    if products_table[0].lower() != "innodb":
        cursor.execute("ALTER TABLE products ENGINE=InnoDB")

    _seed_managers(cursor)

    if description is None:
        cursor.execute("ALTER TABLE products ADD COLUMN description TEXT NULL AFTER price")
    if description is None or description.nullable:
        cursor.execute("UPDATE products SET description = '' WHERE description IS NULL")
        cursor.execute("ALTER TABLE products MODIFY COLUMN description TEXT NOT NULL")

    if manager_code is None:
        cursor.execute(
            f"ALTER TABLE products ADD COLUMN manager_code {code_definition} NULL AFTER description"
        )
    if manager_code is None or manager_code.nullable:
        cursor.execute("UPDATE products SET manager_code = 'A' WHERE manager_code IS NULL")
        cursor.execute(
            f"ALTER TABLE products MODIFY COLUMN manager_code {code_definition} NOT NULL"
        )

    if not has_foreign_key:
        cursor.execute(
            "SELECT COUNT(*) FROM products AS p LEFT JOIN managers AS m "
            "ON m.manager_code = p.manager_code WHERE m.manager_code IS NULL"
        )
        row = cast(tuple[int] | None, cursor.fetchone())
        if row is None or row[0] > 0:
            raise RuntimeError("등록되지 않은 담당자 코드가 있습니다. 외래키 추가 전에 정리해 주세요.")
        cursor.execute(
            "ALTER TABLE products ADD CONSTRAINT fk_products_manager "
            "FOREIGN KEY (manager_code) REFERENCES managers (manager_code) "
            "ON UPDATE CASCADE ON DELETE RESTRICT"
        )


def migrate(settings: Settings | None = None) -> None:
    """검증된 설정을 주입할 수 있으며 기본값은 shop/.env 설정이다."""
    with get_connection(settings if settings is not None else get_settings()) as connection:
        try:
            with get_cursor(connection) as cursor:
                _migrate_schema(cursor)
            connection.commit()
        except Exception:
            # 아직 커밋되지 않은 DML만 되돌린다. 이미 적용된 DDL은 남는다.
            connection.rollback()
            raise
    print("DB 구조 확인 및 변경 완료: 담당자 A/B/C, 상품 설명·담당자 필드, 외래키")


if __name__ == "__main__":
    migrate()
