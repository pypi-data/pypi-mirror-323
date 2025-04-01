from typing import Dict, Any, Generic, Optional, Callable, TypeVar
from pydantic import BaseModel
from test_infinity_stones.network_router.http_types import HttpMethod
from test_infinity_stones.network_router.utils.url_builder import build_url

ResponseType = TypeVar("ResponseType")

class HttpRequest(BaseModel, Generic[ResponseType]):
    """
    Represents an HTTP request to be made to an HTTP endpoint.
    """

    method: HttpMethod
    base_url: str
    path: str
    api_version: Optional[str] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any] | list[Any]] = None
    response_body_decoder: Optional[Callable[[Any], ResponseType]] = None
    request_body_encoder: Optional[Callable[[Any], Dict[str, Any]]] = None

    @property
    def url(self) -> str:
        """Constructs the full URL for the endpoint following on the `base_url/api_version/path` scheme"""
        return build_url(self.base_url, self.api_version, self.path)