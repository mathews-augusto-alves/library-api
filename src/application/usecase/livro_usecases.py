from src.domain.model.livro import Livro
from src.domain.model.emprestimo import Emprestimo
from src.domain.enums.emprestimo_status import EmprestimoStatus
from src.domain.exceptions import (
    DadosInvalidosException,
    LivroNaoEncontradoException,
    LivroIndisponivelException,
    EmprestimoAtivoNaoEncontradoException,
    PessoaNaoEncontradaException
)
from src.application.service.livro.livro_service import LivroService
from src.application.service.livro.emprestimo_service import EmprestimoService
from src.application.service.pessoa.pessoa_service import PessoaService
from typing import Tuple

class LivroUseCase:
    def __init__(
        self,
        livro_service: LivroService,
        emprestimo_service: EmprestimoService,
        pessoa_service: PessoaService
    ):
        self._livros = livro_service
        self._emprestimos = emprestimo_service
        self._pessoas = pessoa_service

    def cadastrar_livro(self, titulo: str, autor: str) -> Livro:
        titulo = (titulo or "").strip()
        autor = (autor or "").strip()

        if len(titulo) < 2:
            raise DadosInvalidosException("titulo", titulo)
        if len(autor) < 2:
            raise DadosInvalidosException("autor", autor)

        novo_livro = Livro(id=None, titulo=titulo, autor=autor, disponivel=True)
        return self._livros.criar(novo_livro)

    def listar_livros(self) -> list[Livro]:
        return self._livros.listar()

    def listar_livros_paginado(self, page: int, size: int) -> Tuple[list[Livro], int]:
        return self._livros.listar_paginado(page, size)

    def listar_emprestimos_paginado(self, page: int, size: int, status: EmprestimoStatus = EmprestimoStatus.ATIVOS) -> Tuple[list[Emprestimo], int]:
        return self._emprestimos.listar_paginado(page, size, status)

    def emprestar(self, livro_id: int, pessoa_id: int, usuario_id: int) -> Emprestimo:
        livro = self._obter_livro_disponivel(livro_id)
        self._validar_pessoa_existente(pessoa_id)
        self._garantir_ausencia_de_emprestimo_ativo(livro_id)

        return self._emprestimos.emprestar(livro.id, pessoa_id, usuario_id)

    def devolver(self, livro_id: int) -> Emprestimo:
        livro = self._obter_livro_existente(livro_id)
        emprestimo_ativo = self._emprestimos.buscar_ativo_por_livro(livro.id)

        if not emprestimo_ativo:
            raise EmprestimoAtivoNaoEncontradoException(livro.id)

        return self._emprestimos.devolver(emprestimo_ativo.id, livro.id)

    def _obter_livro_existente(self, livro_id: int) -> Livro:
        livro = self._livros.buscar_por_id(livro_id)
        if not livro:
            raise LivroNaoEncontradoException(livro_id)
        return livro

    def _obter_livro_disponivel(self, livro_id: int) -> Livro:
        livro = self._obter_livro_existente(livro_id)
        if not livro.disponivel:
            raise LivroIndisponivelException(livro_id)
        return livro

    def _validar_pessoa_existente(self, pessoa_id: int) -> None:
        if not self._pessoas.buscar_por_id(pessoa_id):
            raise PessoaNaoEncontradaException(pessoa_id)

    def _garantir_ausencia_de_emprestimo_ativo(self, livro_id: int) -> None:
        if self._emprestimos.buscar_ativo_por_livro(livro_id):
            raise LivroIndisponivelException(livro_id)
