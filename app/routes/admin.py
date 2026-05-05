import random
import string
from datetime import datetime

from app.forms import EmployeeSearchForm, AuditLogSearchForm

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from app.audit import log_action
from app.db import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

#社員番号作成関数
def generate_employee_id():
    db = get_db()

    #重複しない番号ができるまで繰り返す
    while True:
        employee_id = "".join(random.choices(string.digits, k=6))

        exists = db.execute(
            "SELECT 1 FROM users WHERE employee_id = ?",
            (employee_id,)
        ).fetchone()

        if not exists:
            return employee_id

#仮パスワード発行関数
def generate_temp_password():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))

#従業員登録処理
@admin_bp.route("/employees/create", methods=["GET", "POST"])
def employee_create():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    #従業員登録権限の有無を確認
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

        #最後に追加したデータのIDを取得
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

        #ログ画面で確認できる内容
        log_action(
            action="create_employee",
            target_type="employee",
            target_user_id=user_id,
            description=f"{full_name}を登録"
        )

        db.commit()

        flash(f"従業員を登録しました。社員番号: {employee_id} / 仮パスワード: {temp_password}")
        return redirect(url_for("admin.employee_create"))

    return render_template("admin/employee_create.html")

#従業員情報更新処理
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
                home_address = ?,
                employment_type = ?,
                store_code = ?,
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

        log_action(
            action="edit_employee",
            target_type="employee",
            target_user_id=user_id,
            description=f"{full_name}へ更新"
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

#従業員一覧表示処理
@admin_bp.route("/employees")
def employee_list():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    #検索フォーム
    form = EmployeeSearchForm(request.args, meta={"csrf": False})

    keyword = form.keyword.data or ""
    role = form.role.data or ""
    department = form.department.data or ""

    sql = """
        SELECT
            users.id,
            users.employee_id,
            users.email,
            users.role,
            users.is_active,
            employees.full_name,
            employees.store_code,
            employees.department,
            employees.position
        FROM users
        JOIN employees ON users.id = employees.user_id
        WHERE 1 = 1
    """

    params = []

    if keyword:
        sql += """
            AND (
                users.employee_id LIKE ?
                OR users.email LIKE ?
                OR employees.full_name LIKE ?
                OR employees.store_code LIKE ?
            )
        """
        like_keyword = f"%{keyword}%"
        params.extend([like_keyword, like_keyword, like_keyword, like_keyword])

    if role:
        sql += " AND users.role = ?"
        params.append(role)

    if department:
        sql += " AND employees.department = ?"
        params.append(department)

    sql += " ORDER BY users.employee_id ASC"

    db = get_db()
    employees = db.execute(sql, params).fetchall()

    return render_template("admin/employee_list.html", employees=employees, form=form)

#アカウント無効化処理
@admin_bp.route("/employees/<int:user_id>/disable", methods=["POST"])
def employee_disable(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

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

    log_action(
        action="disable_employee",
        target_type="employee",
        target_user_id=user_id,
        description="従業員を無効化"
    )

    db.commit()

    flash("従業員を無効化しました。")
    return redirect(url_for("admin.employee_list"))

#仮パスワード再発行処理(管理者が再発行するもので、念の為の機能)
@admin_bp.route("/employees/<int:user_id>/reset-password", methods=["POST"])
def reset_password(user_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    db = get_db()

    user = db.execute(
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

    log_action(
        action="reset_password",
        target_type="user",
        target_user_id=user_id,
        description="パスワード再発行"
    )
    db.commit()

    flash(f"仮パスワードを再発行しました: {temp_password}")
    return redirect(url_for("admin.employee_list"))

#従業員情報(登録・更新・仮パスワード再発行・アカウント無効化)のログをログ確認画面にて確認する処理
@admin_bp.route("/audit-logs")
def audit_logs():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("role") != "admin":
        flash("権限がありません")
        return redirect(url_for("home"))

    db = get_db()

    user = db.execute(
        "SELECT can_view_audit_logs FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if user["can_view_audit_logs"] != 1:
        flash("監査ログを閲覧する権限がありません")
        return redirect(url_for("home"))

    form = AuditLogSearchForm(request.args, meta={"csrf": False})

    action = form.action.data or ""
    keyword = form.keyword.data or ""

    sql = """
        SELECT
            audit_logs.*,
            users.employee_id AS actor_employee_id
        FROM audit_logs
        LEFT JOIN users ON audit_logs.actor_user_id = users.id
        WHERE 1 = 1
    """

    params = []

    if action:
        sql += " AND audit_logs.action = ?"
        params.append(action)

    if keyword:
        sql += """
            AND (
                users.employee_id LIKE ?
                OR audit_logs.description LIKE ?
            )
        """
        like_keyword = f"%{keyword}%"
        params.extend([like_keyword, like_keyword])

    sql += " ORDER BY audit_logs.created_at DESC"

    logs = db.execute(sql, params).fetchall()

    return render_template("admin/audit_logs.html", logs=logs, form=form)
