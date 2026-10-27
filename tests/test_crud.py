"""Integration tests for the full CRUD contract."""
import pytest

from app import create_app
from db import db


@pytest.fixture()
def client(admin_client):
    return admin_client


def test_manufacturer_crud(client):
    fid = manufacturer(client)
    assert client.get(f"/fabricantes/{fid}").get_json()["sorvetes"] == []
    change = client.patch(f"/fabricantes/{fid}", json={"nome": "Gelados Atualizado"})
    assert change.status_code == 200
    assert change.get_json()["nome"] == "Gelados Atualizado"
    assert client.delete(f"/fabricantes/{fid}").status_code == 204
    assert client.get(f"/fabricantes/{fid}").status_code == 404
    assert client.delete(f"/fabricantes/{fid}").status_code == 404


def test_manufacturer_duplicate_update(client):
    one = manufacturer(client, "Um")
    manufacturer(client, "Dois")
    response = client.patch(f"/fabricantes/{one}", json={"nome": "Dois"})
    assert response.status_code == 409
    assert client.get(f"/fabricantes/{one}").get_json()["nome"] == "Um"


def test_manufacturer_delete_linked_protected(client):
    fid = manufacturer(client)
    sid = icecream(client, fid)
    assert client.delete(f"/fabricantes/{fid}").status_code == 409
    detail = client.get(f"/fabricantes/{fid}").get_json()
    assert len(detail["sorvetes"]) == 1
    assert detail["sorvetes"][0]["id"] == sid
    assert client.delete(f"/sorvetes/{sid}").status_code == 204
    assert client.delete(f"/fabricantes/{fid}").status_code == 204


def test_icecream_crud_and_filters(client):
    first = manufacturer(client, "Primeiro")
    second = manufacturer(client, "Segundo")
    sid = icecream(client, first, nome="Picolé de Morango")
    icecream(client, second, nome="Casquinha", sabor="Baunilha", preco=9)
    assert len(client.get("/sorvetes").get_json()) == 2
    assert len(client.get("/sorvetes?q=pico").get_json()) == 1
    assert len(client.get("/sorvetes?sabor=Bauni").get_json()) == 1
    assert len(client.get(f"/sorvetes?fabricante_id={first}").get_json()) == 1
    response = client.patch(f"/sorvetes/{sid}", json={
        "nome": "Picolé Premium", "sabor": "Coco", "preco": 11, "fabricante_id": second,
    })
    assert response.status_code == 200
    assert response.get_json()["fabricante"] == "Segundo"
    assert response.get_json()["preco"] == 11
    assert client.get(f"/sorvetes/{sid}").get_json()["nome"] == "Picolé Premium"
    assert client.delete(f"/sorvetes/{sid}").status_code == 204
    assert client.get(f"/sorvetes/{sid}").status_code == 404


@pytest.mark.parametrize("path", ["/fabricantes", "/sorvetes"])
def test_invalid_resource_identifiers(client, path):
    assert client.get(f"{path}/invalid-uuid").status_code == 400
    assert client.patch(f"{path}/invalid-uuid", json={}).status_code == 400
    assert client.delete(f"{path}/invalid-uuid").status_code == 400


def test_invalid_patches_do_not_change_data(client):
    fid = manufacturer(client)
    sid = icecream(client, fid)
    assert client.patch(f"/fabricantes/{fid}", json={"nome": "   "}).status_code == 400
    assert client.patch(f"/fabricantes/{fid}", json={"random": "x"}).status_code == 400
    assert client.patch(f"/sorvetes/{sid}", json={"preco": 2.50}).status_code == 400
    assert client.patch(f"/sorvetes/{sid}", json={"preco": True}).status_code == 400
    assert client.patch(f"/sorvetes/{sid}", json={"fabricante_id": "not-uuid"}).status_code == 400
    assert client.patch(f"/sorvetes/{sid}", json={"unknown": 1}).status_code == 400
    assert client.get(f"/sorvetes/{sid}").get_json()["preco"] == 5


def test_invalid_query_uuid(client):
    response = client.get("/sorvetes?fabricante_id=INVALID")
    assert response.status_code == 400


def test_existing_endpoints_keep_shapes(client):
    fid = manufacturer(client)
    sid = icecream(client, fid)
    assert client.get("/fabricantes").get_json() == [{"id": fid, "nome": "Gelados da Serra"}]
    assert client.get("/sorvetes").get_json() == [{
        "id": sid, "nome": "Picolé", "sabor": "Morango", "preco": 5,
        "fabricante_id": fid, "fabricante": "Gelados da Serra",
    }]
