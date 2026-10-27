"""Security and functionality of viewer/admin sessions."""
from uuid import UUID

import pytest
from werkzeug.security import check_password_hash

from app import create_app
from db import db
from models.user import User


@pytest.fixture
def client(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "auth-test-secret",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'auth.db'}",
    })
    with app.test_client() as web:
        yield web
    with app.app_context():
        db.session.remove()
        db.drop_all()


def csrf(client):
    response = client.get("/auth/session")
    assert response.status_code == 200
    return response.get_json()["csrf_token"]


def register(client, email="cliente@example.test", password="MinhaSenhaLonga123", **extra):
    payload = {"name": "Cliente Teste", "email": email, "password": password}
    payload.update(extra)
    return client.post("/auth/register", json=payload, headers={"X-CSRF-Token": csrf(client)})


def login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password},
                       headers={"X-CSRF-Token": csrf(client)})


def test_health_is_public_catalog_requires_account(client):
    assert client.get("/health").status_code == 200
    assert client.get("/fabricantes").status_code == 401
    assert client.get("/sorvetes").status_code == 401
    assert client.get("/sorvetes/invalid").status_code == 401


def test_register_viewer_and_password_is_hashed(client):
    response = register(client, email="  CLIENTE@EXAMPLE.TEST ")
    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["role"] == "viewer"
    assert body["user"]["email"] == "cliente@example.test"
    assert body["user"]["name"] == "Cliente Teste"
    UUID(body["user"]["id"])
    assert "password" not in str(body).lower()
    assert client.get("/auth/session").get_json()["user"]["role"] == "viewer"
    assert client.get("/fabricantes").status_code == 200
    assert client.get("/sorvetes").status_code == 200
    with client.application.app_context():
        account = db.session.query(User).filter_by(email="cliente@example.test").one()
        assert account.password_hash != "MinhaSenhaLonga123"
        assert check_password_hash(account.password_hash, "MinhaSenhaLonga123")


def test_viewer_cannot_mutate_even_with_valid_csrf(client):
    response = register(client)
    assert response.status_code == 201
    csrf_token = response.get_json()["csrf_token"]
    headers = {"X-CSRF-Token": csrf_token}
    assert client.post("/fabricantes", json={"nome": "Bloqueado"}, headers=headers).status_code == 403
    assert client.patch("/fabricantes/abc", json={"nome": "Bloqueado"}, headers=headers).status_code == 403
    assert client.delete("/sorvetes/abc", headers=headers).status_code == 403
    assert client.get("/fabricantes").get_json() == []


def test_public_registration_never_creates_admin(client):
    forbidden = register(client, role="admin")
    assert forbidden.status_code == 400
    assert client.get("/auth/session").get_json()["user"] is None
    normal = register(client, email="outro@example.test")
    assert normal.status_code == 201
    assert normal.get_json()["user"]["role"] == "viewer"


def test_login_and_logout_rotate_csrf(client):
    initial = csrf(client)
    registered = register(client)
    token = registered.get_json()["csrf_token"]
    assert token != initial
    assert client.post("/auth/logout").status_code == 403  # Missing CSRF
    out = client.post("/auth/logout", headers={"X-CSRF-Token": token})
    assert out.status_code == 200
    assert out.get_json()["user"] is None
    assert out.get_json()["csrf_token"] != token
    assert client.get("/sorvetes").status_code == 401
    logged = login(client, "cliente@example.test", "MinhaSenhaLonga123")
    assert logged.status_code == 200
    assert logged.get_json()["user"]["role"] == "viewer"


def test_bad_credentials_duplicate_email_and_short_password(client):
    assert register(client, password="curta").status_code == 400
    assert register(client).status_code == 201
    assert register(client, email="CLIENTE@example.test").status_code == 409
    assert login(client, "cliente@example.test", "senha-errada").status_code == 401
    assert login(client, "naoexiste@example.test", "MinhaSenhaLonga123").status_code == 401


def test_csrf_required_on_all_mutating_requests(client):
    assert client.post("/auth/register", json={
        "name": "Teste", "email": "test@example.test", "password": "SenhaSegura12345"
    }).status_code == 403
    token = csrf(client)
    assert client.post("/auth/register", json={
        "name": "Teste", "email": "test@example.test", "password": "SenhaSegura12345"
    }, headers={"X-CSRF-Token": "invalido"}).status_code == 403
    assert client.post("/auth/register", json={
        "name": "Teste", "email": "test@example.test", "password": "SenhaSegura12345"
    }, headers={"X-CSRF-Token": token}).status_code == 201
    assert client.post("/fabricantes", json={"nome": "Tentativa"},
                       headers={"X-CSRF-Token": token}).status_code == 403  # Rotated token


def test_admin_cli_can_create_and_edit_catalog(client):
    runner = client.application.test_cli_runner()
    result = runner.invoke(args=["create-admin", "--email", "admin@example.test", "--name", "Admin"], input="SenhaMuitoLonga123\nSenhaMuitoLonga123\n")
    assert result.exit_code == 0, result.output
    duplicate = runner.invoke(args=["create-admin", "--email", "admin@example.test", "--name", "Admin"], input="SenhaMuitoLonga123\nSenhaMuitoLonga123\n")
    assert duplicate.exit_code != 0
    signed = login(client, "admin@example.test", "SenhaMuitoLonga123")
    assert signed.status_code == 200
    headers = {"X-CSRF-Token": signed.get_json()["csrf_token"]}
    created = client.post("/fabricantes", json={"nome": "Sorveteria Central"}, headers=headers)
    assert created.status_code == 201
    assert client.get("/fabricantes").get_json()[0]["nome"] == "Sorveteria Central"
    assert client.delete(f"/fabricantes/{created.get_json()['id']}", headers=headers).status_code == 204


@pytest.mark.parametrize("field,value", [
    ("name", ""), ("name", "X" * 81), ("email", "not-an-email"),
    ("password", "short"), ("password", "x" * 129),
])
def test_invalid_registration_fields(client, field, value):
    payload = {"name": "Normal", "email": "valid@example.test", "password": "SenhaMuitoLonga123"}
    payload[field] = value
    response = client.post("/auth/register", json=payload, headers={"X-CSRF-Token": csrf(client)})
    assert response.status_code == 400


def test_session_cookie_security_settings(client):
    config = client.application.config
    assert config["SESSION_COOKIE_HTTPONLY"] is True
    assert config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert "SECRET_KEY" in config

def test_production_requires_persistent_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app()


def test_production_uses_secure_session_cookie(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "fixture-persistent-secret-not-for-real-use")
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'secure.db'}",
    })
    assert app.config["SESSION_COOKIE_SECURE"] is True
    with app.app_context():
        db.session.remove()
        db.drop_all()
