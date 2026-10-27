"""Regression tests for manufacturer nested serialization.

These tests use an isolated SQLite file so the project's local database
is never modified.
"""
from uuid import UUID

import pytest

from app import create_app
from db import db
from models.book import Fabricante, Sorvete


@pytest.fixture()
def app(tmp_path):
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'model-tests.db'}",
    })
    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


def test_fabricante_dict_without_sorvetes(app):
    with app.app_context():
        fabricante = Fabricante(nome="Gelados da Serra")
        db.session.add(fabricante)
        db.session.commit()

        result = fabricante.dict()

        assert result == {
            "id": str(fabricante.id),
            "nome": "Gelados da Serra",
            "sorvetes": [],
        }
        UUID(result["id"])


def test_fabricante_dict_with_related_sorvetes(app):
    with app.app_context():
        fabricante = Fabricante(nome="Gelados da Serra")
        sorvetes = [
            Sorvete(nome="Picolé", sabor="Morango", preco=5, fabricante=fabricante),
            Sorvete(nome="Casquinha", sabor="Baunilha", preco=8, fabricante=fabricante),
        ]
        db.session.add_all([fabricante, *sorvetes])
        db.session.commit()

        result = fabricante.dict()

        assert result["id"] == str(fabricante.id)
        assert result["nome"] == "Gelados da Serra"
        assert sorted(result["sorvetes"], key=lambda item: item["nome"]) == sorted(
            [sorvete.as_dict() for sorvete in sorvetes],
            key=lambda item: item["nome"],
        )
        assert all(item["fabricante_id"] == fabricante.id for item in result["sorvetes"])
