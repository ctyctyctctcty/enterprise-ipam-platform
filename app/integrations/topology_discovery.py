class LldpDiscoveryAdapter:
    def fetch_neighbors(self) -> dict:
        return {"status": "stubbed", "message": "Future LLDP discovery adapter."}


class CdpDiscoveryAdapter:
    def fetch_neighbors(self) -> dict:
        return {"status": "stubbed", "message": "Future CDP discovery adapter."}


class MacTableDiscoveryAdapter:
    def fetch_mac_paths(self) -> dict:
        return {"status": "stubbed", "message": "Future MAC-table topology discovery adapter."}
