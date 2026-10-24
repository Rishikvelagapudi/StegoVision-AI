"""FastAPI application factory. Run with:  uvicorn app.main:app --reload"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import __version__, service
from .api import router
from .config import get_settings
from .errors import AppError

log = logging.getLogger("stegovision")


def _err(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


@asynccontextmanager
async def lifespan(app: FastAPI):
    async def janitor():
        while True:
            await asyncio.sleep(300)
            try:
                service.get_store().cleanup_expired()
            except Exception:  # never crash the loop
                log.exception("cleanup failed")

    task = asyncio.create_task(janitor())
    try:
        yield
    finally:
        task.cancel()
        service.reset_store()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="StegoVision AI", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=False,
        expose_headers=["Content-Disposition", "X-Stego-Payload-Type", "X-Stego-Payload-Bytes",
                        "X-Stego-Capacity-Bytes", "X-Stego-Demo-Carrier", "X-Stego-Demo-Payload"],
    )

    @app.exception_handler(AppError)
    async def app_error(_: Request, exc: AppError):
        return _err(exc.status, exc.code, exc.message)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException):
        return _err(exc.status_code, "http_error", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        return _err(422, "invalid_request", "Invalid request: " + "; ".join(
            f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()))

    @app.exception_handler(Exception)
    async def unhandled(_: Request, exc: Exception):
        log.exception("unhandled error")
        return _err(500, "internal_error", "An unexpected server error occurred.")

    app.include_router(router)
    return app


app = create_app()
