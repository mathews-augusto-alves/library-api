"""
Testes para os DTOs de pessoa.
"""
import pytest
from datetime import date
from src.presentation.dto.pessoa_dto import PessoaCreateRequest, PessoaResponse


class TestPessoaCreateRequest:
    """Testes para PessoaCreateRequest."""
    
    def test_criar_pessoa_valida(self):
        dto = PessoaCreateRequest(
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="maria@email.com"
        )
        assert dto.nome == "Maria Santos"
        assert dto.telefone == "11999999999"
        assert dto.data_nascimento == date(1990, 1, 1)
        assert dto.email == "maria@email.com"
    
    def test_criar_pessoa_sem_email(self):
        dto = PessoaCreateRequest(
            nome="João Silva",
            telefone="11988888888",
            data_nascimento=date(1985, 5, 15),
            email=None
        )
        assert dto.email is None
    
    def test_criar_pessoa_nome_minimo(self):
        dto = PessoaCreateRequest(
            nome="Jo",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="joao@email.com"
        )
        assert dto.nome == "Jo"
    
    def test_criar_pessoa_telefone_minimo(self):
        dto = PessoaCreateRequest(
            nome="João Silva",
            telefone="11999999",  # 8 caracteres (mínimo)
            data_nascimento=date(1990, 1, 1),
            email="joao@email.com"
        )
        assert dto.telefone == "11999999"
    
    def test_criar_pessoa_email_valido(self):
        dto = PessoaCreateRequest(
            nome="João Silva",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="joao.silva@empresa.com.br"
        )
        assert dto.email == "joao.silva@empresa.com.br"
    
    def test_validacao_nome_vazio(self):
        with pytest.raises(ValueError, match="Nome deve ter pelo menos 2 caracteres"):
            PessoaCreateRequest(nome="", telefone="11999999999", data_nascimento=date(1990, 1, 1), email="x@y.com")
    
    def test_validacao_nome_muito_curto(self):
        with pytest.raises(ValueError, match="Nome deve ter pelo menos 2 caracteres"):
            PessoaCreateRequest(nome="A", telefone="11999999999", data_nascimento=date(1990, 1, 1), email="x@y.com")
    
    def test_validacao_telefone_muito_curto(self):
        with pytest.raises(ValueError, match="Telefone deve ter pelo menos 8 caracteres"):
            PessoaCreateRequest(nome="João Silva", telefone="1199999", data_nascimento=date(1990, 1, 1), email="x@y.com")
    
    def test_validacao_email_invalido(self):
        with pytest.raises(ValueError, match="Email deve ser válido"):
            PessoaCreateRequest(nome="João Silva", telefone="11999999999", data_nascimento=date(1990, 1, 1), email="email_invalido")
    
    def test_email_vazio_permitido(self):
        dto = PessoaCreateRequest(nome="João Silva", telefone="11999999999", data_nascimento=date(1990, 1, 1), email="")
        assert dto.email == ""


class TestPessoaResponse:
    """Testes para PessoaResponse."""
    
    def test_criar_resposta_valida(self):
        dto = PessoaResponse(
            id=1,
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="maria@email.com"
        )
        assert dto.id == 1
        assert dto.nome == "Maria Santos"
        assert dto.telefone == "11999999999"
        assert dto.data_nascimento == date(1990, 1, 1)
    
    def test_serializacao_dto(self):
        dto = PessoaResponse(
            id=1,
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="maria@email.com"
        )
        dados = dto.model_dump()
        assert dados["id"] == 1
        assert dados["nome"] == "Maria Santos"
        assert dados["telefone"] == "11999999999"
        assert dados["data_nascimento"] == date(1990, 1, 1)
    
    def test_serializacao_json(self):
        dto = PessoaResponse(
            id=1,
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="maria@email.com"
        )
        dados_json = dto.model_dump(mode="json")
        assert dados_json["id"] == 1
        assert dados_json["nome"] == "Maria Santos"
        assert dados_json["telefone"] == "11999999999"
        assert dados_json["data_nascimento"] == "1990-01-01"
    
    def test_resposta_sem_email(self):
        dto = PessoaResponse(
            id=1,
            nome="João Silva",
            telefone="11988888888",
            data_nascimento=date(1985, 5, 15),
            email=None
        )
        assert dto.email is None 