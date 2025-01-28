# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import date, datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "Charge",
    "Data",
    "DataConfig",
    "DataDevice",
    "DataStatusDetails",
    "DataStatusHistory",
    "DataCustomerDetails",
    "DataPaykeyDetails",
    "Meta",
]


class DataConfig(BaseModel):
    balance_check: Literal["required", "enabled", "disabled"]
    """Defines whether to check the customer's balance before processing the charge."""


class DataDevice(BaseModel):
    ip_address: str
    """
    The IP address of the device used when the customer authorized the charge or
    payout. Use `0.0.0.0` to represent an offline consent interaction.
    """


class DataStatusDetails(BaseModel):
    changed_at: datetime
    """The time the status change occurred."""

    message: str
    """A human-readable description of the current status."""

    reason: Literal[
        "insufficient_funds",
        "closed_bank_account",
        "invalid_bank_account",
        "invalid_routing",
        "disputed",
        "payment_stopped",
        "owner_deceased",
        "frozen_bank_account",
        "risk_review",
        "fraudulent",
        "duplicate_entry",
        "invalid_paykey",
        "payment_blocked",
        "amount_too_large",
        "too_many_attempts",
        "internal_system_error",
        "user_request",
        "ok",
        "other_network_return",
        "payout_refused",
    ]
    """
    A machine-readable identifier for the specific status, useful for programmatic
    handling.
    """

    source: Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]
    """Identifies the origin of the status change (e.g., `bank_decline`, `watchtower`).

    This helps in tracking the cause of status updates.
    """


class DataStatusHistory(BaseModel):
    changed_at: datetime
    """The time the status change occurred."""

    message: str
    """A human-readable description of the status."""

    reason: Literal[
        "insufficient_funds",
        "closed_bank_account",
        "invalid_bank_account",
        "invalid_routing",
        "disputed",
        "payment_stopped",
        "owner_deceased",
        "frozen_bank_account",
        "risk_review",
        "fraudulent",
        "duplicate_entry",
        "invalid_paykey",
        "payment_blocked",
        "amount_too_large",
        "too_many_attempts",
        "internal_system_error",
        "user_request",
        "ok",
        "other_network_return",
        "payout_refused",
    ]
    """
    A machine-readable identifier for the specific status, useful for programmatic
    handling.
    """

    source: Literal["watchtower", "bank_decline", "customer_dispute", "user_action", "system"]
    """Identifies the origin of the status change (e.g., `bank_decline`, `watchtower`).

    This helps in tracking the cause of status updates.
    """

    status: Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    """The current status of the `charge` or `payout`."""

    code: Optional[str] = None
    """The status code if applicable."""


class DataCustomerDetails(BaseModel):
    id: str
    """Unique identifier for the customer."""

    customer_type: Literal["individual", "business"]
    """The type of customer."""

    name: str
    """The name of the customer."""


class DataPaykeyDetails(BaseModel):
    id: str
    """Unique identifier for the paykey."""

    customer_id: str
    """Unique identifier for the customer associated with the paykey."""

    label: str
    """Human-readable label used to represent this paykey in a UI."""

    balance: Optional[int] = None
    """
    The most recent balance of the bank account associated with the paykey in
    dollars.
    """


class Data(BaseModel):
    id: str
    """Unique identifier for the charge."""

    amount: int
    """The amount of the charge in cents."""

    config: DataConfig
    """Configuration options for the charge."""

    consent_type: Literal["internet", "signed"]
    """The channel or mechanism through which the payment was authorized.

    Use `internet` for payments made online or through a mobile app and `signed` for
    signed agreements where there is a consent form or contract. Use `signed` for
    PDF signatures.
    """

    currency: str
    """The currency of the charge. Only USD is supported."""

    description: str
    """An arbitrary description for the charge."""

    device: DataDevice
    """Information about the device used when the customer authorized the payment."""

    external_id: str
    """Unique identifier for the charge in your database.

    This value must be unique across all charges.
    """

    paykey: str
    """Value of the `paykey` used for the charge."""

    payment_date: date
    """The desired date on which the payment should be occur.

    For charges, this means the date you want the customer to be debited on.
    """

    status: Literal["created", "scheduled", "failed", "cancelled", "on_hold", "pending", "paid", "reversed"]
    """The current status of the charge."""

    status_details: DataStatusDetails
    """Additional details about the current status of the charge."""

    status_history: List[DataStatusHistory]

    created_at: Optional[datetime] = None
    """Timestamp of when the charge was created."""

    customer_details: Optional[DataCustomerDetails] = None
    """Information about the customer associated with the charge."""

    effective_at: Optional[datetime] = None
    """
    Timestamp of when the charge was effective in the customer's bank account,
    otherwise known as the date on which the customer is debited.
    """

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the charge in a structured
    format.
    """

    paykey_details: Optional[DataPaykeyDetails] = None
    """Information about the paykey used for the charge."""

    payment_rail: Optional[Literal["ach"]] = None
    """The payment rail that the charge will be processed through."""

    processed_at: Optional[datetime] = None
    """
    Timestamp of when the charge was processed by Straddle and originated to the
    payment rail.
    """

    updated_at: Optional[datetime] = None
    """Timestamp of when the charge was last updated."""


class Meta(BaseModel):
    api_request_id: str
    """Unique identifier for this API request, useful for troubleshooting."""

    api_request_timestamp: datetime
    """Timestamp for this API request, useful for troubleshooting."""


class Charge(BaseModel):
    data: Data

    meta: Meta
    """Metadata about the API request, including an identifier and timestamp."""

    response_type: Literal["object", "array", "error", "none"]
    """Indicates the structure of the returned content.

    - "object" means the `data` field contains a single JSON object.
    - "array" means the `data` field contains an array of objects.
    - "error" means the `data` field contains an error object with details of the
      issue.
    - "none" means no data is returned.
    """
