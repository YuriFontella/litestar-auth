import os
from typing import Optional, List

from dataclasses import dataclass, field
from functools import lru_cache


@dataclass
class DatabaseSettings:
    DSN: Optional[str] = None
    MIN_SIZE: int = 4
    MAX_SIZE: int = 16
    MAX_QUERIES: int = 50000
    MAX_INACTIVE_CONNECTION_LIFETIME: float = 300.0

    def __post_init__(self):
        self.DSN = self.DSN or os.getenv("DATABASE_DSN")
        self.MIN_SIZE = int(os.getenv("DATABASE_MIN_SIZE", self.MIN_SIZE))
        self.MAX_SIZE = int(os.getenv("DATABASE_MAX_SIZE", self.MAX_SIZE))
        self.MAX_QUERIES = int(os.getenv("DATABASE_MAX_QUERIES", self.MAX_QUERIES))
        self.MAX_INACTIVE_CONNECTION_LIFETIME = float(
            os.getenv(
                "DATABASE_MAX_INACTIVE_CONNECTION_LIFETIME",
                self.MAX_INACTIVE_CONNECTION_LIFETIME,
            )
        )


@dataclass
class AppSettings:
    SECRET_KEY: Optional[str] = None
    ALLOWED_CORS_ORIGINS: List[str] = field(default_factory=list)
    CSRF_COOKIE_NAME: str = "XSRF-TOKEN"
    CSRF_COOKIE_SECURE: bool = False
    JWT_ALGORITHM: str = "HS256"
    SESSION_SALT: Optional[str] = None
    PBKDF2_ITERATIONS: int = 600_000
    PBKDF2_ALGORITHM: str = "sha256"
    MAX_FINGERPRINT_VALUE: int = 100_000_000
    BCRYPT_GENSALT: int = 12
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    def __post_init__(self):
        self.SECRET_KEY = self.SECRET_KEY or os.getenv("SECRET_KEY")
        self.SESSION_SALT = self.SESSION_SALT or os.getenv("SESSION_SALT")
        self.PBKDF2_ITERATIONS = int(
            os.getenv("PBKDF2_ITERATIONS", self.PBKDF2_ITERATIONS)
        )
        self.PBKDF2_ALGORITHM = os.getenv("PBKDF2_ALGORITHM", self.PBKDF2_ALGORITHM)
        self.MAX_FINGERPRINT_VALUE = int(
            os.getenv("MAX_FINGERPRINT_VALUE", self.MAX_FINGERPRINT_VALUE)
        )
        self.BCRYPT_GENSALT = int(os.getenv("BCRYPT_GENSALT", self.BCRYPT_GENSALT))
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", self.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", self.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        if not self.ALLOWED_CORS_ORIGINS:
            cors_origins = os.getenv("ALLOWED_CORS_ORIGINS")
            if cors_origins:
                self.ALLOWED_CORS_ORIGINS = [
                    origin.strip() for origin in cors_origins.split(",")
                ]
            else:
                self.ALLOWED_CORS_ORIGINS = ["*"]

        self.CSRF_COOKIE_NAME = os.getenv("CSRF_COOKIE_NAME", self.CSRF_COOKIE_NAME)
        self.CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "").lower() in (
            "true",
            "1",
            "yes",
        )
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", self.JWT_ALGORITHM)


@dataclass
class Settings:
    app: AppSettings = field(default_factory=AppSettings)
    db: DatabaseSettings = field(default_factory=DatabaseSettings)

    @classmethod
    def from_env(cls, dotenv_filename: str = ".env") -> "Settings":
        from pathlib import Path
        from dotenv import load_dotenv

        env_file = Path(f"{os.curdir}/{dotenv_filename}")
        if env_file.is_file():
            load_dotenv(env_file, override=True)
        return Settings()


@lru_cache(maxsize=1, typed=True)
def get_settings() -> Settings:
    return Settings.from_env()
