from src.domain.model.usuario import Usuario
from src.domain.exceptions import DadosInvalidosException, EmailJaExisteException, PessoaNaoEncontradaException
from src.application.service.usuario.usuario_service import UsuarioService
from src.infrastructure.config.security.auth import create_access_token, verify_password, get_password_hash
import re
from typing import Tuple

class UsuarioUseCase:
    def __init__(self, service: UsuarioService):
        self.service = service

    def _validar_email(self, email: str) -> None:
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise DadosInvalidosException("email", email)

    def _validar_nome(self, nome: str) -> None:
        if not nome or len(nome.strip()) < 2:
            raise DadosInvalidosException("nome", nome)

    def _validar_senha(self, senha: str) -> None:
        if not senha or len(senha) < 6:
            raise DadosInvalidosException("senha", "<oculta>")

    def cadastrar(self, nome: str, email: str, senha: str) -> Usuario:
        self._validar_nome(nome)
        self._validar_email(email)
        self._validar_senha(senha)
        if self.service.buscar_por_email(email):
            raise EmailJaExisteException(email)
        senha_hash = get_password_hash(senha)
        return self.service.criar(Usuario(None, nome, email, senha_hash))

    def atualizar(self, usuario_id: int, nome: str, email: str, senha: str) -> Usuario | None:
        self._validar_nome(nome)
        self._validar_email(email)
        self._validar_senha(senha)
        existente = self.service.buscar_por_id(usuario_id)
        if not existente:
            raise PessoaNaoEncontradaException(usuario_id)
        outro = self.service.buscar_por_email(email)
        if outro and outro.id != usuario_id:
            raise EmailJaExisteException(email)
        senha_hash = get_password_hash(senha)
        return self.service.atualizar(usuario_id, Usuario(None, nome, email, senha_hash))

    def remover(self, usuario_id: int) -> bool:
        existente = self.service.buscar_por_id(usuario_id)
        if not existente:
            raise PessoaNaoEncontradaException(usuario_id)
        return self.service.remover(usuario_id)

    def listar(self) -> list[Usuario]:
        return self.service.listar()

    def listar_paginado(self, page: int, size: int) -> Tuple[list[Usuario], int]:
        return self.service.listar_paginado(page, size)

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        u = self.service.buscar_por_id(usuario_id)
        if not u:
            raise PessoaNaoEncontradaException(usuario_id)
        return u

    def buscar_por_email(self, email: str) -> Usuario | None:
        self._validar_email(email)
        return self.service.buscar_por_email(email)

    def login(self, email: str, senha: str) -> dict:
        self._validar_email(email)
        if not senha:
            raise DadosInvalidosException("senha", "<oculta>")
        usuario = self.service.buscar_por_email(email)
        if not usuario or not verify_password(senha, usuario.senha_hash):
            raise DadosInvalidosException("credenciais", "invalidas")
        token = create_access_token({"sub": str(usuario.id), "email": usuario.email})
        return {"access_token": token, "token_type": "bearer"} 