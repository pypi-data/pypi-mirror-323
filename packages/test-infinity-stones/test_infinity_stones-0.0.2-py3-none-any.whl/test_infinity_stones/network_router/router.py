from typing import Callable, Optional, TypeVar, overload
import httpx


from test_infinity_stones.network_router.http_exception import HttpException
from test_infinity_stones.network_router.http_request import HttpRequest
from test_infinity_stones.network_router.http_response import HttpResponse

ResponseType = TypeVar('ResponseType')

class NetworkRouter:
    @overload
    async def execute_http_request(self, http_request: HttpRequest[ResponseType]) -> HttpResponse[ResponseType]:
        """Executes the provided HttpRequest and returns the response."""
        ...


    @overload
    async def execute_http_request(
        self, http_request: HttpRequest[ResponseType],
        batch_processor: Callable[[HttpRequest], list[HttpRequest]]
    ) -> HttpResponse[ResponseType]:
        """Executes the provided HttpRequest and returns the response."""
        ...


    async def execute_http_request(
        self,
        http_request: HttpRequest[ResponseType],
        batch_processor: Optional[Callable[[HttpRequest], list[HttpRequest]]] = None
    ) -> HttpResponse[ResponseType] | list[HttpResponse[ResponseType]]:
        """Executes the provided HttpRequest and returns the response."""

        if batch_processor:
            return await self._execute_batch_http_request(http_request, batch_processor)
        else:
            return await self._execute_plain_http_request(http_request)


    async def _execute_plain_http_request(
        self, http_request: HttpRequest[ResponseType]
    ) -> HttpResponse[ResponseType]:
        """Executes the provided HttpRequest and returns the response."""

        async with httpx.AsyncClient() as client:
            try:
                httpx_response = await client.request(
                    method=http_request.method.value,
                    url=http_request.url,
                    headers=http_request.headers,
                    params=http_request.query_params,
                    json=http_request.body,
                )
            except httpx.HTTPStatusError as e:
                raise HttpException(e.response.status_code, e.response.text)

        http_response = self.create_http_response(http_request, httpx_response)

        return http_response


    async def _execute_batch_http_request(
        self,
        http_request: HttpRequest,
        batch_processor: Callable[[HttpRequest], list[HttpRequest]]
    ) -> list[HttpResponse]:
        """Executes the provided HttpRequest and returns the response."""

        batched_http_requests = batch_processor(http_request)
        batched_http_responses: list[HttpResponse] = []

        for batched_http_request in batched_http_requests:
            batched_http_response = await self._execute_plain_http_request(batched_http_request)
            batched_http_responses.append(
                HttpResponse(
                    status_code=200,
                    body=batched_http_response,
                )
            )

        return batched_http_responses


    def create_http_response(
        self, http_request: HttpRequest[ResponseType], httpx_response: httpx.Response
    ) -> HttpResponse[ResponseType]:
        httpx_response_body = httpx_response.json()

        response_body = (
            http_request.response_body_decoder(httpx_response_body)
            if http_request.response_body_decoder and 200 <= httpx_response.status_code <= 299
            else httpx_response_body
        )

        http_response = HttpResponse(
            status_code=httpx_response.status_code,
            headers=httpx_response.headers.__dict__,
            body=response_body,
        )

        return http_response