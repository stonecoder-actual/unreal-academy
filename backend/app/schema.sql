CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO settings (key, value)
VALUES ('welcome_message', 'Your game-making journey starts here.');
PRAGMA user_version = 1;
