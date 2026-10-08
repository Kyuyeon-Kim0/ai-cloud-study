import os

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.database import get_connection
from app.main import app
from init_db import initialize


@pytest.fixture(scope="session", autouse=True)
def isolated_database():
    if os.getenv("INVENTORY_TEST_MODE") != "1" or get_settings().mysql_database != "inventory_test":
        pytest.skip("Run python run_tests.py to use an isolated MySQL database.")
    initialize()


@pytest.fixture
def client():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM stock_movements")
    cursor.execute("DELETE FROM products")
    connection.commit()
    cursor.close()
    connection.close()
    with TestClient(app) as test_client:
        yield test_client
