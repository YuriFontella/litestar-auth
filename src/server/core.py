from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.plugins import InitPluginProtocol
from litestar.status_codes import HTTP_500_INTERNAL_SERVER_ERROR

from src.lib.exceptions import app_exception_handler, internal_server_error_handler
from src.lib.deps import provide_current_user
from src.config.app import (
    compression as compression_config,
    cors as cors_config,
    csrf as csrf_config,
    rate_limit_config,
)
from src.server.lifespan import on_shutdown, on_startup
from src.server.plugins import get_plugins


class ApplicationCore(InitPluginProtocol):
    def on_app_init(self, app_config):
        from src.domain.users.controllers import UserController

        app_config.route_handlers.extend([UserController])

        app_config.plugins.extend(get_plugins())

        app_config.cors_config = cors_config
        app_config.csrf_config = csrf_config
        app_config.compression_config = compression_config

        app_config.middleware.extend([rate_limit_config.middleware])

        app_config.dependencies.update(
            {
                "current_user": Provide(provide_current_user, sync_to_thread=False),
            }
        )

        app_config.on_startup.extend([on_startup])
        app_config.on_shutdown.extend([on_shutdown])

        app_config.exception_handlers = {
            HTTPException: app_exception_handler,
            HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error_handler,
        }

        return app_config
