"""CRUD routes for manufacturers."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from db import db
from models.book import Fabricante
from .common import _uuid, _valid_name, _error, _serialize_fabricante

bp = Blueprint("fabricantes", __name__)

@bp.get("/fabricantes")
def list_fabricantes():
    items = Fabricante.query.order_by(Fabricante.nome).all()
    return jsonify([_serialize_fabricante(item) for item in items])

@bp.post("/fabricantes")
def create_fabricante():
    payload = request.get_json(silent=True)
    nome = payload.get("nome") if isinstance(payload, dict) else None
    if not _valid_name(nome):
        return _error("Informe um nome de fabricante válido (até 100 caracteres).")
    item = Fabricante(nome=nome.strip())
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Já existe um fabricante com esse nome.", 409)
    return jsonify(_serialize_fabricante(item)), 201

@bp.get("/fabricantes/<fabricante_id>")
def get_fabricante(fabricante_id):
    identifier = _uuid(fabricante_id)
    if identifier is None:
        return _error("ID de fabricante inválido.")
    item = db.session.get(Fabricante, identifier)
    if item is None:
        return _error("Fabricante não encontrado.", 404)
    return jsonify(item.dict())

@bp.patch("/fabricantes/<fabricante_id>")
def update_fabricante(fabricante_id):
    identifier = _uuid(fabricante_id)
    if identifier is None:
        return _error("ID de fabricante inválido.")
    item = db.session.get(Fabricante, identifier)
    if item is None:
        return _error("Fabricante não encontrado.", 404)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or set(payload) != {"nome"}:
        return _error("Informe somente o campo nome.")
    if not _valid_name(payload["nome"]):
        return _error("Informe um nome de fabricante válido (até 100 caracteres).")
    item.nome = payload["nome"].strip()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Já existe um fabricante com esse nome.", 409)
    return jsonify(_serialize_fabricante(item))

@bp.delete("/fabricantes/<fabricante_id>")
def delete_fabricante(fabricante_id):
    identifier = _uuid(fabricante_id)
    if identifier is None:
        return _error("ID de fabricante inválido.")
    item = db.session.get(Fabricante, identifier)
    if item is None:
        return _error("Fabricante não encontrado.", 404)
    if item.sorvetes:
        return _error("Remova os sorvetes vinculados antes de excluir o fabricante.", 409)
    db.session.delete(item)
    db.session.commit()
    return "", 204
