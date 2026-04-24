from app.importers.base import BaseImporter


class DHCPImporter(BaseImporter):
    source_name = "dhcp"

    def validate(self, payload: dict) -> dict:
        return {"status": "stubbed", "required_config": ["server", "scope", "credential_reference"]}

    def run(self, payload: dict) -> dict:
        return {"status": "stubbed", "message": "Future DHCP import service stub."}

