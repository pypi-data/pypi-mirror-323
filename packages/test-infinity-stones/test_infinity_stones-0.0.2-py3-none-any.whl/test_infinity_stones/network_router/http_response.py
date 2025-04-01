from typing import Any, Generic, TypeVar
from pydantic import BaseModel

ResponseType = TypeVar("ResponseType")

class HttpResponse(BaseModel, Generic[ResponseType]):
    """
    Represents an HTTP response from an API endpoint.
    """

    status_code: int
    headers: Any = {}
    body: ResponseType