from sqlalchemy import Column, Integer, DateTime, ForeignKey
from src.infrastructure.config.db.database import Base

class EmprestimoModel(Base):
    __tablename__ = "emprestimos"
    id = Column(Integer, primary_key=True, index=True)
    livro_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    pessoa_id = Column(Integer, ForeignKey("pessoas.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_emprestimo = Column(DateTime, nullable=False)
    data_devolucao = Column(DateTime, nullable=True)