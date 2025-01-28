# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import date, datetime
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "CustomerReview",
    "Data",
    "DataCustomerDetails",
    "DataCustomerDetailsAddress",
    "DataCustomerDetailsComplianceProfile",
    "DataCustomerDetailsComplianceProfileIndividualComplianceProfile",
    "DataCustomerDetailsComplianceProfileBusinessComplianceProfile",
    "DataCustomerDetailsDevice",
    "DataIdentityDetails",
    "DataIdentityDetailsBreakdown",
    "DataIdentityDetailsBreakdownAddress",
    "DataIdentityDetailsBreakdownEmail",
    "DataIdentityDetailsBreakdownFraud",
    "DataIdentityDetailsBreakdownPhone",
    "DataIdentityDetailsBreakdownSynthetic",
    "DataIdentityDetailsKYC",
    "DataIdentityDetailsKYCValidations",
    "DataIdentityDetailsNetworkAlerts",
    "DataIdentityDetailsWatchList",
    "Meta",
]


class DataCustomerDetailsAddress(BaseModel):
    address1: str
    """Primary address line (e.g., street, PO Box)."""

    city: str
    """City, district, suburb, town, or village."""

    state: str
    """Two-letter state code."""

    zip: str
    """Zip or postal code."""

    address2: Optional[str] = None
    """Secondary address line (e.g., apartment, suite, unit, or building)."""


class DataCustomerDetailsComplianceProfileIndividualComplianceProfile(BaseModel):
    dob: date
    """Date of birth in YYYY-MM-DD format."""

    ssn: str
    """Social Security Number in the format XXX-XX-XXXX."""


class DataCustomerDetailsComplianceProfileBusinessComplianceProfile(BaseModel):
    ein: str
    """Employer Identification Number in the format XX-XXXXXXX."""

    legal_business_name: str
    """The official registered name of the business.

    This name should be correlated with the `ein` value.
    """

    website: Optional[str] = None
    """Business website URL."""


DataCustomerDetailsComplianceProfile: TypeAlias = Union[
    DataCustomerDetailsComplianceProfileIndividualComplianceProfile,
    DataCustomerDetailsComplianceProfileBusinessComplianceProfile,
]


class DataCustomerDetailsDevice(BaseModel):
    ip_address: str
    """The customer's IP address at the time of profile creation.

    Use `0.0.0.0` to represent an offline customer registration.
    """


class DataCustomerDetails(BaseModel):
    id: str
    """Unique identifier for the customer."""

    created_at: datetime
    """Timestamp of when the customer record was created."""

    email: str
    """The customer's email address."""

    name: str
    """Full name of the individual or business name."""

    phone: str
    """The customer's phone number in E.164 format."""

    status: Literal["pending", "review", "verified", "inactive", "rejected"]

    type: Literal["individual", "business"]

    updated_at: datetime
    """Timestamp of the most recent update to the customer record."""

    address: Optional[DataCustomerDetailsAddress] = None

    compliance_profile: Optional[DataCustomerDetailsComplianceProfile] = None
    """Compliance profile for individual customers"""

    device: Optional[DataCustomerDetailsDevice] = None

    external_id: Optional[str] = None
    """
    Unique identifier for the customer in your database, used for cross-referencing
    between Straddle and your systems.
    """

    metadata: Optional[Dict[str, str]] = None
    """Up to 20 additional user-defined key-value pairs.

    Useful for storing additional information about the customer in a structured
    format.
    """


class DataIdentityDetailsBreakdownAddress(BaseModel):
    codes: Optional[List[str]] = None
    """List of specific result codes from the fraud and risk screening."""

    correlation_score: Optional[float] = None
    """
    Represents the strength of the correlation between provided and known
    information. A higher score indicates a stronger correlation.
    """

    decision: Optional[Literal["accept", "reject", "review"]] = None

    risk_score: Optional[float] = None
    """Predicts the inherent risk associated with the customer for a given module.

    A higher score indicates a greater likelihood of fraud.
    """


class DataIdentityDetailsBreakdownEmail(BaseModel):
    codes: Optional[List[str]] = None
    """List of specific result codes from the fraud and risk screening."""

    correlation_score: Optional[float] = None
    """
    Represents the strength of the correlation between provided and known
    information. A higher score indicates a stronger correlation.
    """

    decision: Optional[Literal["accept", "reject", "review"]] = None

    risk_score: Optional[float] = None
    """Predicts the inherent risk associated with the customer for a given module.

    A higher score indicates a greater likelihood of fraud.
    """


