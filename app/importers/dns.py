from app.importers.base import BaseImporter


class DNSImporter(BaseImporter):
    source_name = "dns"

    def validate(self, payload: dict) -> dict:
        return {"status": "stubbed", "required_config": ["server", "zone", "credential_reference"]}

    def run(self, payload: dict) -> dict:
        return {"status": "stubbed", "message": "Future DNS import service stub."}

