import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_migrate import Migrate
from sqlalchemy import Text

from db import db
from models.book import Sorvete


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

    @app.get("/health")
    def health() -> tuple[dict[str, str], int]:
        db.session.execute(Text("SELECT 1"))
        return {"status": "ok", "database": "connected"}, 200

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

        if not isinstance(nome, str) or not nome.strip():
            return {"error": "Informe o nome do sorvete."}, 400

        if not isinstance(sabor, str) or not sabor.strip():
            return {"error": "Informe o sabor do sorvete."}, 400

        if isinstance(preco, bool) or not isinstance(preco, int) or preco < 0:
            return {"error": "O preço deve ser um número inteiro não negativo."}, 400

        sorvete = Sorvete(
            nome=nome.strip(),
            sabor=sabor.strip(),
            preco=preco
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
        "preco": sorvete.preco
    }