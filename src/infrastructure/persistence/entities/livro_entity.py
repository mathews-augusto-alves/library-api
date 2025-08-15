from sqlalchemy import Column, Integer, String, Boolean
from src.infrastructure.config.db.database import Base

class LivroModel(Base):
    __tablename__ = "livros"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    disponivel = Column(Boolean, nullable=False, default=True)