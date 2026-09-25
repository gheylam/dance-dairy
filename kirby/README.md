# kirby — data ingestion
Canonical parsers + pipeline.

## Local DB (Docker, dev parity only)

cp -n .env.example .env
docker compose up -d db
psql "$DATABASE_URL" -f db/migrations/001_base.sql
psql "$DATABASE_URL" -f db/migrations/002_indexes.sql
psql "$DATABASE_URL" -f db/seed.sql
