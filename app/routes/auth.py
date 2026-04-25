from flask import Blueprint, render_template, request, redirect, url_for,  flash, session
from werkzeug.security import check_password_hash

from app.db import get_db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        employee_id = request.form.get("employee_id", "")
        password = request.form.get("password", "")

        db = get_db()

        user = db.execute(
            """
            SELECT id, employee_id, password_hash, role
            FROM users
            WHERE employee_id = ?
            """,
            (employee_id,)
        ).fetchone()

        if user is None:
            flash("社員番号またはパスワードが違います。")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user["password_hash"], password):
            flash("社員番号またはパスワードが違います。")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user["id"]
        session["employee_id"] = user["employee_id"]
        session["role"] = user["role"]

        return redirect(url_for("home"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
