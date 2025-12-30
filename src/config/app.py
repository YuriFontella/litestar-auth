from typing import Literal, Tuple

from litestar.config.compression import CompressionConfig
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar_asyncpg import AsyncpgConfig, PoolConfig

from src.config.base import get_settings

settings = get_settings()

csrf = CSRFConfig(
    secret=settings.app.SECRET_KEY,
    cookie_name=settings.app.CSRF_COOKIE_NAME,
    cookie_secure=settings.app.CSRF_COOKIE_SECURE,
    cookie_samesite=settings.app.CSRF_COOKIE_SAMESITE,
    cookie_httponly=settings.app.CSRF_COOKIE_HTTPONLY,
    safe_methods={
        "POST",
        "GET",
        "OPTIONS",
    },
)

cors = CORSConfig(
    allow_origins=settings.app.ALLOWED_CORS_ORIGINS,
    allow_methods=[
        "GET",
        "POST",
        "DELETE",
        "PUT",
        "PATCH",
        "OPTIONS",
    ],
    allow_headers=["Origin", "Content-Type", "X-CSRFToken", "X-Access-Token"],
    allow_credentials=True,
)

compression = CompressionConfig(backend="gzip", gzip_compress_level=9)

rate_limit: Tuple[Literal["second"], int] = ("second", 10)
rate_limit_config = RateLimitConfig(rate_limit=rate_limit, exclude=["/schema"])

asyncpg = AsyncpgConfig(
    pool_config=PoolConfig(
        dsn=settings.db.DSN,
        min_size=settings.db.MIN_SIZE,
        max_size=settings.db.MAX_SIZE,
        max_queries=settings.db.MAX_QUERIES,
        max_inactive_connection_lifetime=settings.db.MAX_INACTIVE_CONNECTION_LIFETIME,
    )
)
