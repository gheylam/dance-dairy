# Dance Dairy — Global Implementation Plan
Date: 2026-09-26
Status: live — update as we plan and build

## Decisions
- Squirtle: Python monolith, backend+UI in one app. FastAPI + Jinja SSR + HTMX, FullCalendar via CDN. Serves HTML + `/api/*` from same process.
- Kirby: separate scheduled worker, writes Postgres. Squirtle read-only, no migrations.
- DB: Postgres 16, existing `db/migrations` + `pg_trgm`/FTS. Prod: Oracle free tier 2 VMs (app+db split) or GCP e2-micro co-host or Neon managed. Choice deferred to deploy.
- Deploy: Docker Compose on VM, Caddy TLS, GH Action SSH `git pull + compose up --build`. Migrate before app restart.

## Phases (per requirements.md §9)
- Phase 0: Stack locked (Python squirtle). Record in requirements §5.
- Phase 1: Canonical contract freeze, one parser per studio (Lum3x, DGC) to canonical JSON, fixture snapshots.
- Phase 2: Pipeline + store — scheduler hourly, normalize/dedupe, last-good fallback, `scrape_runs` staleness.
- Phase 3: Greenfield UI — calendar, list, search, filters, detail modal, landing, mobile pass.
- Phase 4: Hardening — error/empty states, perf weak-mobile, live QA.

## Non-goals (MVP)
No auth, favourites, alerts, analytics, map, Spotify/YT, self-submit, digests — per requirements §7.
