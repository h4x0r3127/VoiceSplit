from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.config import settings
from app.database import init_db
from app.utils.logging import configure_logging, get_logger

configure_logging("DEBUG" if settings.ENVIRONMENT == "development" else "INFO")
logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("voicesplit_startup", environment=settings.ENVIRONMENT)
    await init_db()
    await _ensure_storage_bucket()
    yield
    logger.info("voicesplit_shutdown")


async def _ensure_storage_bucket() -> None:
    try:
        import asyncio
        from app.services.storage.minio import MinioStorageService
        storage = MinioStorageService()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, storage.ensure_bucket_exists)
        logger.info("storage_bucket_ready", bucket=settings.MINIO_BUCKET)
    except Exception as exc:
        logger.warning("storage_bucket_check_failed", error=str(exc))


app = FastAPI(
    title="VoiceSplit API",
    description="AI-powered speaker isolation — backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENVIRONMENT == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["voicesplit.app", "*.voicesplit.app"])


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    import time
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    return response


app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }
