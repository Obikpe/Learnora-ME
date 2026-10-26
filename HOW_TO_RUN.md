# Learnora — Local Runbook

This runbook describes the current repository layout. It replaces older instructions that refer to the legacy `frontend/` and `backend-node/` runtime.

## Prerequisites

- Node.js and npm compatible with Next.js 14
- Python 3.11+
- Git
- Access to a disposable Supabase/PostgreSQL test environment for database tests

## Install

From the repository root:

```bash
npm run install:all
```

Configure `backend-python/.env` from `backend-python/.env.example`. Do not commit real keys or passwords. For non-development execution, the backend requires a Supabase URL, a service/secret key, and a strong JWT secret.

## Start Learnora ME and the API

From the repository root:

```bash
npm run dev
```

- Learnora ME: http://localhost:3000
- FastAPI: http://localhost:8000

The production API disables Swagger/OpenAPI documentation. For local development, the API docs are available at http://localhost:8000/docs only when `APP_ENV` is set to a non-production value and the backend environment is configured accordingly.

## Start Learnora Teams

In a second terminal:

```bash
npm run dev:teams
```

Learnora Teams uses port 3001 by default to avoid colliding with Learnora ME on port 3000. Both frontends proxy `/api` to FastAPI through `next.config.mjs`; development defaults to `http://localhost:8000`. Set `API_PROXY_TARGET` to a different backend base URL when needed. Browser sessions use HttpOnly cookies, so deploy the backend and both frontends together after the release gates are approved.

## Build the frontends

```bash
npm run build:me
npm run build:teams
```

## Backend tests

Backend tests live under `backend-python/tests/`. Use the repository's GitHub Actions workflows as the canonical automated verification entry point. Database integration tests require the workflow's disposable PostgreSQL/PostgREST services and must not be pointed at production.

Before accepting a result, check that all required workflows completed successfully for the same commit SHA. A cancelled, skipped, or stale run is not a pass.

## Supabase safety

- Do not replay `supabase/legacy_migrations/001_initial.sql` through `015_learnora_ai_permissions.sql` against an existing database.
- Do not run catalog-derived reconstruction fixtures as production migrations.
- Do not fabricate migration-ledger entries or re-run seed/data migrations to make the ledger appear complete.
- Validate schema, grants, default ACLs, RLS, policies, and security-definer functions in a disposable database first.
- Production changes require an explicit migration plan, rollback/recovery plan, and authorised approval. Repository commits do not authorise production database changes.

See [the roadmap](docs/ROADMAP.md) and [migration reconciliation report](docs/active-pheonix-migration-reconciliation.md) for current blockers.
