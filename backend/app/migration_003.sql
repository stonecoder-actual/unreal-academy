BEGIN IMMEDIATE;
CREATE TABLE guided_lessons (
 id TEXT PRIMARY KEY, lesson_id TEXT NOT NULL UNIQUE REFERENCES lessons(id),
 status TEXT NOT NULL CHECK(status IN ('draft','published')),
 document TEXT NOT NULL, video_hash TEXT NOT NULL, subtitle_hash TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE quiz_attempts (
 id INTEGER PRIMARY KEY, guide_id TEXT NOT NULL REFERENCES guided_lessons(id),
 question_id TEXT NOT NULL, answer TEXT NOT NULL, correct INTEGER NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE xp_transactions (
 id INTEGER PRIMARY KEY, award_key TEXT NOT NULL UNIQUE,
 guide_id TEXT NOT NULL REFERENCES guided_lessons(id),
 amount INTEGER NOT NULL CHECK(amount > 0), reason TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE practice_submissions (
 id TEXT PRIMARY KEY, guide_id TEXT NOT NULL REFERENCES guided_lessons(id),
 evidence TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending'
 CHECK(status IN ('pending','approved','changes_requested')),
 feedback TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT OR IGNORE INTO settings(key,value) VALUES('xp_per_level','100');
PRAGMA user_version = 3;
COMMIT;
