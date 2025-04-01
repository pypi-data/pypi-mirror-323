# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = [
    "AccountPaged",
    "Data",
    "DataStatusDetail",
    "DataBusinessProfile",
    "DataBusinessProfileAddress",
    "DataBusinessProfileIndustry",
    "DataBusinessProfileSupportChannels",
    "DataCapabilities",
    "DataCapabilitiesConsentTypes",
    "DataCapabilitiesConsentTypesInternet",
    "DataCapabilitiesConsentTypesSignedAgreement",
    "DataCapabilitiesCustomerTypes",
    "DataCapabilitiesCustomerTypesBusinesses",
    "DataCapabilitiesCustomerTypesIndividuals",
    "DataCapabilitiesPaymentTypes",
    "DataCapabilitiesPaymentTypesCharges",
    "DataCapabilitiesPaymentTypesPayouts",
    "DataSettings",
    "DataSettingsCharges",
    "DataSettingsPayouts",
    "DataTermsOfService",
    "Meta",
]


class DataStatusDetail(BaseModel):
    code: str
    """
    A machine-readable code for the specific status, useful for programmatic
    handling.
    """

    message: str
    """A human-readable message describing the current status."""

    reason: Literal[
        "unverified", "in_review", "pending", "stuck", "verified", "failed_verification", "disabled", "terminated"
    ]
    """
    A machine-readable identifier for the specific status, useful for programmatic
    handling.
    """

    source: Literal["watchtower"]
    """Identifies the origin of the status change (e.g., `bank_decline`, `watchtower`).

    This helps in tracking the cause of status updates.
    """


class DataBusinessProfileAddress(BaseModel):
    city: Optional[str] = None
    """City, district, suburb, town, or village."""

    country: Optional[str] = None
    """The country of the address, in ISO 3166-1 alpha-2 format."""

    line1: Optional[str] = None
    """Primary address line (e.g., street, PO Box)."""

    line2: Optional[str] = None
    """Secondary address line (e.g., apartment, suite, unit, or building)."""

    postal_code: Optional[str] = None
    """Postal or ZIP code."""

    state: Optional[str] = None
    """Two-letter state code."""


class DataBusinessProfileIndustry(BaseModel):
    category: Optional[str] = None
    """The general category of the industry. Required if not providing MCC."""

    mcc: Optional[str] = None
    """The Merchant Category Code (MCC) that best describes the business. Optional."""

    sector: Optional[str] = None
    """The specific sector within the industry category.

    Required if not providing MCC.
    """


class DataBusinessProfileSupportChannels(BaseModel):
    email: Optional[str] = None
    """The email address for customer support inquiries."""

    phone: Optional[str] = None
    """The phone number for customer support."""

    url: Optional[str] = None
    """The URL of the business's customer support page or contact form."""


class DataBusinessProfile(BaseModel):
    name: str
    """The operating or trade name of the business."""

    website: str
    """URL of the business's primary marketing website."""

    address: Optional[DataBusinessProfileAddress] = None
    """The address object is optional. If provided, it must be a valid address."""

    description: Optional[str] = None
    """A brief description of the business and its products or services."""

    industry: Optional[DataBusinessProfileIndustry] = None

    legal_name: Optional[str] = None
    """The official registered name of the business."""

    phone: Optional[str] = None
    """The primary contact phone number for the business."""

    support_channels: Optional[DataBusinessProfileSupportChannels] = None

    tax_id: Optional[str] = None
    """The business's tax identification number (e.g., EIN in the US)."""

    use_case: Optional[str] = None
    """A description of how the business intends to use Straddle's services."""


class DataCapabilitiesConsentTypesInternet(BaseModel):
    capability_status: Literal["active", "inactive"]


class DataCapabilitiesConsentTypesSignedAgreement(BaseModel):
    capability_status: Literal["active", "inactive"]


class DataCapabilitiesConsentTypes(BaseModel):
    internet: DataCapabilitiesConsentTypesInternet
    """
    Whether the internet payment authorization capability is enabled for the
    account.
    """

    signed_agreement: DataCapabilitiesConsentTypesSignedAgreement
    """
    Whether the signed agreement payment authorization capability is enabled for the
    account.
    """


class DataCapabilitiesCustomerTypesBusinesses(BaseModel):
    capability_status: Literal["active", "inactive"]


