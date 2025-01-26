from enum import StrEnum

from pydantic import BaseModel


class WorkTypes(StrEnum):
    NS = "NS"  # No Supply


class ChildWorkTypes(StrEnum):
    NSA = "NSA"  # No Supply (Area)
    NSIP = "NSIP"  # No Supply (only your property)
    NSLS = "NSLS"  # Supply not back after load shedding
    NSTL = "NSTL"  # No Power to Traffic Light


class CustomLookupCodes(StrEnum):
    DOMESTIC = "Domestic"
    LARGE_POWER_USER = "Large Power User"
    PREPAID = "Prepaid"


class Address(BaseModel):
    address3: str = ""  # Building
    address4: str = ""  # Street Number
    address5: str = ""  # Street Name
    address6: str  # Suburb
    address7: str = ""  # City
    address8: str = ""  # Postal Code
    latitude: float = 0.0
    longitude: float = 0.0


class FaultData(BaseModel):
    workType: WorkTypes
    childWorkType: ChildWorkTypes
    customLookupCode2: CustomLookupCodes
    description: str
    custom2: str = ""  # Meter Number
    custom4: str = ""  # Account Number
    address: Address | None = None
    contactNumber: str
    contactName: str
