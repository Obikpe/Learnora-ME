# Learnora — Pheonix Analytics

Learnora is maintained as a multi-application repository. The product and engineering documents under `docs/` define the intended product boundaries, data invariants, security requirements, and acceptance gates.

## Active applications

- **Learnora ME** — learner and creator-facing application: `frontend-v02/`
- **Learnora Teams** — organisation and internal operations interface: `frontend-team/`
- **FastAPI backend** — API and access-control boundary: `backend-python/`
- **Supabase SQL** — migration history, schema snapshots, and operational SQL: `supabase/`
- **Engineering documents** — product specification, roadmap, decisions, and migration reconciliation: `docs/`

The root-level legacy `frontend/` and `backend-node/` references in older setup notes are not the source of truth for the current Learnora applications.

## Local development

Requirements: Node.js/npm and Python 3.11 or newer.

1. Install dependencies for the active apps and backend:

   ```bash
   npm run install:all
   ```

2. Configure the backend environment in `backend-python/.env`. Start from `backend-python/.env.example`; supply valid credentials locally and never commit secrets. The backend requires `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (or the supported secret-key alias), and a strong `JWT_SECRET` outside development.

3. Start Learnora ME and the FastAPI backend:

   ```bash
   npm run dev
   ```

   Learnora ME runs on port 3000 and FastAPI on port 8000.

4. To run Learnora Teams instead, use a separate terminal:

   ```bash
   npm run dev:teams
   ```

   Learnora Teams runs on port 3001 to avoid conflicting with Learnora ME's default port.

5. Run production builds:

   ```bash
   npm run build:me
   npm run build:teams
   ```

   Backend regression and migration tests are maintained under `backend-python/tests/` and in the GitHub Actions workflows.

## Security and release status

Do not infer production readiness from this README or a successful frontend build. Browser access to protected data must be mediated by the backend and database permissions. Migration files must be reconciled and tested against disposable databases before any production migration is approved. Changes to this repository do not themselves authorise production database changes or deployments.

Known release gates are tracked in [the engineering roadmap](docs/ROADMAP.md) and [active schema/migration reconciliation](docs/active-pheonix-migration-reconciliation.md). The documented managed-role default-ACL issue and migration provenance gaps must remain open until verified with appropriate evidence.

## Engineering documents

- [Product engineering specification](docs/PRODUCT_ENGINEERING_SPEC.md)
- [Engineering roadmap](docs/ROADMAP.md)
- [Engineering history and decisions](docs/ENGINEERING_HISTORY_AND_DECISIONS.md)
- [UI/UX research and decisions](docs/learnora-ui-ux-research.md)
- [Active schema and migration reconciliation](docs/active-pheonix-migration-reconciliation.md)
