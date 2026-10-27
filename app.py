"""Flask application factory for the Sorvetes catalog."""
import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

from db import db
from routes.fabricantes import bp as fabricantes_bp
from routes.sorvetes import bp as sorvetes_bp
from routes.health import bp as health_bp
from routes.common import serialize_sorvete  # Backward-compatible import


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    instance_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance")
    os.makedirs(instance_dir, exist_ok=True)
    default_url = f"sqlite:///{os.path.join(instance_dir, 'sorvetes.db')}"
    database_url = os.getenv("DATABASE_URL", "").strip() or default_url

    if not database_url.startswith(("sqlite://", "postgresql://", "postgresql+psycopg://")):
        raise ValueError("DATABASE_URL deve usar SQLite ou PostgreSQL.")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    Migrate(app, db)
    with app.app_context():
        db.create_all()

    app.register_blueprint(health_bp)
    app.register_blueprint(fabricantes_bp)
    app.register_blueprint(sorvetes_bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
