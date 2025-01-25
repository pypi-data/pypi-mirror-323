# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import outbound_create_call_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.outbound_create_call_response import OutboundCreateCallResponse

__all__ = ["OutboundResource", "AsyncOutboundResource"]


class OutboundResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OutboundResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#accessing-raw-response-data-eg-headers
        """
        return OutboundResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OutboundResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#with_streaming_response
        """
        return OutboundResourceWithStreamingResponse(self)

    def create_call(
        self,
        *,
        agent_id: str,
        extras: object,
        from_phone: str,
        to_phone: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OutboundCreateCallResponse:
        """
        This operation allows you create a call

        Args:
          agent_id: Agent ID which will communicate with user

          extras: Extra parameters needed for agent on call

          from_phone: From phone number

          to_phone: The phone number to call

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/outbound/create-call",
            body=maybe_transform(
                {
                    "agent_id": agent_id,
                    "extras": extras,
                    "from_phone": from_phone,
                    "to_phone": to_phone,
                },
                outbound_create_call_params.OutboundCreateCallParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutboundCreateCallResponse,
        )


class AsyncOutboundResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOutboundResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncOutboundResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOutboundResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/Zywa-co/nebula-python-sdk#with_streaming_response
        """
        return AsyncOutboundResourceWithStreamingResponse(self)

    async def create_call(
        self,
        *,
        agent_id: str,
        extras: object,
        from_phone: str,
        to_phone: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> OutboundCreateCallResponse:
        """
        This operation allows you create a call

        Args:
          agent_id: Agent ID which will communicate with user

          extras: Extra parameters needed for agent on call

          from_phone: From phone number

          to_phone: The phone number to call

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/outbound/create-call",
            body=await async_maybe_transform(
                {
                    "agent_id": agent_id,
                    "extras": extras,
                    "from_phone": from_phone,
                    "to_phone": to_phone,
                },
                outbound_create_call_params.OutboundCreateCallParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OutboundCreateCallResponse,
        )


class OutboundResourceWithRawResponse:
    def __init__(self, outbound: OutboundResource) -> None:
        self._outbound = outbound

        self.create_call = to_raw_response_wrapper(
            outbound.create_call,
        )


class AsyncOutboundResourceWithRawResponse:
    def __init__(self, outbound: AsyncOutboundResource) -> None:
        self._outbound = outbound

        self.create_call = async_to_raw_response_wrapper(
            outbound.create_call,
        )


class OutboundResourceWithStreamingResponse:
    def __init__(self, outbound: OutboundResource) -> None:
        self._outbound = outbound

        self.create_call = to_streamed_response_wrapper(
            outbound.create_call,
        )


class AsyncOutboundResourceWithStreamingResponse:
    def __init__(self, outbound: AsyncOutboundResource) -> None:
        self._outbound = outbound

        self.create_call = async_to_streamed_response_wrapper(
            outbound.create_call,
        )
