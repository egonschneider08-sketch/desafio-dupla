"""Session-based authentication. Public registration only creates viewer accounts."""
import re
import secrets

from flask import Blueprint, g, jsonify, request, session
from sqlalchemy.exc import IntegrityError

from db import db
from models.user import User

bp = Blueprint("auth", __name__)

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PASSWORD_MIN = 12
PASSWORD_MAX = 128


def normalize_email(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    email = value.strip().lower()
    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        return None
    return email


def valid_name(value: object) -> bool:
    return isinstance(value, str) and 1 <= len(value.strip()) <= 80


def valid_password(value: object) -> bool:
    return isinstance(value, str) and PASSWORD_MIN <= len(value) <= PASSWORD_MAX


def csrf_token() -> str:
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def csrf_valid() -> bool:
    supplied = request.headers.get("X-CSRF-Token", "")
    expected = session.get("csrf_token")
    return bool(expected and supplied and secrets.compare_digest(supplied, expected))


def current_user() -> User | None:
    if hasattr(g, "_current_user"):
        return g._current_user
    user_id = session.get("user_id")
    user = db.session.get(User, user_id) if isinstance(user_id, str) else None
    if user_id and user is None:
        session.clear()
    g._current_user = user
    return user


def _start_session(user: User) -> dict:
    session.clear()  # Rotate the authenticated session and CSRF token.
    session.permanent = True
    session["user_id"] = user.id
    return {"user": user.as_dict(), "csrf_token": csrf_token()}


@bp.get("/auth/session")
def status():
    response = jsonify({"user": current_user().as_dict() if current_user() else None,
                        "csrf_token": csrf_token()})
    response.headers["Cache-Control"] = "no-store"
    return response


@bp.post("/auth/register")
def register():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) != {"name", "email", "password"}:
        return {"error": "Informe nome, e-mail e senha, sem campos adicionais."}, 400
    name = payload["name"]
    email = normalize_email(payload["email"])
    password = payload["password"]
    if not valid_name(name):
        return {"error": "Informe um nome entre 1 e 80 caracteres."}, 400
    if email is None:
        return {"error": "Informe um e-mail válido."}, 400
    if not valid_password(password):
        return {"error": "A senha deve ter entre 12 e 128 caracteres."}, 400
    account = User(name=name.strip(), email=email, role="viewer")
    account.set_password(password)
    db.session.add(account)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Este e-mail já está cadastrado."}, 409
    return _start_session(account), 201


@bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) != {"email", "password"}:
        return {"error": "Informe e-mail e senha."}, 400
    email = normalize_email(payload.get("email"))
    password = payload.get("password")
    if email is None or not isinstance(password, str):
        return {"error": "E-mail ou senha inválidos."}, 401
    account = db.session.query(User).filter_by(email=email).first()
    if account is None or not account.check_password(password):
        return {"error": "E-mail ou senha inválidos."}, 401
    return _start_session(account)


@bp.post("/auth/logout")
def logout():
    session.clear()
    return {"user": None, "csrf_token": csrf_token()}
