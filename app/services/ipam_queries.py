from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.enums import IPAddressStatus
from app.models.ipam import IPAddress, InformationOutlet, Subnet, SwitchPort
from app.schemas.ipam import ConflictSummary, IPAddressListFilter, SubnetUsageRead


class IPAMQueryService:
    def __init__(self, db: Session):
        self.db = db

    def list_ips(self, filters: IPAddressListFilter | None = None) -> list[IPAddress]:
        query = self.db.query(IPAddress).options(
            joinedload(IPAddress.subnet),
            joinedload(IPAddress.primary_source_record),
            joinedload(IPAddress.source_observations),
        )
        if filters:
            if filters.status:
                query = query.filter(IPAddress.status == filters.status)
            if filters.subnet_id:
                query = query.filter(IPAddress.subnet_id == filters.subnet_id)
            if filters.address_contains:
                query = query.filter(IPAddress.address.contains(filters.address_contains))
        return query.order_by(IPAddress.address).all()

    def get_ip(self, ip_id: str) -> IPAddress | None:
        return (
            self.db.query(IPAddress)
            .options(
                joinedload(IPAddress.subnet),
                joinedload(IPAddress.primary_source_record),
                joinedload(IPAddress.source_observations),
            )
            .filter(IPAddress.id == ip_id)
            .first()
        )

    def get_by_address(self, address: str) -> IPAddress | None:
        return self.db.query(IPAddress).filter(IPAddress.address == address).first()

    def list_conflicts(self) -> list[ConflictSummary]:
        conflicts = self.db.query(IPAddress).filter(IPAddress.status == IPAddressStatus.CONFLICT_SUSPECTED).all()
        return [
            ConflictSummary(
                ip_address=item.address,
                hostname=item.hostname,
                mac_address=item.mac_address,
                confidence_score=item.confidence_score,
                last_seen_source=item.source_summary,
            )
            for item in conflicts
        ]

    def outlet_port_mapping(self) -> list[dict]:
        rows = (
            self.db.query(InformationOutlet, SwitchPort)
            .outerjoin(SwitchPort, SwitchPort.information_outlet_id == InformationOutlet.id)
            .all()
        )
        return [
            {
                "id": outlet.id,
                "code": outlet.code,
                "label": outlet.label,
                "room_name": outlet.room.name if outlet.room else None,
                "switch_port_name": port.name if port else None,
                "switch_device_hostname": (
                    port.network_device.hostname if port and port.network_device else None
                ),
                "switch_port_status": port.status if port else None,
            }
            for outlet, port in rows
        ]

    def subnet_usage(self, subnet_id: str) -> SubnetUsageRead | None:
        subnet = self.db.query(Subnet).filter(Subnet.id == subnet_id).first()
        if not subnet:
            return None

        counts = dict(
            self.db.query(IPAddress.status, func.count(IPAddress.id))
            .filter(IPAddress.subnet_id == subnet_id)
            .group_by(IPAddress.status)
            .all()
        )
        return SubnetUsageRead(
            subnet_id=subnet.id,
            cidr=subnet.cidr,
            total_ips_known=sum(counts.values()),
            allocated_confirmed=counts.get(IPAddressStatus.ALLOCATED_CONFIRMED, 0),
            allocated_unverified=counts.get(IPAddressStatus.ALLOCATED_UNVERIFIED, 0),
            available_candidate=counts.get(IPAddressStatus.AVAILABLE_CANDIDATE, 0),
            conflict_suspected=counts.get(IPAddressStatus.CONFLICT_SUSPECTED, 0),
            reserved=counts.get(IPAddressStatus.RESERVED, 0),
            dhcp_pool=counts.get(IPAddressStatus.DHCP_POOL, 0),
        )

