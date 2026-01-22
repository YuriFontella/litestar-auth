import hmac
import hashlib

from jwt import PyJWTError, ExpiredSignatureError, decode

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult

from src.config.base import get_settings
from src.config import app as config

settings = get_settings()


class AuthenticationMiddleware(AbstractAuthenticationMiddleware):
    @staticmethod
    def _hash_token(token: str, salt: str) -> str:
        """Hash token using HMAC-SHA256 - fast and secure for random tokens."""
        return hmac.new(salt.encode(), token.encode(), hashlib.sha256).hexdigest()

    async def authenticate_request(
        self, connection: ASGIConnection
    ) -> AuthenticationResult:
        try:
            token = connection.headers.get("x-access-token")
            if not token:
                raise NotAuthorizedException()

            auth = decode(
                jwt=token,
                key=settings.app.SECRET_KEY,
                algorithms=[settings.app.JWT_ALGORITHM],
            )
            salt = settings.app.SESSION_SALT
            access_token = self._hash_token(auth["access_token"], salt)
            user_uuid = auth.get("uuid")

            pool = config.asyncpg.provide_pool(connection.scope["app"].state)
            async with pool.acquire() as conn:
                query = """
                    select u.uuid, u.name, u.email, u.role, u.status from users u
                    join sessions s on u.uuid = s.user_uuid
                    where u.uuid = $1 and s.access_token = $2 and s.revoked = false and u.status = true
                    order by s.created_at desc
                    limit 1
                """
                user = await conn.fetchrow(query, user_uuid, access_token)

            if not user:
                raise NotAuthorizedException()

        except ExpiredSignatureError:
            raise NotAuthorizedException(detail="Token expired")
        except PyJWTError:
            raise NotAuthorizedException(detail="Invalid token")

        else:
            return AuthenticationResult(user=user, auth=auth)
