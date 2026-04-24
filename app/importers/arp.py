from app.importers.base import BaseImporter


class ARPImporter(BaseImporter):
    source_name = "arp"

    def validate(self, payload: dict) -> dict:
        return {"status": "stubbed", "required_config": ["collector", "time_window"]}

    def run(self, payload: dict) -> dict:
        return {"status": "stubbed", "message": "Future ARP observation importer stub."}

