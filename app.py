"""Sorvetes Flask application factory, sessions and role-based access control."""
import os
import secrets
from datetime import timedelta

import click
from dotenv import load_dotenv
from flask import Flask, request
from flask_migrate import Migrate

from db import db
from models.user import User
from routes.auth import bp as auth_bp, csrf_valid, current_user, normalize_email, valid_name, valid_password
from routes.fabricantes import bp as fabricantes_bp
from routes.sorvetes import bp as sorvetes_bp
from routes.health import bp as health_bp
from routes.common import serialize_sorvete  # Backward-compatible import


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    production = os.getenv("APP_ENV", "development").lower() == "production"
    secret = os.getenv("SECRET_KEY")
    if production and not secret:
        raise RuntimeError("Defina SECRET_KEY antes de iniciar em produção.")
    app.config.update(
        SECRET_KEY=secret or secrets.token_hex(32),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=production,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    )
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
        db.create_all()  # Adds the users table without modifying existing catalog tables.

    @app.before_request
    def enforce_permissions():
        if request.method in ("POST", "PATCH", "PUT", "DELETE") and not csrf_valid():
            return {"error": "Sessão de segurança inválida. Atualize a página."}, 403
        if request.blueprint in ("fabricantes", "sorvetes"):
            account = current_user()
            if account is None:
                return {"error": "Entre na sua conta para acessar o catálogo."}, 401
            if request.method not in ("GET", "HEAD", "OPTIONS") and account.role != "admin":
                return {"error": "Somente administradores podem modificar o catálogo."}, 403

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.cli.command("create-admin")
    @click.option("--email", prompt="E-mail do administrador")
    @click.option("--name", prompt="Nome do administrador")
    @click.password_option(confirmation_prompt=True)
    def create_admin(email: str, name: str, password: str):
        """Create the first administrator from the server; never from public registration."""
        normalized = normalize_email(email)
        if not normalized or not valid_name(name) or not valid_password(password):
            raise click.ClickException("Use e-mail válido, nome até 80 caracteres e senha de 12 a 128 caracteres.")
        if db.session.query(User).filter_by(email=normalized).first():
            raise click.ClickException("Já existe uma conta com esse e-mail; use outro e-mail para criar o administrador.")
        user = User(email=normalized, name=name.strip(), role="admin")
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise click.ClickException("Não foi possível criar o administrador.")
        click.echo("Conta administrativa criada com sucesso.")

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(fabricantes_bp)
    app.register_blueprint(sorvetes_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
