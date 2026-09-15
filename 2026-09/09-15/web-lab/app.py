"""CSV를 JSON API로 제공하는 가벼운 개발 서버.

실행: py app.py
브라우저: http://127.0.0.1:8000
"""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
DATA_PATH = STATIC_DIR / "data.csv"
HOST = "127.0.0.1"
PORT = 8000


def load_data() -> list[dict[str, object]]:
    """매 API 요청 때 CSV를 읽어, 파일 변경을 즉시 반영한다."""
    data = pd.read_csv(DATA_PATH)
    return json.loads(data.to_json(orient="records", force_ascii=False))


class AppHandler(SimpleHTTPRequestHandler):
    """정적 화면과 장비 목록 API를 함께 제공한다."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        if urlparse(self.path).path == "/api/equipment":
            self.send_equipment()
            return
        if self.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def send_equipment(self) -> None:
        try:
            body = json.dumps(load_data(), ensure_ascii=False).encode("utf-8")
        except (FileNotFoundError, pd.errors.ParserError, UnicodeDecodeError) as error:
            body = json.dumps({"error": f"CSV를 읽을 수 없습니다: {error}"}, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.SERVICE_UNAVAILABLE)
        else:
            self.send_response(HTTPStatus.OK)

        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"장비 점검 API 서버: http://{HOST}:{PORT}")
    print("CSV를 저장하면 다음 API 요청부터 자동 반영됩니다.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
    finally:
        server.server_close()
