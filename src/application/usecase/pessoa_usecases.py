from src.domain.model.pessoa import Pessoa
from src.domain.exceptions import EmailJaExisteException, PessoaNaoEncontradaException, DadosInvalidosException
import re
from typing import Tuple

class PessoaUseCaseValidator:
    @staticmethod
    def validar_email_formato(email: str) -> None:
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise DadosInvalidosException("email", email)

    @staticmethod
    def validar_telefone(telefone: str) -> None:
        if not telefone or len(telefone) < 8:
            raise DadosInvalidosException("telefone", telefone)

    @staticmethod
    def validar_nome(nome: str) -> None:
        if not nome or len(nome.strip()) < 2:
            raise DadosInvalidosException("nome", nome)

    @classmethod
    def validar_pessoa(cls, pessoa: Pessoa) -> None:
        cls.validar_nome(pessoa.nome)
        cls.validar_telefone(pessoa.telefone)
        if pessoa.email:
            cls.validar_email_formato(pessoa.email)

    @classmethod
    def validar_busca_por_email(cls, email: str) -> None:
        cls.validar_email_formato(email)

from src.application.service.pessoa.pessoa_service import PessoaService

class PessoaUseCase:
    def __init__(self, service: PessoaService):
        self.service = service

    def criar_pessoa(self, pessoa: Pessoa) -> Pessoa:
        PessoaUseCaseValidator.validar_pessoa(pessoa)
        if pessoa.email:
            existente = self.service.buscar_pessoa_por_email(pessoa.email)
            if existente:
                raise EmailJaExisteException(pessoa.email)
        return self.service.criar_pessoa(pessoa)

    def listar_pessoas(self) -> list[Pessoa]:
        return self.service.listar_pessoas()

    def listar_pessoas_paginado(self, page: int, size: int) -> Tuple[list[Pessoa], int]:
        return self.service.listar_pessoas_paginado(page, size)

    def buscar_por_id(self, pessoa_id: int) -> Pessoa | None:
        pessoa = self.service.buscar_por_id(pessoa_id)
        if not pessoa:
            raise PessoaNaoEncontradaException(pessoa_id)
        return pessoa

    def buscar_pessoa_por_email(self, email: str) -> Pessoa | None:
        PessoaUseCaseValidator.validar_busca_por_email(email)
        return self.service.buscar_pessoa_por_email(email)

    def atualizar_pessoa(self, pessoa_id: int, pessoa: Pessoa) -> Pessoa | None:
        PessoaUseCaseValidator.validar_pessoa(pessoa)
        pessoa_existente = self.service.buscar_por_id(pessoa_id)
        if not pessoa_existente:
            raise PessoaNaoEncontradaException(pessoa_id)
        if pessoa.email:
            pessoa_com_email = self.service.buscar_pessoa_por_email(pessoa.email)
            if pessoa_com_email and pessoa_com_email.id != pessoa_id:
                raise EmailJaExisteException(pessoa.email)
        return self.service.atualizar_pessoa(pessoa_id, pessoa)

    def remover_pessoa(self, pessoa_id: int) -> bool:
        pessoa_existente = self.service.buscar_por_id(pessoa_id)
        if not pessoa_existente:
            raise PessoaNaoEncontradaException(pessoa_id)
        return self.service.remover_pessoa(pessoa_id) 