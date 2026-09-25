# AGENTS.md — dance-dairy

Monorepo. Source of truth: `requirements.md`.

## Layout

- `kirby/` — data ingestion (scrapers + pipeline)
- `squirtle/` — app (greenfield discovery UI)
- `requirements.md` — problem, functional requirements, stack decision (§5), phases

## Contributing

- Never push to `main` directly. Always create a branch and iterate there.
- Human merge required. No self-merge, no auto-merge.
- Always squash merge. Keeps history clean, one intent per merge.
- Keep branches short-lived. Rebase on `main` before opening PR.

## Pull Requests

- Clear summary + description required.
- Include: what changed, why, how tested, linked issue if any.
- Keep PRs small. One purpose per PR.

## Commits

- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
- Example: `feat(kirby): add Lum3x parser`
- One logical change per commit. Present tense, no fluff.

## Build / Test

- Stack undecided — see `requirements.md §5` (Phase 0 picks A/B/C).
- Update this section once stack + commands exist. Do not invent commands.
