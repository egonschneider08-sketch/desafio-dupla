from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from db import db

class sorvete(db.sorvete):
    __tablename__ = "sorvetes"

    id = Column(UUID(as_uuid=True),
                primary_key=True,
                default=uuid4)
    nome = Column(String(100), 
                  nullable=False)
    sabor = Column(String(100), 
                   nullable=False)
    preco = Column(Integer, 
                   nullable=False)
    fabricante_id = Column(String(36), 
                           ForeignKey("fabricantes.id"), 
                           nullable=False)

    fabricante = relationship("Fabricante", 
                              back_populates="sorvetes")
    
