import hashlib
import secrets
import bcrypt
import jwt

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

    async def create(self, data: UserCreate) -> dict:
        hashed_password = bcrypt.hashpw(
            data.password.encode("utf-8"), bcrypt.gensalt(self.settings.app.BCRYPT_GENSALT)
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
        random_token = secrets.token_hex()
        user_uuid = user_record["uuid"]

        access_token_hash = hashlib.pbkdf2_hmac(
            self.settings.app.PBKDF2_ALGORITHM, random_token.encode(), salt.encode(), self.settings.app.PBKDF2_ITERATIONS
        )

        session = await self.session_repository.create(
            access_token=access_token_hash.hex(),
            user_agent=user_agent,
            ip=ip,
            user_uuid=user_uuid,
        )

        if not session:
            raise ValueError("Something went wrong creating the session")

        token = jwt.encode(
            {"uuid": str(user_uuid), "access_token": random_token},
            key=self.settings.app.SECRET_KEY,
            algorithm=self.settings.app.JWT_ALGORITHM,
        )

        return Token(token=token)
