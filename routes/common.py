"""Validation, HTTP errors and serializers shared by route modules."""
from uuid import UUID

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
