from typing import Optional
from dataclasses import dataclass
from uuid import UUID
from asyncpg import Connection
from src.domain.users.schemas import User


@dataclass
class UserRepository:
    connection: Connection

    async def create(self, data: User) -> dict:
        query = """
            INSERT INTO users (name, email, password, fingerprint) 
            VALUES ($1, $2, $3, $4) 
            RETURNING uuid, name, email, status
        """
        return await self.connection.fetchrow(
            query, data.name, data.email, data.password, data.fingerprint
        )

    async def get_by_email(self, email: str) -> Optional[dict]:
        query = "SELECT * FROM users WHERE email = $1"
        return await self.connection.fetchrow(query, email)

    async def get_by_uuid(self, uuid: UUID) -> Optional[dict]:
        query = "SELECT * FROM users WHERE uuid = $1"
        return await self.connection.fetchrow(query, str(uuid))

    async def email_exists(self, email: str) -> bool:
        query = "SELECT 1 FROM users WHERE email = $1"
        return bool(await self.connection.fetchrow(query, email))
