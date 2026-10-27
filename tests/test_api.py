"""Regression tests for the current public HTTP contract."""
from uuid import UUID

import pytest

from app import create_app
from db import db


@pytest.fixture()
def client(admin_client):
    return admin_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "connected"}


def test_initial_collections_are_empty(client):
    assert client.get("/fabricantes").get_json() == []
    assert client.get("/sorvetes").get_json() == []


def test_create_fabricante_and_prevent_duplicate(client):
    response = client.post("/fabricantes", json={"nome": " Gelados da Serra "})
    assert response.status_code == 201
    data = response.get_json()
    UUID(data["id"])
    assert data["nome"] == "Gelados da Serra"
    assert client.post("/fabricantes", json={"nome": "Gelados da Serra"}).status_code == 409


@pytest.mark.parametrize("payload", [{}, {"nome": ""}, {"nome": 2}, []])
def test_invalid_fabricante(client, payload):
    assert client.post("/fabricantes", json=payload).status_code == 400


def test_create_sorvete_and_list(client):
    fabricante_id = client.post("/fabricantes", json={"nome": "Fábrica A"}).get_json()["id"]
    response = client.post("/sorvetes", json={
        "nome": "Picolé", "sabor": "Morango", "preco": 5,
        "fabricante_id": fabricante_id
    })
    assert response.status_code == 201
    data = response.get_json()
    UUID(data["id"])
    assert data["fabricante"] == "Fábrica A"
    assert data["fabricante_id"] == fabricante_id
    assert client.get("/sorvetes").get_json() == [data]


@pytest.mark.parametrize("price", [-1, 2.5, True, "5", None])
def test_invalid_price(client, price):
    fabricante_id = client.post("/fabricantes", json={"nome": "Fábrica B"}).get_json()["id"]
    response = client.post("/sorvetes", json={
        "nome": "Picolé", "sabor": "Limão", "preco": price,
        "fabricante_id": fabricante_id
    })
    assert response.status_code == 400


def test_unknown_fabricante(client):
    response = client.post("/sorvetes", json={
        "nome": "Picolé", "sabor": "Limão", "preco": 5,
        "fabricante_id": "550e8400-e29b-41d4-a716-446655440000"
    })
    assert response.status_code == 404


def test_malformed_fabricante_uuid(client):
    response = client.post("/sorvetes", json={
        "nome": "Picolé", "sabor": "Limão", "preco": 5,
        "fabricante_id": "uuid-invalido"
    })
    assert response.status_code == 400
