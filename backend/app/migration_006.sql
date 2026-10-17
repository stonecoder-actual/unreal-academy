BEGIN IMMEDIATE;
-- Source bindings for authored portal notes shipped with the application.
-- This contains no purchased transcripts or learner progress.
CREATE TABLE bundled_lesson_sources (
 lesson_id TEXT PRIMARY KEY REFERENCES lessons(id),
 content_hash TEXT NOT NULL
);
PRAGMA user_version = 6;
COMMIT;
