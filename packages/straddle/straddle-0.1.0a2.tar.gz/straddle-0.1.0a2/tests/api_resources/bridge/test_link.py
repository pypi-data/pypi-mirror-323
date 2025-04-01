# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from straddle import Straddle, AsyncStraddle
from tests.utils import assert_matches_type
from straddle.types import Paykey

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLink:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_bank_account(self, client: Straddle) -> None:
        link = client.bridge.link.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    def test_method_bank_account_with_all_params(self, client: Straddle) -> None:
        link = client.bridge.link.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    def test_raw_response_bank_account(self, client: Straddle) -> None:
        response = client.bridge.link.with_raw_response.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        link = response.parse()
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    def test_streaming_response_bank_account(self, client: Straddle) -> None:
        with client.bridge.link.with_streaming_response.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            link = response.parse()
            assert_matches_type(Paykey, link, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_plaid(self, client: Straddle) -> None:
        link = client.bridge.link.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    def test_method_plaid_with_all_params(self, client: Straddle) -> None:
        link = client.bridge.link.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    def test_raw_response_plaid(self, client: Straddle) -> None:
        response = client.bridge.link.with_raw_response.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        link = response.parse()
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    def test_streaming_response_plaid(self, client: Straddle) -> None:
        with client.bridge.link.with_streaming_response.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            link = response.parse()
            assert_matches_type(Paykey, link, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLink:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_bank_account(self, async_client: AsyncStraddle) -> None:
        link = await async_client.bridge.link.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    async def test_method_bank_account_with_all_params(self, async_client: AsyncStraddle) -> None:
        link = await async_client.bridge.link.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    async def test_raw_response_bank_account(self, async_client: AsyncStraddle) -> None:
        response = await async_client.bridge.link.with_raw_response.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        link = await response.parse()
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    async def test_streaming_response_bank_account(self, async_client: AsyncStraddle) -> None:
        async with async_client.bridge.link.with_streaming_response.bank_account(
            account_number="account_number",
            account_type="checking",
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            routing_number="xxxxxxxxx",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            link = await response.parse()
            assert_matches_type(Paykey, link, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_plaid(self, async_client: AsyncStraddle) -> None:
        link = await async_client.bridge.link.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    async def test_method_plaid_with_all_params(self, async_client: AsyncStraddle) -> None:
        link = await async_client.bridge.link.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
            metadata={"foo": "string"},
            correlation_id="Correlation-Id",
            request_id="Request-Id",
            straddle_account_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    async def test_raw_response_plaid(self, async_client: AsyncStraddle) -> None:
        response = await async_client.bridge.link.with_raw_response.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        link = await response.parse()
        assert_matches_type(Paykey, link, path=["response"])

    @parametrize
    async def test_streaming_response_plaid(self, async_client: AsyncStraddle) -> None:
        async with async_client.bridge.link.with_streaming_response.plaid(
            customer_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            plaid_token="plaid_token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            link = await response.parse()
            assert_matches_type(Paykey, link, path=["response"])

        assert cast(Any, response.is_closed) is True
