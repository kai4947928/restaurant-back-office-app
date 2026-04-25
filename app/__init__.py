from flask import Flask
from .db import seed_user
import os

from .db import close_db, init_db, seed_user
from .routes.auth import auth_bp

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

    @app.route("/")
    def home():
        return "App is running"

    return app