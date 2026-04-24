from sqlalchemy.orm import Session

from app.schemas.ipam import IPAddressCreate, IPAddressListFilter
from app.services.ipam_commands import IPAMCommandService
from app.services.ipam_queries import IPAMQueryService


class IPAMService:
    def __init__(self, db: Session):
        self.db = db
        self.queries = IPAMQueryService(db)
        self.commands = IPAMCommandService(db)

    def list_ips(self, filters: IPAddressListFilter | None = None):
        return self.queries.list_ips(filters)

    def get_ip(self, ip_id: str):
        return self.queries.get_ip(ip_id)

    def get_by_address(self, address: str):
        return self.queries.get_by_address(address)

    def create_ip(self, payload: IPAddressCreate, actor_user_id: str | None = None):
        return self.commands.create_ip(payload, actor_user_id=actor_user_id)

    def list_conflicts(self):
        return self.queries.list_conflicts()

    def outlet_port_mapping(self):
        return self.queries.outlet_port_mapping()

    def subnet_usage(self, subnet_id: str):
        return self.queries.subnet_usage(subnet_id)
