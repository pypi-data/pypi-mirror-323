import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel

class HttpMethod(Enum):
    """HTTP methods for HTTP requests"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"
    CONNECT = "CONNECT"

class APIAuth(BaseModel):
    """Authentication types for HTTP requests"""

    @staticmethod
    def basic(username: str, password: str) -> dict[str, str]:
        return {"Authorization": f"Basic {username}:{password}"}

    @staticmethod
    def api_key(api_key: str) -> dict[str, str]:
        return {"API-Key": api_key}

    @staticmethod
    def bearer(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def user_id_and_token(user_id: str, access_token: str) -> dict[str, str]:
        return {"user_id": f"{user_id}", "access_token": f"{access_token}"}

    @staticmethod
    def client_id_and_token(client_id: str, access_token: str) -> dict[str, str]:
        return {"client_id": f"{client_id}", "access_token": f"{access_token}"}

    @staticmethod
    def custom(custom_auth_headers: dict[str, Any]) -> dict[str, str]:
        return custom_auth_headers

    @staticmethod
    def none() -> dict[str, str]:
        return {}