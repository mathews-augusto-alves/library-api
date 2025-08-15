from sqlalchemy.orm import Session
from src.domain.model.usuario import Usuario
from src.infrastructure.persistence.entities.usuario_entity import UsuarioModel
from typing import Tuple

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, usuario: Usuario) -> Usuario:
        db_usuario = UsuarioModel(
            nome=usuario.nome,
            email=usuario.email,
            senha_hash=usuario.senha_hash,
        )
        self.db.add(db_usuario)
        self.db.flush()
        return Usuario(db_usuario.id, db_usuario.nome, db_usuario.email, db_usuario.senha_hash)

    def atualizar(self, usuario_id: int, usuario: Usuario) -> Usuario | None:
        db_usuario = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if not db_usuario:
            return None
        db_usuario.nome = usuario.nome
        db_usuario.email = usuario.email
        db_usuario.senha_hash = usuario.senha_hash
        self.db.flush()
        return Usuario(db_usuario.id, db_usuario.nome, db_usuario.email, db_usuario.senha_hash)

    def remover(self, usuario_id: int) -> bool:
        db_usuario = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        if not db_usuario:
            return False
        self.db.delete(db_usuario)
        self.db.flush()
        return True

    def listar(self) -> list[Usuario]:
        registros = self.db.query(UsuarioModel).all()
        return [Usuario(r.id, r.nome, r.email, r.senha_hash) for r in registros]

    def listar_paginado(self, page: int, size: int) -> Tuple[list[Usuario], int]:
        offset = (page - 1) * size
        total = self.db.query(UsuarioModel).count()
        usuarios = self.db.query(UsuarioModel).offset(offset).limit(size).all()
        result = [Usuario(r.id, r.nome, r.email, r.senha_hash) for r in usuarios]
        
        return result, total

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        r = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
        return Usuario(r.id, r.nome, r.email, r.senha_hash) if r else None

    def buscar_por_email(self, email: str) -> Usuario | None:
        r = self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        return Usuario(r.id, r.nome, r.email, r.senha_hash) if r else None 