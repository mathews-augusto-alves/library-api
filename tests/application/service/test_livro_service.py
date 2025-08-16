"""
Testes para LivroService - Fase 3 do plano de testes.
Testa operações atômicas, gerenciamento de transações, validações de negócio e integração com repositories.
"""
import pytest
from unittest.mock import Mock

from src.application.service.livro.livro_service import LivroService
from src.domain.model.livro import Livro
from src.domain.ports.livro_repository import LivroRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort


class TestLivroService:
    """Testes para a classe LivroService."""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repository de livro."""
        return Mock(spec=LivroRepositoryPort)

    @pytest.fixture
    def mock_uow(self):
        """Mock do Unit of Work."""
        return Mock(spec=UnitOfWorkPort)

    @pytest.fixture
    def service(self, mock_repository, mock_uow):
        """Instância do service para testes."""
        return LivroService(mock_repository, mock_uow)

    @pytest.fixture
    def livro_exemplo(self):
        """Livro de exemplo para testes."""
        return Livro(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )

    def test_criar_livro_sucesso(self, service, mock_repository, mock_uow, livro_exemplo):
        """Testa criação de livro com sucesso."""
        # Arrange
        livro_sem_id = Livro(None, "O Senhor dos Anéis", "J.R.R. Tolkien", True)
        mock_repository.criar.return_value = livro_exemplo
        
        # Act
        resultado = service.criar(livro_sem_id)
        
        # Assert
        assert resultado == livro_exemplo
        mock_repository.criar.assert_called_once_with(livro_sem_id)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_criar_livro_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na criação faz rollback da transação."""
        # Arrange
        livro = Livro(None, "1984", "George Orwell", True)
        mock_repository.criar.side_effect = Exception("Erro no banco")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro no banco"):
            service.criar(livro)
        
        mock_repository.criar.assert_called_once_with(livro)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_listar_livros(self, service, mock_repository, mock_uow, livro_exemplo):
        """Testa listagem de livros."""
        # Arrange
        livros = [
            livro_exemplo,
            Livro(2, "1984", "George Orwell", False)
        ]
        mock_repository.listar.return_value = livros
        
        # Act
        resultado = service.listar()
        
        # Assert
        assert resultado == livros
        assert len(resultado) == 2
        mock_repository.listar.assert_called_once()
        # Operações de leitura não devem usar transação
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_livros_vazio(self, service, mock_repository, mock_uow):
        """Testa listagem quando não há livros."""
        # Arrange
        mock_repository.listar.return_value = []
        
        # Act
        resultado = service.listar()
        
        # Assert
        assert resultado == []
        mock_repository.listar.assert_called_once()
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_paginado_sucesso(self, service, mock_repository, mock_uow, livro_exemplo):
        """Testa listagem paginada de livros."""
        # Arrange
        livros = [livro_exemplo]
        total = 15
        page, size = 1, 10
        # Adicionar método ao mock
        mock_repository.listar_paginado = Mock(return_value=(livros, total))
        
        # Act
        resultado_livros, resultado_total = service.listar_paginado(page, size)
        
        # Assert
        assert resultado_livros == livros
        assert resultado_total == total
        mock_repository.listar_paginado.assert_called_once_with(page, size)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_paginado_pagina_vazia(self, service, mock_repository, mock_uow):
        """Testa listagem paginada com página vazia."""
        # Arrange
        page, size = 3, 10
        # Adicionar método ao mock
        mock_repository.listar_paginado = Mock(return_value=([], 0))
        
        # Act
        resultado_livros, resultado_total = service.listar_paginado(page, size)
        
        # Assert
        assert resultado_livros == []
        assert resultado_total == 0
        mock_repository.listar_paginado.assert_called_once_with(page, size)

    def test_buscar_por_id_encontrado(self, service, mock_repository, mock_uow, livro_exemplo):
        """Testa busca por ID quando livro existe."""
        # Arrange
        livro_id = 1
        mock_repository.buscar_por_id.return_value = livro_exemplo
        
        # Act
        resultado = service.buscar_por_id(livro_id)
        
        # Assert
        assert resultado == livro_exemplo
        mock_repository.buscar_por_id.assert_called_once_with(livro_id)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_buscar_por_id_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa busca por ID quando livro não existe."""
        # Arrange
        livro_id = 999
        mock_repository.buscar_por_id.return_value = None
        
        # Act
        resultado = service.buscar_por_id(livro_id)
        
        # Assert
        assert resultado is None
        mock_repository.buscar_por_id.assert_called_once_with(livro_id)

    def test_set_disponibilidade_para_indisponivel_sucesso(self, service, mock_repository, mock_uow):
        """Testa atualização de disponibilidade para indisponível."""
        # Arrange
        livro_id = 1
        livro_atualizado = Livro(1, "O Senhor dos Anéis", "J.R.R. Tolkien", False)
        mock_repository.atualizar_disponibilidade.return_value = livro_atualizado
        
        # Act
        resultado = service.set_disponibilidade(livro_id, False)
        
        # Assert
        assert resultado == livro_atualizado
        assert resultado.disponivel is False
        mock_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, False)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_set_disponibilidade_para_disponivel_sucesso(self, service, mock_repository, mock_uow):
        """Testa atualização de disponibilidade para disponível."""
        # Arrange
        livro_id = 1
        livro_atualizado = Livro(1, "1984", "George Orwell", True)
        mock_repository.atualizar_disponibilidade.return_value = livro_atualizado
        
        # Act
        resultado = service.set_disponibilidade(livro_id, True)
        
        # Assert
        assert resultado == livro_atualizado
        assert resultado.disponivel is True
        mock_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, True)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_set_disponibilidade_livro_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa atualização de disponibilidade de livro que não existe."""
        # Arrange
        livro_id = 999
        mock_repository.atualizar_disponibilidade.return_value = None
        
        # Act
        resultado = service.set_disponibilidade(livro_id, True)
        
        # Assert
        assert resultado is None
        mock_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, True)
        mock_uow.commit.assert_called_once()

    def test_set_disponibilidade_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na atualização de disponibilidade faz rollback."""
        # Arrange
        livro_id = 1
        mock_repository.atualizar_disponibilidade.side_effect = Exception("Erro na atualização")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro na atualização"):
            service.set_disponibilidade(livro_id, False)
        
        mock_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, False)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_operacoes_transacionais_vs_nao_transacionais(self, service, mock_repository, mock_uow, livro_exemplo):
        """Testa diferença entre operações transacionais e não transacionais."""
        # Arrange
        livro = Livro(None, "Dune", "Frank Herbert", True)
        mock_repository.criar.return_value = livro_exemplo
        mock_repository.listar.return_value = [livro_exemplo]
        mock_repository.buscar_por_id.return_value = livro_exemplo
        mock_repository.atualizar_disponibilidade.return_value = livro_exemplo
        
        # Act - Operação transacional
        service.criar(livro)
        service.set_disponibilidade(1, False)
        
        # Act - Operações não transacionais  
        service.listar()
        service.buscar_por_id(1)
        
        # Assert - Apenas as operações de criação e atualização devem usar transação
        assert mock_uow.commit.call_count == 2
        assert mock_uow.rollback.call_count == 0
        
        mock_repository.criar.assert_called_once()
        mock_repository.atualizar_disponibilidade.assert_called_once()
        mock_repository.listar.assert_called_once()
        mock_repository.buscar_por_id.assert_called_once()

    def test_multiplas_operacoes_disponibilidade(self, service, mock_repository, mock_uow):
        """Testa múltiplas operações de atualização de disponibilidade."""
        # Arrange
        livro_indisponivel = Livro(1, "Livro 1", "Autor 1", False)
        livro_disponivel = Livro(1, "Livro 1", "Autor 1", True)
        
        mock_repository.atualizar_disponibilidade.side_effect = [
            livro_indisponivel,  # Primeira chamada: torna indisponível
            livro_disponivel     # Segunda chamada: torna disponível
        ]
        
        # Act
        resultado1 = service.set_disponibilidade(1, False)
        resultado2 = service.set_disponibilidade(1, True)
        
        # Assert
        assert resultado1.disponivel is False
        assert resultado2.disponivel is True
        assert mock_uow.commit.call_count == 2
        assert mock_repository.atualizar_disponibilidade.call_count == 2

    def test_gerenciamento_estado_livro(self, service, mock_repository, mock_uow, livro_exemplo):
        """Testa operações que gerenciam o estado do livro."""
        # Arrange
        livro_novo = Livro(None, "Novo Livro", "Novo Autor", True)
        livro_criado = Livro(1, "Novo Livro", "Novo Autor", True)
        livro_emprestado = Livro(1, "Novo Livro", "Novo Autor", False)
        
        mock_repository.criar.return_value = livro_criado
        mock_repository.atualizar_disponibilidade.return_value = livro_emprestado
        mock_repository.buscar_por_id.return_value = livro_emprestado
        
        # Act - Simular fluxo completo: criar livro, emprestar (indisponível), consultar
        livro_resultado = service.criar(livro_novo)
        service.set_disponibilidade(livro_resultado.id, False)  # Simular empréstimo
        livro_atual = service.buscar_por_id(livro_resultado.id)
        
        # Assert
        assert livro_resultado.disponivel is True  # Criado como disponível
        assert livro_atual.disponivel is False     # Após empréstimo, indisponível
        assert mock_uow.commit.call_count == 2     # Apenas operações transacionais

    def test_heranca_base_service(self, service):
        """Testa que LivroService herda corretamente de BaseService."""
        # Assert
        from src.application.service.base_service import BaseService
        assert isinstance(service, BaseService)
        assert hasattr(service, '_executar_transacao')
        assert hasattr(service, 'uow')

    def test_interface_repository_definida(self, service, mock_repository):
        """Testa que o service usa a interface correta do repository."""
        # Assert
        assert service.repository == mock_repository
        
        # Verificar que todos os métodos necessários estão disponíveis
        assert hasattr(mock_repository, 'criar')
        assert hasattr(mock_repository, 'listar')
        assert hasattr(mock_repository, 'buscar_por_id')
        assert hasattr(mock_repository, 'atualizar_disponibilidade')

    def test_fluxo_emprestimo_devolucao_simulado(self, service, mock_repository, mock_uow):
        """Testa fluxo simulado de empréstimo e devolução através do service."""
        # Arrange
        livro_id = 1
        livro_disponivel = Livro(1, "Livro Teste", "Autor Teste", True)
        livro_emprestado = Livro(1, "Livro Teste", "Autor Teste", False)
        
        mock_repository.buscar_por_id.return_value = livro_disponivel
        mock_repository.atualizar_disponibilidade.side_effect = [
            livro_emprestado,   # Empréstimo
            livro_disponivel    # Devolução
        ]
        
        # Act - Simular empréstimo
        livro_antes = service.buscar_por_id(livro_id)
        assert livro_antes.disponivel is True
        
        resultado_emprestimo = service.set_disponibilidade(livro_id, False)
        
        # Act - Simular devolução
        resultado_devolucao = service.set_disponibilidade(livro_id, True)
        
        # Assert
        assert resultado_emprestimo.disponivel is False
        assert resultado_devolucao.disponivel is True
        assert mock_uow.commit.call_count == 2  # Duas operações transacionais