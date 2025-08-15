from src.domain.model.livro import Livro
from src.domain.ports.livro_repository import LivroRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort
from src.application.service.base_service import BaseService
from typing import Tuple

class LivroService(BaseService[Livro]):
    def __init__(self, repository: LivroRepositoryPort, uow: UnitOfWorkPort):
        super().__init__(uow)
        self.repository = repository

    def criar(self, livro: Livro) -> Livro:
        return self._executar_transacao(lambda: self.repository.criar(livro))

    def listar(self) -> list[Livro]:
        return self.repository.listar()

    def listar_paginado(self, page: int, size: int) -> Tuple[list[Livro], int]:
        return self.repository.listar_paginado(page, size)

    def buscar_por_id(self, livro_id: int) -> Livro | None:
        return self.repository.buscar_por_id(livro_id)

    def set_disponibilidade(self, livro_id: int, disponivel: bool) -> Livro | None:
        return self._executar_transacao(lambda: self.repository.atualizar_disponibilidade(livro_id, disponivel))
