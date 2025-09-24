import logging

from litestar import MediaType, Request, Response
from litestar.exceptions import HTTPException

logger = logging.getLogger(__name__)


def app_exception_handler(request: Request, exc: HTTPException) -> Response:
    logger.debug(f"App exception handler invoked with error: {exc.detail}")
    return Response(
        content={
            "error": "HTTP Exception",
            "path": request.url.path,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
        status_code=exc.status_code,
    )


def internal_server_error_handler(_: Request, exc: Exception) -> Response:
    logger.debug(f"Internal server error handler invoked with error: {str(exc)}")
    return Response(media_type=MediaType.TEXT, content=str(exc), status_code=500)
