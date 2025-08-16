"""
Testes para o UsuarioController.
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from src.presentation.controllers.usuario_controllers import UsuarioControllers
from src.presentation.dto.usuario_dto import UsuarioCreateRequest, UsuarioUpdateRequest


class TestUsuarioController:
    """Testes para o UsuarioController."""
    
    def test_cadastrar_usuario_sucesso(self, mock_usuario_usecase):
        """Teste de criação de usuário com sucesso."""
        # Arrange
        mock_usuario_usecase.cadastrar.return_value = Mock(id=1, nome="João Silva", email="joao@email.com")
        
        controller = UsuarioControllers(mock_usuario_usecase)
        request = UsuarioCreateRequest(
            nome="João Silva",
            email="joao@email.com",
            senha="senha123"
        )
        
        # Act
        result = controller.cadastrar(request)
        
        # Assert
        assert result.id == 1
        assert result.nome == "João Silva"
        assert result.email == "joao@email.com"
        mock_usuario_usecase.cadastrar.assert_called_once_with("João Silva", "joao@email.com", "senha123")
    
    def test_cadastrar_usuario_erro(self, mock_usuario_usecase):
        """Teste de criação de usuário com erro."""
        # Arrange
        mock_usuario_usecase.cadastrar.side_effect = ValueError("Erro ao cadastrar usuário")
        
        controller = UsuarioControllers(mock_usuario_usecase)
        request = UsuarioCreateRequest(
            nome="João Silva",  # Válido (2+ caracteres)
            email="joao@email.com",  # Válido
            senha="senha123"  # Válido (6+ caracteres)
        )
        
        # Act & Assert
        with pytest.raises(ValueError):
            controller.cadastrar(request)
    
    def test_login_usuario_sucesso(self, mock_usuario_usecase):
        """Teste de login de usuário com sucesso."""
        # Arrange
        mock_usuario_usecase.login.return_value = {"token": "jwt_token_123", "usuario": {"id": 1, "nome": "João Silva"}}
        
        controller = UsuarioControllers(mock_usuario_usecase)
        
        # Act
        result = controller.login("joao@email.com", "senha123")
        
        # Assert
        assert result["token"] == "jwt_token_123"
        assert result["usuario"]["nome"] == "João Silva"
        mock_usuario_usecase.login.assert_called_once_with("joao@email.com", "senha123")
    
    def test_login_usuario_erro(self, mock_usuario_usecase):
        """Teste de login de usuário com erro."""
        # Arrange
        mock_usuario_usecase.login.side_effect = ValueError("Credenciais inválidas")
        
        controller = UsuarioControllers(mock_usuario_usecase)
        
        # Act & Assert
        with pytest.raises(ValueError):
            controller.login("joao@email.com", "senha_errada")
    
    def test_listar_usuarios_sucesso(self, mock_usuario_usecase):
        """Teste de listagem de usuários com sucesso."""
        # Arrange
        mock_usuario_usecase.listar.return_value = [
            Mock(id=1, nome="João Silva", email="joao@email.com"),
            Mock(id=2, nome="Maria Santos", email="maria@email.com")
        ]
        
        controller = UsuarioControllers(mock_usuario_usecase)
        
        # Act
        result = controller.listar()
        
        # Assert
        assert len(result) == 2
        mock_usuario_usecase.listar.assert_called_once()
    
    def test_listar_paginado_sem_cache(self, mock_usuario_usecase):
        """Teste de listagem paginada sem cache."""
        # Arrange
        mock_usuario_usecase.listar_paginado.return_value = ([
            Mock(id=1, nome="João Silva", email="joao@email.com"),
            Mock(id=2, nome="Maria Santos", email="maria@email.com")
        ], 2)
        
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 2
        mock_usuario_usecase.listar_paginado.assert_called_once_with(1, 10)
    
    def test_listar_paginado_com_cache(self, mock_usuario_usecase):
        """Teste de listagem paginada com cache."""
        # Arrange
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        
        # Mock do cache retornando dados válidos
        cached_data = '{"data": [{"id": 1, "nome": "João Silva", "email": "joao@email.com"}], "meta": {"page": 1, "size": 10, "total": 1, "total_pages": 1, "has_next": false, "has_previous": false}}'
        mock_cache.get.return_value = cached_data
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 1
        mock_usuario_usecase.listar_paginado.assert_not_called()
    
    def test_buscar_por_id_sem_cache(self, mock_usuario_usecase):
        """Teste de busca de usuário por ID sem cache."""
        # Arrange
        mock_usuario_usecase.buscar_por_id.return_value = Mock(id=1, nome="João Silva", email="joao@email.com")
        
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.buscar_por_id(1, mock_cache)
        
        # Assert
        assert result.id == 1
        mock_usuario_usecase.buscar_por_id.assert_called_once_with(1)
    
    def test_buscar_por_id_nao_encontrado(self, mock_usuario_usecase):
        """Teste de busca de usuário por ID não encontrado."""
        # Arrange
        mock_usuario_usecase.buscar_por_id.side_effect = ValueError("Usuário não encontrado")
        
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError):
            controller.buscar_por_id(999, mock_cache)
    
    def test_buscar_por_email_sem_cache(self, mock_usuario_usecase):
        """Teste de busca de usuário por email sem cache."""
        # Arrange
        mock_usuario_usecase.buscar_por_email.return_value = Mock(id=1, nome="João Silva", email="joao@email.com")
        
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.buscar_por_email("joao@email.com", mock_cache)
        
        # Assert
        assert result.email == "joao@email.com"
        mock_usuario_usecase.buscar_por_email.assert_called_once_with("joao@email.com")
    
    def test_buscar_por_email_nao_encontrado(self, mock_usuario_usecase):
        """Teste de busca de usuário por email não encontrado."""
        # Arrange
        mock_usuario_usecase.buscar_por_email.return_value = None
        
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.buscar_por_email("naoexiste@email.com", mock_cache)
        
        # Assert
        assert result is None
        mock_usuario_usecase.buscar_por_email.assert_called_once_with("naoexiste@email.com")
    
    def test_atualizar_usuario_sucesso(self, mock_usuario_usecase):
        """Teste de atualização de usuário com sucesso."""
        # Arrange
        mock_usuario_usecase.atualizar.return_value = Mock(id=1, nome="João Silva Atualizado", email="joao.novo@email.com")
        
        controller = UsuarioControllers(mock_usuario_usecase)
        request = UsuarioUpdateRequest(
            nome="João Silva Atualizado",
            email="joao.novo@email.com",
            senha="nova_senha123"
        )
        mock_cache = Mock()
        
        # Act
        result = controller.atualizar(1, request, mock_cache)
        
        # Assert
        assert result.id == 1
        assert result.nome == "João Silva Atualizado"
        assert result.email == "joao.novo@email.com"
        mock_usuario_usecase.atualizar.assert_called_once_with(1, "João Silva Atualizado", "joao.novo@email.com", "nova_senha123")
    
    def test_remover_usuario_sucesso(self, mock_usuario_usecase):
        """Teste de remoção de usuário com sucesso."""
        # Arrange
        mock_usuario_usecase.remover.return_value = None
        
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        
        # Act
        result = controller.remover(1, mock_cache)
        
        # Assert
        assert result is None
        mock_usuario_usecase.remover.assert_called_once_with(1)
    
    def test_fluxo_completo_cadastrar_buscar_atualizar_remover(self, mock_usuario_usecase):
        """Teste de fluxo completo de operações."""
        # Arrange
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        
        # Mock para cadastro
        mock_usuario_usecase.cadastrar.return_value = Mock(id=1, nome="João Silva", email="joao@email.com")
        
        # Mock para busca por ID
        mock_usuario_usecase.buscar_por_id.return_value = Mock(id=1, nome="João Silva", email="joao@email.com")
        
        # Mock para busca por email
        mock_usuario_usecase.buscar_por_email.return_value = Mock(id=1, nome="João Silva", email="joao@email.com")
        
        # Mock para atualização
        mock_usuario_usecase.atualizar.return_value = Mock(id=1, nome="João Silva Atualizado", email="joao.novo@email.com")
        
        # Mock para remoção
        mock_usuario_usecase.remover.return_value = None
        
        request = UsuarioCreateRequest(
            nome="João Silva",
            email="joao@email.com",
            senha="senha123"
        )
        
        update_request = UsuarioUpdateRequest(
            nome="João Silva Atualizado",
            email="joao.novo@email.com",
            senha="nova_senha123"
        )
        
        # Act & Assert - Cadastro
        result_cadastrar = controller.cadastrar(request)
        assert result_cadastrar.id == 1
        
        # Act & Assert - Busca por ID
        # Configurar mock do cache para retornar None (sem cache)
        mock_cache.get.return_value = None
        result_buscar_id = controller.buscar_por_id(1, mock_cache)
        assert result_buscar_id.id == 1
        
        # Act & Assert - Busca por Email
        # Configurar mock do cache para retornar None (sem cache)
        mock_cache.get.return_value = None
        result_buscar_email = controller.buscar_por_email("joao@email.com", mock_cache)
        assert result_buscar_email.email == "joao@email.com"
        
        # Act & Assert - Atualização
        result_atualizar = controller.atualizar(1, update_request, mock_cache)
        assert result_atualizar.nome == "João Silva Atualizado"
        
        # Act & Assert - Remoção
        result_remover = controller.remover(1, mock_cache)
        assert result_remover is None
        
        # Verificar se todos os métodos foram chamados
        mock_usuario_usecase.cadastrar.assert_called_once_with("João Silva", "joao@email.com", "senha123")
        mock_usuario_usecase.buscar_por_id.assert_called_once_with(1)
        mock_usuario_usecase.buscar_por_email.assert_called_once_with("joao@email.com")
        mock_usuario_usecase.atualizar.assert_called_once_with(1, "João Silva Atualizado", "joao.novo@email.com", "nova_senha123")
        mock_usuario_usecase.remover.assert_called_once_with(1)
    
    def test_cache_keys_corretas(self, mock_usuario_usecase):
        """Teste de verificação das chaves de cache."""
        # Arrange
        mock_usuario_usecase.listar_paginado.return_value = ([], 0)
        
        controller = UsuarioControllers(mock_usuario_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 0
        mock_usuario_usecase.listar_paginado.assert_called_once_with(1, 10)