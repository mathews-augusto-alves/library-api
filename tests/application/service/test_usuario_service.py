"""
Testes para UsuarioService - Fase 3 do plano de testes.
Testa operações atômicas, gerenciamento de transações, validações de negócio e integração com repositories.
"""
import pytest
from unittest.mock import Mock, call
from typing import Optional

from src.application.service.usuario.usuario_service import UsuarioService
from src.domain.model.usuario import Usuario
from src.domain.ports.usuario_repository import UsuarioRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort


class TestUsuarioService:
    """Testes para a classe UsuarioService."""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repository de usuário."""
        return Mock(spec=UsuarioRepositoryPort)

    @pytest.fixture
    def mock_uow(self):
        """Mock do Unit of Work."""
        return Mock(spec=UnitOfWorkPort)

    @pytest.fixture
    def service(self, mock_repository, mock_uow):
        """Instância do service para testes."""
        return UsuarioService(mock_repository, mock_uow)

    @pytest.fixture
    def usuario_exemplo(self):
        """Usuário de exemplo para testes."""
        return Usuario(
            id=1,
            nome="João Silva",
            email="joao@email.com",
            senha_hash="hash123"
        )

    def test_criar_usuario_sucesso(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa criação de usuário com sucesso."""
        # Arrange
        usuario_sem_id = Usuario(None, "João Silva", "joao@email.com", "hash123")
        mock_repository.criar.return_value = usuario_exemplo
        
        # Act
        resultado = service.criar(usuario_sem_id)
        
        # Assert
        assert resultado == usuario_exemplo
        mock_repository.criar.assert_called_once_with(usuario_sem_id)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_criar_usuario_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na criação faz rollback da transação."""
        # Arrange
        usuario = Usuario(None, "João Silva", "joao@email.com", "hash123")
        mock_repository.criar.side_effect = Exception("Erro no banco")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro no banco"):
            service.criar(usuario)
        
        mock_repository.criar.assert_called_once_with(usuario)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_atualizar_usuario_sucesso(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa atualização de usuário com sucesso."""
        # Arrange
        usuario_id = 1
        usuario_atualizado = Usuario(1, "João Santos", "joao.santos@email.com", "hash456")
        mock_repository.atualizar.return_value = usuario_atualizado
        
        # Act
        resultado = service.atualizar(usuario_id, usuario_atualizado)
        
        # Assert
        assert resultado == usuario_atualizado
        mock_repository.atualizar.assert_called_once_with(usuario_id, usuario_atualizado)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_atualizar_usuario_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa atualização de usuário que não existe."""
        # Arrange
        usuario_id = 999
        usuario = Usuario(999, "João Silva", "joao@email.com", "hash123")
        mock_repository.atualizar.return_value = None
        
        # Act
        resultado = service.atualizar(usuario_id, usuario)
        
        # Assert
        assert resultado is None
        mock_repository.atualizar.assert_called_once_with(usuario_id, usuario)
        mock_uow.commit.assert_called_once()

    def test_atualizar_usuario_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na atualização faz rollback da transação."""
        # Arrange
        usuario_id = 1
        usuario = Usuario(1, "João Silva", "joao@email.com", "hash123")
        mock_repository.atualizar.side_effect = Exception("Erro na atualização")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro na atualização"):
            service.atualizar(usuario_id, usuario)
        
        mock_repository.atualizar.assert_called_once_with(usuario_id, usuario)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_remover_usuario_sucesso(self, service, mock_repository, mock_uow):
        """Testa remoção de usuário com sucesso."""
        # Arrange
        usuario_id = 1
        mock_repository.remover.return_value = True
        
        # Act
        resultado = service.remover(usuario_id)
        
        # Assert
        assert resultado is True
        mock_repository.remover.assert_called_once_with(usuario_id)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_remover_usuario_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa remoção de usuário que não existe."""
        # Arrange
        usuario_id = 999
        mock_repository.remover.return_value = False
        
        # Act
        resultado = service.remover(usuario_id)
        
        # Assert
        assert resultado is False
        mock_repository.remover.assert_called_once_with(usuario_id)
        mock_uow.commit.assert_called_once()

    def test_remover_usuario_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na remoção faz rollback da transação."""
        # Arrange
        usuario_id = 1
        mock_repository.remover.side_effect = Exception("Erro na remoção")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro na remoção"):
            service.remover(usuario_id)
        
        mock_repository.remover.assert_called_once_with(usuario_id)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_listar_usuarios(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa listagem de usuários."""
        # Arrange
        usuarios = [usuario_exemplo, Usuario(2, "Maria", "maria@email.com", "hash456")]
        mock_repository.listar.return_value = usuarios
        
        # Act
        resultado = service.listar()
        
        # Assert
        assert resultado == usuarios
        assert len(resultado) == 2
        mock_repository.listar.assert_called_once()
        # Operações de leitura não devem usar transação
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_usuarios_vazio(self, service, mock_repository, mock_uow):
        """Testa listagem quando não há usuários."""
        # Arrange
        mock_repository.listar.return_value = []
        
        # Act
        resultado = service.listar()
        
        # Assert
        assert resultado == []
        mock_repository.listar.assert_called_once()
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_paginado_sucesso(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa listagem paginada de usuários."""
        # Arrange
        usuarios = [usuario_exemplo]
        total = 10
        page, size = 1, 5
        # Adicionar método ao mock
        mock_repository.listar_paginado = Mock(return_value=(usuarios, total))
        
        # Act
        resultado_usuarios, resultado_total = service.listar_paginado(page, size)
        
        # Assert
        assert resultado_usuarios == usuarios
        assert resultado_total == total
        mock_repository.listar_paginado.assert_called_once_with(page, size)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_paginado_pagina_vazia(self, service, mock_repository, mock_uow):
        """Testa listagem paginada com página vazia."""
        # Arrange
        page, size = 2, 5
        # Adicionar método ao mock
        mock_repository.listar_paginado = Mock(return_value=([], 0))
        
        # Act
        resultado_usuarios, resultado_total = service.listar_paginado(page, size)
        
        # Assert
        assert resultado_usuarios == []
        assert resultado_total == 0
        mock_repository.listar_paginado.assert_called_once_with(page, size)

    def test_buscar_por_id_encontrado(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa busca por ID quando usuário existe."""
        # Arrange
        usuario_id = 1
        mock_repository.buscar_por_id.return_value = usuario_exemplo
        
        # Act
        resultado = service.buscar_por_id(usuario_id)
        
        # Assert
        assert resultado == usuario_exemplo
        mock_repository.buscar_por_id.assert_called_once_with(usuario_id)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_buscar_por_id_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa busca por ID quando usuário não existe."""
        # Arrange
        usuario_id = 999
        mock_repository.buscar_por_id.return_value = None
        
        # Act
        resultado = service.buscar_por_id(usuario_id)
        
        # Assert
        assert resultado is None
        mock_repository.buscar_por_id.assert_called_once_with(usuario_id)

    def test_buscar_por_email_encontrado(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa busca por email quando usuário existe."""
        # Arrange
        email = "joao@email.com"
        mock_repository.buscar_por_email.return_value = usuario_exemplo
        
        # Act
        resultado = service.buscar_por_email(email)
        
        # Assert
        assert resultado == usuario_exemplo
        mock_repository.buscar_por_email.assert_called_once_with(email)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_buscar_por_email_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa busca por email quando usuário não existe."""
        # Arrange
        email = "naoexiste@email.com"
        mock_repository.buscar_por_email.return_value = None
        
        # Act
        resultado = service.buscar_por_email(email)
        
        # Assert
        assert resultado is None
        mock_repository.buscar_por_email.assert_called_once_with(email)

    def test_operacoes_transacionais_vs_nao_transacionais(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa diferença entre operações transacionais e não transacionais."""
        # Arrange
        usuario = Usuario(None, "João Silva", "joao@email.com", "hash123")
        mock_repository.criar.return_value = usuario_exemplo
        mock_repository.listar.return_value = [usuario_exemplo]
        mock_repository.buscar_por_id.return_value = usuario_exemplo
        
        # Act - Operação transacional
        service.criar(usuario)
        
        # Act - Operações não transacionais
        service.listar()
        service.buscar_por_id(1)
        
        # Assert - Apenas a operação de criação deve usar transação
        assert mock_uow.commit.call_count == 1
        assert mock_uow.rollback.call_count == 0
        
        mock_repository.criar.assert_called_once()
        mock_repository.listar.assert_called_once()
        mock_repository.buscar_por_id.assert_called_once()

    def test_multiplas_operacoes_transacionais(self, service, mock_repository, mock_uow, usuario_exemplo):
        """Testa múltiplas operações transacionais consecutivas."""
        # Arrange
        usuario1 = Usuario(None, "João", "joao@email.com", "hash1")
        usuario2 = Usuario(None, "Maria", "maria@email.com", "hash2")
        
        mock_repository.criar.side_effect = [
            Usuario(1, "João", "joao@email.com", "hash1"),
            Usuario(2, "Maria", "maria@email.com", "hash2")
        ]
        mock_repository.remover.return_value = True
        
        # Act
        service.criar(usuario1)
        service.criar(usuario2)
        service.remover(1)
        
        # Assert
        assert mock_uow.commit.call_count == 3
        assert mock_uow.rollback.call_count == 0
        
        assert mock_repository.criar.call_count == 2
        mock_repository.remover.assert_called_once_with(1)

    def test_transacao_com_erro_parcial(self, service, mock_repository, mock_uow):
        """Testa comportamento quando uma transação falha entre várias operações."""
        # Arrange
        usuario1 = Usuario(None, "João", "joao@email.com", "hash1")
        usuario2 = Usuario(None, "Maria", "maria@email.com", "hash2")
        
        mock_repository.criar.side_effect = [
            Usuario(1, "João", "joao@email.com", "hash1"),  # Primeira operação OK
            Exception("Erro na segunda operação")           # Segunda operação falha
        ]
        
        # Act
        resultado1 = service.criar(usuario1)  # Deve funcionar
        
        with pytest.raises(Exception, match="Erro na segunda operação"):
            service.criar(usuario2)  # Deve falhar
        
        # Assert
        assert resultado1 is not None
        assert mock_uow.commit.call_count == 1  # Apenas primeira operação commitada
        assert mock_uow.rollback.call_count == 1  # Segunda operação fez rollback
        assert mock_repository.criar.call_count == 2

    def test_heranca_base_service(self, service):
        """Testa que UsuarioService herda corretamente de BaseService."""
        # Assert
        from src.application.service.base_service import BaseService
        assert isinstance(service, BaseService)
        assert hasattr(service, '_executar_transacao')
        assert hasattr(service, 'uow')

    def test_interface_repository_definida(self, service, mock_repository):
        """Testa que o service usa a interface correta do repository."""
        # Assert
        assert service.repositorio == mock_repository
        
        # Verificar que todos os métodos necessários estão disponíveis
        assert hasattr(mock_repository, 'criar')
        assert hasattr(mock_repository, 'atualizar')
        assert hasattr(mock_repository, 'remover')
        assert hasattr(mock_repository, 'listar')
        assert hasattr(mock_repository, 'buscar_por_id')
        assert hasattr(mock_repository, 'buscar_por_email')