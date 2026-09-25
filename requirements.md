# Project Requirements (2-person wrap-up)

> Build-only. No roles, no process. Full auto pipeline. Greenfield UI allowed. Stack decided in-doc during build Phase 0.

## 1. Problem + Users

London K-pop dancers check scattered studio sites to find classes.
Need single searchable, filterable calendar to find class by song, artist, teacher, studio, date.

Users: dancers on phones, checking on go. Studios as data sources, not users in MVP.

## 2. Functional Requirements

### 2.1 Ingestion
- MUST automate 2 sources for MVP: Lum3x (easy), DGC (medium). KMDC / Kpopinlondonmin (hard) deferred post-MVP.
- MUST record per-source: listing URL, booking system, scrape permission flag.
- MUST NOT require manual entry for MVP operation.
- Instagram-only studios deferred, documented as known gap.

### 2.2 Normalization
Canonical class record MUST contain:
- `studio` (canonical name + source name raw)
- `teacher`
- `song` (nullable if not K-pop / unknown)
- `artist` (nullable, same rule)
- `difficulty` (normalized: Beginners / Intermediate / Advanced / All Levels / Open)
- `start_datetime`, `end_datetime` (timezone: Europe/London)
- `location` (venue + area)
- `price` (numeric pence + currency + raw text)
- `booking_url`
- `source_url` (exact page scraped)
- `scraped_at`, `updated_at`
- `song_section` (optional, e.g. chorus / part 2)

Dedupe key: `source + source_id` fallback `studio + start_datetime + teacher + song`.

### 2.3 Refresh
- MUST run on schedule (default: hourly; minimum: every 6h).
- MUST surface staleness in UI: "Last updated Xh ago".
- MUST retry failed source without blocking others.
- MUST keep last-good dataset on scraper failure.

### 2.4 Discovery UI (greenfield, UI-agnostic)
- MUST provide: calendar month/week views, list view.
- MUST provide keyword search across song, artist, teacher, studio, location.
- MUST provide filters: song, artist, teacher, studio, date, difficulty. Filters visible, easy reset.
- MUST provide class detail view (modal or page) without losing calendar place.
- MUST provide mobile-first layout. Class card scannable in 1–2s: song/artist, teacher, studio, location, time + duration, level tag, booking link.
- MUST handle empty states: "No classes found", "No classes today" + alternative action.
- Landing MUST explain what the app is. MUST replace current TanStack boilerplate if reusing repo.

## 3. UX Constraints
- Minimal clicks to class detail.
- Consistent card hierarchy, same field positions.
- Fast load on weak mobile connections. No heavy images.
- Booking links obvious, open reliably in new tab.

## 4. Non-Functional
- Timezone-correct for Europe/London including DST.
- Accessible filter controls (keyboard + screen reader labels).
- Basic SEO (title, meta, semantic markup).
- No auth in MVP.

## 5. Stack Decision (deferred to Phase 0)
Decide before building. Criteria: 2-person ops cost, Netlify fit, server search need, history need.

| Option | Shape | Pros | Cons |
|---|---|---|---|
| A | TanStack Start (current) rebuilt clean | Keeps Netlify config, SSR + server functions | Heavier than needed if read-only JSON suffices |
| B | Vite SPA + serverless JSON | Lightest ops, fastest for 2 | No server search/history |
| C | Next/API + Postgres (Supabase/Neon) | Server search, history, robust | Most ops for 2 |

Default recommendation: B unless server-side search or history proves necessary in Phase 1 spikes. Record decision + reason in this doc before Phase 1.

## 6. Success Criteria (cut for 2)
- 2 studios automated.
- Calendar shows correct times.
- Search + filters return accurate results.
- Refresh pipeline runs without manual steps.
- User finds class by song/artist within seconds.
- Stretch only: 50-user test, studio feedback.

## 7. Out of Scope
- Studio 808, ARC, Instagram-only automation.
- KMDC / Kpopinlondonmin automation (deferred post-MVP).
- User accounts, favourites, saved filters.
- Email/push alerts.
- Analytics dashboards.
- Map view.
- Spotify/YouTube integration.
- Teacher self-submit.
- K-pop hub / comebacks content.
- Weekly digests.
- Onboarding walkthrough, FAQ page, contact form (unless trivial static).
- Light/dark mode, calendar export (defer to MVP+).

## 8. Risks
- Scraping permission / blocking per source. Mitigation: permission flag, polite rate limits, fallback to last-good.
- Format variance across studios. Mitigation: per-source parser + raw field preserved.
- Schedule churn. Mitigation: frequent refresh + `updated_at` surfacing.

## 9. Build Phases
- **Phase 0 — Stack pick.** Spike each source fetchability (1 script each). Pick A/B/C. Update §5 with decision.
- **Phase 1 — Contract + spikes.** Freeze canonical model. One parser per studio outputting canonical JSON. Manual fixture snapshots.
- **Phase 2 — Pipeline + store.** Scheduler, normalize, dedupe, versioned JSON or DB, last-good fallback, staleness metadata.
- **Phase 3 — Greenfield UI.** Calendar, list, search, filters, detail, landing, mobile pass.
- **Phase 4 — Hardening.** Error states, empty states, load perf, QA against live sources, focus-group test.
