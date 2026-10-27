from uuid import UUID, uuid4
from sqlalchemy import Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db import db


class Sorvete(db.Model):
    __tablename__ = "sorvetes"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    sabor: Mapped[str] = mapped_column(String(100), nullable=False)
    preco: Mapped[int] = mapped_column(Integer, nullable=False)

    def as_dict(self):
        return {
            "id": str(self.id),
            "nome": self.nome,
            "sabor": self.sabor,
            "preco": self.preco,
        }