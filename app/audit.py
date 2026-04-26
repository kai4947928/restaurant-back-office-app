from datetime import datetime
from flask import session

from app.db import get_db
def log_action(action, target_type, target_user_id=None, description=""):
    db = get_db()

    actor_user_id = session.get("user_id")

    now = datetime.now().isoformat()

    db.execute(
        """
        INSERT INTO audit_logs (
            actor_user_id,
            action,
            target_type,
            target_user_id,
            description,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            actor_user_id,
            action,
            target_type,
            target_user_id,
            description,
            now
        )
    )