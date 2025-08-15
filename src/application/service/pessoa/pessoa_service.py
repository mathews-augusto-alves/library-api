from src.domain.model.pessoa import Pessoa
from src.domain.ports.pessoa_repository import PessoaRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort
from src.application.service.base_service import BaseService
from typing import Tuple

class PessoaService(BaseService[Pessoa]):
    def __init__(self, repository: PessoaRepositoryPort, uow: UnitOfWorkPort):
        super().__init__(uow)
        self.repository = repository

    def criar_pessoa(self, pessoa: Pessoa) -> Pessoa:
        def acao():
            return self.repository.criar(pessoa)
        return self._executar_transacao(acao)

    def listar_pessoas(self) -> list[Pessoa]:
        return self.repository.listar()

    def listar_pessoas_paginado(self, page: int, size: int) -> Tuple[list[Pessoa], int]:
        return self.repository.listar_paginado(page, size)

    def buscar_por_id(self, pessoa_id: int) -> Pessoa | None:
        return self.repository.buscar_por_id(pessoa_id)

    def buscar_pessoa_por_email(self, email: str) -> Pessoa | None:
        return self.repository.buscar_por_email(email)

    def atualizar_pessoa(self, pessoa_id: int, pessoa: Pessoa) -> Pessoa | None:
        def acao():
            return self.repository.atualizar(pessoa_id, pessoa)
        return self._executar_transacao(acao)

    def remover_pessoa(self, pessoa_id: int) -> bool:
        def acao():
            return self.repository.remover(pessoa_id)
        return self._executar_transacao(acao)
