import os
from uuid import UUID
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db import db
from migrations.models.book import Fabricante, Sorvete
from flask_migrate import Migrate


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL", "sqlite:///sorvetes.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    Migrate(app, db)
    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}, 200

    @app.get("/fabricantes")
    def list_fabricantes():
        fabricantes = Fabricante.query.order_by(Fabricante.nome).all()
        return jsonify([{"id": str(item.id), "nome": item.nome} for item in fabricantes])

    @app.post("/fabricantes")
    def create_fabricante():
        payload = request.get_json(silent=True)
        nome = payload.get("nome") if isinstance(payload, dict) else None
        if not isinstance(nome, str) or not nome.strip():
            return {"error": "Informe um nome de fabricante."}, 400

        fabricante = Fabricante(nome=nome.strip())
        db.session.add(fabricante)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"error": "Já existe um fabricante com esse nome."}, 409

        return jsonify({"id": str(fabricante.id), "nome": fabricante.nome}), 201

    @app.get("/sorvetes")
    def list_sorvetes():
        sorvetes = Sorvete.query.order_by(Sorvete.nome).all()
        return jsonify([serialize_sorvete(item) for item in sorvetes])

    @app.post("/sorvetes")
    def create_sorvete():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"error": "O corpo da requisição deve ser um objeto JSON."}, 400

        nome = payload.get("nome")
        sabor = payload.get("sabor")
        preco = payload.get("preco")
        fabricante_id = payload.get("fabricante_id")


        if not isinstance(nome, str) or not nome.strip():
            return {"error": "Informe o nome do sorvete."}, 400

        
        if not isinstance(sabor, str) or not sabor.strip():
            return {"error": "Informe o sabor do sorvete."}, 400

        
        if isinstance(preco, bool) or not isinstance(preco, int) or preco < 0:
            return {"error": "O preço deve ser um número inteiro não negativo."}, 400

        
        if not isinstance(fabricante_id, str):
            return {"error": "Informe um UUID válido em fabricante_id."}, 400

        
        try:
            parsed_fabricante_id = UUID(fabricante_id)
        except (TypeError, ValueError):
            return {"error": "Informe um UUID válido em fabricante_id."}, 400

        

        fabricante = db.session.get(Fabricante, parsed_fabricante_id)
        if fabricante is None:
            return {"error": "Fabricante não encontrado."}, 404

        sorvete = Sorvete(
            nome=nome.strip(),
            sabor=sabor.strip(),
            preco=preco,
            fabricante=fabricante,
        )
        db.session.add(sorvete)
        db.session.commit()
        return jsonify(serialize_sorvete(sorvete)), 201

    return app


def serialize_sorvete(sorvete: Sorvete) -> dict[str, str | int]:
    return {
        "id": str(sorvete.id),
        "nome": sorvete.nome,
        "sabor": sorvete.sabor,
        "preco": sorvete.preco,
        "fabricante_id": str(sorvete.fabricante_id),
        "fabricante": sorvete.fabricante.nome,
    }