class DataCapabilitiesCustomerTypesIndividuals(BaseModel):
    capability_status: Literal["active", "inactive"]


class DataCapabilitiesCustomerTypes(BaseModel):
    businesses: DataCapabilitiesCustomerTypesBusinesses

    individuals: DataCapabilitiesCustomerTypesIndividuals


class DataCapabilitiesPaymentTypesCharges(BaseModel):
    capability_status: Literal["active", "inactive"]


class DataCapabilitiesPaymentTypesPayouts(BaseModel):
    capability_status: Literal["active", "inactive"]


class DataCapabilitiesPaymentTypes(BaseModel):
    charges: DataCapabilitiesPaymentTypesCharges

    payouts: DataCapabilitiesPaymentTypesPayouts


class DataCapabilities(BaseModel):
    consent_types: DataCapabilitiesConsentTypes

    customer_types: DataCapabilitiesCustomerTypes

    payment_types: DataCapabilitiesPaymentTypes


class DataSettingsCharges(BaseModel):
    daily_amount: int
    """The maximum dollar amount of charges in a calendar day."""

    funding_time: Literal["immediate", "next_day", "one_day", "two_day", "three_day"]
    """The amount of time it takes for a charge to be funded.

    This value is defined by Straddle.
    """

    linked_bank_account_id: str
    """The unique identifier of the linked bank account associated with charges.

    This value is defined by Straddle.
    """

    max_amount: int
    """The maximum amount of a single charge."""

    monthly_amount: int
    """The maximum dollar amount of charges in a calendar month."""

    monthly_count: int
    """The maximum number of charges in a calendar month."""


class DataSettingsPayouts(BaseModel):
    daily_amount: int
    """The maximum dollar amount of payouts in a day."""

    funding_time: Literal["immediate", "next_day", "one_day", "two_day", "three_day"]
    """The amount of time it takes for a payout to be funded.

    This value is defined by Straddle.
    """

    linked_bank_account_id: str
    """The unique identifier of the linked bank account to use for payouts."""

    max_amount: int
    """The maximum amount of a single payout."""

    monthly_amount: int
    """The maximum dollar amount of payouts in a month."""

    monthly_count: int
    """The maximum number of payouts in a month."""


class DataSettings(BaseModel):
    charges: DataSettingsCharges

    payouts: DataSettingsPayouts


class DataTermsOfService(BaseModel):
    accepted_date: datetime
    """The datetime of when the terms of service were accepted, in ISO 8601 format."""

    agreement_type: Literal["embedded", "direct"]
    """The type or version of the agreement accepted.

    Use `embedded` unless your platform was specifically enabled for `direct`
    agreements.
    """

    accepted_ip: Optional[str] = None
    """The IP address from which the terms of service were accepted."""

    accepted_user_agent: Optional[str] = None
    """The user agent string of the browser or application used to accept the terms."""

    agreement_url: Optional[str] = None
    """The URL where the full text of the accepted agreement can be found."""


class Data(BaseModel):
    id: str
    """Unique identifier for the account."""

    access_level: Literal["standard", "managed"]
    """The access level granted to the account.

    This is determined by your platform configuration. Use `standard` unless
    instructed otherwise by Straddle.
    """

    organization_id: str
    """The unique identifier of the organization this account belongs to."""

    status: Literal["created", "onboarding", "active", "rejected", "inactive"]
    """The current status of the account (e.g., 'active', 'inactive', 'pending')."""

    status_detail: DataStatusDetail

    type: Literal["business"]
    """The type of account (e.g., 'individual', 'business')."""

    business_profile: Optional[DataBusinessProfile] = None

    capabilities: Optional[DataCapabilities] = None

    created_at: Optional[datetime] = None
    """Timestamp of when the account was created."""

    external_id: Optional[str] = None
    """
    Unique identifier for the account in your database, used for cross-referencing
    between Straddle and your systems.
    """

    metadata: Optional[Dict[str, Optional[str]]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the account in a structured
    format.
    """

    settings: Optional[DataSettings] = None

    terms_of_service: Optional[DataTermsOfService] = None

    updated_at: Optional[datetime] = None
    """Timestamp of the most recent update to the account."""


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


class AccountPaged(BaseModel):
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
