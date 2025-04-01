# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["PaykeyUnmasked", "Data", "DataBankData", "DataStatusDetails", "Meta"]


class DataBankData(BaseModel):
    account_number: str
    """The bank account number.

    This value is masked by default for security reasons. Use the /unmask endpoint
    to access the unmasked value.
    """

    account_type: Literal["checking", "savings"]

    routing_number: str
    """The routing number of the bank account."""


class DataStatusDetails(BaseModel):
    message: str
    """A human-readable description of the current status."""

    reason: str
    """
    A machine-readable identifier for the specific status, useful for programmatic
    handling.
    """

    source: str
    """Identifies the origin of the status change (e.g., `bank_decline`, `watchtower`).

    This helps in tracking the cause of status updates.
    """


class Data(BaseModel):
    id: str
    """Unique identifier for the paykey."""

    created_at: datetime
    """Timestamp of when the paykey was created."""

    label: str
    """Human-readable label used to represent this paykey in a UI."""

    paykey: str
    """The tokenized paykey value.

    This value is used to create payments and should be stored securely.
    """

    source: Literal["bank_account", "straddle", "mx", "plaid"]

    status: Literal["pending", "active", "inactive", "rejected"]

    updated_at: datetime
    """Timestamp of the most recent update to the paykey."""

    bank_data: Optional[DataBankData] = None

    customer_id: Optional[str] = None
    """Unique identifier of the related customer object."""

    expires_at: Optional[datetime] = None
    """Expiration date and time of the paykey, if applicable."""

    institution_name: Optional[str] = None
    """Name of the financial institution."""

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the paykey in a structured
    format.
    """

    status_details: Optional[DataStatusDetails] = None


class Meta(BaseModel):
    api_request_id: str
    """Unique identifier for this API request, useful for troubleshooting."""

    api_request_timestamp: datetime
    """Timestamp for this API request, useful for troubleshooting."""


class PaykeyUnmasked(BaseModel):
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
