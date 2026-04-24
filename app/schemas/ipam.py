from datetime import date, datetime

from pydantic import BaseModel, Field

from app.core.enums import IPAddressStatus, SourceType
from app.schemas.common import TimestampedSchema


class SiteRead(TimestampedSchema):
    code: str
    name: str
    country: str | None = None
    region: str | None = None


class DeviceModelRead(TimestampedSchema):
    manufacturer: str | None = None
    model_name: str
    model_code: str | None = None
    device_type: str | None = None


class SubnetRead(TimestampedSchema):
    cidr: str
    name: str | None = None
    gateway: str | None = None
    usage_type: str | None = None


class VLANRead(TimestampedSchema):
    vlan_id: int
    name: str | None = None
    purpose: str | None = None


class IPAddressRead(TimestampedSchema):
    address: str
    fqdn: str | None = None
    hostname: str | None = None
    mac_address: str | None = None
    status: IPAddressStatus
    ownership_type: str | None = None
    owner_department: str | None = None
    confidence_score: float | None = None
    source_summary: str | None = None
    trace_reference: str | None = None
    reserved_until: date | None = None
    primary_source_record_id: str | None = None
    subnet: SubnetRead | None = None


class IPAddressCreate(BaseModel):
    address: str
    subnet_id: str | None = None
    hostname: str | None = None
    mac_address: str | None = None
    status: IPAddressStatus = IPAddressStatus.AVAILABLE_CANDIDATE
    owner_department: str | None = None
    ownership_type: str | None = None
    primary_source_record_id: str | None = None
    trace_reference: str | None = None
    source_summary: str | None = None


class SourceRecordRead(TimestampedSchema):
    source_type: SourceType
    source_name: str
    source_reference: str | None = None
    source_system: str | None = None
    confidence_score: float | None = None


class OutletMappingRead(TimestampedSchema):
    code: str
    label: str | None = None
    room_name: str | None = None
    switch_port_name: str | None = None
    switch_device_hostname: str | None = None
    switch_port_status: str | None = None


class ConflictSummary(BaseModel):
    ip_address: str
    hostname: str | None = None
    mac_address: str | None = None
    confidence_score: float | None = None
    last_seen_source: str | None = None


class IPAddressListFilter(BaseModel):
    status: IPAddressStatus | None = None
    subnet_id: str | None = None
    address_contains: str | None = Field(default=None, max_length=64)


class IPAddressLookupResult(BaseModel):
    found: bool
    ip: IPAddressRead | None = None


class SubnetUsageRead(BaseModel):
    subnet_id: str
    cidr: str
    total_ips_known: int
    allocated_confirmed: int
    allocated_unverified: int
    available_candidate: int
    conflict_suspected: int
    reserved: int
    dhcp_pool: int


class IPAddressSourceObservationRead(TimestampedSchema):
    source_record_id: str
    observed_hostname: str | None = None
    observed_fqdn: str | None = None
    observed_mac_address: str | None = None
    observed_status: str | None = None
    observed_owner_department: str | None = None
    confidence_score: float | None = None
    is_primary: bool


class ArpObservationRead(TimestampedSchema):
    mac_address: str
    observed_at: datetime | None = None
    observation_source: str | None = None
    switch_port_hint: str | None = None


class IPAddressDetailRead(IPAddressRead):
    primary_source_record: SourceRecordRead | None = None
    source_observations: list[IPAddressSourceObservationRead] = Field(default_factory=list)
