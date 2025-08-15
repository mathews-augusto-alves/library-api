from sqlalchemy import Column, Integer, String, Date
from src.infrastructure.config.db.database import Base

class PessoaModel(Base):
    __tablename__ = "pessoas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String, nullable=True, unique=True, index=True) 
