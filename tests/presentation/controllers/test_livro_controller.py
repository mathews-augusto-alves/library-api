"""
Testes para o LivroController.
"""
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from src.presentation.controllers.livro_controllers import LivroControllers
from src.presentation.dto.livro_dto import LivroCreateRequest, EmprestimoCreateRequest
from src.presentation.dto.common import PaginatedResponse, PaginationMeta


class TestLivroController:
    """Testes para o LivroController."""
    
    def test_cadastrar_livro_sucesso(self, mock_livro_usecase):
        """Teste de criação de livro com sucesso."""
        # Arrange
        mock_livro_usecase.cadastrar_livro.return_value = Mock(id=1, titulo="O Senhor dos Anéis", autor="J.R.R. Tolkien")
        
        controller = LivroControllers(mock_livro_usecase)
        request = LivroCreateRequest(
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien"
        )
        mock_cache = Mock()
        
        # Act
        result = controller.cadastrar(request, mock_cache)
        
        # Assert
        assert result.id == 1
        assert result.titulo == "O Senhor dos Anéis"
        mock_livro_usecase.cadastrar_livro.assert_called_once_with("O Senhor dos Anéis", "J.R.R. Tolkien")
    
    def test_cadastrar_livro_erro(self, mock_livro_usecase):
        """Teste de criação de livro com erro."""
        # Arrange
        mock_livro_usecase.cadastrar_livro.side_effect = ValueError("Erro ao criar livro")
        
        controller = LivroControllers(mock_livro_usecase)
        request = LivroCreateRequest(
            titulo="O Senhor dos Anéis",  # Válido (2+ caracteres)
            autor="J.R.R. Tolkien"        # Válido (2+ caracteres)
        )
        mock_cache = Mock()
        
        # Act & Assert
        with pytest.raises(ValueError):
            controller.cadastrar(request, mock_cache)
    
    def test_listar_livros_sucesso(self, mock_livro_usecase):
        """Teste de listagem de livros com sucesso."""
        # Arrange
        mock_livro_usecase.listar_livros.return_value = [
            Mock(id=1, titulo="Livro 1"),
            Mock(id=2, titulo="Livro 2")
        ]
        
        controller = LivroControllers(mock_livro_usecase)
        
        # Act
        result = controller.listar()
        
        # Assert
        assert len(result) == 2
        mock_livro_usecase.listar_livros.assert_called_once()
    
    def test_listar_paginado_sem_cache(self, mock_livro_usecase):
        """Teste de listagem paginada sem cache."""
        # Arrange
        mock_livro_usecase.listar_livros_paginado.return_value = ([
            Mock(id=1, titulo="Livro 1", autor="Autor 1", disponivel=True),
            Mock(id=2, titulo="Livro 2", autor="Autor 2", disponivel=False)
        ], 2)
        
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 2
        mock_livro_usecase.listar_livros_paginado.assert_called_once_with(1, 10)
    
    def test_listar_paginado_com_cache(self, mock_livro_usecase):
        """Teste de listagem paginada com cache."""
        # Arrange
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        
        # Mock do cache retornando dados válidos
        cached_data = '{"data": [{"id": 1, "titulo": "Livro 1", "autor": "Autor 1", "disponivel": true}], "meta": {"page": 1, "size": 10, "total": 1, "total_pages": 1, "has_next": false, "has_previous": false}}'
        mock_cache.get.return_value = cached_data
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 1
        mock_livro_usecase.listar_livros_paginado.assert_not_called()
    
    def test_listar_paginado_validacao_parametros(self, mock_livro_usecase):
        """Teste de validação de parâmetros de paginação."""
        # Arrange
        mock_livro_usecase.listar_livros_paginado.return_value = ([], 0)
        
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)  # Parâmetros válidos
        
        # Assert
        assert len(result.data) == 0
        mock_livro_usecase.listar_livros_paginado.assert_called_once_with(1, 10)
    
    def test_emprestar_livro_sucesso(self, mock_livro_usecase):
        """Teste de empréstimo de livro com sucesso."""
        # Arrange
        mock_livro_usecase.emprestar.return_value = Mock(id=1, livro_id=1, pessoa_id=1, usuario_id=1)
        
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        
        # Act
        result = controller.emprestar(1, 1, 1, mock_cache)
        
        # Assert
        assert result.id == 1
        mock_livro_usecase.emprestar.assert_called_once_with(1, 1, 1)
    
    def test_listar_emprestimos_paginado_sem_cache(self, mock_livro_usecase):
        """Teste de listagem paginada de empréstimos sem cache."""
        # Arrange
        from src.domain.enums.emprestimo_status import EmprestimoStatus
        mock_livro_usecase.listar_emprestimos_paginado.return_value = ([
            Mock(id=1, livro_id=1, pessoa_id=1, usuario_id=1, data_emprestimo=Mock(isoformat=lambda: "2023-01-01"), data_devolucao=None)
        ], 1)
        
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_emprestimos_paginado(1, 10, EmprestimoStatus.ATIVOS, mock_cache)
        
        # Assert
        assert len(result.data) == 1
        mock_livro_usecase.listar_emprestimos_paginado.assert_called_once_with(1, 10, EmprestimoStatus.ATIVOS)
    
    def test_listar_emprestimos_paginado_com_cache(self, mock_livro_usecase):
        """Teste de listagem paginada de empréstimos com cache."""
        # Arrange
        from src.domain.enums.emprestimo_status import EmprestimoStatus
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        
        # Mock do cache retornando dados válidos
        cached_data = '{"data": [{"id": 1, "livro_id": 1, "pessoa_id": 1, "usuario_id": 1, "data_emprestimo": "2023-01-01", "data_devolucao": null}], "meta": {"page": 1, "size": 10, "total": 1, "total_pages": 1, "has_next": false, "has_previous": false}}'
        mock_cache.get.return_value = cached_data
        
        # Act
        result = controller.listar_emprestimos_paginado(1, 10, EmprestimoStatus.ATIVOS, mock_cache)
        
        # Assert
        assert len(result.data) == 1
        mock_livro_usecase.listar_emprestimos_paginado.assert_not_called()
    
    def test_devolver_livro_sucesso(self, mock_livro_usecase):
        """Teste de devolução de livro com sucesso."""
        # Arrange
        mock_livro_usecase.devolver.return_value = Mock(id=1, livro_id=1, pessoa_id=1, usuario_id=1)
        
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        
        # Act
        result = controller.devolver(1, mock_cache)
        
        # Assert
        assert result.id == 1
        mock_livro_usecase.devolver.assert_called_once_with(1)
    
    def test_cache_keys_corretas(self, mock_livro_usecase):
        """Teste de verificação das chaves de cache."""
        # Arrange
        mock_livro_usecase.listar_livros_paginado.return_value = ([], 0)
        
        controller = LivroControllers(mock_livro_usecase)
        mock_cache = Mock()
        # Mock do cache retornando None (sem cache)
        mock_cache.get.return_value = None
        
        # Act
        result = controller.listar_paginado(1, 10, mock_cache)
        
        # Assert
        assert len(result.data) == 0
        mock_livro_usecase.listar_livros_paginado.assert_called_once_with(1, 10)