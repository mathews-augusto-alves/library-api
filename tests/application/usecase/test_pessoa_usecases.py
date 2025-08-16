"""
Testes para PessoaUseCase - Fase 4 do plano de testes.
Testa execução de regras de negócio, validações de domínio, orquestração de services,
tratamento de exceções e fluxos de sucesso e erro.
"""
import pytest
from unittest.mock import Mock
from datetime import date

from src.application.usecase.pessoa_usecases import PessoaUseCase, PessoaUseCaseValidator
from src.application.service.pessoa.pessoa_service import PessoaService
from src.domain.model.pessoa import Pessoa
from src.domain.exceptions import (
    DadosInvalidosException,
    EmailJaExisteException,
    PessoaNaoEncontradaException
)


class TestPessoaUseCaseValidator:
    """Testes para a classe PessoaUseCaseValidator."""

    # Testes de validação de email
    def test_validar_email_formato_valido(self):
        """Testa validação de email com formato válido."""
        # Act & Assert - Não deve lançar exceção
        PessoaUseCaseValidator.validar_email_formato("joao@email.com")
        PessoaUseCaseValidator.validar_email_formato("maria.silva@empresa.com.br")
        PessoaUseCaseValidator.validar_email_formato("teste123@dominio.org")

    def test_validar_email_formato_invalido(self):
        """Testa validação de email com formato inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            PessoaUseCaseValidator.validar_email_formato("email_invalido")
        assert "email" in str(exc_info.value)

        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_email_formato("@dominio.com")

        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_email_formato("email@")

        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_email_formato("email.com")

    def test_validar_email_formato_vazio_ou_none(self):
        """Testa validação de email vazio ou None."""
        # Act & Assert - Email vazio ou None são permitidos
        PessoaUseCaseValidator.validar_email_formato("")
        PessoaUseCaseValidator.validar_email_formato(None)

    # Testes de validação de telefone
    def test_validar_telefone_valido(self):
        """Testa validação de telefone válido."""
        # Act & Assert - Não deve lançar exceção
        PessoaUseCaseValidator.validar_telefone("11999999999")
        PessoaUseCaseValidator.validar_telefone("(11) 99999-9999")
        PessoaUseCaseValidator.validar_telefone("11 99999-9999")

    def test_validar_telefone_invalido_muito_curto(self):
        """Testa validação de telefone muito curto."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            PessoaUseCaseValidator.validar_telefone("1234567")
        assert "telefone" in str(exc_info.value)

    def test_validar_telefone_vazio_ou_none(self):
        """Testa validação de telefone vazio ou None."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_telefone("")

        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_telefone(None)

    # Testes de validação de nome
    def test_validar_nome_valido(self):
        """Testa validação de nome válido."""
        # Act & Assert - Não deve lançar exceção
        PessoaUseCaseValidator.validar_nome("João Silva")
        PessoaUseCaseValidator.validar_nome("Maria")
        PessoaUseCaseValidator.validar_nome("  Nome com espaços  ")

    def test_validar_nome_invalido_muito_curto(self):
        """Testa validação de nome muito curto."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            PessoaUseCaseValidator.validar_nome("A")
        assert "nome" in str(exc_info.value)

    def test_validar_nome_vazio_ou_none(self):
        """Testa validação de nome vazio ou None."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_nome("")

        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_nome("   ")

        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_nome(None)

    # Testes de validação completa de pessoa
    def test_validar_pessoa_com_email_valida(self):
        """Testa validação completa de pessoa com email."""
        # Arrange
        pessoa = Pessoa(None, "João Silva", "11999999999", date(1990, 1, 1), "joao@email.com")

        # Act & Assert - Não deve lançar exceção
        PessoaUseCaseValidator.validar_pessoa(pessoa)

    def test_validar_pessoa_sem_email_valida(self):
        """Testa validação completa de pessoa sem email."""
        # Arrange
        pessoa = Pessoa(None, "João Silva", "11999999999", date(1990, 1, 1), None)

        # Act & Assert - Não deve lançar exceção
        PessoaUseCaseValidator.validar_pessoa(pessoa)

    def test_validar_pessoa_com_email_vazio_valida(self):
        """Testa validação completa de pessoa com email vazio."""
        # Arrange
        pessoa = Pessoa(None, "João Silva", "11999999999", date(1990, 1, 1), "")

        # Act & Assert - Não deve lançar exceção
        PessoaUseCaseValidator.validar_pessoa(pessoa)

    def test_validar_pessoa_nome_invalido(self):
        """Testa validação de pessoa com nome inválido."""
        # Arrange
        pessoa = Pessoa(None, "A", "11999999999", date(1990, 1, 1), "joao@email.com")

        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_pessoa(pessoa)

    def test_validar_pessoa_telefone_invalido(self):
        """Testa validação de pessoa com telefone inválido."""
        # Arrange
        pessoa = Pessoa(None, "João Silva", "123", date(1990, 1, 1), "joao@email.com")

        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_pessoa(pessoa)

    def test_validar_pessoa_email_invalido(self):
        """Testa validação de pessoa com email inválido."""
        # Arrange
        pessoa = Pessoa(None, "João Silva", "11999999999", date(1990, 1, 1), "email_invalido")

        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            PessoaUseCaseValidator.validar_pessoa(pessoa)


class TestPessoaUseCase:
    """Testes para a classe PessoaUseCase."""

    @pytest.fixture
    def mock_service(self):
        """Mock do PessoaService."""
        return Mock(spec=PessoaService)

    @pytest.fixture
    def usecase(self, mock_service):
        """Instância do usecase para testes."""
        return PessoaUseCase(mock_service)

    @pytest.fixture
    def pessoa_exemplo(self):
        """Pessoa de exemplo para testes."""
        return Pessoa(
            id=1,
            nome="João Silva",
            telefone="11999999999",
            data_nascimento=date(1990, 1, 1),
            email="joao@email.com"
        )

    @pytest.fixture
    def pessoa_sem_email(self):
        """Pessoa sem email para testes."""
        return Pessoa(
            id=2,
            nome="Maria Santos",
            telefone="11888888888",
            data_nascimento=date(1985, 5, 15),
            email=None
        )

    # Testes de criação de pessoa
    def test_criar_pessoa_com_email_sucesso(self, usecase, mock_service, pessoa_exemplo):
        """Testa criação de pessoa com email com sucesso."""
        # Arrange
        mock_service.buscar_pessoa_por_email.return_value = None
        mock_service.criar_pessoa.return_value = pessoa_exemplo

        # Act
        resultado = usecase.criar_pessoa(pessoa_exemplo)

        # Assert
        assert resultado == pessoa_exemplo
        mock_service.buscar_pessoa_por_email.assert_called_once_with("joao@email.com")
        mock_service.criar_pessoa.assert_called_once_with(pessoa_exemplo)

    def test_criar_pessoa_sem_email_sucesso(self, usecase, mock_service, pessoa_sem_email):
        """Testa criação de pessoa sem email com sucesso."""
        # Arrange
        mock_service.criar_pessoa.return_value = pessoa_sem_email

        # Act
        resultado = usecase.criar_pessoa(pessoa_sem_email)

        # Assert
        assert resultado == pessoa_sem_email
        mock_service.buscar_pessoa_por_email.assert_not_called()
        mock_service.criar_pessoa.assert_called_once_with(pessoa_sem_email)

    def test_criar_pessoa_email_ja_existe(self, usecase, mock_service, pessoa_exemplo):
        """Testa criação de pessoa com email que já existe."""
        # Arrange
        pessoa_existente = Pessoa(2, "Outro Nome", "11777777777", date(1988, 3, 10), "joao@email.com")
        mock_service.buscar_pessoa_por_email.return_value = pessoa_existente

        # Act & Assert
        with pytest.raises(EmailJaExisteException) as exc_info:
            usecase.criar_pessoa(pessoa_exemplo)

        assert "joao@email.com" in str(exc_info.value)
        mock_service.buscar_pessoa_por_email.assert_called_once_with("joao@email.com")
        mock_service.criar_pessoa.assert_not_called()

    def test_criar_pessoa_nome_invalido(self, usecase, mock_service):
        """Testa criação de pessoa com nome inválido."""
        # Arrange
        pessoa_invalida = Pessoa(None, "A", "11999999999", date(1990, 1, 1), "joao@email.com")

        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.criar_pessoa(pessoa_invalida)

        mock_service.buscar_pessoa_por_email.assert_not_called()
        mock_service.criar_pessoa.assert_not_called()

    def test_criar_pessoa_telefone_invalido(self, usecase, mock_service):
        """Testa criação de pessoa com telefone inválido."""
        # Arrange
        pessoa_invalida = Pessoa(None, "João Silva", "123", date(1990, 1, 1), "joao@email.com")

        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.criar_pessoa(pessoa_invalida)

        mock_service.buscar_pessoa_por_email.assert_not_called()
        mock_service.criar_pessoa.assert_not_called()

    def test_criar_pessoa_email_invalido(self, usecase, mock_service):
        """Testa criação de pessoa com email inválido."""
        # Arrange
        pessoa_invalida = Pessoa(None, "João Silva", "11999999999", date(1990, 1, 1), "email_invalido")

        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.criar_pessoa(pessoa_invalida)

        mock_service.buscar_pessoa_por_email.assert_not_called()
        mock_service.criar_pessoa.assert_not_called()

    # Testes de listagem
    def test_listar_pessoas(self, usecase, mock_service, pessoa_exemplo, pessoa_sem_email):
        """Testa listagem de todas as pessoas."""
        # Arrange
        pessoas = [pessoa_exemplo, pessoa_sem_email]
        mock_service.listar_pessoas.return_value = pessoas

        # Act
        resultado = usecase.listar_pessoas()

        # Assert
        assert resultado == pessoas
        mock_service.listar_pessoas.assert_called_once()

    def test_listar_pessoas_paginado(self, usecase, mock_service, pessoa_exemplo):
        """Testa listagem paginada de pessoas."""
        # Arrange
        pessoas = [pessoa_exemplo]
        total = 10
        mock_service.listar_pessoas_paginado.return_value = (pessoas, total)

        # Act
        resultado_pessoas, resultado_total = usecase.listar_pessoas_paginado(1, 5)

        # Assert
        assert resultado_pessoas == pessoas
        assert resultado_total == total
        mock_service.listar_pessoas_paginado.assert_called_once_with(1, 5)

    # Testes de busca por ID
    def test_buscar_por_id_encontrada(self, usecase, mock_service, pessoa_exemplo):
        """Testa busca por ID quando pessoa existe."""
        # Arrange
        mock_service.buscar_por_id.return_value = pessoa_exemplo

        # Act
        resultado = usecase.buscar_por_id(1)

        # Assert
        assert resultado == pessoa_exemplo
        mock_service.buscar_por_id.assert_called_once_with(1)

    def test_buscar_por_id_nao_encontrada(self, usecase, mock_service):
        """Testa busca por ID quando pessoa não existe."""
        # Arrange
        mock_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException) as exc_info:
            usecase.buscar_por_id(999)

        assert "999" in str(exc_info.value)
        mock_service.buscar_por_id.assert_called_once_with(999)

    # Testes de busca por email
    def test_buscar_pessoa_por_email_encontrada(self, usecase, mock_service, pessoa_exemplo):
        """Testa busca por email quando pessoa existe."""
        # Arrange
        mock_service.buscar_pessoa_por_email.return_value = pessoa_exemplo

        # Act
        resultado = usecase.buscar_pessoa_por_email("joao@email.com")

        # Assert
        assert resultado == pessoa_exemplo
        mock_service.buscar_pessoa_por_email.assert_called_once_with("joao@email.com")

    def test_buscar_pessoa_por_email_nao_encontrada(self, usecase, mock_service):
        """Testa busca por email quando pessoa não existe."""
        # Arrange
        mock_service.buscar_pessoa_por_email.return_value = None

        # Act
        resultado = usecase.buscar_pessoa_por_email("joao@email.com")

        # Assert
        assert resultado is None
        mock_service.buscar_pessoa_por_email.assert_called_once_with("joao@email.com")

    def test_buscar_pessoa_por_email_invalido(self, usecase, mock_service):
        """Testa busca por email com formato inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.buscar_pessoa_por_email("email_invalido")

        mock_service.buscar_pessoa_por_email.assert_not_called()

    # Testes de atualização
    def test_atualizar_pessoa_com_email_sucesso(self, usecase, mock_service, pessoa_exemplo):
        """Testa atualização de pessoa com email com sucesso."""
        # Arrange
        pessoa_atualizada = Pessoa(1, "João Santos", "11777777777", date(1990, 1, 1), "joao.santos@email.com")
        mock_service.buscar_por_id.return_value = pessoa_exemplo
        mock_service.buscar_pessoa_por_email.return_value = None
        mock_service.atualizar_pessoa.return_value = pessoa_atualizada

        # Act
        resultado = usecase.atualizar_pessoa(1, pessoa_atualizada)

        # Assert
        assert resultado == pessoa_atualizada
        mock_service.buscar_por_id.assert_called_once_with(1)
        mock_service.buscar_pessoa_por_email.assert_called_once_with("joao.santos@email.com")
        mock_service.atualizar_pessoa.assert_called_once_with(1, pessoa_atualizada)

    def test_atualizar_pessoa_sem_email_sucesso(self, usecase, mock_service, pessoa_exemplo):
        """Testa atualização de pessoa removendo email com sucesso."""
        # Arrange
        pessoa_atualizada = Pessoa(1, "João Santos", "11777777777", date(1990, 1, 1), None)
        mock_service.buscar_por_id.return_value = pessoa_exemplo
        mock_service.atualizar_pessoa.return_value = pessoa_atualizada

        # Act
        resultado = usecase.atualizar_pessoa(1, pessoa_atualizada)

        # Assert
        assert resultado == pessoa_atualizada
        mock_service.buscar_por_id.assert_called_once_with(1)
        mock_service.buscar_pessoa_por_email.assert_not_called()
        mock_service.atualizar_pessoa.assert_called_once_with(1, pessoa_atualizada)

    def test_atualizar_pessoa_mesmo_email(self, usecase, mock_service, pessoa_exemplo):
        """Testa atualização mantendo o mesmo email."""
        # Arrange
        pessoa_atualizada = Pessoa(1, "João Santos", "11777777777", date(1990, 1, 1), "joao@email.com")
        mock_service.buscar_por_id.return_value = pessoa_exemplo
        mock_service.buscar_pessoa_por_email.return_value = pessoa_exemplo  # Mesma pessoa
        mock_service.atualizar_pessoa.return_value = pessoa_atualizada

        # Act
        resultado = usecase.atualizar_pessoa(1, pessoa_atualizada)

        # Assert
        assert resultado == pessoa_atualizada
        mock_service.atualizar_pessoa.assert_called_once_with(1, pessoa_atualizada)

    def test_atualizar_pessoa_nao_encontrada(self, usecase, mock_service):
        """Testa atualização de pessoa que não existe."""
        # Arrange
        pessoa_dados = Pessoa(None, "João Silva", "11999999999", date(1990, 1, 1), "joao@email.com")
        mock_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException) as exc_info:
            usecase.atualizar_pessoa(999, pessoa_dados)

        assert "999" in str(exc_info.value)
        mock_service.buscar_por_id.assert_called_once_with(999)
        mock_service.buscar_pessoa_por_email.assert_not_called()
        mock_service.atualizar_pessoa.assert_not_called()

    def test_atualizar_pessoa_email_ja_existe_outra_pessoa(self, usecase, mock_service, pessoa_exemplo):
        """Testa atualização com email de outra pessoa."""
        # Arrange
        outra_pessoa = Pessoa(2, "Maria Silva", "11888888888", date(1985, 5, 15), "maria@email.com")
        pessoa_atualizada = Pessoa(1, "João Santos", "11777777777", date(1990, 1, 1), "maria@email.com")
        mock_service.buscar_por_id.return_value = pessoa_exemplo
        mock_service.buscar_pessoa_por_email.return_value = outra_pessoa

        # Act & Assert
        with pytest.raises(EmailJaExisteException):
            usecase.atualizar_pessoa(1, pessoa_atualizada)

        mock_service.buscar_pessoa_por_email.assert_called_once_with("maria@email.com")
        mock_service.atualizar_pessoa.assert_not_called()

    def test_atualizar_pessoa_dados_invalidos(self, usecase, mock_service, pessoa_exemplo):
        """Testa atualização com dados inválidos."""
        # Arrange
        pessoa_invalida = Pessoa(1, "A", "123", date(1990, 1, 1), "joao@email.com")
        mock_service.buscar_por_id.return_value = pessoa_exemplo

        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.atualizar_pessoa(1, pessoa_invalida)

        mock_service.buscar_pessoa_por_email.assert_not_called()
        mock_service.atualizar_pessoa.assert_not_called()

    # Testes de remoção
    def test_remover_pessoa_sucesso(self, usecase, mock_service, pessoa_exemplo):
        """Testa remoção de pessoa com sucesso."""
        # Arrange
        mock_service.buscar_por_id.return_value = pessoa_exemplo
        mock_service.remover_pessoa.return_value = True

        # Act
        resultado = usecase.remover_pessoa(1)

        # Assert
        assert resultado is True
        mock_service.buscar_por_id.assert_called_once_with(1)
        mock_service.remover_pessoa.assert_called_once_with(1)

    def test_remover_pessoa_nao_encontrada(self, usecase, mock_service):
        """Testa remoção de pessoa que não existe."""
        # Arrange
        mock_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException) as exc_info:
            usecase.remover_pessoa(999)

        assert "999" in str(exc_info.value)
        mock_service.buscar_por_id.assert_called_once_with(999)
        mock_service.remover_pessoa.assert_not_called()

    # Testes de fluxos completos
    def test_fluxo_completo_criar_atualizar_remover(self, usecase, mock_service):
        """Testa fluxo completo de criação, atualização e remoção."""
        # Arrange
        pessoa_inicial = Pessoa(None, "João Silva", "11999999999", date(1990, 1, 1), "joao@email.com")
        pessoa_criada = Pessoa(1, "João Silva", "11999999999", date(1990, 1, 1), "joao@email.com")
        pessoa_atualizada = Pessoa(1, "João Santos", "11777777777", date(1990, 1, 1), "joao.santos@email.com")

        # Configurar mocks para criação
        mock_service.buscar_pessoa_por_email.side_effect = [None, None]  # Não existe, depois não existe outro
        mock_service.criar_pessoa.return_value = pessoa_criada

        # Configurar mocks para atualização
        mock_service.buscar_por_id.return_value = pessoa_criada
        mock_service.atualizar_pessoa.return_value = pessoa_atualizada

        # Configurar mocks para remoção
        mock_service.remover_pessoa.return_value = True

        # Act - Criação
        resultado_criacao = usecase.criar_pessoa(pessoa_inicial)

        # Act - Atualização
        resultado_atualizacao = usecase.atualizar_pessoa(1, pessoa_atualizada)

        # Act - Remoção
        resultado_remocao = usecase.remover_pessoa(1)

        # Assert
        assert resultado_criacao == pessoa_criada
        assert resultado_atualizacao == pessoa_atualizada
        assert resultado_remocao is True

        # Verifica se todos os métodos foram chamados
        mock_service.criar_pessoa.assert_called_once_with(pessoa_inicial)
        mock_service.atualizar_pessoa.assert_called_once_with(1, pessoa_atualizada)
        mock_service.remover_pessoa.assert_called_once_with(1)

    def test_orquestracao_service_metodos(self, usecase, mock_service, pessoa_exemplo):
        """Testa que o usecase orquestra corretamente os métodos do service."""
        # Arrange
        pessoas = [pessoa_exemplo]
        mock_service.listar_pessoas.return_value = pessoas
        mock_service.buscar_pessoa_por_email.return_value = pessoa_exemplo
        mock_service.listar_pessoas_paginado.return_value = (pessoas, 1)

        # Act
        resultado_listagem = usecase.listar_pessoas()
        resultado_busca = usecase.buscar_pessoa_por_email("joao@email.com")
        resultado_paginado, total = usecase.listar_pessoas_paginado(1, 10)

        # Assert
        assert resultado_listagem == pessoas
        assert resultado_busca == pessoa_exemplo
        assert resultado_paginado == pessoas
        assert total == 1

        mock_service.listar_pessoas.assert_called_once()
        mock_service.buscar_pessoa_por_email.assert_called_once_with("joao@email.com")
        mock_service.listar_pessoas_paginado.assert_called_once_with(1, 10)