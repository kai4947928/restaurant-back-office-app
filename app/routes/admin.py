import random
import string
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from app.db import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def generate_employee_id():
    db = get_db()

    while True:
        employee_id = "".join(random.choices(string.digits, k=6))

        exists = db.execute(
            "SELECT 1 FROM users WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()

        if not exists:
            return employee_id

def generate_temp_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))

@admin_bp.route("/employees/create", methods=["GET", "POST"])
def employee_create():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        gender = request.form.get("gender", "")
        birth_date = request.form.get("birth_date", "")
        home_address = request.form.get("home_address", "")
        employment_type = request.form.get("employment_type", "")
        hire_date = request.form.get("hire_date", "")
        store_code = request.form.get("store_code", "")
        department = request.form.get("department", "")
        position = request.form.get("position", "")
        phone_number = request.form.get("phone_number", "")
        role = request.form.get("role", "staff")

        employee_id = generate_employee_id()
        temp_password = generate_temp_password()
        now = datetime.now().isoformat()

        db = get_db()

        db.execute(
            """
            INSERT INTO users (
                employee_id,
                email,
                password_hash,
                role,
                is_active,
                must_change_password,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                employee_id,
                email,
                generate_password_hash(temp_password),
                role,
                1,
                1,
                now,
                now
            )
        )

        user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        db.execute(
            """
            INSERT INTO employees (
                user_id,
                full_name,
                gender,
                birth_date,
                home_address,
                store_code,
                department,
                position,
                phone_number,
                employment_type,
                hire_date,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                full_name,
                gender,
                birth_date,
                home_address,
                store_code,
                department,
                position,
                phone_number,
                employment_type,
                hire_date,
                now,
                now
            )
        )

        db.commit()

        flash(f"従業員を登録しました。社員番号: {employee_id} / 仮パスワード: {temp_password}")
        return redirect(url_for("admin.employee_create"))

    return render_template("admin/employee_create.html")

@admin_bp.route("/employees/<int:user_id>/edit", methods=["GET", "POST"])
def employee_edit(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    db = get_db()

    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        home_address = request.form.get("home_address", "")
        employment_type = request.form.get("employment_type", "")
        store_code = request.form.get("store_code", "")
        department = request.form.get("department", "")
        position = request.form.get("position", "")
        phone_number = request.form.get("phone_number", "")
        role = request.form.get("role", "staff")

        now = datetime.now().isoformat()

        db.execute(
            """
            UPDATE users
            SET email = ?, role = ?, updated_at = ?
            WHERE id = ?
            """,
            (email, role, now, user_id)
        )

        db.execute(
            """
            UPDATE employees
            SET
                full_name = ?,
                home_address = ?
                employment_type = ?,
                store_code,
                department = ?,
                position = ?,
                phone_number = ?,
                updated_at = ?
            WHERE user_id = ?
            """,
            (
                full_name,
                home_address,
                employment_type,
                store_code,
                department,
                position,
                phone_number,
                now,
                user_id
            )
        )

        db.commit()

        flash("従業員情報を更新しました。")
        return redirect(url_for("admin.employee_list"))

    employee = db.execute(
        """
        SELECT
            users.id,
            users.email,
            users.role,
            employees.*
        FROM users
        JOIN employees ON users.id = employees.user_id
        WHERE users.id = ?
        """,
        (user_id,)
    ).fetchone()

    return render_template("admin/employee_edit.html", emp=employee)

@admin_bp.route("/employees")
def employee_list():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    db = get_db()

    employees = db.execute(
        """
        SELECT
            users.id,
            users.employee_id,
            users.email,
            users.role,
            employees.full_name,
            employees.store_code,
            employees.department,
            employees.position
        FROM users
        JOIN employees ON users.id = employees.user_id
        """
    ).fetchall()

    return render_template("admin/employee_list.html", employees=employees)

@admin_bp.route("/employees/<int:user_id>/disable", methods=["POST"])
def employee_disable(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth/login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    db = get_db()

    db.execute(
        """
        UPDATE users
        SET is_active = 0
        WHERE id = ?
        """,
        (user_id,)
    )

    db.commit()

    flash("従業員を無効化しました。")
    return redirect(url_for("admin.employee_list"))

@admin_bp.route("/employees/<int:user_id>/reset-password", methods=["POST"])
def reset_password(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    db = get_db()

    user= db.execute(
        "SELECT id FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        flash("ユーザーが存在しません")
        return redirect(url_for("admin.employee_list"))

    temp_password = generate_temp_password()
    now = datetime.now().isoformat()

    db.execute(
        """
        UPDATE users
        SET password_hash = ?, must_change_password = 1, updated_at = ?
        WHERE id = ?
        """,
        (
            generate_password_hash(temp_password),
            now,
            user_id
        )
    )

    db.commit()

    flash(f"仮パスワードを再発行しました: {temp_password}")
    return redirect(url_for("admin.employee_list"))