class DataIdentityDetailsBreakdownFraud(BaseModel):
    codes: Optional[List[str]] = None
    """List of specific result codes from the fraud and risk screening."""

    correlation_score: Optional[float] = None
    """
    Represents the strength of the correlation between provided and known
    information. A higher score indicates a stronger correlation.
    """

    decision: Optional[Literal["accept", "reject", "review"]] = None

    risk_score: Optional[float] = None
    """Predicts the inherent risk associated with the customer for a given module.

    A higher score indicates a greater likelihood of fraud.
    """


class DataIdentityDetailsBreakdownPhone(BaseModel):
    codes: Optional[List[str]] = None
    """List of specific result codes from the fraud and risk screening."""

    correlation_score: Optional[float] = None
    """
    Represents the strength of the correlation between provided and known
    information. A higher score indicates a stronger correlation.
    """

    decision: Optional[Literal["accept", "reject", "review"]] = None

    risk_score: Optional[float] = None
    """Predicts the inherent risk associated with the customer for a given module.

    A higher score indicates a greater likelihood of fraud.
    """


class DataIdentityDetailsBreakdownSynthetic(BaseModel):
    codes: Optional[List[str]] = None
    """List of specific result codes from the fraud and risk screening."""

    correlation_score: Optional[float] = None
    """
    Represents the strength of the correlation between provided and known
    information. A higher score indicates a stronger correlation.
    """

    decision: Optional[Literal["accept", "reject", "review"]] = None

    risk_score: Optional[float] = None
    """Predicts the inherent risk associated with the customer for a given module.

    A higher score indicates a greater likelihood of fraud.
    """


class DataIdentityDetailsBreakdown(BaseModel):
    address: Optional[DataIdentityDetailsBreakdownAddress] = None

    email: Optional[DataIdentityDetailsBreakdownEmail] = None

    fraud: Optional[DataIdentityDetailsBreakdownFraud] = None

    phone: Optional[DataIdentityDetailsBreakdownPhone] = None

    synthetic: Optional[DataIdentityDetailsBreakdownSynthetic] = None


class DataIdentityDetailsKYCValidations(BaseModel):
    address: Optional[bool] = None

    city: Optional[bool] = None

    dob: Optional[bool] = None

    email: Optional[bool] = None

    first_name: Optional[bool] = None

    last_name: Optional[bool] = None

    phone: Optional[bool] = None

    ssn: Optional[bool] = None

    state: Optional[bool] = None

    zip: Optional[bool] = None


class DataIdentityDetailsKYC(BaseModel):
    validations: DataIdentityDetailsKYCValidations
    """Boolean values indicating the result of each validation in the KYC process."""

    codes: Optional[List[str]] = None
    """List of specific result codes from the KYC screening process."""

    decision: Optional[Literal["accept", "reject", "review"]] = None


class DataIdentityDetailsNetworkAlerts(BaseModel):
    alerts: Optional[List[str]] = None
    """Any alerts or flags raised during the consortium alert screening."""

    codes: Optional[List[str]] = None
    """List of specific result codes from the consortium alert screening."""

    decision: Optional[Literal["accept", "reject", "review"]] = None


class DataIdentityDetailsWatchList(BaseModel):
    codes: Optional[List[str]] = None
    """Specific codes related to the Straddle watchlist screening results."""

    decision: Optional[Literal["accept", "reject", "review"]] = None

    matched: Optional[List[str]] = None
    """Information about any matches found during screening."""


class DataIdentityDetails(BaseModel):
    breakdown: DataIdentityDetailsBreakdown
    """
    Detailed breakdown of the customer verification results, including decisions,
    risk scores, correlation score, and more.
    """

    created_at: datetime
    """Timestamp of when the review was initiated."""

    decision: Literal["accept", "reject", "review"]

    review_id: str
    """Unique identifier for the review."""

    updated_at: datetime
    """Timestamp of the most recent update to the review."""

    kyc: Optional[DataIdentityDetailsKYC] = None

    messages: Optional[Dict[str, str]] = None
    """Dictionary of all messages from the customer verification process."""

    network_alerts: Optional[DataIdentityDetailsNetworkAlerts] = None

    watch_list: Optional[DataIdentityDetailsWatchList] = None


class Data(BaseModel):
    customer_details: DataCustomerDetails

    identity_details: Optional[DataIdentityDetails] = None


class Meta(BaseModel):
    api_request_id: str
    """Unique identifier for this API request, useful for troubleshooting."""

    api_request_timestamp: datetime
    """Timestamp for this API request, useful for troubleshooting."""


class CustomerReview(BaseModel):
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
