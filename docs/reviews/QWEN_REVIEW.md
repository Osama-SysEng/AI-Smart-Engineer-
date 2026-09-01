# Qwen Material Review

## Source
Qwen material supplied with the project contained a small `ai-smart-engineer-mvp` implementation.

## Decision
It is treated as reference material, not as the project base.

## Useful concepts retained
- Material and unit normalization.
- Confidence scoring.
- Source locators for extracted values.
- Engineering-vs-reference reconciliation.
- Audit events.
- Simple CSV fixture data for smoke testing.

## Rejected as production architecture
- SQLite as primary DB.
- CSV-only ingestion.
- No authentication.
- Local-only storage.
- Wildcard CORS.
- Single-file `main.py` architecture.
- Synchronous heavy document processing.
- Mock SAP presented as the operational integration.

## Result
Those concepts are mapped into the larger AI Smart Engineer architecture. The supplied Qwen MVP does not replace the PostgreSQL, Redis/Celery, modular service, RBAC, AI provider, document pipeline, workflow, and security layers.
