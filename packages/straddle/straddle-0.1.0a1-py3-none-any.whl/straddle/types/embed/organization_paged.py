# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["OrganizationPaged", "Data", "Meta"]


class Data(BaseModel):
    id: str
    """Straddle's unique identifier for the organization."""

    name: str
    """The name of the organization."""

    created_at: Optional[datetime] = None
    """Timestamp of when the organization was created."""

    external_id: Optional[str] = None
    """
    Unique identifier for the organization in your database, used for
    cross-referencing between Straddle and your systems.
    """

    metadata: Optional[Dict[str, Optional[str]]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the organization in a structured
    format.
    """

    updated_at: Optional[datetime] = None
    """Timestamp of the most recent update to the organization."""


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


class OrganizationPaged(BaseModel):
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
