BEGIN IMMEDIATE;
CREATE TABLE courses (
    id TEXT PRIMARY KEY,
    folder TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE lessons (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(id),
    relative_path TEXT NOT NULL,
    title TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    modified_ns INTEGER NOT NULL,
    duration REAL,
    video_codec TEXT,
    audio_codec TEXT,
    playable INTEGER NOT NULL DEFAULT 0,
    caption_path TEXT,
    available INTEGER NOT NULL DEFAULT 1,
    UNIQUE(course_id, relative_path)
);
CREATE TABLE resources (
    id TEXT PRIMARY KEY,
    course_id TEXT NOT NULL REFERENCES courses(id),
    lesson_id TEXT REFERENCES lessons(id),
    relative_path TEXT NOT NULL,
    available INTEGER NOT NULL DEFAULT 1,
    UNIQUE(course_id, relative_path)
);
CREATE TABLE lesson_progress (
    lesson_id TEXT PRIMARY KEY REFERENCES lessons(id),
    position REAL NOT NULL DEFAULT 0 CHECK(position >= 0),
    watched INTEGER NOT NULL DEFAULT 0 CHECK(watched IN (0, 1)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
PRAGMA user_version = 2;
COMMIT;
