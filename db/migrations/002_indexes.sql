-- Calendar + filter lookups
CREATE INDEX IF NOT EXISTS idx_classes_start ON classes (start_at);
CREATE INDEX IF NOT EXISTS idx_classes_studio_start ON classes (studio_slug, start_at);
CREATE INDEX IF NOT EXISTS idx_classes_difficulty_start ON classes (difficulty, start_at);

-- Trigram fuzzy match for song/artist/teacher/studio
CREATE INDEX IF NOT EXISTS idx_classes_song_trgm ON classes USING gin (song gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_classes_artist_trgm ON classes USING gin (artist gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_classes_teacher_trgm ON classes USING gin (teacher gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_classes_studio_trgm ON classes USING gin (studio_slug gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_classes_title_trgm ON classes USING gin (title_raw gin_trgm_ops);

-- Full-text search across song/artist/teacher/title
CREATE INDEX IF NOT EXISTS idx_classes_search_tsv ON classes USING gin (to_tsvector('english',
  coalesce(song,'') || ' ' || coalesce(artist,'') || ' ' || coalesce(teacher,'') || ' ' || title_raw));
