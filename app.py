"""API HTTP do catálogo Sorvetes.

Os endpoints originais permanecem compatíveis. CRUD adicional usa identificadores
UUID e mantém tratamento explícito de erros previsíveis.
"""
import os
from uuid import UUID

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db import db
from models.book import Fabricante, Sorvete


def _uuid(value):
    if not isinstance(value, str):
        return None
    try:
        return str(UUID(value))
    except (TypeError, ValueError):
        return None


def _valid_name(value):
    return isinstance(value, str) and 0 < len(value.strip()) <= 100


def _valid_price(value):
    return type(value) is int and 0 <= value <= 2_147_483_647


def _error(message, code=400):
    return {"error": message}, code


def _serialize_fabricante(item):
    return {"id": str(item.id), "nome": item.nome}


def serialize_sorvete(item):
    return {
        "id": str(item.id),
        "nome": item.nome,
        "sabor": item.sabor,
        "preco": item.preco,
        "fabricante_id": str(item.fabricante_id),
        "fabricante": item.fabricante.nome,
    }


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

    @app.get("/health")
    def health():
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}, 200

    @app.get("/fabricantes")
    def list_fabricantes():
        items = Fabricante.query.order_by(Fabricante.nome).all()
        return jsonify([_serialize_fabricante(item) for item in items])

    @app.post("/fabricantes")
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

    @app.get("/fabricantes/<fabricante_id>")
    def get_fabricante(fabricante_id):
        identifier = _uuid(fabricante_id)
        if identifier is None:
            return _error("ID de fabricante inválido.")
        item = db.session.get(Fabricante, identifier)
        if item is None:
            return _error("Fabricante não encontrado.", 404)
        return jsonify(item.dict())

    @app.patch("/fabricantes/<fabricante_id>")
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

    @app.delete("/fabricantes/<fabricante_id>")
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

    @app.get("/sorvetes")
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

    @app.post("/sorvetes")
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

    @app.get("/sorvetes/<sorvete_id>")
    def get_sorvete(sorvete_id):
        identifier = _uuid(sorvete_id)
        if identifier is None:
            return _error("ID de sorvete inválido.")
        item = db.session.get(Sorvete, identifier)
        if item is None:
            return _error("Sorvete não encontrado.", 404)
        return jsonify(serialize_sorvete(item))

    @app.patch("/sorvetes/<sorvete_id>")
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

    @app.delete("/sorvetes/<sorvete_id>")
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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
