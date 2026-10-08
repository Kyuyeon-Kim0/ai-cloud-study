from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from mysql.connector import Error
from app.database import get_connection

from app.config import get_settings
from app.routers.products import router as products_router


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
)


app.include_router(products_router)
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.exception_handler(Error)
async def database_error(request, exc):
    return JSONResponse(status_code=503, content={"detail": "DB 요청을 처리할 수 없습니다. DB 상태와 초기화를 확인하세요."})


@app.get("/health")
def health():
    connection = get_connection()
    try:
        connection.ping(reconnect=False)
        return {"status": "ok", "database": "mysql"}
    finally:
        connection.close()


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Inventory API is running",
        "environment": settings.app_env,
    }
