from sqlalchemy.orm import Session, joinedload

from app.models.ipam import (
    Building,
    Floor,
    IPAddress,
    InformationOutlet,
    NetworkDevice,
    Room,
    Site,
    Subnet,
    SwitchPort,
    VLAN,
)
from app.schemas.topology import TopologyEdge, TopologyGraphResponse, TopologyNode


class TopologyService:
    """Read-only topology graph builder.

    Extension points for future LLDP/CDP/MAC discovery should enrich the
    same node/edge shape rather than changing the API contract.
    """

    def __init__(self, db: Session):
        self.db = db

    def build_graph(
        self,
        *,
        site_id: str | None = None,
        floor_id: str | None = None,
        include_ip_overlay: bool = False,
    ) -> TopologyGraphResponse:
        nodes: list[TopologyNode] = []
        edges: list[TopologyEdge] = []

        sites = self._load_sites(site_id=site_id, floor_id=floor_id)
        floor_filter = floor_id

        included_floor_ids: set[str] = set()
        included_room_ids: set[str] = set()
        included_outlet_ids: set[str] = set()

        for site in sites:
            nodes.append(
                TopologyNode(
                    id=f"site:{site.id}",
                    label=site.code,
                    kind="site",
                    group="location",
                    title=site.name,
                    metadata={"name": site.name, "region": site.region, "country": site.country},
                )
            )
            for building in site.buildings:
                building_has_matching_floor = False
                building_node_added = False
                for floor in building.floors:
                    if floor_filter and floor.id != floor_filter:
                        continue
                    building_has_matching_floor = True
                    if not building_node_added:
                        nodes.append(
                            TopologyNode(
                                id=f"building:{building.id}",
                                label=building.code,
                                kind="building",
                                group="location",
                                title=building.name,
                                metadata={"site": site.name},
                            )
                        )
                        edges.append(
                            TopologyEdge(
                                id=f"edge:site-building:{site.id}:{building.id}",
                                source=f"site:{site.id}",
                                target=f"building:{building.id}",
                                label="building",
                                kind="contains",
                            )
                        )
                        building_node_added = True
                    included_floor_ids.add(floor.id)
                    nodes.append(
                        TopologyNode(
                            id=f"floor:{floor.id}",
                            label=floor.code,
                            kind="floor",
                            group="location",
                            title=floor.name or floor.code,
                            metadata={
                                "building": building.name,
                                "floor_number": floor.floor_number,
                            },
                        )
                    )
                    edges.append(
                        TopologyEdge(
                            id=f"edge:building-floor:{building.id}:{floor.id}",
                            source=f"building:{building.id}",
                            target=f"floor:{floor.id}",
                            label="floor",
                            kind="contains",
                        )
                    )
                    for room in floor.rooms:
                        included_room_ids.add(room.id)
                        nodes.append(
                            TopologyNode(
                                id=f"room:{room.id}",
                                label=room.code,
                                kind="room",
                                group="location",
                                title=room.name or room.code,
                                metadata={"usage_type": room.usage_type},
                            )
                        )
                        edges.append(
                            TopologyEdge(
                                id=f"edge:floor-room:{floor.id}:{room.id}",
                                source=f"floor:{floor.id}",
                                target=f"room:{room.id}",
                                label="room",
                                kind="contains",
                            )
                        )
                        for outlet in room.information_outlets:
                            included_outlet_ids.add(outlet.id)
                            nodes.append(
                                TopologyNode(
                                    id=f"outlet:{outlet.id}",
                                    label=outlet.code,
                                    kind="information_outlet",
                                    group="endpoint",
                                    title=outlet.label or outlet.code,
                                    metadata={
                                        "status": outlet.status,
                                        "wall_faceplate": outlet.wall_faceplate,
                                        "jack_number": outlet.jack_number,
                                    },
                                )
                            )
                            edges.append(
                                TopologyEdge(
                                    id=f"edge:room-outlet:{room.id}:{outlet.id}",
                                    source=f"room:{room.id}",
                                    target=f"outlet:{outlet.id}",
                                    label="outlet",
                                    kind="contains",
                                )
                            )

                if building_has_matching_floor and not building_node_added:
                    nodes.append(
                        TopologyNode(
                            id=f"building:{building.id}",
                            label=building.code,
                            kind="building",
                            group="location",
                            title=building.name,
                            metadata={"site": site.name},
                        )
                    )
                    edges.append(
                        TopologyEdge(
                            id=f"edge:site-building:{site.id}:{building.id}",
                            source=f"site:{site.id}",
                            target=f"building:{building.id}",
                            label="building",
                            kind="contains",
                        )
                    )

        device_query = self.db.query(NetworkDevice).options(
            joinedload(NetworkDevice.switch_ports).joinedload(SwitchPort.information_outlet),
            joinedload(NetworkDevice.device_model),
        )
        if site_id:
            device_query = device_query.filter(NetworkDevice.site_id == site_id)
        if floor_filter:
            room_ids = list(included_room_ids)
            device_query = device_query.filter(
                (NetworkDevice.room_id.in_(room_ids)) | (NetworkDevice.room_id.is_(None))
            )

        devices = device_query.all()
        for device in devices:
            nodes.append(
                TopologyNode(
                    id=f"device:{device.id}",
                    label=device.hostname,
                    kind="network_device",
                    group="network_device",
                    title=device.device_role or device.hostname,
                    metadata={
                        "vendor": device.vendor,
                        "management_ip": device.management_ip,
                        "device_role": device.device_role,
                        "model": device.device_model.model_name if device.device_model else None,
                    },
                )
            )
            if device.room_id and device.room_id in included_room_ids:
                edges.append(
                    TopologyEdge(
                        id=f"edge:room-device:{device.room_id}:{device.id}",
                        source=f"room:{device.room_id}",
                        target=f"device:{device.id}",
                        label="installed",
                        kind="physical_location",
                    )
                )

            for port in device.switch_ports:
                if floor_filter and port.information_outlet_id and port.information_outlet_id not in included_outlet_ids:
                    continue
                nodes.append(
                    TopologyNode(
                        id=f"port:{port.id}",
                        label=port.name,
                        kind="switch_port",
                        group="switch_port",
                        title=port.interface_description or port.name,
                        metadata={
                            "status": port.status,
                            "speed": port.speed,
                            "vlan_name": port.vlan_name,
                            "vlan_id_text": port.vlan_id_text,
                            "is_trunk": port.is_trunk,
                        },
                    )
                )
                edges.append(
                    TopologyEdge(
                        id=f"edge:device-port:{device.id}:{port.id}",
                        source=f"device:{device.id}",
                        target=f"port:{port.id}",
                        label="port",
                        kind="port_membership",
                    )
                )
                if port.information_outlet_id and port.information_outlet_id in included_outlet_ids:
                    edges.append(
                        TopologyEdge(
                            id=f"edge:port-outlet:{port.id}:{port.information_outlet_id}",
                            source=f"port:{port.id}",
                            target=f"outlet:{port.information_outlet_id}",
                            label="mapped",
                            kind="physical_mapping",
                        )
                    )

        if include_ip_overlay:
            self._add_ip_overlay(nodes=nodes, edges=edges, site_id=site_id)

        return TopologyGraphResponse(
            nodes=self._dedupe_nodes(nodes),
            edges=self._dedupe_edges(edges),
            filters={
                "site_id": site_id,
                "floor_id": floor_id,
                "include_ip_overlay": include_ip_overlay,
            },
        )

    def _load_sites(self, *, site_id: str | None, floor_id: str | None) -> list[Site]:
        query = self.db.query(Site).options(
            joinedload(Site.buildings)
            .joinedload(Building.floors)
            .joinedload(Floor.rooms)
            .joinedload(Room.information_outlets),
            joinedload(Site.subnets).joinedload(Subnet.vlan),
        )
        if site_id:
            query = query.filter(Site.id == site_id)
        sites = query.all()
        if not floor_id:
            return sites

        filtered: list[Site] = []
        for site in sites:
            keep = False
            for building in site.buildings:
                for floor in building.floors:
                    if floor.id == floor_id:
                        keep = True
                        break
                if keep:
                    break
            if keep:
                filtered.append(site)
        return filtered

    def _add_ip_overlay(
        self,
        *,
        nodes: list[TopologyNode],
        edges: list[TopologyEdge],
        site_id: str | None,
    ) -> None:
        subnet_query = self.db.query(Subnet).options(
            joinedload(Subnet.vlan),
            joinedload(Subnet.ip_addresses),
        )
        if site_id:
            subnet_query = subnet_query.filter(Subnet.site_id == site_id)

        for subnet in subnet_query.all():
            subnet_label = subnet.name or subnet.cidr
            nodes.append(
                TopologyNode(
                    id=f"subnet:{subnet.id}",
                    label=subnet_label,
                    kind="subnet",
                    group="overlay",
                    title=subnet.cidr,
                    metadata={
                        "cidr": subnet.cidr,
                        "gateway": subnet.gateway,
                        "vlan": subnet.vlan.vlan_id if subnet.vlan else None,
                    },
                )
            )
            if subnet.site_id:
                edges.append(
                    TopologyEdge(
                        id=f"edge:site-subnet:{subnet.site_id}:{subnet.id}",
                        source=f"site:{subnet.site_id}",
                        target=f"subnet:{subnet.id}",
                        label="subnet",
                        kind="logical_overlay",
                    )
                )
            if subnet.vlan_id:
                vlan = subnet.vlan
                if vlan:
                    nodes.append(
                        TopologyNode(
                            id=f"vlan:{vlan.id}",
                            label=f"VLAN {vlan.vlan_id}",
                            kind="vlan",
                            group="overlay",
                            title=vlan.name or f"VLAN {vlan.vlan_id}",
                            metadata={"purpose": vlan.purpose},
                        )
                    )
                    edges.append(
                        TopologyEdge(
                            id=f"edge:vlan-subnet:{vlan.id}:{subnet.id}",
                            source=f"vlan:{vlan.id}",
                            target=f"subnet:{subnet.id}",
                            label="contains",
                            kind="logical_overlay",
                        )
                    )

            for ip in subnet.ip_addresses[:25]:
                nodes.append(
                    TopologyNode(
                        id=f"ip:{ip.id}",
                        label=ip.address,
                        kind="ip_address",
                        group="overlay_ip",
                        title=ip.hostname or ip.address,
                        metadata={
                            "status": ip.status.value,
                            "hostname": ip.hostname,
                            "mac_address": ip.mac_address,
                        },
                    )
                )
                edges.append(
                    TopologyEdge(
                        id=f"edge:subnet-ip:{subnet.id}:{ip.id}",
                        source=f"subnet:{subnet.id}",
                        target=f"ip:{ip.id}",
                        label=ip.status.value,
                        kind="logical_overlay",
                    )
                )

    @staticmethod
    def _dedupe_nodes(nodes: list[TopologyNode]) -> list[TopologyNode]:
        seen: dict[str, TopologyNode] = {}
        for node in nodes:
            seen[node.id] = node
        return list(seen.values())

    @staticmethod
    def _dedupe_edges(edges: list[TopologyEdge]) -> list[TopologyEdge]:
        seen: dict[str, TopologyEdge] = {}
        for edge in edges:
            seen[edge.id] = edge
        return list(seen.values())
