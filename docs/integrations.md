# Integration Roadmap

## Microsoft Power Apps

Planned role:

- user-facing request intake shell
- site / outlet / subnet assisted forms
- request tracking surface for business users

Expected integration style:

- Power Apps submits to backend API
- backend stores request as `IntakeRequest`
- backend remains source of truth

## Power Automate

Planned role:

- multi-step approval orchestration
- notifications and escalations
- enrichment triggers from enterprise sources

Expected integration style:

- workflow trigger endpoints call integration adapters
- external workflow state is reconciled back into `ApprovalStep`

## DHCP / DNS / ARP

Current state:

- interface stubs only

Future state:

- authenticated connectors
- scheduled imports
- source confidence scoring
- reconciliation with IP inventory

## Entra ID / SSO

Current state:

- local auth scaffold

Future state:

- external subject mapping on `User`
- role mapping bridge
- token validation and delegated identity

