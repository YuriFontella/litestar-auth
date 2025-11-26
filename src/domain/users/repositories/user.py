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

    async def get_users(self, limit: Optional[int] = None, offset: int = 0) -> Optional[list]:
        query = "SELECT uuid, name, email, status FROM users ORDER BY date DESC"

        if limit is not None:
            query += " LIMIT $1 OFFSET $2"
            return await self.connection.fetch(query, limit, offset)
        else:
            query += " OFFSET $1"
            return await self.connection.fetch(query, offset)

    async def count_users(self) -> int:
        query = "SELECT COUNT(*) as total FROM users"
        result = await self.connection.fetchrow(query)
        return result["total"] if result else 0
