from sqlalchemy.orm import Session
from src.domain.model.livro import Livro
from src.domain.ports.livro_repository import LivroRepositoryPort
from src.infrastructure.persistence.entities.livro_entity import LivroModel
from typing import Tuple

class LivroRepository(LivroRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def criar(self, livro: Livro) -> Livro:
        db_livro = LivroModel(titulo=livro.titulo, autor=livro.autor, disponivel=livro.disponivel)
        self.db.add(db_livro)
        self.db.flush()
        return Livro(db_livro.id, db_livro.titulo, db_livro.autor, db_livro.disponivel)

    def listar(self) -> list[Livro]:
        return [Livro(r.id, r.titulo, r.autor, r.disponivel) for r in self.db.query(LivroModel).all()]

    def listar_paginado(self, page: int, size: int) -> Tuple[list[Livro], int]:
        offset = (page - 1) * size
        total = self.db.query(LivroModel).count()
        livros = self.db.query(LivroModel).offset(offset).limit(size).all()
        result = [Livro(r.id, r.titulo, r.autor, r.disponivel) for r in livros]
        return result, total

    def buscar_por_id(self, livro_id: int) -> Livro | None:
        r = self.db.query(LivroModel).filter(LivroModel.id == livro_id).first()
        return Livro(r.id, r.titulo, r.autor, r.disponivel) if r else None

    def atualizar_disponibilidade(self, livro_id: int, disponivel: bool) -> Livro | None:
        db_livro = self.db.query(LivroModel).filter(LivroModel.id == livro_id).first()
        if not db_livro:
            return None
        db_livro.disponivel = disponivel
        self.db.flush()
        return Livro(db_livro.id, db_livro.titulo, db_livro.autor, db_livro.disponivel)
