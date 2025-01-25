# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cozmox_sdk import CozmoxSDK, AsyncCozmoxSDK
from tests.utils import assert_matches_type
from cozmox_sdk.types import OutboundCreateCallResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOutbound:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_call(self, client: CozmoxSDK) -> None:
        outbound = client.outbound.create_call(
            agent_id="cx_xxxxxx",
            extras='{"Name": "Liza", "current_datetime": "2025-01-01 10:10:10"}',
            from_phone="+1234567890",
            to_phone="+1234567890",
        )
        assert_matches_type(OutboundCreateCallResponse, outbound, path=["response"])

    @parametrize
    def test_raw_response_create_call(self, client: CozmoxSDK) -> None:
        response = client.outbound.with_raw_response.create_call(
            agent_id="cx_xxxxxx",
            extras='{"Name": "Liza", "current_datetime": "2025-01-01 10:10:10"}',
            from_phone="+1234567890",
            to_phone="+1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outbound = response.parse()
        assert_matches_type(OutboundCreateCallResponse, outbound, path=["response"])

    @parametrize
    def test_streaming_response_create_call(self, client: CozmoxSDK) -> None:
        with client.outbound.with_streaming_response.create_call(
            agent_id="cx_xxxxxx",
            extras='{"Name": "Liza", "current_datetime": "2025-01-01 10:10:10"}',
            from_phone="+1234567890",
            to_phone="+1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outbound = response.parse()
            assert_matches_type(OutboundCreateCallResponse, outbound, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncOutbound:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create_call(self, async_client: AsyncCozmoxSDK) -> None:
        outbound = await async_client.outbound.create_call(
            agent_id="cx_xxxxxx",
            extras='{"Name": "Liza", "current_datetime": "2025-01-01 10:10:10"}',
            from_phone="+1234567890",
            to_phone="+1234567890",
        )
        assert_matches_type(OutboundCreateCallResponse, outbound, path=["response"])

    @parametrize
    async def test_raw_response_create_call(self, async_client: AsyncCozmoxSDK) -> None:
        response = await async_client.outbound.with_raw_response.create_call(
            agent_id="cx_xxxxxx",
            extras='{"Name": "Liza", "current_datetime": "2025-01-01 10:10:10"}',
            from_phone="+1234567890",
            to_phone="+1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        outbound = await response.parse()
        assert_matches_type(OutboundCreateCallResponse, outbound, path=["response"])

    @parametrize
    async def test_streaming_response_create_call(self, async_client: AsyncCozmoxSDK) -> None:
        async with async_client.outbound.with_streaming_response.create_call(
            agent_id="cx_xxxxxx",
            extras='{"Name": "Liza", "current_datetime": "2025-01-01 10:10:10"}',
            from_phone="+1234567890",
            to_phone="+1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            outbound = await response.parse()
            assert_matches_type(OutboundCreateCallResponse, outbound, path=["response"])

        assert cast(Any, response.is_closed) is True
