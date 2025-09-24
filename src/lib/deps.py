from typing import Dict, Optional
from litestar import Request


def provide_current_user(request: Request) -> Optional[Dict]:
    return request.user if hasattr(request, "user") else None
