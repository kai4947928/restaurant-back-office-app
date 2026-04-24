from flask import Flask
import os

from .db import close_db, init_db

def create_app():
    app = Flask(__name__)

    app.config["DATABASE"] = os.path.join(
        app.instance_path,
        "app.db"
    )

    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        init_db()

    app.teardown_appcontext(close_db)

    @app.route("/")
    def home():
        return "App is running"

    return app