from litestar import Controller, Request, post
from litestar.di import Provide
from litestar.channels import ChannelsPlugin
from litestar.exceptions import HTTPException

from src.domain.users.schemas import Token, UserCreate, UserLogin, UserRead
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
