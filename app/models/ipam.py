from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.enums import IPAddressStatus, SourceType
from app.models.base import TimestampMixin


class Site(TimestampMixin, Base):
    __tablename__ = "sites"

    code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    buildings: Mapped[list["Building"]] = relationship("Building", back_populates="site")
    subnets: Mapped[list["Subnet"]] = relationship("Subnet", back_populates="site")
    requests: Mapped[list["IntakeRequest"]] = relationship("IntakeRequest", back_populates="site")


class Building(TimestampMixin, Base):
    __tablename__ = "buildings"

    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"))
    code: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255))
    site: Mapped[Site] = relationship("Site", back_populates="buildings")
    floors: Mapped[list["Floor"]] = relationship("Floor", back_populates="building")
    requests: Mapped[list["IntakeRequest"]] = relationship("IntakeRequest", back_populates="building")


class Floor(TimestampMixin, Base):
    __tablename__ = "floors"

    building_id: Mapped[str] = mapped_column(ForeignKey("buildings.id"))
    code: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    floor_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    building: Mapped[Building] = relationship("Building", back_populates="floors")
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="floor")
    requests: Mapped[list["IntakeRequest"]] = relationship("IntakeRequest", back_populates="floor")


class Room(TimestampMixin, Base):
    __tablename__ = "rooms"

    floor_id: Mapped[str] = mapped_column(ForeignKey("floors.id"))
    code: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    usage_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    floor: Mapped[Floor] = relationship("Floor", back_populates="rooms")
    information_outlets: Mapped[list["InformationOutlet"]] = relationship(
        "InformationOutlet", back_populates="room"
    )
    requests: Mapped[list["IntakeRequest"]] = relationship("IntakeRequest", back_populates="room")


class DeviceModel(TimestampMixin, Base):
    __tablename__ = "device_models"

    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_name: Mapped[str] = mapped_column(String(255), index=True)
    model_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lifecycle_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    devices: Mapped[list["NetworkDevice"]] = relationship("NetworkDevice", back_populates="device_model")
    requests: Mapped[list["IntakeRequest"]] = relationship(
        "IntakeRequest", back_populates="device_model"
    )


