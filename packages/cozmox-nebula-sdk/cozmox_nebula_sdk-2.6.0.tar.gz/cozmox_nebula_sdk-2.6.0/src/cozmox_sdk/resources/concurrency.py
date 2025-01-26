# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.concurrency_hello_response import ConcurrencyHelloResponse

__all__ = ["ConcurrencyResource", "AsyncConcurrencyResource"]


class ConcurrencyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ConcurrencyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#accessing-raw-response-data-eg-headers
        """
        return ConcurrencyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ConcurrencyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#with_streaming_response
        """
        return ConcurrencyResourceWithStreamingResponse(self)

    def hello(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConcurrencyHelloResponse:
        """This operation allows you get the number of concurrent calls for a user"""
        return self._get(
            "/v1/concurrency/retrieve",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConcurrencyHelloResponse,
        )


class AsyncConcurrencyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncConcurrencyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncConcurrencyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncConcurrencyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#with_streaming_response
        """
        return AsyncConcurrencyResourceWithStreamingResponse(self)

    async def hello(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ConcurrencyHelloResponse:
        """This operation allows you get the number of concurrent calls for a user"""
        return await self._get(
            "/v1/concurrency/retrieve",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConcurrencyHelloResponse,
        )


class ConcurrencyResourceWithRawResponse:
    def __init__(self, concurrency: ConcurrencyResource) -> None:
        self._concurrency = concurrency

        self.hello = to_raw_response_wrapper(
            concurrency.hello,
        )


class AsyncConcurrencyResourceWithRawResponse:
    def __init__(self, concurrency: AsyncConcurrencyResource) -> None:
        self._concurrency = concurrency

        self.hello = async_to_raw_response_wrapper(
            concurrency.hello,
        )


class ConcurrencyResourceWithStreamingResponse:
    def __init__(self, concurrency: ConcurrencyResource) -> None:
        self._concurrency = concurrency

        self.hello = to_streamed_response_wrapper(
            concurrency.hello,
        )


class AsyncConcurrencyResourceWithStreamingResponse:
    def __init__(self, concurrency: AsyncConcurrencyResource) -> None:
        self._concurrency = concurrency

        self.hello = async_to_streamed_response_wrapper(
            concurrency.hello,
        )
