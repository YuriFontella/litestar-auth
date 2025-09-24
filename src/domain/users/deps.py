from asyncpg import Connection
from src.domain.users.services import UsersService


def provide_users_service(
    db_connection: Connection,
) -> UsersService:
    return UsersService(db_connection)
