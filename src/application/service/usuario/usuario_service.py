from typing import Optional, Tuple
from src.application.service.base_service import BaseService
from src.domain.model.usuario import Usuario
from src.domain.ports.usuario_repository import UsuarioRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort

class UsuarioService(BaseService[Usuario]):
    def __init__(self, repositorio: UsuarioRepositoryPort, uow: UnitOfWorkPort):
        super().__init__(uow)
        self.repositorio = repositorio

    def criar(self, usuario: Usuario) -> Usuario:
        return self._executar_transacao(lambda: self.repositorio.criar(usuario))

    def atualizar(self, usuario_id: int, usuario: Usuario) -> Optional[Usuario]:
        return self._executar_transacao(lambda: self.repositorio.atualizar(usuario_id, usuario))

    def remover(self, usuario_id: int) -> bool:
        return self._executar_transacao(lambda: self.repositorio.remover(usuario_id))

    def listar(self) -> list[Usuario]:
        return self.repositorio.listar()

    def listar_paginado(self, page: int, size: int) -> Tuple[list[Usuario], int]:
        return self.repositorio.listar_paginado(page, size)

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        return self.repositorio.buscar_por_id(usuario_id)

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        return self.repositorio.buscar_por_email(email)
