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
        refresh_token: str,
        user_agent: Optional[str],
        ip: Optional[str],
        user_uuid: UUID,
    ) -> dict:
        query = """
            INSERT INTO sessions (access_token, refresh_token, user_agent, ip, user_uuid) 
            VALUES ($1, $2, $3, $4, $5) 
            RETURNING access_token, refresh_token
        """
        return await self.connection.fetchrow(
            query, access_token, refresh_token, user_agent, ip, str(user_uuid)
        )

    async def get_by_refresh_token(self, refresh_token: str) -> Optional[dict]:
        query = """
            SELECT s.uuid, s.user_uuid, s.revoked, s.access_token, s.refresh_token, u.status as user_status
            FROM sessions s
            JOIN users u ON s.user_uuid = u.uuid
            WHERE s.refresh_token = $1 AND s.revoked = false AND u.status = true
        """
        return await self.connection.fetchrow(query, refresh_token)

    async def revoke_session(self, session_uuid: UUID) -> bool:
        query = """
            UPDATE sessions SET revoked = true WHERE uuid = $1
        """
        await self.connection.execute(query, str(session_uuid))
        return True

    async def update_access_token(
        self,
        session_uuid: str,
        access_token: str,
        user_agent: Optional[str],
        ip: Optional[str],
    ) -> None:
        """Atualiza o access_token, user_agent e ip de uma sessão existente"""
        query = """
            UPDATE sessions
            SET access_token = $1, user_agent = $2, ip = $3, update = NOW()
            WHERE uuid = $4 AND revoked = false
        """
        await self.connection.execute(query, access_token, user_agent, ip, session_uuid)
