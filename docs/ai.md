# AI Module Notes

The AI module is intentionally advisory only in this skeleton.

## Current Placeholders

- `check_ip_availability`
- `find_available_ips`
- `explain_ip_risk`
- `explain_request_risk`

## Boundaries

- AI should not perform authoritative validation alone
- deterministic rules belong in `services`
- AI outputs should be explainable, logged, and attributable to input evidence
- future agent access should be mediated through API and policy-aware service boundaries

## Planned Expansion

- evidence bundles for skill inputs
- risk scoring explanations
- retrieval over audit/import/source records
- agent-safe query interfaces

