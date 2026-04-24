from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.enums import ApprovalStatus, RequestStatus, SourceType
from app.models.base import TimestampMixin


class IntakeRequest(TimestampMixin, Base):
    __tablename__ = "intake_requests"

    request_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[RequestStatus] = mapped_column(Enum(RequestStatus), default=RequestStatus.DRAFT)
    applicant_name: Mapped[str] = mapped_column(String(255))
    applicant_email: Mapped[str] = mapped_column(String(255), index=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_site_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_building_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_floor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_room_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"), nullable=True)
    building_id: Mapped[str | None] = mapped_column(ForeignKey("buildings.id"), nullable=True)
    floor_id: Mapped[str | None] = mapped_column(ForeignKey("floors.id"), nullable=True)
    room_id: Mapped[str | None] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    information_outlet_id: Mapped[str | None] = mapped_column(
        ForeignKey("information_outlets.id"), nullable=True
    )
    information_outlet_code: Mapped[str | None] = mapped_column(String(150), nullable=True)
    vlan_id: Mapped[str | None] = mapped_column(ForeignKey("vlans.id"), nullable=True)
    subnet_id: Mapped[str | None] = mapped_column(ForeignKey("subnets.id"), nullable=True)
    vlan_or_subnet: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    device_model_id: Mapped[str | None] = mapped_column(ForeignKey("device_models.id"), nullable=True)
    device_model_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_by_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fixed_ip_required: Mapped[bool] = mapped_column(Boolean, default=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), default=SourceType.API)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_channel: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_request_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_approval_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    assigned_ip_address_id: Mapped[str | None] = mapped_column(ForeignKey("ip_addresses.id"), nullable=True)
    recommended_ip_address_id: Mapped[str | None] = mapped_column(
        ForeignKey("ip_addresses.id"), nullable=True
    )
    eligibility_outcome: Mapped[str | None] = mapped_column(String(50), nullable=True)
    eligibility_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    site: Mapped["Site"] = relationship("Site", back_populates="requests")
    building: Mapped["Building"] = relationship("Building", back_populates="requests")
    floor: Mapped["Floor"] = relationship("Floor", back_populates="requests")
    room: Mapped["Room"] = relationship("Room", back_populates="requests")
    information_outlet: Mapped["InformationOutlet"] = relationship(
        "InformationOutlet", back_populates="requests"
    )
    vlan: Mapped["VLAN"] = relationship("VLAN", back_populates="requests")
    subnet: Mapped["Subnet"] = relationship("Subnet", back_populates="requests")
    device_model: Mapped["DeviceModel"] = relationship(
        "DeviceModel", back_populates="requests"
    )
    approval_steps: Mapped[list["ApprovalStep"]] = relationship(
        "ApprovalStep", back_populates="intake_request", order_by="ApprovalStep.step_order"
    )
    assigned_ip_address: Mapped["IPAddress"] = relationship(
        "IPAddress", foreign_keys=[assigned_ip_address_id]
    )
    recommended_ip_address: Mapped["IPAddress"] = relationship(
        "IPAddress", foreign_keys=[recommended_ip_address_id]
    )


class ApprovalStep(TimestampMixin, Base):
    __tablename__ = "approval_steps"

    intake_request_id: Mapped[str] = mapped_column(ForeignKey("intake_requests.id"))
    step_order: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    approver_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approver_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    external_step_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    intake_request: Mapped[IntakeRequest] = relationship("IntakeRequest", back_populates="approval_steps")
