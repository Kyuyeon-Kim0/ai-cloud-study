from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from fastapi.testclient import TestClient

from app.database import get_connection
from app.main import app
from app.schemas import StockInput
from app.services.product_service import change_stock
from init_db import initialize


def create(client, **values):
    response = client.post("/api/products", json={"product_name": "테스트 상품", "price": "1234.50", **values})
    assert response.status_code == 201, response.text
    return response.json()


def test_product_lifecycle_and_preserved_history(client):
    product = create(client, quantity=10, min_stock=3)
    product_id = product["product_id"]
    assert Decimal(product["price"]) == Decimal("1234.50")
    assert client.get(f"/api/products/{product_id}").json()["quantity"] == 10
    updated = client.put(f"/api/products/{product_id}", json={"product_name": "변경 상품", "price": "2000", "min_stock": 5})
    assert updated.status_code == 200
    assert updated.json()["quantity"] == 10
    assert client.delete(f"/api/products/{product_id}").status_code == 409
    response = client.post(f"/api/products/{product_id}/stock", json={"direction": "out", "quantity": 10, "reason": "판매"})
    assert response.status_code == 200
    assert client.delete(f"/api/products/{product_id}").status_code == 204
    assert client.get(f"/api/products/{product_id}").status_code == 404
    assert client.get("/api/products").json() == []
    history = client.get("/api/movements").json()
    assert [row["change_amount"] for row in history] == [-10, 10]
    assert [row["resulting_quantity"] for row in history] == [0, 10]


def test_stock_and_rejected_outbound_are_atomic(client):
    product = create(client, quantity=2)
    url = f'/api/products/{product["product_id"]}/stock'
    assert client.post(url, json={"direction": "in", "quantity": 5, "reason": "입고"}).json()["quantity"] == 7
    assert client.post(url, json={"direction": "out", "quantity": 8, "reason": "판매"}).status_code == 409
    assert client.get(f'/api/products/{product["product_id"]}').json()["quantity"] == 7
    assert len(client.get("/api/movements").json()) == 2


def test_search_pagination_low_stock_and_summary(client):
    create(client, product_name="노트", quantity=4, min_stock=5)
    create(client, product_name="펜", quantity=10, price="500")
    assert len(client.get("/api/products?q=노트").json()) == 1
    assert len(client.get("/api/products?low_stock=true").json()) == 1
    first = client.get("/api/products?limit=1").json()
    second = client.get("/api/products?limit=1&offset=1").json()
    assert first[0]["product_id"] != second[0]["product_id"]
    summary = client.get("/api/summary").json()
    assert summary["products"] == 2 and summary["units"] == 14 and summary["low_stock"] == 1
    assert Decimal(summary["stock_value"]) == Decimal("9938")


def test_validation_and_missing_products(client):
    for values in [{"quantity": -1}, {"quantity": 1.5}, {"quantity": True}, {"price": "-1"},
                   {"price": "0.001"}, {"product_name": "   "}, {"min_stock": -1}, {"unknown": 1}]:
        response = client.post("/api/products", json={"product_name": "상품", "price": "100", **values})
        assert response.status_code == 422
    assert client.get("/api/products/999999").status_code == 404
    assert client.get("/api/products?offset=-1").status_code == 422
    assert client.get("/api/products?limit=101").status_code == 422
    product = create(client)
    url = f'/api/products/{product["product_id"]}/stock'
    for values in [{"quantity": 0}, {"reason": " "}, {"direction": "invalid"}]:
        assert client.post(url, json={"direction": "in", "quantity": 1, "reason": "입고", **values}).status_code == 422


def test_concurrent_outbound_never_overdraws(client):
    product = create(client, quantity=5)
    def withdraw(_):
        with TestClient(app) as worker:
            return worker.post(f'/api/products/{product["product_id"]}/stock',
                               json={"direction": "out", "quantity": 4, "reason": "동시 출고"}).status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(withdraw, range(2)))
    assert sorted(statuses) == [200, 409]
    assert client.get(f'/api/products/{product["product_id"]}').json()["quantity"] == 1


def test_movement_failure_rolls_back_stock(client, monkeypatch):
    from app.services import product_service
    product = create(client, quantity=5)
    def fail(*args):
        raise RuntimeError("simulated movement insert failure")
    monkeypatch.setattr(product_service, "record_movement", fail)
    import pytest
    with pytest.raises(RuntimeError):
        change_stock(product["product_id"], StockInput(direction="in", quantity=2, reason="입고"))
    assert client.get(f'/api/products/{product["product_id"]}').json()["quantity"] == 5


def test_health_dashboard_and_idempotent_setup(client):
    product = create(client)
    initialize()
    assert client.get(f'/api/products/{product["product_id"]}').status_code == 200
    assert client.get("/health").json()["database"] == "mysql"
    assert client.get("/dashboard").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_database_error_hides_credentials(client, monkeypatch):
    import mysql.connector
    from app.services import product_service
    def fail():
        raise mysql.connector.Error("password=secret", errno=2003)
    monkeypatch.setattr(product_service, "get_connection", fail)
    response = client.get("/api/products")
    assert response.status_code == 503
    assert "secret" not in response.text


def test_legacy_schema_migration_preserves_products(client):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DROP TABLE stock_movements")
    cursor.execute("DROP TABLE products")
    cursor.execute("""CREATE TABLE products (
        product_id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(100) NOT NULL, price INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB""")
    cursor.execute("INSERT INTO products (product_name,price) VALUES (%s,%s)", ("기존 상품", 12345))
    connection.commit()
    cursor.close()
    connection.close()
    initialize()
    initialize()
    rows = client.get("/api/products").json()
    assert len(rows) == 1
    assert rows[0]["product_name"] == "기존 상품"
    assert Decimal(rows[0]["price"]) == Decimal("12345")
    assert rows[0]["quantity"] == 0 and rows[0]["min_stock"] == 0
