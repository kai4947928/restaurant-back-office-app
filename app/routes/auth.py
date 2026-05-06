from flask import Blueprint, render_template, request, redirect, url_for,  flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app.forms import LoginForm, ChangePasswordForm
from app.db import get_db

auth_bp = Blueprint("auth", __name__)

#ログイン処理(社員番号とパスワード)
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        employee_id = form.employee_id.data
        password = form.password.data

        db = get_db()

        user = db.execute(
            """
            SELECT id, employee_id, password_hash, role, is_active, must_change_password
            FROM users
            WHERE employee_id = ?
            """,
            (employee_id,)
        ).fetchone()

        #アカウントの有無と無効化されているのか確認
        if user is None or user["is_active"] == 0:
            flash("社員番号またはパスワードが違います。")
            return redirect(url_for("auth.login"))

        #パスワード設定の確認
        if user["password_hash"] is None:
            flash("パスワードが未設定です。")
            return redirect(url_for("auth.login"))

        #入力パスワードとDBのパスワードハッシュが一致するか確認
        if not check_password_hash(user["password_hash"], password):
            flash("社員番号またはパスワードが違います。")
            return redirect(url_for("auth.login"))

        #セッション管理
        session.clear()
        session["user_id"] = user["id"]
        session["employee_id"] = user["employee_id"]
        session["role"] = user["role"]

        #初回ログイン時にパスワード再設定画面へ遷移する
        if user["must_change_password"] == 1:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("auth.change_password"))

        return redirect(url_for("home"))

    return render_template("login.html", form=form, hide_nav=True)

#パスワード再設定・変更処理
@auth_bp.route("/change-password", methods=["GET", "POST"])
def change_password():

    #ログインしてない場合、ログインしてください
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    form = ChangePasswordForm()

    if form.validate_on_submit():
        new_password = form.new_password.data
        now = datetime.now().isoformat()

        db = get_db()

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

    return render_template("change_password.html", form=form, hide_nav=True)

#ログアウト処理
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
