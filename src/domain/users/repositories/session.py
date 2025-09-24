from typing import Optional
from dataclasses import dataclass
from uuid import UUID
from asyncpg import Connection


@dataclass
class SessionRepository:
    connection: Connection

    async def create(
        self,
        access_token: str,
        user_agent: Optional[str],
        ip: Optional[str],
        user_uuid: UUID,
    ) -> dict:
        query = """
            INSERT INTO sessions (access_token, user_agent, ip, user_uuid) 
            VALUES ($1, $2, $3, $4) 
            RETURNING access_token
        """
        return await self.connection.fetchrow(
            query, access_token, user_agent, ip, str(user_uuid)
        )
