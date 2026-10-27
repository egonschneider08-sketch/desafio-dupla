from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db


class Fabricante(db.Model):
    __tablename__ = "fabricantes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    sorvetes: Mapped[list["Sorvete"]] = relationship(back_populates="fabricante")

    def dict(self):
        return {
            "id": str(self.id),
            "nome": self.nome,
            "sorvetes": [sorvete.as_dict() for sorvete in self.sorvetes],
        }


class Sorvete(db.Model):
    __tablename__ = "sorvetes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    sabor: Mapped[str] = mapped_column(String(100), nullable=False)
    preco: Mapped[int] = mapped_column(Integer, nullable=False)
    fabricante_id: Mapped[str] = mapped_column(String(36), ForeignKey("fabricantes.id"), nullable=False)
    fabricante: Mapped[Fabricante] = relationship(back_populates="sorvetes")

    def as_dict(self):
        return {
            "id": str(self.id),
            "nome": self.nome,
            "sabor": self.sabor,
            "preco": self.preco,
            "fabricante_id": str(self.fabricante_id),
        }

