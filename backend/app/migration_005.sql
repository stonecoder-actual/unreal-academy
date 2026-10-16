BEGIN IMMEDIATE;
CREATE TABLE progression_unlocks (
 rank_id TEXT PRIMARY KEY,
 unlocked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE progression_equipment (
 id INTEGER PRIMARY KEY CHECK(id=1),
 title_id TEXT REFERENCES progression_unlocks(rank_id),
 icon_id TEXT REFERENCES progression_unlocks(rank_id)
);
INSERT INTO progression_equipment(id) VALUES(1);
CREATE TABLE mastery_plan (
 lesson_id TEXT PRIMARY KEY REFERENCES lessons(id),
 course_id TEXT NOT NULL REFERENCES courses(id)
);
CREATE TABLE mastery_state (
 id INTEGER PRIMARY KEY CHECK(id=1),
 finalized INTEGER NOT NULL DEFAULT 0 CHECK(finalized IN (0,1))
);
INSERT INTO mastery_state(id) VALUES(1);
PRAGMA user_version = 5;
COMMIT;
