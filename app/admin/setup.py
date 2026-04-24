from fastapi import FastAPI
from sqladmin import Admin, ModelView

from app.core.config import settings
from app.core.db import engine
from app.core.enums import IPAddressStatus
from app.models.audit import AuditLog
from app.models.auth import Permission, Role, User
from app.models.intake import ApprovalStep, IntakeRequest
from app.models.ipam import (
    AllocationHistory,
    ArpObservation,
    Building,
    DeviceModel,
    DhcpScope,
    DnsRecord,
    Floor,
    IPAddress,
    IPAddressSourceObservation,
    InformationOutlet,
    NetworkDevice,
    Room,
    Site,
    SourceRecord,
    Subnet,
    SwitchPort,
    VLAN,
)
from app.models.jobs import ImportJob


class BaseAdmin(ModelView):
    page_size = 50
    can_export = True
    column_default_sort = ("created_at", True)


class UserAdmin(BaseAdmin, model=User):
    category = "Security"
    column_list = [User.email, User.username, User.full_name, User.department, User.auth_provider]
    column_searchable_list = [User.email, User.username, User.full_name]


class RoleAdmin(BaseAdmin, model=Role):
    category = "Security"
    column_list = [Role.name, Role.description]


class PermissionAdmin(BaseAdmin, model=Permission):
    category = "Security"
    column_list = [Permission.code, Permission.name]


class SiteAdmin(BaseAdmin, model=Site):
    category = "Locations"
    column_list = [Site.code, Site.name, Site.country, Site.region]
    column_searchable_list = [Site.code, Site.name]


class BuildingAdmin(BaseAdmin, model=Building):
    category = "Locations"
    column_list = [Building.code, Building.name, Building.site_id]


class FloorAdmin(BaseAdmin, model=Floor):
    category = "Locations"
    column_list = [Floor.code, Floor.floor_number, Floor.building_id]


class RoomAdmin(BaseAdmin, model=Room):
    category = "Locations"
    column_list = [Room.code, Room.name, Room.floor_id]


class InformationOutletAdmin(BaseAdmin, model=InformationOutlet):
    name = "Information Outlet"
    name_plural = "Information Outlet List"
    category = "Locations"
    column_list = [InformationOutlet.code, InformationOutlet.label, InformationOutlet.room_id, InformationOutlet.status]
    column_searchable_list = [InformationOutlet.code, InformationOutlet.label]


class SwitchPortAdmin(BaseAdmin, model=SwitchPort):
    name = "Switch Port Mapping"
    name_plural = "Switch Port Mapping View"
    category = "Network"
    column_list = [
        SwitchPort.name,
        SwitchPort.network_device_id,
        SwitchPort.information_outlet_id,
        SwitchPort.status,
        SwitchPort.vlan_name,
        SwitchPort.speed,
    ]
    column_searchable_list = [SwitchPort.name, SwitchPort.interface_description]


class DeviceModelAdmin(BaseAdmin, model=DeviceModel):
    category = "Inventory"
    column_list = [DeviceModel.manufacturer, DeviceModel.model_name, DeviceModel.device_type]
    column_searchable_list = [DeviceModel.manufacturer, DeviceModel.model_name, DeviceModel.model_code]


class NetworkDeviceAdmin(BaseAdmin, model=NetworkDevice):
    category = "Inventory"
    column_list = [NetworkDevice.hostname, NetworkDevice.vendor, NetworkDevice.device_role, NetworkDevice.management_ip]
    column_searchable_list = [NetworkDevice.hostname, NetworkDevice.serial_number, NetworkDevice.management_ip]


class VLANAdmin(BaseAdmin, model=VLAN):
    category = "IPAM"
    column_list = [VLAN.vlan_id, VLAN.name, VLAN.purpose]


class SubnetAdmin(BaseAdmin, model=Subnet):
    category = "IPAM"
    column_list = [Subnet.cidr, Subnet.name, Subnet.gateway, Subnet.site_id, Subnet.vlan_id]
    column_searchable_list = [Subnet.cidr, Subnet.name]


class IPAddressAdmin(BaseAdmin, model=IPAddress):
    name = "IP Detail"
    name_plural = "IP List"
    category = "IPAM"
    column_list = [
        IPAddress.address,
        IPAddress.hostname,
        IPAddress.mac_address,
        IPAddress.status,
        IPAddress.owner_department,
        IPAddress.confidence_score,
    ]
    column_searchable_list = [IPAddress.address, IPAddress.hostname, IPAddress.mac_address, IPAddress.fqdn]
    column_details_list = [
        IPAddress.address,
        IPAddress.hostname,
        IPAddress.fqdn,
        IPAddress.mac_address,
        IPAddress.status,
        IPAddress.owner_department,
        IPAddress.ownership_type,
        IPAddress.confidence_score,
        IPAddress.source_summary,
        IPAddress.trace_reference,
        IPAddress.primary_source_record_id,
    ]


class ConflictReviewAdmin(BaseAdmin, model=IPAddress):
    name = "Conflict Review"
    name_plural = "Conflict Review"
    category = "IPAM"
    column_list = [
        IPAddress.address,
        IPAddress.hostname,
        IPAddress.mac_address,
        IPAddress.status,
        IPAddress.confidence_score,
        IPAddress.source_summary,
    ]

    def list_query(self, request):
        return super().list_query(request).filter(
            IPAddress.status == IPAddressStatus.CONFLICT_SUSPECTED
        )


