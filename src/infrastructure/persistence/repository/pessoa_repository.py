from sqlalchemy.orm import Session
from src.domain.model.pessoa import Pessoa
from src.infrastructure.persistence.entities.pessoa_entity import PessoaModel
from typing import Tuple

class PessoaRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, pessoa: Pessoa) -> Pessoa:
        db_pessoa = PessoaModel(
            nome=pessoa.nome,
            telefone=pessoa.telefone,
            data_nascimento=pessoa.data_nascimento,
            email=pessoa.email
        )
        self.db.add(db_pessoa)
        self.db.flush()
        return Pessoa(db_pessoa.id, db_pessoa.nome, db_pessoa.telefone, db_pessoa.data_nascimento, db_pessoa.email)

    def listar(self) -> list[Pessoa]:
        pessoas = self.db.query(PessoaModel).all()
        return [Pessoa(p.id, p.nome, p.telefone, p.data_nascimento, p.email) for p in pessoas]

    def listar_paginado(self, page: int, size: int) -> Tuple[list[Pessoa], int]:
        offset = (page - 1) * size
        total = self.db.query(PessoaModel).count()
        pessoas = self.db.query(PessoaModel).offset(offset).limit(size).all()
        result = [Pessoa(p.id, p.nome, p.telefone, p.data_nascimento, p.email) for p in pessoas]
        return result, total

    def buscar_por_id(self, pessoa_id: int) -> Pessoa | None:
        p = self.db.query(PessoaModel).filter(PessoaModel.id == pessoa_id).first()
        return Pessoa(p.id, p.nome, p.telefone, p.data_nascimento, p.email) if p else None

    def buscar_por_email(self, email: str) -> Pessoa | None:
        p = self.db.query(PessoaModel).filter(PessoaModel.email == email).first()
        return Pessoa(p.id, p.nome, p.telefone, p.data_nascimento, p.email) if p else None

    def email_existe(self, email: str) -> bool:
        return self.db.query(PessoaModel).filter(PessoaModel.email == email).first() is not None

    def atualizar(self, pessoa_id: int, pessoa: Pessoa) -> Pessoa | None:
        db_pessoa = self.db.query(PessoaModel).filter(PessoaModel.id == pessoa_id).first()
        if db_pessoa:
            db_pessoa.nome = pessoa.nome
            db_pessoa.telefone = pessoa.telefone
            db_pessoa.data_nascimento = pessoa.data_nascimento
            db_pessoa.email = pessoa.email
            self.db.flush()
            return Pessoa(db_pessoa.id, db_pessoa.nome, db_pessoa.telefone, db_pessoa.data_nascimento, db_pessoa.email)
        return None

    def remover(self, pessoa_id: int) -> bool:
        db_pessoa = self.db.query(PessoaModel).filter(PessoaModel.id == pessoa_id).first()
        if db_pessoa:
            self.db.delete(db_pessoa)
            self.db.flush()
            return True
        return False
