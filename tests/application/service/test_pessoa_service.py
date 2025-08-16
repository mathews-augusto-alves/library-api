"""
Testes para PessoaService - Fase 3 do plano de testes.
Testa operações atômicas, gerenciamento de transações, validações de negócio e integração com repositories.
"""
import pytest
from unittest.mock import Mock
from datetime import date

from src.application.service.pessoa.pessoa_service import PessoaService
from src.domain.model.pessoa import Pessoa
from src.domain.ports.pessoa_repository import PessoaRepositoryPort
from src.domain.ports.unit_of_work import UnitOfWorkPort


class TestPessoaService:
    """Testes para a classe PessoaService."""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repository de pessoa."""
        return Mock(spec=PessoaRepositoryPort)

    @pytest.fixture
    def mock_uow(self):
        """Mock do Unit of Work."""
        return Mock(spec=UnitOfWorkPort)

    @pytest.fixture
    def service(self, mock_repository, mock_uow):
        """Instância do service para testes."""
        return PessoaService(mock_repository, mock_uow)

    @pytest.fixture
    def pessoa_exemplo(self):
        """Pessoa de exemplo para testes."""
        return Pessoa(
            id=1,
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 5, 15),
            email="maria@email.com"
        )

    def test_criar_pessoa_sucesso(self, service, mock_repository, mock_uow, pessoa_exemplo):
        """Testa criação de pessoa com sucesso."""
        # Arrange
        pessoa_sem_id = Pessoa(None, "Maria Santos", "11999999999", date(1990, 5, 15), "maria@email.com")
        mock_repository.criar.return_value = pessoa_exemplo
        
        # Act
        resultado = service.criar_pessoa(pessoa_sem_id)
        
        # Assert
        assert resultado == pessoa_exemplo
        mock_repository.criar.assert_called_once_with(pessoa_sem_id)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_criar_pessoa_sem_email_sucesso(self, service, mock_repository, mock_uow):
        """Testa criação de pessoa sem email."""
        # Arrange
        pessoa_sem_email = Pessoa(None, "João Silva", "11888888888", date(1985, 10, 20), None)
        pessoa_criada = Pessoa(1, "João Silva", "11888888888", date(1985, 10, 20), None)
        mock_repository.criar.return_value = pessoa_criada
        
        # Act
        resultado = service.criar_pessoa(pessoa_sem_email)
        
        # Assert
        assert resultado == pessoa_criada
        assert resultado.email is None
        mock_repository.criar.assert_called_once_with(pessoa_sem_email)
        mock_uow.commit.assert_called_once()

    def test_criar_pessoa_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na criação faz rollback da transação."""
        # Arrange
        pessoa = Pessoa(None, "Ana Costa", "11777777777", date(1992, 3, 8), "ana@email.com")
        mock_repository.criar.side_effect = Exception("Erro no banco")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro no banco"):
            service.criar_pessoa(pessoa)
        
        mock_repository.criar.assert_called_once_with(pessoa)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_listar_pessoas(self, service, mock_repository, mock_uow, pessoa_exemplo):
        """Testa listagem de pessoas."""
        # Arrange
        pessoas = [
            pessoa_exemplo,
            Pessoa(2, "João Silva", "11888888888", date(1985, 10, 20), None)
        ]
        mock_repository.listar.return_value = pessoas
        
        # Act
        resultado = service.listar_pessoas()
        
        # Assert
        assert resultado == pessoas
        assert len(resultado) == 2
        mock_repository.listar.assert_called_once()
        # Operações de leitura não devem usar transação
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_pessoas_vazio(self, service, mock_repository, mock_uow):
        """Testa listagem quando não há pessoas."""
        # Arrange
        mock_repository.listar.return_value = []
        
        # Act
        resultado = service.listar_pessoas()
        
        # Assert
        assert resultado == []
        mock_repository.listar.assert_called_once()
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_pessoas_paginado_sucesso(self, service, mock_repository, mock_uow, pessoa_exemplo):
        """Testa listagem paginada de pessoas."""
        # Arrange
        pessoas = [pessoa_exemplo]
        total = 25
        page, size = 1, 10
        mock_repository.listar_paginado.return_value = (pessoas, total)
        
        # Act
        resultado_pessoas, resultado_total = service.listar_pessoas_paginado(page, size)
        
        # Assert
        assert resultado_pessoas == pessoas
        assert resultado_total == total
        mock_repository.listar_paginado.assert_called_once_with(page, size)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_listar_pessoas_paginado_pagina_vazia(self, service, mock_repository, mock_uow):
        """Testa listagem paginada com página vazia."""
        # Arrange
        page, size = 5, 10
        mock_repository.listar_paginado.return_value = ([], 0)
        
        # Act
        resultado_pessoas, resultado_total = service.listar_pessoas_paginado(page, size)
        
        # Assert
        assert resultado_pessoas == []
        assert resultado_total == 0
        mock_repository.listar_paginado.assert_called_once_with(page, size)

    def test_buscar_por_id_encontrado(self, service, mock_repository, mock_uow, pessoa_exemplo):
        """Testa busca por ID quando pessoa existe."""
        # Arrange
        pessoa_id = 1
        mock_repository.buscar_por_id.return_value = pessoa_exemplo
        
        # Act
        resultado = service.buscar_por_id(pessoa_id)
        
        # Assert
        assert resultado == pessoa_exemplo
        mock_repository.buscar_por_id.assert_called_once_with(pessoa_id)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_buscar_por_id_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa busca por ID quando pessoa não existe."""
        # Arrange
        pessoa_id = 999
        mock_repository.buscar_por_id.return_value = None
        
        # Act
        resultado = service.buscar_por_id(pessoa_id)
        
        # Assert
        assert resultado is None
        mock_repository.buscar_por_id.assert_called_once_with(pessoa_id)

    def test_buscar_pessoa_por_email_encontrado(self, service, mock_repository, mock_uow, pessoa_exemplo):
        """Testa busca por email quando pessoa existe."""
        # Arrange
        email = "maria@email.com"
        mock_repository.buscar_por_email.return_value = pessoa_exemplo
        
        # Act
        resultado = service.buscar_pessoa_por_email(email)
        
        # Assert
        assert resultado == pessoa_exemplo
        mock_repository.buscar_por_email.assert_called_once_with(email)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_not_called()

    def test_buscar_pessoa_por_email_nao_encontrado(self, service, mock_repository, mock_uow):
        """Testa busca por email quando pessoa não existe."""
        # Arrange
        email = "naoexiste@email.com"
        mock_repository.buscar_por_email.return_value = None
        
        # Act
        resultado = service.buscar_pessoa_por_email(email)
        
        # Assert
        assert resultado is None
        mock_repository.buscar_por_email.assert_called_once_with(email)

    def test_atualizar_pessoa_sucesso(self, service, mock_repository, mock_uow, pessoa_exemplo):
        """Testa atualização de pessoa com sucesso."""
        # Arrange
        pessoa_id = 1
        pessoa_atualizada = Pessoa(1, "Maria Oliveira", "11555555555", date(1990, 5, 15), "maria.oliveira@email.com")
        mock_repository.atualizar.return_value = pessoa_atualizada
        
        # Act
        resultado = service.atualizar_pessoa(pessoa_id, pessoa_atualizada)
        
        # Assert
        assert resultado == pessoa_atualizada
        mock_repository.atualizar.assert_called_once_with(pessoa_id, pessoa_atualizada)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_atualizar_pessoa_nao_encontrada(self, service, mock_repository, mock_uow):
        """Testa atualização de pessoa que não existe."""
        # Arrange
        pessoa_id = 999
        pessoa = Pessoa(999, "Pessoa Inexistente", "11000000000", date(1990, 1, 1), "inexistente@email.com")
        mock_repository.atualizar.return_value = None
        
        # Act
        resultado = service.atualizar_pessoa(pessoa_id, pessoa)
        
        # Assert
        assert resultado is None
        mock_repository.atualizar.assert_called_once_with(pessoa_id, pessoa)
        mock_uow.commit.assert_called_once()

    def test_atualizar_pessoa_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na atualização faz rollback da transação."""
        # Arrange
        pessoa_id = 1
        pessoa = Pessoa(1, "Maria Santos", "11999999999", date(1990, 5, 15), "maria@email.com")
        mock_repository.atualizar.side_effect = Exception("Erro na atualização")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro na atualização"):
            service.atualizar_pessoa(pessoa_id, pessoa)
        
        mock_repository.atualizar.assert_called_once_with(pessoa_id, pessoa)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_remover_pessoa_sucesso(self, service, mock_repository, mock_uow):
        """Testa remoção de pessoa com sucesso."""
        # Arrange
        pessoa_id = 1
        mock_repository.remover.return_value = True
        
        # Act
        resultado = service.remover_pessoa(pessoa_id)
        
        # Assert
        assert resultado is True
        mock_repository.remover.assert_called_once_with(pessoa_id)
        mock_uow.commit.assert_called_once()
        mock_uow.rollback.assert_not_called()

    def test_remover_pessoa_nao_encontrada(self, service, mock_repository, mock_uow):
        """Testa remoção de pessoa que não existe."""
        # Arrange
        pessoa_id = 999
        mock_repository.remover.return_value = False
        
        # Act
        resultado = service.remover_pessoa(pessoa_id)
        
        # Assert
        assert resultado is False
        mock_repository.remover.assert_called_once_with(pessoa_id)
        mock_uow.commit.assert_called_once()

    def test_remover_pessoa_erro_rollback(self, service, mock_repository, mock_uow):
        """Testa que erro na remoção faz rollback da transação."""
        # Arrange
        pessoa_id = 1
        mock_repository.remover.side_effect = Exception("Erro na remoção")
        
        # Act & Assert
        with pytest.raises(Exception, match="Erro na remoção"):
            service.remover_pessoa(pessoa_id)
        
        mock_repository.remover.assert_called_once_with(pessoa_id)
        mock_uow.commit.assert_not_called()
        mock_uow.rollback.assert_called_once()

    def test_operacoes_transacionais_vs_nao_transacionais(self, service, mock_repository, mock_uow, pessoa_exemplo):
        """Testa diferença entre operações transacionais e não transacionais."""
        # Arrange
        pessoa = Pessoa(None, "Carlos Lima", "11666666666", date(1988, 12, 25), "carlos@email.com")
        mock_repository.criar.return_value = pessoa_exemplo
        mock_repository.listar.return_value = [pessoa_exemplo]
        mock_repository.buscar_por_id.return_value = pessoa_exemplo
        mock_repository.buscar_por_email.return_value = pessoa_exemplo
        mock_repository.atualizar.return_value = pessoa_exemplo
        
        # Act - Operações transacionais
        service.criar_pessoa(pessoa)
        service.atualizar_pessoa(1, pessoa_exemplo)
        service.remover_pessoa(1)
        
        # Act - Operações não transacionais
        service.listar_pessoas()
        service.buscar_por_id(1)
        service.buscar_pessoa_por_email("test@email.com")
        
        # Assert - Apenas as operações de escrita devem usar transação
        assert mock_uow.commit.call_count == 3
        assert mock_uow.rollback.call_count == 0
        
        mock_repository.criar.assert_called_once()
        mock_repository.atualizar.assert_called_once()
        mock_repository.remover.assert_called_once()
        mock_repository.listar.assert_called_once()
        mock_repository.buscar_por_id.assert_called_once()
        mock_repository.buscar_por_email.assert_called_once()

    def test_fluxo_completo_pessoa(self, service, mock_repository, mock_uow):
        """Testa fluxo completo de operações com pessoa."""
        # Arrange
        pessoa_nova = Pessoa(None, "Teste Completo", "11444444444", date(1995, 7, 14), "teste@email.com")
        pessoa_criada = Pessoa(1, "Teste Completo", "11444444444", date(1995, 7, 14), "teste@email.com")
        pessoa_atualizada = Pessoa(1, "Teste Atualizado", "11333333333", date(1995, 7, 14), "teste.novo@email.com")
        
        mock_repository.criar.return_value = pessoa_criada
        mock_repository.buscar_por_id.return_value = pessoa_criada
        mock_repository.atualizar.return_value = pessoa_atualizada
        mock_repository.remover.return_value = True
        
        # Act - Fluxo: criar, buscar, atualizar, remover
        resultado_criacao = service.criar_pessoa(pessoa_nova)
        resultado_busca = service.buscar_por_id(resultado_criacao.id)
        resultado_atualizacao = service.atualizar_pessoa(resultado_criacao.id, pessoa_atualizada)
        resultado_remocao = service.remover_pessoa(resultado_criacao.id)
        
        # Assert
        assert resultado_criacao == pessoa_criada
        assert resultado_busca == pessoa_criada
        assert resultado_atualizacao == pessoa_atualizada
        assert resultado_remocao is True
        
        # Verificar transações (3 operações transacionais: criar, atualizar, remover)
        assert mock_uow.commit.call_count == 3
        assert mock_uow.rollback.call_count == 0

    def test_multiplas_pessoas_diferentes_operacoes(self, service, mock_repository, mock_uow):
        """Testa múltiplas operações com pessoas diferentes."""
        # Arrange
        pessoa1 = Pessoa(None, "Pessoa 1", "11111111111", date(1990, 1, 1), "pessoa1@email.com")
        pessoa2 = Pessoa(None, "Pessoa 2", "11222222222", date(1991, 2, 2), "pessoa2@email.com")
        
        pessoa1_criada = Pessoa(1, "Pessoa 1", "11111111111", date(1990, 1, 1), "pessoa1@email.com")
        pessoa2_criada = Pessoa(2, "Pessoa 2", "11222222222", date(1991, 2, 2), "pessoa2@email.com")
        
        mock_repository.criar.side_effect = [pessoa1_criada, pessoa2_criada]
        mock_repository.listar.return_value = [pessoa1_criada, pessoa2_criada]
        mock_repository.buscar_por_email.side_effect = [pessoa1_criada, pessoa2_criada]
        
        # Act
        resultado1 = service.criar_pessoa(pessoa1)
        resultado2 = service.criar_pessoa(pessoa2)
        lista_pessoas = service.listar_pessoas()
        busca1 = service.buscar_pessoa_por_email("pessoa1@email.com")
        busca2 = service.buscar_pessoa_por_email("pessoa2@email.com")
        
        # Assert
        assert resultado1 == pessoa1_criada
        assert resultado2 == pessoa2_criada
        assert len(lista_pessoas) == 2
        assert busca1 == pessoa1_criada
        assert busca2 == pessoa2_criada
        
        # Verificar que apenas as criações usaram transação
        assert mock_uow.commit.call_count == 2

    def test_heranca_base_service(self, service):
        """Testa que PessoaService herda corretamente de BaseService."""
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
        assert hasattr(mock_repository, 'listar_paginado')
        assert hasattr(mock_repository, 'buscar_por_id')
        assert hasattr(mock_repository, 'buscar_por_email')
        assert hasattr(mock_repository, 'atualizar')
        assert hasattr(mock_repository, 'remover')

    def test_tratamento_dados_pessoais(self, service, mock_repository, mock_uow):
        """Testa tratamento adequado de dados pessoais."""
        # Arrange
        pessoa_com_todos_dados = Pessoa(None, "Pessoa Completa", "11999999999", date(1990, 1, 1), "completa@email.com")
        pessoa_sem_email = Pessoa(None, "Pessoa Sem Email", "11888888888", date(1985, 5, 5), None)
        
        pessoa_completa_criada = Pessoa(1, "Pessoa Completa", "11999999999", date(1990, 1, 1), "completa@email.com")
        pessoa_sem_email_criada = Pessoa(2, "Pessoa Sem Email", "11888888888", date(1985, 5, 5), None)
        
        mock_repository.criar.side_effect = [pessoa_completa_criada, pessoa_sem_email_criada]
        
        # Act
        resultado_completa = service.criar_pessoa(pessoa_com_todos_dados)
        resultado_sem_email = service.criar_pessoa(pessoa_sem_email)
        
        # Assert
        assert resultado_completa.email == "completa@email.com"
        assert resultado_sem_email.email is None
        
        # Verificar que ambas as pessoas foram criadas com sucesso
        assert resultado_completa.id == 1
        assert resultado_sem_email.id == 2
        assert mock_uow.commit.call_count == 2