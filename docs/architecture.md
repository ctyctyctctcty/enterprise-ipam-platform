# Architecture Overview

## Purpose

This platform is designed to become the backend system of record for enterprise fixed IP request intake, allocation, reconciliation, workflow, and future agent-driven analysis.

## Layering

- `models`: persistence and traceability model only
- `schemas`: DTO and external API contracts
- `services/ipam_queries.py`: read-side IP lookup and operator views
- `services/ipam_commands.py`: write-side IP commands with audit
- `services/intake_queries.py`: request read model and status lookup
- `services/intake_commands.py`: request submission path and normalization hooks
- `services/workflow.py`: status transition and external workflow trigger boundary
- `services/import_jobs.py`: import job lifecycle and execution placeholder
- `services/audit.py`: audit write/query boundary
- `api`: transport layer only, not business rule location
- `admin`: internal operational visibility via SQLAdmin
- `importers`: source-specific data intake adapters
- `integrations`: infrastructure and Microsoft integration boundaries
- `ai`: skill registry and orchestration placeholders, intentionally separated from validation logic

## Domain Model Highlights

- Location hierarchy: `Site -> Building -> Floor -> Room -> InformationOutlet`
- Physical network hierarchy: `NetworkDevice -> SwitchPort -> InformationOutlet`
- Addressing hierarchy: `VLAN -> Subnet -> IPAddress`
- Traceability: `SourceRecord`, `IPAddressSourceObservation`, `ImportJob`, `AuditLog`, `AllocationHistory`
- Intake and workflow: `IntakeRequest -> ApprovalStep`

## Design Notes

- PostgreSQL-oriented relational design with SQLite-compatible local development
- Read-side and write-side service boundaries are explicit to avoid routers becoming the business layer
- `IntakeRequest` preserves raw inbound location text while also allowing normalized foreign keys
- `IPAddress` now supports a primary source plus multiple source observations for future reconciliation
- Audit-first write paths via service layer
- Replaceable frontend strategy: Power Apps, internal admin, or future portals
- AI kept as advisory orchestration only, not the source of truth
- Importers and integrations separated to allow deterministic ingestion pipelines
