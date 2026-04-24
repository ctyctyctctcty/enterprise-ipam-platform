# Enterprise Internal IP Management Platform

A local-first, extensible enterprise IP management backend skeleton built with FastAPI, SQLAlchemy, Alembic, SQLAdmin, PostgreSQL-oriented modeling, and Docker Compose.

This project is intentionally designed as a large expandable framework rather than a tiny MVP. Many integrations and workflows are placeholders by design, so the system can evolve into the source of truth for enterprise fixed IP request and management operations.

## Core Principles

- Backend is the system of record
- Replaceable frontend shells
- Auditability and traceability by default
- Rich relational modeling for future enterprise needs
- Service-layer business logic
- AI isolated from validation and hard rules
- Local-first development with SQLite, production-oriented for PostgreSQL

## Included Modules

- `auth`: local auth scaffold with future SSO / Entra ID extension points
- `ipam`: IP inventory, subnets, VLANs, allocation, devices, switch ports
- `intake`: incoming fixed IP request domain
- `workflow`: approval workflow placeholders
- `importers`: Excel / DHCP / DNS / ARP importer placeholders
- `integrations`: future Microsoft / infra integration interfaces
- `audit`: audit logging and change history
- `ai`: future-ready skill registry and orchestration skeleton
- `admin`: SQLAdmin internal admin UI
- `core`: settings, db, security, enums, shared utilities
- `api`: router structure and versioned endpoints
- `models`, `schemas`, `services`, `tests`, `docs`

## Second-Round Refinements

- separated read-side and write-side services for IPAM and intake
- improved intake model to preserve external request payload and raw location text
- improved IP/source traceability with multi-source observation support
- expanded import job lifecycle structure
- strengthened admin coverage for source traceability and operational review

## Quick Start

### Local Python

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python scripts/init_db.py
uvicorn app.main:app --reload
```

Open:

- API docs: `http://localhost:8000/docs`
- Admin UI: `http://localhost:8000/admin`
- Health: `http://localhost:8000/api/v1/health`

## Windows Hyper-V Quick Start

For a simple internal Windows VM deployment without Docker:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\windows-hyperv-init.ps1
.\scripts\windows-hyperv-run.ps1 -Port 18000
```

This mode is intended for internal demo / PoC server use on a Windows Hyper-V VM.
The repository also includes a portable demo seed database at `demo/enterprise_ipam_demo_seed.db` so a Windows Hyper-V VM can restore a ready-to-demo dataset immediately.

### Docker Compose

```bash
docker compose up --build
```

The default compose stack includes PostgreSQL plus the application container.

## Default Local Credentials

Seeded during `scripts/init_db.py`:

- Email: `admin@example.com`
- Password: `admin123`

These are for local development only.

## Demo Walkthrough

This repository now includes a demo-ready vertical slice for fixed IP request review.

### Prepare Demo Data

```bash
alembic upgrade head
python scripts/init_db.py
python scripts/generate_demo_excel.py
```

This creates:

- baseline site/building/room/outlet/switch-port demo data
- `demo/demo_ips.xlsx` with four realistic IP rows:
  - available candidate
  - DHCP pool
  - allocated confirmed
  - conflict suspected

### Run Demo Import

1. Start the app.
2. Create an Excel import job:

```bash
curl -X POST http://localhost:8000/api/v1/imports/excel -H "Content-Type: application/json" -d "{\"workbook_path\":\"demo/demo_ips.xlsx\"}"
```

3. Execute the job:

```bash
curl -X POST http://localhost:8000/api/v1/imports/jobs/<JOB_ID>/execute
```

### Submit Demo Fixed IP Request

```bash
curl -X POST http://localhost:8000/api/v1/requests/submit ^
  -H "Content-Type: application/json" ^
  -d "{\"applicant_name\":\"Demo User\",\"applicant_email\":\"demo@example.com\",\"department\":\"IT\",\"information_outlet_code\":\"IO-10F-1001-A\",\"vlan_or_subnet\":\"10.10.110.0/24\",\"hostname\":\"demo-device-01\",\"mac_address\":\"00:AA:BB:CC:DD:EE\",\"fixed_ip_required\":true}"
```

The backend will:

- persist the request
- run deterministic rule evaluation
- return `candidate`, `blocked`, or `review_needed`
- store recommended IP when a candidate exists
- write audit logs

### Review / Approve Demo Request

Approve and assign the recommended IP:

```bash
curl -X POST http://localhost:8000/api/v1/requests/<REQUEST_ID>/transition ^
  -H "Content-Type: application/json" ^
  -d "{\"target_status\":\"assigned\",\"comment\":\"Approved in demo\"}"
```

### See It In Admin UI

Open `http://localhost:8000/admin` and review:

- `IPAM > IP List`
- `IPAM > Conflict Review`
- `Requests > Request List`
- `Operations > Import Jobs`
- `Operations > Source Records`
- `Operations > IP Source Observations`
- `Operations > Audit Logs`

## Migrations

Alembic is configured and ready for iterative migrations:

```bash
alembic upgrade head
alembic revision --autogenerate -m "initial"
```

SQLite is supported for local development, while the schema is designed with PostgreSQL in mind.

## Testing

```bash
pytest
```

## Documentation

- [Architecture](C:\codex-workspace\enterprise-ipam\docs\architecture.md)
- [Integrations Roadmap](C:\codex-workspace\enterprise-ipam\docs\integrations.md)
- [AI Skills](C:\codex-workspace\enterprise-ipam\docs\ai.md)
- [Demo Guide (Chinese)](C:\codex-workspace\enterprise-ipam\docs\demo-guide.zh-CN.md)
- [Company Install Guide (Chinese)](C:\codex-workspace\enterprise-ipam\docs\company-install.zh-CN.md)
- [Company Required Info Checklist (Chinese)](C:\codex-workspace\enterprise-ipam\docs\company-required-info.zh-CN.md)
- [Hyper-V Windows Server Guide (Chinese)](C:\codex-workspace\enterprise-ipam\docs\hyperv-windows-server.zh-CN.md)
