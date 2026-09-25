CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- One row per studio booking system (BookWhen slugs from live probe)
CREATE TABLE IF NOT EXISTS studios (
  slug TEXT PRIMARY KEY,
  canonical_name TEXT NOT NULL,
  listing_url TEXT NOT NULL,
  booking_system TEXT NOT NULL DEFAULT 'bookwhen',
  scrape_permission BOOLEAN NOT NULL DEFAULT TRUE,
  timezone TEXT NOT NULL DEFAULT 'Europe/London'
);

-- Raw fetch audit + last-good fallback + staleness (requirements §2.3)
CREATE TABLE IF NOT EXISTS scrape_runs (
  id BIGSERIAL PRIMARY KEY,
  studio_slug TEXT NOT NULL REFERENCES studios(slug),
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  status TEXT NOT NULL CHECK (status IN ('ok','partial','failed')),
  rows_fetched INT NOT NULL DEFAULT 0,
  error TEXT,
  snapshot_url TEXT
);
CREATE INDEX IF NOT EXISTS idx_scrape_runs_studio_started ON scrape_runs (studio_slug, started_at DESC);

-- Canonical occurrence: one row per class date.
-- Course (LUM3X multi-date) expands to N rows sharing event_group_id.
-- Dedupe: UNIQUE below covers BookWhen (source_id always present).
-- requirements §2.2 fallback (studio+start+teacher+song) lives in kirby
-- upsert logic, not the DB: a unique index would false-conflict on
-- same-slot rows that differ by venue/section.
CREATE TABLE IF NOT EXISTS classes (
  id BIGSERIAL PRIMARY KEY,
  studio_slug TEXT NOT NULL REFERENCES studios(slug),
  source_id TEXT NOT NULL,
  event_group_id TEXT,
  status TEXT NOT NULL DEFAULT 'scheduled'
    CHECK (status IN ('scheduled','cancelled','waitlist','soldout')),

  studio_raw TEXT NOT NULL,
  teacher TEXT,
  teacher_confidence TEXT NOT NULL DEFAULT 'unknown'
    CHECK (teacher_confidence IN ('direct','title','tag-join','unknown')),

  song TEXT,
  artist TEXT,
  difficulty TEXT NOT NULL DEFAULT 'All Levels'
    CHECK (difficulty IN ('Beginners','Intermediate','Advanced','All Levels','Open')),
  song_section TEXT,

  start_at TIMESTAMPTZ NOT NULL,
  end_at TIMESTAMPTZ NOT NULL CHECK (end_at > start_at),

  venue TEXT NOT NULL,
  address TEXT,
  area TEXT,

  price_pence INT CHECK (price_pence IS NULL OR price_pence >= 0),
  price_currency CHAR(3) NOT NULL DEFAULT 'GBP',
  price_raw TEXT,
  price_tier TEXT NOT NULL DEFAULT 'single'
    CHECK (price_tier IN ('single','course','pass')),

  booking_url TEXT NOT NULL,
  source_url TEXT NOT NULL,

  title_raw TEXT NOT NULL,
  tags TEXT[] NOT NULL DEFAULT '{}',

  scraped_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  scrape_run_id BIGINT REFERENCES scrape_runs(id),

  UNIQUE (studio_slug, source_id, start_at)
);

-- updated_at auto-bump: plain UPDATEs must not leave stale timestamps.
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_classes_updated_at ON classes;
CREATE TRIGGER trg_classes_updated_at
  BEFORE UPDATE ON classes
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
