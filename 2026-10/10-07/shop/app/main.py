import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path


# 파일 직접 실행 시에도 shop을 기준으로 app 패키지를 찾는다.
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR, Settings, get_settings
from app.repositories.product import ProductDataError, ProductStorageError
from app.routers.product import router


logger = logging.getLogger("uvicorn.error")


def create_app(settings: Settings | None = None) -> FastAPI:
    """테스트에서는 검증된 설정을 주입하고 운영에서는 시작 시 읽는다."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.settings = settings if settings is not None else get_settings()
        yield

    application = FastAPI(title="상품 관리", lifespan=lifespan)
    if settings is not None:
        application.dependency_overrides[get_settings] = lambda: settings
    application.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
    application.include_router(router)

    @application.exception_handler(ProductStorageError)
    async def storage_error(request: Request, exc: ProductStorageError) -> JSONResponse:
        cause = exc.__cause__
        logger.error(
            "Product storage failed: type=%s errno=%s sqlstate=%s",
            type(cause).__name__, getattr(cause, "errno", None), getattr(cause, "sqlstate", None),
        )
        return JSONResponse(
            status_code=503,
            content={"detail": "상품을 불러올 수 없습니다. 잠시 후 다시 시도해 주세요."},
        )

    @application.exception_handler(ProductDataError)
    async def data_error(request: Request, exc: ProductDataError) -> JSONResponse:
        logger.error("Stored product data failed validation")
        return JSONResponse(status_code=500, content={"detail": "상품 데이터가 올바르지 않습니다."})

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
