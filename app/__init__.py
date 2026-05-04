from flask import Flask, render_template, session, redirect, url_for
import os

from .db import close_db, init_db, seed_user
from .routes.auth import auth_bp
from .routes.admin import admin_bp

def create_app():
    app = Flask(__name__, template_folder="../templates")

    app.config["DATABASE"] = os.path.join(
        app.instance_path,
        "app.db"
    )

    app.config["SECRET_KEY"] = "dev"

    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        init_db()
        seed_user()

    app.teardown_appcontext(close_db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))

        return render_template("home.html")
    return app