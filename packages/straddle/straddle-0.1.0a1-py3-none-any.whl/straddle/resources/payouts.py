# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from datetime import date

import httpx

from ..types import (
    payout_hold_params,
    payout_cancel_params,
    payout_create_params,
    payout_update_params,
    payout_release_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    strip_not_given,
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
from ..types.payout import Payout

__all__ = ["PayoutsResource", "AsyncPayoutsResource"]


class PayoutsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PayoutsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return PayoutsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PayoutsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return PayoutsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        amount: int,
        currency: str,
        description: str,
        device: payout_create_params.Device,
        external_id: str,
        paykey: str,
        payment_date: Union[str, date],
        config: object | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """
        Use payouts to send money to your customers.

        Args:
          amount: The amount of the payout in cents.

          currency: The currency of the payout. Only USD is supported.

          description: An arbitrary description for the payout.

          device: Information about the device used when the customer authorized the payout.

          external_id: Unique identifier for the payout in your database. This value must be unique
              across all payouts.

          paykey: Value of the `paykey` used for the payout.

          payment_date: The desired date on which the payout should be occur. For payouts, this means
              the date you want the funds to be sent from your bank account.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the payout in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._post(
            "/v1/payouts",
            body=maybe_transform(
                {
                    "amount": amount,
                    "currency": currency,
                    "description": description,
                    "device": device,
                    "external_id": external_id,
                    "paykey": paykey,
                    "payment_date": payment_date,
                    "config": config,
                    "metadata": metadata,
                },
                payout_create_params.PayoutCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    def update(
        self,
        id: str,
        *,
        amount: int,
        description: str,
        payment_date: Union[str, date],
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Update the details of a payout prior to processing.

        The status of the payout
        must be `created`, `scheduled`, or `on_hold`.

        Args:
          amount: The amount of the payout in cents.

          description: An arbitrary description for the payout.

          payment_date: The desired date on which the payment should be occur. For payouts, this means
              the date you want the funds to be sent from your bank account.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the payout in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/payouts/{id}",
            body=maybe_transform(
                {
                    "amount": amount,
                    "description": description,
                    "payment_date": payment_date,
                    "metadata": metadata,
                },
                payout_update_params.PayoutUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    def cancel(
        self,
        id: str,
        *,
        reason: str,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Cancel a payout to prevent it from being processed.

        The status of the payout
        must be `created`, `scheduled`, or `on_hold`.

        Args:
          reason: Details about why the payout status was updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/payouts/{id}/cancel",
            body=maybe_transform({"reason": reason}, payout_cancel_params.PayoutCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    def get(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Retrieves the details of an existing payout.

        Supply the unique payout `id` to
        retrieve the corresponding payout information.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._get(
            f"/v1/payouts/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    def hold(
        self,
        id: str,
        *,
        reason: str,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Hold a payout to prevent it from being processed.

        The status of the payout must
        be `created`, `scheduled`, or `on_hold`.

        Args:
          reason: Details about why the payout status was updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/payouts/{id}/hold",
            body=maybe_transform({"reason": reason}, payout_hold_params.PayoutHoldParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    def release(
        self,
        id: str,
        *,
        reason: str,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """
        Release a payout from a `hold` status to allow it to be rescheduled for
        processing.

        Args:
          reason: Details about why the payout status was updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return self._put(
            f"/v1/payouts/{id}/release",
            body=maybe_transform({"reason": reason}, payout_release_params.PayoutReleaseParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )


class AsyncPayoutsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPayoutsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/straddleio/straddle-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPayoutsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPayoutsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/straddleio/straddle-python#with_streaming_response
        """
        return AsyncPayoutsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        amount: int,
        currency: str,
        description: str,
        device: payout_create_params.Device,
        external_id: str,
        paykey: str,
        payment_date: Union[str, date],
        config: object | NotGiven = NOT_GIVEN,
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """
        Use payouts to send money to your customers.

        Args:
          amount: The amount of the payout in cents.

          currency: The currency of the payout. Only USD is supported.

          description: An arbitrary description for the payout.

          device: Information about the device used when the customer authorized the payout.

          external_id: Unique identifier for the payout in your database. This value must be unique
              across all payouts.

          paykey: Value of the `paykey` used for the payout.

          payment_date: The desired date on which the payout should be occur. For payouts, this means
              the date you want the funds to be sent from your bank account.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the payout in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._post(
            "/v1/payouts",
            body=await async_maybe_transform(
                {
                    "amount": amount,
                    "currency": currency,
                    "description": description,
                    "device": device,
                    "external_id": external_id,
                    "paykey": paykey,
                    "payment_date": payment_date,
                    "config": config,
                    "metadata": metadata,
                },
                payout_create_params.PayoutCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    async def update(
        self,
        id: str,
        *,
        amount: int,
        description: str,
        payment_date: Union[str, date],
        metadata: Optional[Dict[str, str]] | NotGiven = NOT_GIVEN,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Update the details of a payout prior to processing.

        The status of the payout
        must be `created`, `scheduled`, or `on_hold`.

        Args:
          amount: The amount of the payout in cents.

          description: An arbitrary description for the payout.

          payment_date: The desired date on which the payment should be occur. For payouts, this means
              the date you want the funds to be sent from your bank account.

          metadata: Up to 20 additional user-defined key-value pairs. Useful for storing additional
              information about the payout in a structured format.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/payouts/{id}",
            body=await async_maybe_transform(
                {
                    "amount": amount,
                    "description": description,
                    "payment_date": payment_date,
                    "metadata": metadata,
                },
                payout_update_params.PayoutUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    async def cancel(
        self,
        id: str,
        *,
        reason: str,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Cancel a payout to prevent it from being processed.

        The status of the payout
        must be `created`, `scheduled`, or `on_hold`.

        Args:
          reason: Details about why the payout status was updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/payouts/{id}/cancel",
            body=await async_maybe_transform({"reason": reason}, payout_cancel_params.PayoutCancelParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    async def get(
        self,
        id: str,
        *,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Retrieves the details of an existing payout.

        Supply the unique payout `id` to
        retrieve the corresponding payout information.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._get(
            f"/v1/payouts/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    async def hold(
        self,
        id: str,
        *,
        reason: str,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """Hold a payout to prevent it from being processed.

        The status of the payout must
        be `created`, `scheduled`, or `on_hold`.

        Args:
          reason: Details about why the payout status was updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/payouts/{id}/hold",
            body=await async_maybe_transform({"reason": reason}, payout_hold_params.PayoutHoldParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )

    async def release(
        self,
        id: str,
        *,
        reason: str,
        correlation_id: str | NotGiven = NOT_GIVEN,
        request_id: str | NotGiven = NOT_GIVEN,
        straddle_account_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Payout:
        """
        Release a payout from a `hold` status to allow it to be rescheduled for
        processing.

        Args:
          reason: Details about why the payout status was updated.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {
            **strip_not_given(
                {
                    "Correlation-Id": correlation_id,
                    "Request-Id": request_id,
                    "Straddle-Account-Id": straddle_account_id,
                }
            ),
            **(extra_headers or {}),
        }
        return await self._put(
            f"/v1/payouts/{id}/release",
            body=await async_maybe_transform({"reason": reason}, payout_release_params.PayoutReleaseParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Payout,
        )


class PayoutsResourceWithRawResponse:
    def __init__(self, payouts: PayoutsResource) -> None:
        self._payouts = payouts

        self.create = to_raw_response_wrapper(
            payouts.create,
        )
        self.update = to_raw_response_wrapper(
            payouts.update,
        )
        self.cancel = to_raw_response_wrapper(
            payouts.cancel,
        )
        self.get = to_raw_response_wrapper(
            payouts.get,
        )
        self.hold = to_raw_response_wrapper(
            payouts.hold,
        )
        self.release = to_raw_response_wrapper(
            payouts.release,
        )


class AsyncPayoutsResourceWithRawResponse:
    def __init__(self, payouts: AsyncPayoutsResource) -> None:
        self._payouts = payouts

        self.create = async_to_raw_response_wrapper(
            payouts.create,
        )
        self.update = async_to_raw_response_wrapper(
            payouts.update,
        )
        self.cancel = async_to_raw_response_wrapper(
            payouts.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            payouts.get,
        )
        self.hold = async_to_raw_response_wrapper(
            payouts.hold,
        )
        self.release = async_to_raw_response_wrapper(
            payouts.release,
        )


class PayoutsResourceWithStreamingResponse:
    def __init__(self, payouts: PayoutsResource) -> None:
        self._payouts = payouts

        self.create = to_streamed_response_wrapper(
            payouts.create,
        )
        self.update = to_streamed_response_wrapper(
            payouts.update,
        )
        self.cancel = to_streamed_response_wrapper(
            payouts.cancel,
        )
        self.get = to_streamed_response_wrapper(
            payouts.get,
        )
        self.hold = to_streamed_response_wrapper(
            payouts.hold,
        )
        self.release = to_streamed_response_wrapper(
            payouts.release,
        )


class AsyncPayoutsResourceWithStreamingResponse:
    def __init__(self, payouts: AsyncPayoutsResource) -> None:
        self._payouts = payouts

        self.create = async_to_streamed_response_wrapper(
            payouts.create,
        )
        self.update = async_to_streamed_response_wrapper(
            payouts.update,
        )
        self.cancel = async_to_streamed_response_wrapper(
            payouts.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            payouts.get,
        )
        self.hold = async_to_streamed_response_wrapper(
            payouts.hold,
        )
        self.release = async_to_streamed_response_wrapper(
            payouts.release,
        )
