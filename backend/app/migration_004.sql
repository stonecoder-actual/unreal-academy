BEGIN IMMEDIATE;
ALTER TABLE courses ADD COLUMN source_type TEXT NOT NULL DEFAULT 'local' CHECK(source_type IN ('local','udemy'));
ALTER TABLE courses ADD COLUMN source_url TEXT;
ALTER TABLE courses ADD COLUMN difficulty TEXT CHECK(difficulty IN ('Beginner','Intermediate','Advanced'));
ALTER TABLE lessons ADD COLUMN external_id TEXT;
ALTER TABLE lessons ADD COLUMN external_url TEXT;
ALTER TABLE lessons ADD COLUMN item_kind TEXT NOT NULL DEFAULT 'video' CHECK(item_kind IN ('video','article','quiz'));
ALTER TABLE lessons ADD COLUMN section_title TEXT;
CREATE UNIQUE INDEX external_lesson_identity ON lessons(course_id,external_id) WHERE external_id IS NOT NULL;
CREATE TABLE lesson_transcripts (
 lesson_id TEXT PRIMARY KEY REFERENCES lessons(id),
 cues TEXT NOT NULL,
 content_hash TEXT NOT NULL,
 captured_at TEXT NOT NULL,
 source_url TEXT NOT NULL
);
PRAGMA user_version = 4;
COMMIT;
