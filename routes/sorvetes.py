"""CRUD and filtering routes for ice creams."""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from db import db
from models.book import Fabricante, Sorvete
from .common import _uuid, _valid_name, _valid_price, _error, serialize_sorvete

bp = Blueprint("sorvetes", __name__)

@bp.get("/sorvetes")
def list_sorvetes():
    query = Sorvete.query
    term = request.args.get("q", "").strip()
    sabor = request.args.get("sabor", "").strip()
    fabricante_id = request.args.get("fabricante_id", "").strip()
    if term:
        query = query.filter(Sorvete.nome.ilike(f"%{term}%"))
    if sabor:
        query = query.filter(Sorvete.sabor.ilike(f"%{sabor}%"))
    if fabricante_id:
        identifier = _uuid(fabricante_id)
        if identifier is None:
            return _error("ID de fabricante inválido.")
        query = query.filter_by(fabricante_id=identifier)
    return jsonify([serialize_sorvete(item) for item in query.order_by(Sorvete.nome).all()])

@bp.post("/sorvetes")
def create_sorvete():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("O corpo da requisição deve ser um objeto JSON.")
    if not _valid_name(payload.get("nome")):
        return _error("Informe o nome do sorvete (até 100 caracteres).")
    if not _valid_name(payload.get("sabor")):
        return _error("Informe o sabor do sorvete (até 100 caracteres).")
    if not _valid_price(payload.get("preco")):
        return _error("O preço deve ser um número inteiro não negativo.")
    identifier = _uuid(payload.get("fabricante_id"))
    if identifier is None:
        return _error("Informe um UUID válido em fabricante_id.")
    fabricante = db.session.get(Fabricante, identifier)
    if fabricante is None:
        return _error("Fabricante não encontrado.", 404)
    item = Sorvete(
        nome=payload["nome"].strip(),
        sabor=payload["sabor"].strip(),
        preco=payload["preco"],
        fabricante=fabricante,
    )
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Não foi possível cadastrar o sorvete.", 409)
    return jsonify(serialize_sorvete(item)), 201

@bp.get("/sorvetes/<sorvete_id>")
def get_sorvete(sorvete_id):
    identifier = _uuid(sorvete_id)
    if identifier is None:
        return _error("ID de sorvete inválido.")
    item = db.session.get(Sorvete, identifier)
    if item is None:
        return _error("Sorvete não encontrado.", 404)
    return jsonify(serialize_sorvete(item))

@bp.patch("/sorvetes/<sorvete_id>")
def update_sorvete(sorvete_id):
    identifier = _uuid(sorvete_id)
    if identifier is None:
        return _error("ID de sorvete inválido.")
    item = db.session.get(Sorvete, identifier)
    if item is None:
        return _error("Sorvete não encontrado.", 404)
    payload = request.get_json(silent=True)
    allowed = {"nome", "sabor", "preco", "fabricante_id"}
    if not isinstance(payload, dict) or not payload or set(payload) - allowed:
        return _error("Informe campos válidos para atualizar o sorvete.")
    for key in ("nome", "sabor"):
        if key in payload:
            if not _valid_name(payload[key]):
                return _error(f"Informe {key} válido (até 100 caracteres).")
            setattr(item, key, payload[key].strip())
    if "preco" in payload:
        if not _valid_price(payload["preco"]):
            return _error("O preço deve ser um número inteiro não negativo.")
        item.preco = payload["preco"]
    if "fabricante_id" in payload:
        fk = _uuid(payload["fabricante_id"])
        if fk is None:
            return _error("Informe um UUID válido em fabricante_id.")
        fabricante = db.session.get(Fabricante, fk)
        if fabricante is None:
            return _error("Fabricante não encontrado.", 404)
        item.fabricante = fabricante
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _error("Não foi possível atualizar o sorvete.", 409)
    return jsonify(serialize_sorvete(item))

@bp.delete("/sorvetes/<sorvete_id>")
def delete_sorvete(sorvete_id):
    identifier = _uuid(sorvete_id)
    if identifier is None:
        return _error("ID de sorvete inválido.")
    item = db.session.get(Sorvete, identifier)
    if item is None:
        return _error("Sorvete não encontrado.", 404)
    db.session.delete(item)
    db.session.commit()
    return "", 204
