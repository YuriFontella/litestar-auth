import logging

from litestar import Litestar
from src.server.core import ApplicationCore


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)


def create_app() -> Litestar:
    return Litestar(plugins=[ApplicationCore()])


app = create_app()
