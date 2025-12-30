from litestar import Controller, Request, post, get
from litestar.di import Provide
from litestar.channels import ChannelsPlugin
from litestar.exceptions import HTTPException
from litestar.params import Parameter

from src.server.auth import AuthenticationMiddleware

from src.domain.users.schemas import (
    Token,
    UserCreate,
    UserLogin,
    UserRead,
    PaginatedUsersResponse,
)
from src.domain.users.deps import provide_users_service
from src.domain.users.services import UsersService


class UserController(Controller):
    path = "/users"
    tags = ["Users"]
    dependencies = {
        "users_service": Provide(provide_users_service, sync_to_thread=False)
    }

    @post(path="/register")
    async def create_user(
        self, data: UserCreate, channels: ChannelsPlugin, users_service: UsersService
    ) -> UserRead:
        if await users_service.email_exists(data.email):
            raise HTTPException(
                detail="A user with this email already exists", status_code=400
            )

        user_record = await users_service.create(data)
        if user_record:
            channels.publish("User created successfully!", channels=["notifications"])

        return UserRead(
            uuid=user_record["uuid"],
            name=user_record["name"],
            email=user_record["email"],
            status=user_record["status"],
        )

    @post(path="/auth")
    async def authenticate_user(
        self, data: UserLogin, request: Request, users_service: UsersService
    ) -> Token:
        try:
            user_agent = request.headers.get("user-agent")
            ip = request.headers.get("x-real-ip") or request.headers.get(
                "x-forwarded-for"
            )
            return await users_service.authenticate(data, user_agent=user_agent, ip=ip)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @get(path="/", cache=2)
    async def get_users(
        self,
        users_service: UsersService,
        limit: int = Parameter(
            default=50, ge=1, le=100, description="Number of users per page"
        ),
        offset: int = Parameter(default=0, ge=0, description="Number of users to skip"),
    ) -> PaginatedUsersResponse:
        users = await users_service.get_users(limit=limit, offset=offset)
        total = await users_service.count_users()

        return PaginatedUsersResponse(
            data=[UserRead(**user) for user in users],
            total=total,
            limit=limit,
            offset=offset,
        )

    @post(path="/refresh", middleware=[AuthenticationMiddleware])
    async def refresh_token(
        self, request: Request, users_service: UsersService
    ) -> Token:
        try:
            refresh_token = request.headers.get("x-refresh-token")
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Refresh token is required")

            user_agent = request.headers.get("user-agent")
            ip = request.headers.get("x-real-ip") or request.headers.get(
                "x-forwarded-for"
            )

            return await users_service.refresh_access_token(
                refresh_token=refresh_token, user_agent=user_agent, ip=ip
            )
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
