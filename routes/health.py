"""Health route."""
from flask import Blueprint
from sqlalchemy import text
from db import db

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    db.session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}, 200
