import hashlib
import secrets
import bcrypt
import jwt

from datetime import datetime, timezone, timedelta

from dataclasses import dataclass, field
from typing import Optional
from asyncpg import Connection

from src.config.base import get_settings, Settings
from src.domain.users.repositories.user import UserRepository
from src.domain.users.repositories.session import SessionRepository
from src.domain.users.schemas import Token, UserCreate, UserLogin, User


@dataclass
class UsersService:
    connection: Connection
    user_repository: UserRepository = field(init=False)
    session_repository: SessionRepository = field(init=False)
    settings: Settings = field(init=False)

    def __post_init__(self) -> None:
        self.user_repository = UserRepository(self.connection)
        self.session_repository = SessionRepository(self.connection)
        self.settings = get_settings()

    async def email_exists(self, email: str) -> bool:
        return await self.user_repository.email_exists(email)

    async def get_users(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> list[dict]:
        users = await self.user_repository.get_users(limit=limit, offset=offset)
        return users

    async def count_users(self) -> int:
        return await self.user_repository.count_users()

    async def create(self, data: UserCreate) -> dict:
        hashed_password = bcrypt.hashpw(
            data.password.encode("utf-8"),
            bcrypt.gensalt(self.settings.app.BCRYPT_GENSALT),
        )

        fingerprint = secrets.randbelow(self.settings.app.MAX_FINGERPRINT_VALUE)

        user_data = User(
            name=data.name,
            email=data.email,
            password=hashed_password.decode("utf-8"),
            fingerprint=fingerprint,
        )

        return await self.user_repository.create(user_data)

    async def authenticate(
        self, data: UserLogin, user_agent: Optional[str], ip: Optional[str]
    ) -> Token:
        user_record = await self.user_repository.get_by_email(data.email)
        if not user_record or not user_record.get("status", False):
            raise ValueError("No user found")

        stored_password = user_record["password"].encode("utf-8")
        if not bcrypt.checkpw(data.password.encode("utf-8"), stored_password):
            raise ValueError("The password is incorrect")

        salt = self.settings.app.SESSION_SALT
        random_access_token = secrets.token_hex()
        random_refresh_token = secrets.token_hex()
        user_uuid = user_record["uuid"]

        access_token_hash = hashlib.pbkdf2_hmac(
            self.settings.app.PBKDF2_ALGORITHM,
            random_access_token.encode(),
            salt.encode(),
            self.settings.app.PBKDF2_ITERATIONS,
        )

        refresh_token_hash = hashlib.pbkdf2_hmac(
            self.settings.app.PBKDF2_ALGORITHM,
            random_refresh_token.encode(),
            salt.encode(),
            self.settings.app.PBKDF2_ITERATIONS,
        )

        session = await self.session_repository.create(
            access_token=access_token_hash.hex(),
            refresh_token=refresh_token_hash.hex(),
            user_agent=user_agent,
            ip=ip,
            user_uuid=user_uuid,
        )

        if not session:
            raise ValueError("Something went wrong creating the session")

        # Calculate expiration times
        access_token_exp = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.app.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token_exp = datetime.now(timezone.utc) + timedelta(
            days=self.settings.app.REFRESH_TOKEN_EXPIRE_DAYS
        )

        access_token_jwt = jwt.encode(
            {
                "uuid": str(user_uuid),
                "access_token": random_access_token,
                "exp": access_token_exp,
            },
            key=self.settings.app.SECRET_KEY,
            algorithm=self.settings.app.JWT_ALGORITHM,
        )

        refresh_token_jwt = jwt.encode(
            {
                "uuid": str(user_uuid),
                "refresh_token": random_refresh_token,
                "exp": refresh_token_exp,
            },
            key=self.settings.app.SECRET_KEY,
            algorithm=self.settings.app.JWT_ALGORITHM,
        )

        return Token(access_token=access_token_jwt, refresh_token=refresh_token_jwt)

    async def refresh_access_token(
        self, refresh_token: str, user_agent: Optional[str], ip: Optional[str]
    ) -> Token:
        """Refreshes the access_token using a valid refresh_token"""
        try:
            decoded = jwt.decode(
                jwt=refresh_token,
                key=self.settings.app.SECRET_KEY,
                algorithms=[self.settings.app.JWT_ALGORITHM],
            )

            random_refresh_token = decoded.get("refresh_token")
            user_uuid = decoded.get("uuid")

            if not random_refresh_token or not user_uuid:
                raise ValueError("Invalid refresh token")

            # Generate the refresh token hash to search in the database
            salt = self.settings.app.SESSION_SALT
            refresh_token_hash = hashlib.pbkdf2_hmac(
                self.settings.app.PBKDF2_ALGORITHM,
                random_refresh_token.encode(),
                salt.encode(),
                self.settings.app.PBKDF2_ITERATIONS,
            )

            # Fetch the session by refresh token
            session = await self.session_repository.get_by_refresh_token(
                refresh_token_hash.hex()
            )

            if not session or str(session["user_uuid"]) != user_uuid:
                raise ValueError("Invalid or expired refresh token")

            # Generate a new access token
            random_access_token = secrets.token_hex()

            access_token_hash = hashlib.pbkdf2_hmac(
                self.settings.app.PBKDF2_ALGORITHM,
                random_access_token.encode(),
                salt.encode(),
                self.settings.app.PBKDF2_ITERATIONS,
            )

            # Update only the access token in the existing session
            await self.session_repository.update_access_token(
                session_uuid=session["uuid"],
                access_token=access_token_hash.hex(),
                user_agent=user_agent,
                ip=ip,
            )

            # Calculate expiration time for new access token
            access_token_exp = datetime.now(timezone.utc) + timedelta(
                minutes=self.settings.app.ACCESS_TOKEN_EXPIRE_MINUTES
            )

            # Generate new access token JWT
            access_token_jwt = jwt.encode(
                {
                    "uuid": user_uuid,
                    "access_token": random_access_token,
                    "exp": access_token_exp,
                },
                key=self.settings.app.SECRET_KEY,
                algorithm=self.settings.app.JWT_ALGORITHM,
            )

            # Return the new access token and keep the same refresh token
            return Token(access_token=access_token_jwt, refresh_token=refresh_token)

        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token expired")
        except jwt.PyJWTError:
            raise ValueError("Invalid refresh token format")
