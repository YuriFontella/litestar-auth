from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar_asyncpg import AsyncpgPlugin

from src.config import app as config


asyncpg = AsyncpgPlugin(config=config.asyncpg)
channels = ChannelsPlugin(
    backend=MemoryChannelsBackend(),
    channels=["notifications"],
    create_ws_route_handlers=True,
)


def get_plugins() -> list:
    return [asyncpg, channels]
