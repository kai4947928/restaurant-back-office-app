import sqlite3
from datetime import datetime

from flask import current_app, g
from werkzeug.security import generate_password_hash

#DB接続するための関数
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"]
        )
        g.db.row_factory = sqlite3.Row

    return g.db

#リクエスト終了時にDB接続を閉じる関数
def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

#テーブルの構造を作る関数
def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

#初期ユーザーをDBに登録する関数
def seed_user():
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE employee_id = ?",
        ("admin",)
    ).fetchone()

    if user is None:
        now = datetime.now().isoformat()

        db.execute(
            """
            INSERT INTO users (
                employee_id,
                email,
                password_hash,
                role,
                is_active,
                must_change_password,
                can_view_audit_logs,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "admin",
                "admin@example.com",
                generate_password_hash("password"),
                "admin",
                1,
                0,
                1,
                now,
                now
            )
        )

        db.commit()