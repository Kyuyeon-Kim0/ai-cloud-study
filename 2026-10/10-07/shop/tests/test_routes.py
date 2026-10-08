import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import get_settings
from app.main import create_app
from app.models.product import Product, ProductCreate
from app.repositories.product import ProductDataError, ProductInputError, ProductStorageError
from app.routers.product import get_product_service
from app.routers.product import templates
from app.services.product import ProductService
from tests.helpers import MemoryProductReader, test_settings


class FailingProductReader:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def list_products(self, keyword: str = "") -> list[Product]:
        raise self.error

    def get_by_id(self, product_id: int) -> Product | None:
        raise self.error

    def save_product(self, product: ProductCreate) -> None:
        raise self.error


class RouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.application = create_app(test_settings())
        self.reader = MemoryProductReader([
            Product(id=1, name="노트북", price=1200000),
            Product(id=2, name="<script>alert(1)</script>", price=100),
        ])
        self.application.dependency_overrides[get_product_service] = lambda: ProductService(self.reader)

    def test_list_renders_prices_counts_and_escapes_names(self) -> None:
        with TestClient(self.application) as client:
            response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("총 2개 상품", response.text)
        self.assertIn("1,200,000원", response.text)
        self.assertIn("&lt;script&gt;", response.text)
        self.assertNotIn("<script>alert(1)</script>", response.text)
        self.assertIn("/products/1", response.text)
        self.assertIn("/static/css/style.css", response.text)

    def test_search_and_empty_state(self) -> None:
        with TestClient(self.application) as client:
            found = client.get("/", params={"q": "  노트  "})
            missing = client.get("/", params={"q": "없는상품"})
        self.assertEqual(found.status_code, 200)
        self.assertIn("총 1개 상품", found.text)
        self.assertIn('value="  노트  "', found.text)
        self.assertIn("검색 결과가 없습니다.", missing.text)
        self.assertIn("총 0개 상품", missing.text)

    def test_query_length_limit(self) -> None:
        with TestClient(self.application) as client:
            self.assertEqual(client.get("/", params={"q": "a" * 200}).status_code, 200)
            self.assertEqual(client.get("/", params={"q": "a" * 201}).status_code, 422)

    def test_errors_do_not_expose_internal_details(self) -> None:
        for error, status in ((ProductStorageError("private connection details"), 503),
                              (ProductDataError("private row details"), 500)):
            with self.subTest(status=status):
                self.application.dependency_overrides[get_product_service] = (
                    lambda error=error: ProductService(FailingProductReader(error))
                )
                with TestClient(self.application) as client, self.assertLogs("uvicorn.error", level="ERROR") as logs:
                    for path in ("/", "/products/1"):
                        response = client.get(path)
                        self.assertEqual(response.status_code, status)
                        self.assertIn("detail", response.json())
                        self.assertNotIn("private", response.text)
                self.assertNotIn("private", "\n".join(logs.output))

    def test_static_files_and_registration_form(self) -> None:
        with TestClient(self.application) as client:
            css = client.get("/static/css/style.css")
            form = client.get("/product")
        self.assertEqual(css.status_code, 200)
        self.assertIn("text/css", css.headers["content-type"])
        self.assertEqual(form.status_code, 200)
        self.assertIn("text/html", form.headers["content-type"])
        self.assertIn("상품 등록", form.text)
        self.assertIn('method="post"', form.text)
        self.assertIn('action="http://testserver/product"', form.text)

    def test_registration_saves_trimmed_input_and_redirects(self) -> None:
        with TestClient(self.application) as client:
            response = client.post("/product", data={
                "name": "  새 상품  ", "price": "1234", "description": "  상세 설명  ", "manager_code": " A ",
            }, follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "http://testserver/product")
        self.assertEqual(len(self.reader.saved), 1)
        self.assertEqual(self.reader.saved[0].name, "새 상품")
        self.assertEqual(self.reader.saved[0].price, 1234)
        self.assertEqual(self.reader.saved[0].description, "상세 설명")
        self.assertEqual(self.reader.saved[0].manager_code, "A")

    def test_registration_rejects_invalid_input_before_save(self) -> None:
        defaults = {"name": "상품", "price": "100", "description": "설명", "manager_code": "A"}
        cases = [("name", " "), ("name", "a" * 256), ("price", "-1"),
                 ("price", "1.5"), ("price", "2147483648"), ("description", "\t"),
                 ("description", "가" * 21846), ("manager_code", " "), ("manager_code", "A" * 21)]
        with TestClient(self.application) as client:
            for field, value in cases:
                with self.subTest(field=field, size=len(value)):
                    response = client.post("/product", data={**defaults, field: value})
                    self.assertEqual(response.status_code, 422)
            self.assertEqual(client.post("/product", data={"name": "상품"}).status_code, 422)
        self.assertEqual(self.reader.saved, [])

    def test_registration_unknown_manager_returns_400(self) -> None:
        self.application.dependency_overrides[get_product_service] = lambda: ProductService(
            FailingProductReader(ProductInputError("등록되지 않은 담당자 코드입니다."))
        )
        with TestClient(self.application) as client:
            response = client.post("/product", data={
                "name": "상품", "price": "100", "description": "설명", "manager_code": "UNKNOWN",
            })
        self.assertEqual(response.status_code, 400)

    def test_registration_database_failure_returns_503(self) -> None:
        self.application.dependency_overrides[get_product_service] = lambda: ProductService(
            FailingProductReader(ProductStorageError("private storage details"))
        )
        with TestClient(self.application) as client, self.assertLogs("uvicorn.error", level="ERROR"):
            response = client.post("/product", data={
                "name": "상품", "price": "100", "description": "설명", "manager_code": "A",
            })
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)

    def test_detail_renders_product_and_escapes_name(self) -> None:
        with TestClient(self.application) as client:
            response = client.get("/products/1")
            escaped = client.get("/products/2")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("노트북", response.text)
        self.assertIn("1,200,000원", response.text)
        self.assertIn("상품 목록으로 돌아가기", response.text)
        self.assertIn("/static/css/style.css", response.text)
        self.assertIn("&lt;script&gt;", escaped.text)
        self.assertNotIn("<script>alert(1)</script>", escaped.text)

    def test_detail_missing_product_returns_404(self) -> None:
        with TestClient(self.application) as client:
            response = client.get("/products/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "상품을 찾을 수 없습니다."})

    def test_detail_rejects_invalid_ids(self) -> None:
        with TestClient(self.application) as client:
            for product_id in ("0", "-1", "abc", "1.5"):
                with self.subTest(product_id=product_id):
                    self.assertEqual(client.get(f"/products/{product_id}").status_code, 422)

    def test_invalid_environment_prevents_startup(self) -> None:
        get_settings.cache_clear()
        try:
            with patch.dict(os.environ, {}, clear=True), patch("app.config.load_dotenv"):
                with self.assertRaises(ValidationError), TestClient(create_app()):
                    pass
        finally:
            get_settings.cache_clear()

    def test_registration_template_uses_shared_stylesheet(self) -> None:
        from starlette.requests import Request

        request = Request({"type": "http", "scheme": "http", "server": ("testserver", 80),
                           "path": "/product", "root_path": "", "headers": [],
                           "router": self.application.router})
        response = templates.TemplateResponse(request=request, name="product.html")
        html = response.body.decode("utf-8")
        self.assertIn("상품 등록", html)
        self.assertIn("/static/css/style.css", html)
        self.assertNotIn("<style>", html)
