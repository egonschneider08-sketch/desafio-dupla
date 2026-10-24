import unittest

from app import create_app
from db import db
from migrations.models.book import Fabricante, Sorvete


class SorvetesApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            }
        )
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        db.session.query(Sorvete).delete()
        db.session.query(Fabricante).delete()
        db.session.commit()

    def test_health_checks_database_connection(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["database"], "connected")

    def test_create_and_list_fabricante_and_sorvete(self):
        fabricante_response = self.client.post(
            "/fabricantes", json={"nome": "Gelados da Serra"}
        )
        fabricante_id = fabricante_response.json["id"]

        sorvete_response = self.client.post(
            "/sorvetes",
            json={
                "nome": "Picolé",
                "sabor": "Morango",
                "preco": 5,
                "fabricante_id": fabricante_id,
            },
        )

        self.assertEqual(fabricante_response.status_code, 201)
        self.assertEqual(sorvete_response.status_code, 201)
        self.assertEqual(sorvete_response.json["fabricante"], "Gelados da Serra")
        self.assertEqual(self.client.get("/sorvetes").json[0]["sabor"], "Morango")

    def test_rejects_invalid_sorvete_payload(self):
        response = self.client.post(
            "/sorvetes",
            json={
                "nome": "Picolé",
                "sabor": "Morango",
                "preco": -1,
                "fabricante_id": "not-a-uuid",
            },
        )

        self.assertEqual(response.status_code, 400)
