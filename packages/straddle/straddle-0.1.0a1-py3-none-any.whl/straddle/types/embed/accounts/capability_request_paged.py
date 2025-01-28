# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["CapabilityRequestPaged", "Data", "Meta"]


class Data(BaseModel):
    id: str
    """Unique identifier for the capability request."""

    account_id: str
    """The unique identifier of the account associated with this capability request."""

    category: Literal["payment_type", "customer_type", "consent_type"]
    """The category of the requested capability.

    Use `payment_type` for charges and payouts, `customer_type` to define
    `individuals` or `businesses`, and `consent_type` for `signed_agreement` or
    `internet` payment authorization.
    """

    created_at: datetime
    """Timestamp of when the capability request was created."""

    status: Literal["active", "inactive", "in_review", "rejected"]
    """The current status of the capability request."""

    type: Literal["charges", "payouts", "individuals", "businesses", "signed_agreement", "internet"]
    """The specific type of capability being requested within the category."""

    updated_at: datetime
    """Timestamp of the most recent update to the capability request."""

    settings: Optional[Dict[str, object]] = None
    """Any specific settings or configurations related to the requested capability."""


class Meta(BaseModel):
    api_request_id: str
    """Unique identifier for this API request, useful for troubleshooting."""

    api_request_timestamp: datetime
    """Timestamp for this API request, useful for troubleshooting."""

    max_page_size: int
    """Maximum allowed page size for this endpoint."""

    page_number: int
    """Page number for paginated results."""

    page_size: int
    """Number of items per page in this response."""

    sort_by: str
    """The field that the results were sorted by."""

    sort_order: Literal["asc", "desc"]
    """The order that the results were sorted by."""

    total_items: int
    """Total number of items returned in this response."""


class CapabilityRequestPaged(BaseModel):
    data: List[Data]

    meta: Meta
    """
    Metadata about the API request, including an identifier, timestamp, and
    pagination details.
    """

    response_type: Literal["object", "array", "error", "none"]
    """Indicates the structure of the returned content.

    - "object" means the `data` field contains a single JSON object.
    - "array" means the `data` field contains an array of objects.
    - "error" means the `data` field contains an error object with details of the
      issue.
    - "none" means no data is returned.
    """
