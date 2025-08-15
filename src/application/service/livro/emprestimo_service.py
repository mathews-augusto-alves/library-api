from datetime import datetime
from zoneinfo import ZoneInfo
from src.domain.model.emprestimo import Emprestimo
from src.domain.ports.emprestimo_repository import EmprestimoRepositoryPort
from src.domain.ports.livro_repository import LivroRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort
from src.application.service.base_service import BaseService
from src.domain.enums.emprestimo_status import EmprestimoStatus
from typing import Tuple

class EmprestimoService(BaseService[Emprestimo]):
    def __init__(self, repositorio: EmprestimoRepositoryPort, livro_repo: LivroRepositoryPort, uow: UnitOfWorkPort, tz: ZoneInfo):
        super().__init__(uow)
        self.repositorio = repositorio
        self.livros = livro_repo
        self._tz = tz

    def emprestar(self, livro_id: int, pessoa_id: int, usuario_id: int) -> Emprestimo:
        def acao():
            self.livros.atualizar_disponibilidade(livro_id, False)
            return self.repositorio.criar(Emprestimo(
                id=None,
                livro_id=livro_id,
                pessoa_id=pessoa_id,
                usuario_id=usuario_id,
                data_emprestimo=datetime.now(self._tz),
                data_devolucao=None
            ))
        return self._executar_transacao(acao)

    def devolver(self, emprestimo_id: int, livro_id: int) -> Emprestimo | None:
        def acao():
            emprestimo = self.repositorio.finalizar(emprestimo_id)
            if emprestimo:
                self.livros.atualizar_disponibilidade(livro_id, True)
            return emprestimo
        return self._executar_transacao(acao)

    def buscar_ativo_por_livro(self, livro_id: int) -> Emprestimo | None:
        return self.repositorio.buscar_ativo_por_livro(livro_id)

    def listar_paginado(self, page: int, size: int, status: EmprestimoStatus = EmprestimoStatus.ATIVOS) -> Tuple[list[Emprestimo], int]:
        return self.repositorio.listar_paginado(page, size, status)
