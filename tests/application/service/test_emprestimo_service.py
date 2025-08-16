"""
Testes para EmprestimoService - Fase 3 do plano de testes.
Testa operações atômicas, gerenciamento de transações, validações de negócio e integração com repositories.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime
from zoneinfo import ZoneInfo

from src.application.service.livro.emprestimo_service import EmprestimoService
from src.domain.model.emprestimo import Emprestimo
from src.domain.model.livro import Livro
from src.domain.enums.emprestimo_status import EmprestimoStatus
from src.domain.ports.emprestimo_repository import EmprestimoRepositoryPort
from src.domain.ports.livro_repository import LivroRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort


class TestEmprestimoService:
    """Testes para a classe EmprestimoService."""

    @pytest.fixture
    def mock_emprestimo_repository(self):
        """Mock do repository de empréstimo."""
        return Mock(spec=EmprestimoRepositoryPort)

    @pytest.fixture
    def mock_livro_repository(self):
        """Mock do repository de livro."""
        return Mock(spec=LivroRepositoryPort)

    @pytest.fixture
    def mock_uow(self):
        """Mock do Unit of Work."""
        return Mock(spec=UnitOfWorkPort)

    @pytest.fixture
    def timezone_sao_paulo(self):
        """Timezone de São Paulo para testes."""
        return ZoneInfo("America/Sao_Paulo")

    @pytest.fixture
    def service(self, mock_emprestimo_repository, mock_livro_repository, mock_uow, timezone_sao_paulo):
        """Instância do service para testes."""
        return EmprestimoService(mock_emprestimo_repository, mock_livro_repository, mock_uow, timezone_sao_paulo)

    @pytest.fixture
    def emprestimo_exemplo(self, timezone_sao_paulo):
        """Empréstimo de exemplo para testes."""
        return Emprestimo(
            id=1,
            livro_id=1,
            pessoa_id=1,
            usuario_id=1,
            data_emprestimo=datetime.now(timezone_sao_paulo),
            data_devolucao=None
        )

    @pytest.fixture
    def livro_exemplo(self):
        """Livro de exemplo para testes."""
        return Livro(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )

    def test_emprestar_livro_sucesso(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow, emprestimo_exemplo):
        """Testa empréstimo de livro com sucesso."""
        # Arrange
        livro_id, pessoa_id, usuario_id = 1, 1, 1
        mock_livro_repository.atualizar_disponibilidade.return_value = True
        mock_emprestimo_repository.criar.return_value = emprestimo_exemplo
        
        # Act
        resultado = service.emprestar(livro_id, pessoa_id, usuario_id)
        
        # Assert
        assert resultado == emprestimo_exemplo
        mock_livro_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, False)
        mock_emprestimo_repository.criar.assert_called_once()
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()
        
        # Verificar que o empréstimo foi criado com data atual
        args = mock_emprestimo_repository.criar.call_args[0][0]
        assert args.livro_id == livro_id
        assert args.pessoa_id == pessoa_id
        assert args.usuario_id == usuario_id
        assert args.data_emprestimo is not None
        assert args.data_devolucao is None

    def test_emprestar_livro_erro_disponibilidade_rollback(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow):
        """Testa que erro ao atualizar disponibilidade faz rollback."""
        # Arrange
        livro_id, pessoa_id, usuario_id = 1, 1, 1
        mock_livro_repository.atualizar_disponibilidade.side_effect = Exception("Erro ao atualizar livro")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro ao atualizar livro"):
            service.emprestar(livro_id, pessoa_id, usuario_id)
        
        mock_livro_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, False)
        mock_emprestimo_repository.criar.assert_not_called()
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_emprestar_livro_erro_criar_emprestimo_rollback(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow):
        """Testa que erro ao criar empréstimo faz rollback."""
        # Arrange
        livro_id, pessoa_id, usuario_id = 1, 1, 1
        mock_livro_repository.atualizar_disponibilidade.return_value = True
        mock_emprestimo_repository.criar.side_effect = Exception("Erro ao criar empréstimo")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro ao criar empréstimo"):
            service.emprestar(livro_id, pessoa_id, usuario_id)
        
        mock_livro_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, False)
        mock_emprestimo_repository.criar.assert_called_once()
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_devolver_livro_sucesso(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow, emprestimo_exemplo, timezone_sao_paulo):
        """Testa devolução de livro com sucesso."""
        # Arrange
        emprestimo_id, livro_id = 1, 1
        emprestimo_finalizado = Emprestimo(
            id=1,
            livro_id=1,
            pessoa_id=1,
            usuario_id=1,
            data_emprestimo=emprestimo_exemplo.data_emprestimo,
            data_devolucao=datetime.now(timezone_sao_paulo)
        )
        
        mock_emprestimo_repository.finalizar.return_value = emprestimo_finalizado
        mock_livro_repository.atualizar_disponibilidade.return_value = True
        
        # Act
        resultado = service.devolver(emprestimo_id, livro_id)
        
        # Assert
        assert resultado == emprestimo_finalizado
        assert resultado.data_devolucao is not None
        mock_emprestimo_repository.finalizar.assert_called_once_with(emprestimo_id)
        mock_livro_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, True)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_devolver_livro_emprestimo_nao_encontrado(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow):
        """Testa devolução quando empréstimo não é encontrado."""
        # Arrange
        emprestimo_id, livro_id = 999, 1
        mock_emprestimo_repository.finalizar.return_value = None
        
        # Act
        resultado = service.devolver(emprestimo_id, livro_id)
        
        # Assert
        assert resultado is None
        mock_emprestimo_repository.finalizar.assert_called_once_with(emprestimo_id)
        mock_livro_repository.atualizar_disponibilidade.assert_not_called()
        mock_uow.commit.assert_called_once()

    def test_devolver_livro_erro_finalizar_rollback(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow):
        """Testa que erro ao finalizar empréstimo faz rollback."""
        # Arrange
        emprestimo_id, livro_id = 1, 1
        mock_emprestimo_repository.finalizar.side_effect = Exception("Erro ao finalizar")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro ao finalizar"):
            service.devolver(emprestimo_id, livro_id)
        
        mock_emprestimo_repository.finalizar.assert_called_once_with(emprestimo_id)
        mock_livro_repository.atualizar_disponibilidade.assert_not_called()
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_devolver_livro_erro_atualizar_disponibilidade_rollback(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow, emprestimo_exemplo, timezone_sao_paulo):
        """Testa que erro ao atualizar disponibilidade do livro faz rollback."""
        # Arrange
        emprestimo_id, livro_id = 1, 1
        emprestimo_finalizado = Emprestimo(
            id=1, livro_id=1, pessoa_id=1, usuario_id=1,
            data_emprestimo=emprestimo_exemplo.data_emprestimo,
            data_devolucao=datetime.now(timezone_sao_paulo)
        )
        
        mock_emprestimo_repository.finalizar.return_value = emprestimo_finalizado
        mock_livro_repository.atualizar_disponibilidade.side_effect = Exception("Erro ao atualizar livro")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro ao atualizar livro"):
            service.devolver(emprestimo_id, livro_id)
        
        mock_emprestimo_repository.finalizar.assert_called_once_with(emprestimo_id)
        mock_livro_repository.atualizar_disponibilidade.assert_called_once_with(livro_id, True)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_buscar_ativo_por_livro_encontrado(self, service, mock_emprestimo_repository, mock_uow, emprestimo_exemplo):
        """Testa busca de empréstimo ativo por livro quando existe."""
        # Arrange
        livro_id = 1
        mock_emprestimo_repository.buscar_ativo_por_livro.return_value = emprestimo_exemplo
        
        # Act
        resultado = service.buscar_ativo_por_livro(livro_id)
        
        # Assert
        assert resultado == emprestimo_exemplo
        mock_emprestimo_repository.buscar_ativo_por_livro.assert_called_once_with(livro_id)
        # Operação de leitura não deve usar transação
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_buscar_ativo_por_livro_nao_encontrado(self, service, mock_emprestimo_repository, mock_uow):
        """Testa busca de empréstimo ativo por livro quando não existe."""
        # Arrange
        livro_id = 999
        mock_emprestimo_repository.buscar_ativo_por_livro.return_value = None
        
        # Act
        resultado = service.buscar_ativo_por_livro(livro_id)
        
        # Assert
        assert resultado is None
        mock_emprestimo_repository.buscar_ativo_por_livro.assert_called_once_with(livro_id)

    def test_listar_paginado_status_ativos(self, service, mock_emprestimo_repository, mock_uow, emprestimo_exemplo):
        """Testa listagem paginada de empréstimos ativos."""
        # Arrange
        emprestimos = [emprestimo_exemplo]
        total = 5
        page, size = 1, 10
        mock_emprestimo_repository.listar_paginado.return_value = (emprestimos, total)
        
        # Act
        resultado_emprestimos, resultado_total = service.listar_paginado(page, size, EmprestimoStatus.ATIVOS)
        
        # Assert
        assert resultado_emprestimos == emprestimos
        assert resultado_total == total
        mock_emprestimo_repository.listar_paginado.assert_called_once_with(page, size, EmprestimoStatus.ATIVOS)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_paginado_status_devolvidos(self, service, mock_emprestimo_repository, mock_uow, timezone_sao_paulo):
        """Testa listagem paginada de empréstimos devolvidos."""
        # Arrange
        emprestimo_devolvido = Emprestimo(
            id=1, livro_id=1, pessoa_id=1, usuario_id=1,
            data_emprestimo=datetime.now(timezone_sao_paulo),
            data_devolucao=datetime.now(timezone_sao_paulo)
        )
        emprestimos = [emprestimo_devolvido]
        total = 3
        page, size = 1, 10
        mock_emprestimo_repository.listar_paginado.return_value = (emprestimos, total)
        
        # Act
        resultado_emprestimos, resultado_total = service.listar_paginado(page, size, EmprestimoStatus.DEVOLVIDOS)
        
        # Assert
        assert resultado_emprestimos == emprestimos
        assert resultado_total == total
        mock_emprestimo_repository.listar_paginado.assert_called_once_with(page, size, EmprestimoStatus.DEVOLVIDOS)

    def test_listar_paginado_status_todos(self, service, mock_emprestimo_repository, mock_uow, emprestimo_exemplo, timezone_sao_paulo):
        """Testa listagem paginada de todos os empréstimos."""
        # Arrange
        emprestimo_devolvido = Emprestimo(
            id=2, livro_id=2, pessoa_id=2, usuario_id=1,
            data_emprestimo=datetime.now(timezone_sao_paulo),
            data_devolucao=datetime.now(timezone_sao_paulo)
        )
        emprestimos = [emprestimo_exemplo, emprestimo_devolvido]
        total = 8
        page, size = 1, 10
        mock_emprestimo_repository.listar_paginado.return_value = (emprestimos, total)
        
        # Act
        resultado_emprestimos, resultado_total = service.listar_paginado(page, size, EmprestimoStatus.TODOS)
        
        # Assert
        assert resultado_emprestimos == emprestimos
        assert resultado_total == total
        assert len(resultado_emprestimos) == 2
        mock_emprestimo_repository.listar_paginado.assert_called_once_with(page, size, EmprestimoStatus.TODOS)

    def test_listar_paginado_sem_parametro_status_usa_default(self, service, mock_emprestimo_repository, mock_uow, emprestimo_exemplo):
        """Testa que listagem sem parâmetro de status usa ATIVOS como padrão."""
        # Arrange
        emprestimos = [emprestimo_exemplo]
        total = 1
        page, size = 1, 5
        mock_emprestimo_repository.listar_paginado.return_value = (emprestimos, total)
        
        # Act
        resultado_emprestimos, resultado_total = service.listar_paginado(page, size)
        
        # Assert
        assert resultado_emprestimos == emprestimos
        assert resultado_total == total
        # Deve usar ATIVOS como padrão
        mock_emprestimo_repository.listar_paginado.assert_called_once_with(page, size, EmprestimoStatus.ATIVOS)

    def test_fluxo_completo_emprestimo_devolucao(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow, timezone_sao_paulo):
        """Testa fluxo completo de empréstimo e devolução."""
        # Arrange
        livro_id, pessoa_id, usuario_id = 1, 1, 1
        emprestimo_criado = Emprestimo(
            id=1, livro_id=livro_id, pessoa_id=pessoa_id, usuario_id=usuario_id,
            data_emprestimo=datetime.now(timezone_sao_paulo), data_devolucao=None
        )
        emprestimo_finalizado = Emprestimo(
            id=1, livro_id=livro_id, pessoa_id=pessoa_id, usuario_id=usuario_id,
            data_emprestimo=emprestimo_criado.data_emprestimo,
            data_devolucao=datetime.now(timezone_sao_paulo)
        )
        
        # Setup mocks para empréstimo
        mock_livro_repository.atualizar_disponibilidade.return_value = True
        mock_emprestimo_repository.criar.return_value = emprestimo_criado
        mock_emprestimo_repository.buscar_ativo_por_livro.side_effect = [emprestimo_criado, None]
        
        # Setup mocks para devolução
        mock_emprestimo_repository.finalizar.return_value = emprestimo_finalizado
        
        # Act - Emprestar
        resultado_emprestimo = service.emprestar(livro_id, pessoa_id, usuario_id)
        
        # Act - Verificar empréstimo ativo
        emprestimo_ativo = service.buscar_ativo_por_livro(livro_id)
        
        # Act - Devolver
        resultado_devolucao = service.devolver(resultado_emprestimo.id, livro_id)
        
        # Act - Verificar que não há mais empréstimo ativo
        emprestimo_ativo_apos = service.buscar_ativo_por_livro(livro_id)
        
        # Assert
        assert resultado_emprestimo.data_devolucao is None
        assert emprestimo_ativo is not None
        assert resultado_devolucao.data_devolucao is not None
        assert emprestimo_ativo_apos is None
        
        # Verificar transações (2 operações transacionais: emprestar e devolver)
        assert mock_uow.commit.call_count == 2
        assert mock_uow.rollback.call_count == 0
        
        # Verificar chamadas para disponibilidade do livro
        assert mock_livro_repository.atualizar_disponibilidade.call_count == 2
        mock_livro_repository.atualizar_disponibilidade.assert_any_call(livro_id, False)  # Empréstimo
        mock_livro_repository.atualizar_disponibilidade.assert_any_call(livro_id, True)   # Devolução

    def test_multiplos_emprestimos_diferentes_livros(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow, timezone_sao_paulo):
        """Testa múltiplos empréstimos de livros diferentes."""
        # Arrange
        emprestimo1 = Emprestimo(1, 1, 1, 1, datetime.now(timezone_sao_paulo), None)
        emprestimo2 = Emprestimo(2, 2, 2, 1, datetime.now(timezone_sao_paulo), None)
        
        mock_livro_repository.atualizar_disponibilidade.return_value = True
        mock_emprestimo_repository.criar.side_effect = [emprestimo1, emprestimo2]
        
        # Act
        resultado1 = service.emprestar(1, 1, 1)
        resultado2 = service.emprestar(2, 2, 1)
        
        # Assert
        assert resultado1 == emprestimo1
        assert resultado2 == emprestimo2
        assert mock_uow.commit.call_count == 2
        assert mock_livro_repository.atualizar_disponibilidade.call_count == 2

    def test_timezone_aplicado_corretamente(self, service, mock_emprestimo_repository, mock_livro_repository, mock_uow, timezone_sao_paulo):
        """Testa que timezone é aplicado corretamente nas datas."""
        # Arrange
        livro_id, pessoa_id, usuario_id = 1, 1, 1
        mock_livro_repository.atualizar_disponibilidade.return_value = True
        mock_emprestimo_repository.criar.return_value = Mock()
        
        # Act
        service.emprestar(livro_id, pessoa_id, usuario_id)
        
        # Assert
        args = mock_emprestimo_repository.criar.call_args[0][0]
        assert args.data_emprestimo.tzinfo == timezone_sao_paulo

    def test_heranca_base_service(self, service):
        """Testa que EmprestimoService herda corretamente de BaseService."""
        # Assert
        from src.application.service.base_service import BaseService
        assert isinstance(service, BaseService)
        assert hasattr(service, '_executar_transacao')
        assert hasattr(service, 'uow')

    def test_interface_repositories_definidas(self, service, mock_emprestimo_repository, mock_livro_repository):
        """Testa que o service usa as interfaces corretas dos repositories."""
        # Assert
        assert service.repositorio == mock_emprestimo_repository
        assert service.livros == mock_livro_repository
        
        # Verificar métodos do emprestimo repository
        assert hasattr(mock_emprestimo_repository, 'criar')
        assert hasattr(mock_emprestimo_repository, 'finalizar')
        assert hasattr(mock_emprestimo_repository, 'buscar_ativo_por_livro')
        assert hasattr(mock_emprestimo_repository, 'listar_paginado')
        
        # Verificar métodos do livro repository
        assert hasattr(mock_livro_repository, 'atualizar_disponibilidade')

    def test_configuracao_timezone_service(self, service, timezone_sao_paulo):
        """Testa que o service está configurado com o timezone correto."""
        # Assert
        assert service._tz == timezone_sao_paulo