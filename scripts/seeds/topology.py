from app.models.ipam import (
    Building,
    DeviceModel,
    Floor,
    InformationOutlet,
    NetworkDevice,
    Room,
    Site,
    Subnet,
    SwitchPort,
    VLAN,
)
from scripts.seeds import SeedContext


def _get_or_create(db, model, defaults: dict | None = None, **filters):
    instance = db.query(model).filter_by(**filters).first()
    if instance:
        return instance
    payload = {**filters, **(defaults or {})}
    instance = model(**payload)
    db.add(instance)
    db.flush()
    return instance


def seed_topology(context: SeedContext) -> dict[str, object]:
    db = context.db

    switch_model = _get_or_create(
        db,
        DeviceModel,
        manufacturer="Cisco",
        model_name="Catalyst 9300",
        defaults={"device_type": "switch"},
    )
    edge_model = _get_or_create(
        db,
        DeviceModel,
        manufacturer="Cisco",
        model_name="Catalyst 9200",
        defaults={"device_type": "switch"},
    )

    tokyo = _get_or_create(
        db, Site, code="TOKYO-HQ", defaults={"name": "Tokyo HQ", "country": "JP", "region": "Tokyo"}
    )
    osaka = _get_or_create(
        db, Site, code="OSAKA-BR", defaults={"name": "Osaka Branch", "country": "JP", "region": "Osaka"}
    )

    topology_index: dict[str, object] = {"sites": {"TOKYO-HQ": tokyo, "OSAKA-BR": osaka}, "subnets": {}, "outlets": {}}

    site_specs = [
        {
            "site": tokyo,
            "building_code": "B1",
            "building_name": "Main Building",
            "floors": [
                {
                    "code": "F10",
                    "name": "Floor 10",
                    "number": 10,
                    "room_code": "R1001",
                    "room_name": "Network Room",
                    "outlets": ["IO-10F-1001-A", "IO-10F-1001-B"],
                    "device_hostname": "sw-tokyo-hq-10f-01",
                    "management_ip": "10.10.0.10",
                    "model": switch_model,
                    "vlan_id": 110,
                    "vlan_name": "Office Clients",
                    "subnet_cidr": "10.10.110.0/24",
                    "subnet_name": "Tokyo Office Fixed",
                    "gateway": "10.10.110.1",
                },
                {
                    "code": "F11",
                    "name": "Floor 11",
                    "number": 11,
                    "room_code": "R1102",
                    "room_name": "Support Area",
                    "outlets": ["IO-11F-1102-A", "IO-11F-1102-B"],
                    "device_hostname": "sw-tokyo-hq-11f-01",
                    "management_ip": "10.10.0.11",
                    "model": edge_model,
                    "vlan_id": 120,
                    "vlan_name": "Operations Devices",
                    "subnet_cidr": "10.10.120.0/24",
                    "subnet_name": "Tokyo Operations Fixed",
                    "gateway": "10.10.120.1",
                },
            ],
        },
        {
            "site": osaka,
            "building_code": "B1",
            "building_name": "Branch Building",
            "floors": [
                {
                    "code": "F03",
                    "name": "Floor 3",
                    "number": 3,
                    "room_code": "R0301",
                    "room_name": "Branch Office",
                    "outlets": ["IO-03F-0301-A", "IO-03F-0301-B"],
                    "device_hostname": "sw-osaka-br-03f-01",
                    "management_ip": "10.20.0.3",
                    "model": edge_model,
                    "vlan_id": 210,
                    "vlan_name": "Branch Clients",
                    "subnet_cidr": "10.20.210.0/24",
                    "subnet_name": "Osaka Branch Fixed",
                    "gateway": "10.20.210.1",
                }
            ],
        },
    ]

    for site_spec in site_specs:
        building = _get_or_create(
            db,
            Building,
            site_id=site_spec["site"].id,
            code=site_spec["building_code"],
            defaults={"name": site_spec["building_name"]},
        )
        for floor_spec in site_spec["floors"]:
            floor = _get_or_create(
                db,
                Floor,
                building_id=building.id,
                code=floor_spec["code"],
                defaults={"name": floor_spec["name"], "floor_number": floor_spec["number"]},
            )
            room = _get_or_create(
                db,
                Room,
                floor_id=floor.id,
                code=floor_spec["room_code"],
                defaults={"name": floor_spec["room_name"]},
            )
            vlan = _get_or_create(
                db,
                VLAN,
                site_id=site_spec["site"].id,
                vlan_id=floor_spec["vlan_id"],
                defaults={"name": floor_spec["vlan_name"], "purpose": "Demo fixed IP usage"},
            )
            subnet = _get_or_create(
                db,
                Subnet,
                cidr=floor_spec["subnet_cidr"],
                defaults={
                    "name": floor_spec["subnet_name"],
                    "gateway": floor_spec["gateway"],
                    "site_id": site_spec["site"].id,
                    "vlan_id": vlan.id,
                    "usage_type": "fixed_ip",
                    "owner_department": "Infrastructure",
                },
            )
            topology_index["subnets"][subnet.cidr] = subnet

            device = _get_or_create(
                db,
                NetworkDevice,
                hostname=floor_spec["device_hostname"],
                defaults={
                    "management_ip": floor_spec["management_ip"],
                    "site_id": site_spec["site"].id,
                    "building_id": building.id,
                    "room_id": room.id,
                    "device_model_id": floor_spec["model"].id,
                    "device_role": "access_switch",
                    "vendor": "Cisco",
                },
            )

            for index, outlet_code in enumerate(floor_spec["outlets"], start=1):
                outlet = _get_or_create(
                    db,
                    InformationOutlet,
                    code=outlet_code,
                    defaults={"room_id": room.id, "label": f"{floor_spec['room_name']} outlet {index}", "status": "active"},
                )
                topology_index["outlets"][outlet.code] = outlet
                _get_or_create(
                    db,
                    SwitchPort,
                    network_device_id=device.id,
                    name=f"Gi1/0/{23 + index}",
                    defaults={
                        "information_outlet_id": outlet.id,
                        "interface_description": outlet.code,
                        "status": "connected" if index == 1 else "notconnect",
                        "vlan_name": vlan.name,
                        "vlan_id_text": str(vlan.vlan_id),
                        "speed": "1000",
                    },
                )

    return topology_index

