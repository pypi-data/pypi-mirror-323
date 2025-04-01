from typing import Any

from fastapi import HTTPException, status
from test_infinity_stones.auth.user_auth_schemas import UserAuthResponse
from test_infinity_stones.network_router import HttpRequest, APIAuth, HttpMethod, NetworkRouter
from test_infinity_stones.config import Settings
import logging

logger = logging.getLogger()

class Authenticator:
    def __init__(self, settings: Settings, network_router: NetworkRouter = NetworkRouter()):
        self._settings = settings
        self._network_router = network_router


    async def authenticate_user(self, access_token: str) -> UserAuthResponse:
        request = HttpRequest[Any](
            method=HttpMethod.GET,
            base_url=self._settings.AUTH_SERVICE_BASE_URL,
            path=self._settings.AUTHENTICATE_USER_ENDPOINT_PATH,
            headers=APIAuth.bearer(access_token),
        )

        try:
            response = await self._network_router.execute_http_request(request)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.body)

        except Exception as e:
            logger.error(f"Error while authenticating user {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return UserAuthResponse(**response.body)