class IntakeRequestAdmin(BaseAdmin, model=IntakeRequest):
    name = "Request Detail"
    name_plural = "Request List"
    category = "Requests"
    column_list = [
        IntakeRequest.request_number,
        IntakeRequest.status,
        IntakeRequest.applicant_name,
        IntakeRequest.department,
        IntakeRequest.information_outlet_code,
        IntakeRequest.hostname,
        IntakeRequest.eligibility_outcome,
        IntakeRequest.recommended_ip_address_id,
    ]
    column_searchable_list = [
        IntakeRequest.request_number,
        IntakeRequest.applicant_name,
        IntakeRequest.applicant_email,
        IntakeRequest.information_outlet_code,
        IntakeRequest.hostname,
    ]
    column_details_list = [
        IntakeRequest.request_number,
        IntakeRequest.status,
        IntakeRequest.applicant_name,
        IntakeRequest.applicant_email,
        IntakeRequest.department,
        IntakeRequest.requested_site_name,
        IntakeRequest.requested_building_name,
        IntakeRequest.requested_floor_name,
        IntakeRequest.requested_room_name,
        IntakeRequest.information_outlet_code,
        IntakeRequest.vlan_or_subnet,
        IntakeRequest.hostname,
        IntakeRequest.mac_address,
        IntakeRequest.device_model_name,
        IntakeRequest.source_type,
        IntakeRequest.source_channel,
        IntakeRequest.external_request_reference,
        IntakeRequest.eligibility_outcome,
        IntakeRequest.eligibility_summary,
        IntakeRequest.recommended_ip_address_id,
        IntakeRequest.assigned_ip_address_id,
    ]


class ApprovalStepAdmin(BaseAdmin, model=ApprovalStep):
    category = "Requests"
    column_list = [ApprovalStep.intake_request_id, ApprovalStep.step_order, ApprovalStep.name, ApprovalStep.status]


class ImportJobAdmin(BaseAdmin, model=ImportJob):
    name_plural = "Import Jobs"
    category = "Operations"
    column_list = [
        ImportJob.job_name,
        ImportJob.importer_name,
        ImportJob.source_type,
        ImportJob.status,
        ImportJob.source_reference,
        ImportJob.processed_count,
        ImportJob.created_count,
        ImportJob.updated_count,
        ImportJob.failed_count,
    ]


class AuditLogAdmin(BaseAdmin, model=AuditLog):
    name_plural = "Audit Logs"
    category = "Operations"
    column_list = [
        AuditLog.action,
        AuditLog.entity_type,
        AuditLog.entity_id,
        AuditLog.correlation_id,
        AuditLog.source_type,
        AuditLog.created_at,
    ]


class SourceRecordAdmin(BaseAdmin, model=SourceRecord):
    category = "Operations"
    column_list = [
        SourceRecord.source_type,
        SourceRecord.source_name,
        SourceRecord.source_reference,
        SourceRecord.source_system,
        SourceRecord.confidence_score,
        SourceRecord.import_job_id,
    ]
    column_searchable_list = [SourceRecord.source_name, SourceRecord.source_reference, SourceRecord.row_identifier]


class IPAddressSourceObservationAdmin(BaseAdmin, model=IPAddressSourceObservation):
    name = "IP Source Observation"
    name_plural = "IP Source Observations"
    category = "Operations"
    column_list = [
        IPAddressSourceObservation.ip_address_id,
        IPAddressSourceObservation.source_record_id,
        IPAddressSourceObservation.observed_hostname,
        IPAddressSourceObservation.observed_mac_address,
        IPAddressSourceObservation.confidence_score,
        IPAddressSourceObservation.is_primary,
    ]


class AllocationHistoryAdmin(BaseAdmin, model=AllocationHistory):
    category = "Operations"
    column_list = [
        AllocationHistory.ip_address_id,
        AllocationHistory.intake_request_id,
        AllocationHistory.action,
        AllocationHistory.previous_status,
        AllocationHistory.new_status,
        AllocationHistory.source_type,
    ]


class DnsRecordAdmin(BaseAdmin, model=DnsRecord):
    category = "Operations"
    column_list = [DnsRecord.hostname, DnsRecord.record_type, DnsRecord.zone_name, DnsRecord.ip_address_id]


class DhcpScopeAdmin(BaseAdmin, model=DhcpScope):
    category = "Operations"
    column_list = [DhcpScope.name, DhcpScope.server_name, DhcpScope.start_ip, DhcpScope.end_ip]


class ArpObservationAdmin(BaseAdmin, model=ArpObservation):
    category = "Operations"
    column_list = [
        ArpObservation.ip_address_id,
        ArpObservation.mac_address,
        ArpObservation.observed_at,
        ArpObservation.switch_port_hint,
    ]


def setup_admin(app: FastAPI) -> None:
    admin = Admin(app, engine, title=settings.admin_title, templates_dir="templates")
    for view in [
        UserAdmin,
        RoleAdmin,
        PermissionAdmin,
        SiteAdmin,
        BuildingAdmin,
        FloorAdmin,
        RoomAdmin,
        InformationOutletAdmin,
        SwitchPortAdmin,
        DeviceModelAdmin,
        NetworkDeviceAdmin,
        VLANAdmin,
        SubnetAdmin,
        IPAddressAdmin,
        ConflictReviewAdmin,
        IntakeRequestAdmin,
        ApprovalStepAdmin,
        ImportJobAdmin,
        AuditLogAdmin,
        SourceRecordAdmin,
        IPAddressSourceObservationAdmin,
        AllocationHistoryAdmin,
        DnsRecordAdmin,
        DhcpScopeAdmin,
        ArpObservationAdmin,
    ]:
        admin.add_view(view)
