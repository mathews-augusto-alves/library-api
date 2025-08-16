"""
Testes para os DTOs de usuário.
"""
import pytest
from src.presentation.dto.usuario_dto import UsuarioCreateRequest, UsuarioUpdateRequest, UsuarioResponse


class TestUsuarioCreateRequest:
    """Testes para UsuarioCreateRequest."""
    
    def test_criar_usuario_valido(self):
        dto = UsuarioCreateRequest(
            nome="João Silva",
            email="joao@email.com",
            senha="senha123"
        )
        assert dto.nome == "João Silva"
        assert dto.email == "joao@email.com"
        assert dto.senha == "senha123"
    
    def test_criar_usuario_nome_minimo(self):
        dto = UsuarioCreateRequest(
            nome="Jo",
            email="joao@email.com",
            senha="senha123"
        )
        assert dto.nome == "Jo"
    
    def test_criar_usuario_nome_medio(self):
        dto = UsuarioCreateRequest(
            nome="João Silva Santos",
            email="joao@email.com",
            senha="senha123"
        )
        assert dto.nome == "João Silva Santos"
    
    def test_criar_usuario_email_valido(self):
        dto = UsuarioCreateRequest(
            nome="João Silva",
            email="joao.silva@empresa.com.br",
            senha="senha123"
        )
        assert dto.email == "joao.silva@empresa.com.br"
    
    def test_criar_usuario_senha_minima(self):
        dto = UsuarioCreateRequest(
            nome="João Silva",
            email="joao@email.com",
            senha="123456"
        )
        assert dto.senha == "123456"
    
    def test_validacao_nome_vazio(self):
        with pytest.raises(ValueError, match="Nome deve ter pelo menos 2 caracteres"):
            UsuarioCreateRequest(nome="", email="joao@email.com", senha="senha123")
    
    def test_validacao_nome_muito_curto(self):
        with pytest.raises(ValueError, match="Nome deve ter pelo menos 2 caracteres"):
            UsuarioCreateRequest(nome="A", email="joao@email.com", senha="senha123")
    
    def test_validacao_email_invalido(self):
        with pytest.raises(ValueError, match="Email inválido"):
            UsuarioCreateRequest(nome="João Silva", email="email_invalido", senha="senha123")
    
    def test_validacao_email_vazio(self):
        with pytest.raises(ValueError, match="Email inválido"):
            UsuarioCreateRequest(nome="João Silva", email="", senha="senha123")
    
    def test_validacao_senha_muito_curta(self):
        with pytest.raises(ValueError, match="Senha deve ter pelo menos 6 caracteres"):
            UsuarioCreateRequest(nome="João Silva", email="joao@email.com", senha="12345")


class TestUsuarioUpdateRequest:
    """Testes para UsuarioUpdateRequest (sem validações customizadas)."""
    
    def test_criar_atualizacao_valida(self):
        dto = UsuarioUpdateRequest(
            nome="João Silva Atualizado",
            email="joao.novo@email.com",
            senha="nova_senha123"
        )
        assert dto.nome == "João Silva Atualizado"
        assert dto.email == "joao.novo@email.com"
        assert dto.senha == "nova_senha123"


class TestUsuarioResponse:
    """Testes para UsuarioResponse."""
    
    def test_criar_resposta_valida(self):
        dto = UsuarioResponse(id=1, nome="João Silva", email="joao@email.com")
        assert dto.id == 1
        assert dto.nome == "João Silva"
        assert dto.email == "joao@email.com"
    
    def test_serializacao_dto(self):
        dto = UsuarioResponse(id=1, nome="João Silva", email="joao@email.com")
        dados = dto.model_dump()
        assert dados["id"] == 1
        assert dados["nome"] == "João Silva"
        assert dados["email"] == "joao@email.com"
        assert "senha_hash" not in dados
    
    def test_serializacao_json(self):
        dto = UsuarioResponse(id=1, nome="João Silva", email="joao@email.com")
        dados_json = dto.model_dump(mode="json")
        assert dados_json["id"] == 1
        assert dados_json["nome"] == "João Silva"
        assert dados_json["email"] == "joao@email.com"
    
    def test_fluxo_completo_criar_atualizar_responder(self):
        create_dto = UsuarioCreateRequest(nome="João Silva", email="joao@email.com", senha="senha123")
        assert create_dto.nome == "João Silva"
        update_dto = UsuarioUpdateRequest(nome="João Silva Atualizado", email="joao.novo@email.com", senha="nova_senha123")
        assert update_dto.nome == "João Silva Atualizado"
        response_dto = UsuarioResponse(id=1, nome="João Silva Atualizado", email="joao.novo@email.com")
        assert response_dto.id == 1
        assert response_dto.nome == "João Silva Atualizado" 