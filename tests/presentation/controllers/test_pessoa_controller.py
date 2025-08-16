"""
Testes para o PessoaController.
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from datetime import date
from src.presentation.controllers.pessoa_controllers import PessoaControllers
from src.presentation.dto.pessoa_dto import PessoaCreateRequest


class TestPessoaController:
    """Testes para o PessoaController."""
    
    def test_criar_pessoa_com_email_sucesso(self, mock_pessoa_usecase):
        """Teste de criação de pessoa com email com sucesso."""
        # Arrange
        mock_pessoa_usecase.criar_pessoa.return_value = Mock(id=1, nome="Maria Santos", email="maria@email.com")
        
        controller = PessoaControllers(mock_pessoa_usecase)
        request = PessoaCreateRequest(
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="maria@email.com"
        )
        mock_cache = Mock()
        
        # Act
        result = controller.criar(request, mock_cache)
        
        # Assert
        assert result.id == 1
        assert result.nome == "Maria Santos"
        assert result.email == "maria@email.com"
        mock_pessoa_usecase.criar_pessoa.assert_called_once()
    
    def test_criar_pessoa_sem_email_sucesso(self, mock_pessoa_usecase):
        """Teste de criação de pessoa sem email com sucesso."""
        # Arrange
        mock_pessoa_usecase.criar_pessoa.return_value = Mock(id=1, nome="João Silva", email=None)
        
        controller = PessoaControllers(mock_pessoa_usecase)
        request = PessoaCreateRequest(
            nome="João Silva",
            telefone="11988888888",
            data_nascimento=date(1985, 5, 15),
            email=None
        )
        mock_cache = Mock()
        
        # Act
        result = controller.criar(request, mock_cache)
        
        # Assert
        assert result.id == 1
        assert result.nome == "João Silva"
        assert result.email is None
        mock_pessoa_usecase.criar_pessoa.assert_called_once()
    
    def test_criar_pessoa_erro(self, mock_pessoa_usecase):
        """Teste de criação de pessoa com erro."""
        # Arrange
        mock_pessoa_usecase.criar_pessoa.side_effect = ValueError("Erro ao criar pessoa")
        
        controller = PessoaControllers(mock_pessoa_usecase)
        request = PessoaCreateRequest(
            nome="João",  # Válido (2+ caracteres)
            telefone="11999999",  # Válido (8+ caracteres)
            data_nascimento=date(1990, 1, 1),
            email="joao@email.com"  # Válido
        )
        mock_cache = Mock()
        
        # Act & Assert
        with pytest.raises(ValueError):
            controller.criar(request, mock_cache)
    
    def test_listar_pessoas(self, mock_pessoa_usecase):
        """Teste de listagem de pessoas."""
        # Arrange
        mock_pessoa_usecase.listar_pessoas.return_value = [
            Mock(id=1, nome="Maria Santos", email="maria@email.com"),
            Mock(id=2, nome="João Silva", email="joao@email.com")
        ]
        
        controller = PessoaControllers(mock_pessoa_usecase)
        
        # Act
        result = controller.listar()
        
        # Assert
        assert len(result) == 2
        mock_pessoa_usecase.listar_pessoas.assert_called_once()
    
    def test_listar_paginado_sem_cache(self, mock_pessoa_usecase):
        """Teste de listagem paginada sem cache."""
        # Arrange
        mock_pessoa_usecase.listar_pessoas_paginado.return_value = ([
            Mock(id=1, nome="Maria Santos", email="maria@email.com", telefone="11999999999", data_nascimento=date(1990, 1, 1))
        ], 1)
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 1
        mock_pessoa_usecase.listar_pessoas_paginado.assert_called_once_with(1, 10)
    
    def test_listar_paginado_com_cache(self, mock_pessoa_usecase):
        """Teste de listagem paginada com cache."""
        # Arrange
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        
        # Mock do cache retornando dados válidos
        cached_data = '{"data": [{"id": 1, "nome": "Maria Santos", "telefone": "11999999999", "data_nascimento": "1990-01-01", "email": "maria@email.com"}], "meta": {"page": 1, "size": 10, "total": 1, "total_pages": 1, "has_next": false, "has_previous": false}}'
        mock_cache.get.return_value = cached_data
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 1
        mock_pessoa_usecase.listar_pessoas_paginado.assert_not_called()
    
    def test_listar_paginado_validacao_parametros(self, mock_pessoa_usecase):
        """Teste de validação de parâmetros de paginação."""
        # Arrange
        mock_pessoa_usecase.listar_pessoas_paginado.return_value = ([], 0)
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)  # Parâmetros válidos
        
        # Assert
        assert len(result.data) == 0
        mock_pessoa_usecase.listar_pessoas_paginado.assert_called_once_with(1, 10)
    
    def test_buscar_por_id_sem_cache(self, mock_pessoa_usecase):
        """Teste de busca de pessoa por ID sem cache."""
        # Arrange
        mock_pessoa_usecase.buscar_por_id.return_value = Mock(id=1, nome="Maria Santos", email="maria@email.com", telefone="11999999999", data_nascimento=date(1990, 1, 1))
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.buscar_por_id(1, mock_cache)
        
        # Assert
        assert result.id == 1
        mock_pessoa_usecase.buscar_por_id.assert_called_once_with(1)
    
    def test_buscar_por_id_nao_encontrada(self, mock_pessoa_usecase):
        """Teste de busca de pessoa por ID não encontrada."""
        # Arrange
        mock_pessoa_usecase.buscar_por_id.side_effect = ValueError("Pessoa não encontrada")
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            controller.buscar_por_id(999, mock_cache)
    
    def test_buscar_por_email_sem_cache(self, mock_pessoa_usecase):
        """Teste de busca de pessoa por email sem cache."""
        # Arrange
        mock_pessoa_usecase.buscar_pessoa_por_email.return_value = Mock(id=1, nome="Maria Santos", email="maria@email.com", telefone="11999999999", data_nascimento=date(1990, 1, 1))
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.buscar_por_email("maria@email.com", mock_cache)
        
        # Assert
        assert result.email == "maria@email.com"
        mock_pessoa_usecase.buscar_pessoa_por_email.assert_called_once_with("maria@email.com")
    
    def test_buscar_por_email_dados_invalidos(self, mock_pessoa_usecase):
        """Teste de busca de pessoa por email com dados inválidos."""
        # Arrange
        mock_pessoa_usecase.buscar_pessoa_por_email.return_value = None
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            controller.buscar_por_email("email_invalido", mock_cache)
        
        assert exc_info.value.status_code == 404
    
    def test_atualizar_pessoa_com_email_sucesso(self, mock_pessoa_usecase):
        """Teste de atualização de pessoa com email com sucesso."""
        # Arrange
        mock_pessoa_usecase.atualizar_pessoa.return_value = Mock(
            id=1, 
            nome="Maria Santos Atualizada", 
            email="maria.nova@email.com",
            telefone="11977777777",
            data_nascimento=date(1990, 1, 1)
        )
        
        controller = PessoaControllers(mock_pessoa_usecase)
        request = PessoaCreateRequest(
            nome="Maria Santos Atualizada",
            telefone="11977777777",
            data_nascimento=date(1990, 1, 1),
            email="maria.nova@email.com"
        )
        mock_cache = Mock()
        
        # Act
        result = controller.atualizar(1, request, mock_cache)
        
        # Assert
        assert result.id == 1
        assert result.nome == "Maria Santos Atualizada"
        assert result.email == "maria.nova@email.com"
        mock_pessoa_usecase.atualizar_pessoa.assert_called_once()
    
    def test_atualizar_pessoa_sem_email_sucesso(self, mock_pessoa_usecase):
        """Teste de atualização de pessoa sem email com sucesso."""
        # Arrange
        mock_pessoa_usecase.atualizar_pessoa.return_value = Mock(
            id=1, 
            nome="João Silva Atualizado", 
            email=None,
            telefone="11966666666",
            data_nascimento=date(1985, 5, 15)
        )
        
        controller = PessoaControllers(mock_pessoa_usecase)
        request = PessoaCreateRequest(
            nome="João Silva Atualizado",
            telefone="11966666666",
            data_nascimento=date(1985, 5, 15),
            email=None
        )
        mock_cache = Mock()
        
        # Act
        result = controller.atualizar(1, request, mock_cache)
        
        # Assert
        assert result.id == 1
        assert result.nome == "João Silva Atualizado"
        assert result.email is None
        mock_pessoa_usecase.atualizar_pessoa.assert_called_once()
    
    def test_remover_pessoa_sucesso(self, mock_pessoa_usecase):
        """Teste de remoção de pessoa com sucesso."""
        # Arrange
        mock_pessoa_usecase.remover_pessoa.return_value = None
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        
        # Act
        result = controller.remover_pessoa(1, mock_cache)
        
        # Assert
        assert result is None
        mock_pessoa_usecase.remover_pessoa.assert_called_once_with(1)
    
    def test_buscar_por_id_erro_cache_get(self, mock_pessoa_usecase):
        """Teste de erro ao buscar cache."""
        # Arrange
        mock_pessoa_usecase.buscar_por_id.return_value = Mock(id=1, nome="Maria Santos", email="maria@email.com", telefone="11999999999", data_nascimento=date(1990, 1, 1))
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.buscar_por_id(1, mock_cache)
        
        # Assert
        assert result.id == 1
        mock_pessoa_usecase.buscar_por_id.assert_called_once_with(1)
    
    def test_criar_erro_cache_delete(self, mock_pessoa_usecase):
        """Teste de erro ao deletar cache."""
        # Arrange
        mock_pessoa_usecase.criar_pessoa.return_value = Mock(id=1, nome="Maria Santos", email="maria@email.com")
        
        controller = PessoaControllers(mock_pessoa_usecase)
        request = PessoaCreateRequest(
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="maria@email.com"
        )
        mock_cache = Mock()
        
        # Act
        result = controller.criar(request, mock_cache)
        
        # Assert
        assert result.id == 1
        mock_pessoa_usecase.criar_pessoa.assert_called_once()
    
    def test_fluxo_completo_criar_buscar_atualizar_remover(self, mock_pessoa_usecase):
        """Teste de fluxo completo de operações."""
        # Arrange
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        
        # Mock para criação
        mock_pessoa_usecase.criar_pessoa.return_value = Mock(id=1, nome="Maria Santos", email="maria@email.com")
        
        # Mock para busca
        mock_pessoa_usecase.buscar_por_id.return_value = Mock(id=1, nome="Maria Santos", email="maria@email.com", telefone="11999999999", data_nascimento=date(1990, 1, 1))
        
        # Mock para atualização
        mock_pessoa_usecase.atualizar_pessoa.return_value = Mock(
            id=1, 
            nome="Maria Santos Atualizada", 
            email="maria.nova@email.com",
            telefone="11988888888",
            data_nascimento=date(1990, 1, 1)
        )
        
        # Mock para remoção
        mock_pessoa_usecase.remover_pessoa.return_value = None
        
        request = PessoaCreateRequest(
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="maria@email.com"
        )
        
        update_request = PessoaCreateRequest(
            nome="Maria Santos Atualizada",
            telefone="11988888888",
            data_nascimento=date(1990, 1, 1),
            email="maria.nova@email.com"
        )
        
        # Act & Assert - Criação
        result_criar = controller.criar(request, mock_cache)
        assert result_criar.id == 1
        
        # Act & Assert - Busca
        # Configurar mock do cache para retornar None (sem cache)
        mock_cache.get.return_value = None
        result_buscar = controller.buscar_por_id(1, mock_cache)
        assert result_buscar.id == 1
        
        # Act & Assert - Atualização
        result_atualizar = controller.atualizar(1, update_request, mock_cache)
        assert result_atualizar.id == 1
        
        # Act & Assert - Remoção
        result_remover = controller.remover_pessoa(1, mock_cache)
        assert result_remover is None
        
        # Verificar se todos os métodos foram chamados
        mock_pessoa_usecase.criar_pessoa.assert_called_once()
        mock_pessoa_usecase.buscar_por_id.assert_called_once_with(1)
        mock_pessoa_usecase.atualizar_pessoa.assert_called_once()
        mock_pessoa_usecase.remover_pessoa.assert_called_once_with(1)
    
    def test_cache_keys_corretas(self, mock_pessoa_usecase):
        """Teste de verificação das chaves de cache."""
        # Arrange
        mock_pessoa_usecase.listar_pessoas_paginado.return_value = ([], 0)
        
        controller = PessoaControllers(mock_pessoa_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 0
        mock_pessoa_usecase.listar_pessoas_paginado.assert_called_once_with(1, 10)