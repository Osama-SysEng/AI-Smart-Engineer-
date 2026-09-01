# Managed PostgreSQL Runbook

This project is prepared for a managed **PostgreSQL 16+** database reachable through `postgresql+asyncpg`. The database provider, network, KMS, backup policy, and secret manager remain deployment decisions; this repository deliberately contains no database credentials or provider-specific provisioning tokens.

| Control | Required production setting | Verification |
|---|---|---|
| Transport | `DATABASE_SSL_MODE=require` | Application startup rejects weaker PostgreSQL TLS mode. |
| Credentials | Secret manager injection only | No connection string is committed to Git. |
| Schema | `alembic upgrade head` in a one-shot release job | `alembic current` equals `alembic heads`. |
| Connection safety | `pool_pre_ping`, bounded pool/overflow, recycle and timeout | Readiness endpoint returns `200` only after `SELECT 1`. |
| Recovery | Provider point-in-time recovery plus a tested logical restore | Quarterly restore exercise documented outside the production database. |

## Release sequence

First provision a non-public PostgreSQL endpoint with TLS enforcement, an application database role restricted to the application schema, and a separate migration role. Set `ENVIRONMENT=production`, a 32+ character `SECRET_KEY`, restrictive `CORS_ORIGINS`, and `DATABASE_SSL_MODE=require` in the deployment secret manager. Run the migration job once per release, then deploy API workers. Do not let every web replica run migrations on startup.

> The API readiness endpoint is intentionally stricter than liveness: it returns HTTP 503 when the database cannot answer a query, allowing an orchestrator to keep an unhealthy replica out of service.

## Backup and restoration acceptance test

Schedule provider backups and point-in-time recovery according to the organization’s retention policy. At least quarterly, restore the latest backup into an isolated environment, run `alembic current`, exercise a representative login and document query, compare row counts for critical tenant tables, and record elapsed recovery time. Never use the production endpoint for load or destructive recovery testing.

## Migration safety

Migration `0002_security_sessions_managed_database` adds server-side authentication sessions, tenant-scoped role uniqueness, and audit/session indexes. It is additive except for replacing the original globally unique role name with a tenant-scoped unique constraint; check any external process that creates roles before applying it. Execute the migration first in staging against a recent sanitized snapshot.
