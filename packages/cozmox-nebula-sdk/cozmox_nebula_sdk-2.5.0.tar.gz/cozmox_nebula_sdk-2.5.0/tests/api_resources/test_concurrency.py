# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from cozmox_sdk import CozmoxSDK, AsyncCozmoxSDK
from tests.utils import assert_matches_type
from cozmox_sdk.types import ConcurrencyHelloResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestConcurrency:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_hello(self, client: CozmoxSDK) -> None:
        concurrency = client.concurrency.hello()
        assert_matches_type(ConcurrencyHelloResponse, concurrency, path=["response"])

    @parametrize
    def test_raw_response_hello(self, client: CozmoxSDK) -> None:
        response = client.concurrency.with_raw_response.hello()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        concurrency = response.parse()
        assert_matches_type(ConcurrencyHelloResponse, concurrency, path=["response"])

    @parametrize
    def test_streaming_response_hello(self, client: CozmoxSDK) -> None:
        with client.concurrency.with_streaming_response.hello() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            concurrency = response.parse()
            assert_matches_type(ConcurrencyHelloResponse, concurrency, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncConcurrency:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_hello(self, async_client: AsyncCozmoxSDK) -> None:
        concurrency = await async_client.concurrency.hello()
        assert_matches_type(ConcurrencyHelloResponse, concurrency, path=["response"])

    @parametrize
    async def test_raw_response_hello(self, async_client: AsyncCozmoxSDK) -> None:
        response = await async_client.concurrency.with_raw_response.hello()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        concurrency = await response.parse()
        assert_matches_type(ConcurrencyHelloResponse, concurrency, path=["response"])

    @parametrize
    async def test_streaming_response_hello(self, async_client: AsyncCozmoxSDK) -> None:
        async with async_client.concurrency.with_streaming_response.hello() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            concurrency = await response.parse()
            assert_matches_type(ConcurrencyHelloResponse, concurrency, path=["response"])

        assert cast(Any, response.is_closed) is True
