# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cozmox_sdk import CozmoxSDK, AsyncCozmoxSDK
from tests.utils import assert_matches_type
from cozmox_sdk.types import NebulaHelloResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestNebula:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_hello(self, client: CozmoxSDK) -> None:
        nebula = client.nebula.hello()
        assert_matches_type(NebulaHelloResponse, nebula, path=["response"])

    @parametrize
    def test_raw_response_hello(self, client: CozmoxSDK) -> None:
        response = client.nebula.with_raw_response.hello()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        nebula = response.parse()
        assert_matches_type(NebulaHelloResponse, nebula, path=["response"])

    @parametrize
    def test_streaming_response_hello(self, client: CozmoxSDK) -> None:
        with client.nebula.with_streaming_response.hello() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            nebula = response.parse()
            assert_matches_type(NebulaHelloResponse, nebula, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncNebula:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_hello(self, async_client: AsyncCozmoxSDK) -> None:
        nebula = await async_client.nebula.hello()
        assert_matches_type(NebulaHelloResponse, nebula, path=["response"])

    @parametrize
    async def test_raw_response_hello(self, async_client: AsyncCozmoxSDK) -> None:
        response = await async_client.nebula.with_raw_response.hello()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        nebula = await response.parse()
        assert_matches_type(NebulaHelloResponse, nebula, path=["response"])

    @parametrize
    async def test_streaming_response_hello(self, async_client: AsyncCozmoxSDK) -> None:
        async with async_client.nebula.with_streaming_response.hello() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            nebula = await response.parse()
            assert_matches_type(NebulaHelloResponse, nebula, path=["response"])

        assert cast(Any, response.is_closed) is True
