DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TET NOT NULL DEFAULT 'staff',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);