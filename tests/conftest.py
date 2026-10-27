"""Shared authenticated test client for existing catalog regression tests."""
import pytest
from app import create_app
from db import db
from models.user import User


@pytest.fixture
def admin_client(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "only-for-tests",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'catalog.db'}",
    })
    with app.app_context():
        administrator = User(name="Administrador Teste", email="admin@example.test", role="admin")
        administrator.set_password("SenhaSegura12345")
        db.session.add(administrator)
        db.session.commit()

    with app.test_client() as client:
        token = client.get("/auth/session").get_json()["csrf_token"]
        login = client.post(
            "/auth/login", json={"email": "admin@example.test", "password": "SenhaSegura12345"},
            headers={"X-CSRF-Token": token},
        )
        assert login.status_code == 200
        client.environ_base["HTTP_X_CSRF_TOKEN"] = login.get_json()["csrf_token"]
        yield client

    with app.app_context():
        db.session.remove()
        db.drop_all()
