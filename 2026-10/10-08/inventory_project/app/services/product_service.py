from contextlib import contextmanager
from decimal import Decimal

from fastapi import HTTPException

from app.database import get_connection
from app.schemas import ProductCreate, ProductInput, StockInput


@contextmanager
def transaction():
    connection = get_connection()
    cursor = None
    try:
        connection.start_transaction()
        cursor = connection.cursor(dictionary=True)
        yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


FIELDS = "product_id, product_name, price, quantity, min_stock, created_at"


def find_product(cursor, product_id: int, *, lock: bool = False):
    cursor.execute(
        f"SELECT {FIELDS} FROM products WHERE product_id=%s AND deleted_at IS NULL"
        + (" FOR UPDATE" if lock else ""), (product_id,),
    )
    row = cursor.fetchone()
    if row is None:
        raise HTTPException(404, "상품을 찾을 수 없습니다.")
    return row


def get_products(q: str = "", low_stock: bool = False, limit: int = 100, offset: int = 0):
    conditions = ["deleted_at IS NULL"]
    params = []
    if q:
        conditions.append("LOCATE(%s, product_name) > 0")
        params.append(q)
    if low_stock:
        conditions.append("quantity <= min_stock")
    with transaction() as cursor:
        cursor.execute(
            f"SELECT {FIELDS} FROM products WHERE " + " AND ".join(conditions)
            + " ORDER BY product_id DESC LIMIT %s OFFSET %s", (*params, limit, offset),
        )
        return cursor.fetchall()


def get_product(product_id: int):
    with transaction() as cursor:
        return find_product(cursor, product_id)


def record_movement(cursor, product_id, delta, quantity, reason):
    cursor.execute(
        "INSERT INTO stock_movements (product_id, change_amount, resulting_quantity, reason) "
        "VALUES (%s, %s, %s, %s)", (product_id, delta, quantity, reason),
    )


def create_product(data: ProductCreate):
    with transaction() as cursor:
        cursor.execute(
            "INSERT INTO products (product_name, price, quantity, min_stock) VALUES (%s,%s,%s,%s)",
            (data.product_name, data.price, data.quantity, data.min_stock),
        )
        product_id = cursor.lastrowid
        if data.quantity:
            record_movement(cursor, product_id, data.quantity, data.quantity, "최초 재고 등록")
        return find_product(cursor, product_id)


def update_product(product_id: int, data: ProductInput):
    with transaction() as cursor:
        find_product(cursor, product_id, lock=True)
        cursor.execute(
            "UPDATE products SET product_name=%s, price=%s, min_stock=%s WHERE product_id=%s",
            (data.product_name, data.price, data.min_stock, product_id),
        )
        return find_product(cursor, product_id)


def delete_product(product_id: int):
    with transaction() as cursor:
        product = find_product(cursor, product_id, lock=True)
        if product["quantity"]:
            raise HTTPException(409, "재고가 남아 있습니다. 출고 처리 후 삭제하세요.")
        cursor.execute("UPDATE products SET deleted_at=CURRENT_TIMESTAMP WHERE product_id=%s", (product_id,))


def change_stock(product_id: int, data: StockInput):
    with transaction() as cursor:
        product = find_product(cursor, product_id, lock=True)
        delta = data.quantity if data.direction == "in" else -data.quantity
        quantity = product["quantity"] + delta
        if quantity < 0:
            raise HTTPException(409, "출고 수량이 현재 재고보다 많습니다.")
        if quantity > 2_147_483_647:
            raise HTTPException(409, "재고 수량의 최대 범위를 초과했습니다.")
        cursor.execute("UPDATE products SET quantity=%s WHERE product_id=%s", (quantity, product_id))
        record_movement(cursor, product_id, delta, quantity, data.reason)
        return find_product(cursor, product_id)


def get_movements(product_id: int | None = None, limit: int = 100, offset: int = 0):
    with transaction() as cursor:
        cursor.execute(
            "SELECT m.*, p.product_name FROM stock_movements m "
            "JOIN products p ON p.product_id=m.product_id "
            + ("WHERE m.product_id=%s " if product_id is not None else "")
            + "ORDER BY m.movement_id DESC LIMIT %s OFFSET %s",
            (product_id, limit, offset) if product_id is not None else (limit, offset),
        )
        return cursor.fetchall()


def get_summary():
    with transaction() as cursor:
        cursor.execute(
            "SELECT COUNT(*) AS products, COALESCE(SUM(quantity),0) AS units, "
            "COALESCE(SUM(price*quantity),0) AS stock_value, "
            "COALESCE(SUM(quantity <= min_stock),0) AS low_stock "
            "FROM products WHERE deleted_at IS NULL"
        )
        row = cursor.fetchone()
        return {"products": int(row["products"]), "units": int(row["units"]),
                "stock_value": str(Decimal(row["stock_value"])), "low_stock": int(row["low_stock"])}