class NetworkDevice(TimestampMixin, Base):
    __tablename__ = "network_devices"

    hostname: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    management_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    building_id: Mapped[str | None] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    room_id: Mapped[str | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    device_model_id: Mapped[str | None] = mapped_column(ForeignKey("device_models.id"), nullable=True)
    device_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vendor: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    device_model: Mapped[DeviceModel | None] = relationship("DeviceModel", back_populates="devices")
    switch_ports: Mapped[list["SwitchPort"]] = relationship("SwitchPort", back_populates="network_device")


class InformationOutlet(TimestampMixin, Base):
    __tablename__ = "information_outlets"

    room_id: Mapped[str | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    code: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wall_faceplate: Mapped[str | None] = mapped_column(String(100), nullable=True)
    jack_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    room: Mapped[Room | None] = relationship("Room", back_populates="information_outlets")
    switch_ports: Mapped[list["SwitchPort"]] = relationship(
        "SwitchPort", back_populates="information_outlet"
    )
    requests: Mapped[list["IntakeRequest"]] = relationship(
        "IntakeRequest", back_populates="information_outlet"
    )


class SwitchPort(TimestampMixin, Base):
    __tablename__ = "switch_ports"
    __table_args__ = (UniqueConstraint("network_device_id", "name", name="uq_switch_port_device_name"),)

    network_device_id: Mapped[str | None] = mapped_column(ForeignKey("network_devices.id"), nullable=True)
    information_outlet_id: Mapped[str | None] = mapped_column(
        ForeignKey("information_outlets.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    interface_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vlan_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vlan_id_text: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duplex: Mapped[str | None] = mapped_column(String(50), nullable=True)
    speed: Mapped[str | None] = mapped_column(String(50), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_trunk: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    network_device: Mapped[NetworkDevice | None] = relationship(
        "NetworkDevice", back_populates="switch_ports"
    )
    information_outlet: Mapped[InformationOutlet | None] = relationship(
        "InformationOutlet", back_populates="switch_ports"
    )


class VLAN(TimestampMixin, Base):
    __tablename__ = "vlans"
    __table_args__ = (UniqueConstraint("site_id", "vlan_id", name="uq_vlan_site_vlan_id"),)

    vlan_id: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    subnets: Mapped[list["Subnet"]] = relationship("Subnet", back_populates="vlan")
    requests: Mapped[list["IntakeRequest"]] = relationship("IntakeRequest", back_populates="vlan")


class Subnet(TimestampMixin, Base):
    __tablename__ = "subnets"

    cidr: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gateway: Mapped[str | None] = mapped_column(String(64), nullable=True)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    vlan_id: Mapped[str | None] = mapped_column(ForeignKey("vlans.id"), nullable=True)
    usage_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    owner_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    site: Mapped[Site | None] = relationship("Site", back_populates="subnets")
    vlan: Mapped[VLAN | None] = relationship("VLAN", back_populates="subnets")
    ip_addresses: Mapped[list["IPAddress"]] = relationship("IPAddress", back_populates="subnet")
    dhcp_scopes: Mapped[list["DhcpScope"]] = relationship("DhcpScope", back_populates="subnet")
    reservation_policies: Mapped[list["ReservationPolicy"]] = relationship(
        "ReservationPolicy", back_populates="subnet"
    )
    requests: Mapped[list["IntakeRequest"]] = relationship("IntakeRequest", back_populates="subnet")


class SourceRecord(TimestampMixin, Base):
    __tablename__ = "source_records"

    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType))
    source_name: Mapped[str] = mapped_column(String(255))
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    import_job_id: Mapped[str | None] = mapped_column(ForeignKey("import_jobs.id"), nullable=True)
    row_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_system: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    import_job: Mapped["ImportJob"] = relationship("ImportJob", back_populates="source_records")
    ip_addresses: Mapped[list["IPAddress"]] = relationship("IPAddress", back_populates="primary_source_record")
    ip_observations: Mapped[list["IPAddressSourceObservation"]] = relationship(
        "IPAddressSourceObservation", back_populates="source_record"
    )
    dns_records: Mapped[list["DnsRecord"]] = relationship("DnsRecord", back_populates="source_record")
    dhcp_scopes: Mapped[list["DhcpScope"]] = relationship("DhcpScope", back_populates="source_record")
    arp_observations: Mapped[list["ArpObservation"]] = relationship(
        "ArpObservation", back_populates="source_record"
    )


class IPAddress(TimestampMixin, Base):
    __tablename__ = "ip_addresses"

    address: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    subnet_id: Mapped[str | None] = mapped_column(ForeignKey("subnets.id"), nullable=True)
    primary_source_record_id: Mapped[str | None] = mapped_column(
        ForeignKey("source_records.id"), nullable=True
    )
    assigned_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    fqdn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[IPAddressStatus] = mapped_column(
        Enum(IPAddressStatus), default=IPAddressStatus.AVAILABLE_CANDIDATE
    )
    ownership_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    owner_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reserved_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    subnet: Mapped[Subnet | None] = relationship("Subnet", back_populates="ip_addresses")
    primary_source_record: Mapped[SourceRecord | None] = relationship(
        "SourceRecord", back_populates="ip_addresses"
    )
    allocation_history: Mapped[list["AllocationHistory"]] = relationship(
        "AllocationHistory", back_populates="ip_address"
    )
    dns_records: Mapped[list["DnsRecord"]] = relationship("DnsRecord", back_populates="ip_address")
    arp_observations: Mapped[list["ArpObservation"]] = relationship(
        "ArpObservation", back_populates="ip_address"
    )
    source_observations: Mapped[list["IPAddressSourceObservation"]] = relationship(
        "IPAddressSourceObservation", back_populates="ip_address"
    )


class IPAddressSourceObservation(TimestampMixin, Base):
    __tablename__ = "ip_address_source_observations"
    __table_args__ = (
        UniqueConstraint("ip_address_id", "source_record_id", name="uq_ip_source_observation"),
    )

    ip_address_id: Mapped[str] = mapped_column(ForeignKey("ip_addresses.id"))
    source_record_id: Mapped[str] = mapped_column(ForeignKey("source_records.id"))
    observed_hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observed_fqdn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observed_mac_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    observed_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    observed_owner_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    ip_address: Mapped[IPAddress] = relationship("IPAddress", back_populates="source_observations")
    source_record: Mapped[SourceRecord] = relationship("SourceRecord", back_populates="ip_observations")


class DnsRecord(TimestampMixin, Base):
    __tablename__ = "dns_records"

    ip_address_id: Mapped[str | None] = mapped_column(ForeignKey("ip_addresses.id"), nullable=True)
    record_type: Mapped[str] = mapped_column(String(20), default="A")
    hostname: Mapped[str] = mapped_column(String(255), index=True)
    zone_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ttl: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"), nullable=True)
    ip_address: Mapped[IPAddress | None] = relationship("IPAddress", back_populates="dns_records")
    source_record: Mapped[SourceRecord | None] = relationship("SourceRecord", back_populates="dns_records")


class DhcpScope(TimestampMixin, Base):
    __tablename__ = "dhcp_scopes"

    subnet_id: Mapped[str | None] = mapped_column(ForeignKey("subnets.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    start_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    end_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    server_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"), nullable=True)
    lease_duration_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_authoritative: Mapped[bool] = mapped_column(Boolean, default=False)
    subnet: Mapped[Subnet | None] = relationship("Subnet", back_populates="dhcp_scopes")
    source_record: Mapped[SourceRecord | None] = relationship("SourceRecord", back_populates="dhcp_scopes")


class ArpObservation(TimestampMixin, Base):
    __tablename__ = "arp_observations"

    ip_address_id: Mapped[str | None] = mapped_column(ForeignKey("ip_addresses.id"), nullable=True)
    mac_address: Mapped[str] = mapped_column(String(50), index=True)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observation_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_record_id: Mapped[str | None] = mapped_column(ForeignKey("source_records.id"), nullable=True)
    switch_port_hint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[IPAddress | None] = relationship("IPAddress", back_populates="arp_observations")
    source_record: Mapped[SourceRecord | None] = relationship("SourceRecord", back_populates="arp_observations")


class ReservationPolicy(TimestampMixin, Base):
    __tablename__ = "reservation_policies"

    subnet_id: Mapped[str | None] = mapped_column(ForeignKey("subnets.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    match_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fixed_ip_required_only: Mapped[bool] = mapped_column(Boolean, default=False)
    subnet: Mapped[Subnet | None] = relationship("Subnet", back_populates="reservation_policies")


class AllocationHistory(TimestampMixin, Base):
    __tablename__ = "allocation_history"

    ip_address_id: Mapped[str] = mapped_column(ForeignKey("ip_addresses.id"))
    intake_request_id: Mapped[str | None] = mapped_column(ForeignKey("intake_requests.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    source_type: Mapped[SourceType | None] = mapped_column(Enum(SourceType), nullable=True)
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    previous_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    previous_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    new_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[IPAddress] = relationship("IPAddress", back_populates="allocation_history")
