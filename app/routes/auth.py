from flask import Blueprint, render_template, request, redirect, url_for,  flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

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
            SELECT id, employee_id, password_hash, role, is_active, must_change_password
            FROM users
            WHERE employee_id = ?
            """,
            (employee_id,)
        ).fetchone()

        if user is None or user["is_active"] == 0:
            flash("社員番号またはパスワードが違います。")
            return redirect(url_for("auth.login"))

        if user["password_hash"] is None:
            flash("パスワードが未設定です。")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user["password_hash"], password):
            flash("社員番号またはパスワードが違います。")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user["id"]
        session["employee_id"] = user["employee_id"]
        session["role"] = user["role"]

        if user["must_change_password"] == 1:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("auth.change_password"))

        return redirect(url_for("home"))

    return render_template("login.html")

@auth_bp.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if new_password == "" or confirm_password == "":
            flash("パスワードを入力してください")
            return redirect(url_for("auth.change_password"))

        if new_password != confirm_password:
            flash("パスワードが一致しません")
            return redirect(url_for("auth.change_password"))

        db = get_db()

        now = datetime.now().isoformat()

        db.execute(
            """
            UPDATE users
            SET password_hash = ?, must_change_password = 0, updated_at = ?
            WHERE id = ?
            """,
            (
                generate_password_hash(new_password),
                now,
                session["user_id"]
            )
        )

        db.commit()

        flash("パスワードを更新しました")
        return redirect(url_for("home"))

    return render_template("change_password.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
