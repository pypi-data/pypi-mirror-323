# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = [
    "AccountCreateParams",
    "BusinessProfile",
    "BusinessProfileAddress",
    "BusinessProfileIndustry",
    "BusinessProfileSupportChannels",
]


class AccountCreateParams(TypedDict, total=False):
    access_level: Required[Literal["standard", "managed"]]
    """The access level granted to the account.

    This is determined by your platform configuration. Use `standard` unless
    instructed otherwise by Straddle.
    """

    account_type: Required[Literal["business"]]
    """The type of account to be created. Currently, only `business` is supported."""

    business_profile: Required[BusinessProfile]

    organization_id: Required[str]
    """The unique identifier of the organization related to this account."""

    external_id: Optional[str]
    """
    Unique identifier for the account in your database, used for cross-referencing
    between Straddle and your systems.
    """

    metadata: Optional[Dict[str, Optional[str]]]
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the account in a structured
    format.
    """

    correlation_id: Annotated[str, PropertyInfo(alias="correlation-id")]

    request_id: Annotated[str, PropertyInfo(alias="request-id")]


class BusinessProfileAddress(TypedDict, total=False):
    city: Optional[str]
    """City, district, suburb, town, or village."""

    country: Optional[str]
    """The country of the address, in ISO 3166-1 alpha-2 format."""

    line1: Optional[str]
    """Primary address line (e.g., street, PO Box)."""

    line2: Optional[str]
    """Secondary address line (e.g., apartment, suite, unit, or building)."""

    postal_code: Optional[str]
    """Postal or ZIP code."""

    state: Optional[str]
    """Two-letter state code."""


class BusinessProfileIndustry(TypedDict, total=False):
    category: Optional[str]
    """The general category of the industry. Required if not providing MCC."""

    mcc: Optional[str]
    """The Merchant Category Code (MCC) that best describes the business. Optional."""

    sector: Optional[str]
    """The specific sector within the industry category.

    Required if not providing MCC.
    """


class BusinessProfileSupportChannels(TypedDict, total=False):
    email: Optional[str]
    """The email address for customer support inquiries."""

    phone: Optional[str]
    """The phone number for customer support."""

    url: Optional[str]
    """The URL of the business's customer support page or contact form."""


class BusinessProfile(TypedDict, total=False):
    name: Required[str]
    """The operating or trade name of the business."""

    website: Required[str]
    """URL of the business's primary marketing website."""

    address: Optional[BusinessProfileAddress]
    """The address object is optional. If provided, it must be a valid address."""

    description: Optional[str]
    """A brief description of the business and its products or services."""

    industry: BusinessProfileIndustry

    legal_name: Optional[str]
    """The official registered name of the business."""

    phone: Optional[str]
    """The primary contact phone number for the business."""

    support_channels: BusinessProfileSupportChannels

    tax_id: Optional[str]
    """The business's tax identification number (e.g., EIN in the US)."""

    use_case: Optional[str]
    """A description of how the business intends to use Straddle's services."""
