"""
Testes para LivroUseCase - Fase 4 do plano de testes.
Testa execução de regras de negócio, validações de domínio, orquestração de services,
tratamento de exceções e fluxos de sucesso e erro.
"""
import pytest
from unittest.mock import Mock

from src.application.usecase.livro_usecases import LivroUseCase
from src.application.service.livro.livro_service import LivroService
from src.application.service.livro.emprestimo_service import EmprestimoService
from src.application.service.pessoa.pessoa_service import PessoaService
from src.domain.model.livro import Livro
from src.domain.model.emprestimo import Emprestimo
from src.domain.model.pessoa import Pessoa
from src.domain.enums.emprestimo_status import EmprestimoStatus
from datetime import datetime
from src.domain.exceptions import (
    DadosInvalidosException,
    LivroNaoEncontradoException,
    LivroIndisponivelException,
    EmprestimoAtivoNaoEncontradoException,
    PessoaNaoEncontradaException
)


class TestLivroUseCase:
    """Testes para a classe LivroUseCase."""

    @pytest.fixture
    def mock_livro_service(self):
        """Mock do LivroService."""
        return Mock(spec=LivroService)

    @pytest.fixture
    def mock_emprestimo_service(self):
        """Mock do EmprestimoService."""
        return Mock(spec=EmprestimoService)

    @pytest.fixture
    def mock_pessoa_service(self):
        """Mock do PessoaService."""
        return Mock(spec=PessoaService)

    @pytest.fixture
    def usecase(self, mock_livro_service, mock_emprestimo_service, mock_pessoa_service):
        """Instância do usecase para testes."""
        return LivroUseCase(mock_livro_service, mock_emprestimo_service, mock_pessoa_service)

    @pytest.fixture
    def livro_exemplo(self):
        """Livro de exemplo para testes."""
        return Livro(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )

    @pytest.fixture
    def pessoa_exemplo(self):
        """Pessoa de exemplo para testes."""
        return Pessoa(
            id=1,
            nome="João Silva",
            telefone="11999999999",
            data_nascimento=datetime.now().date(),
            email="joao@email.com"
        )

    @pytest.fixture
    def emprestimo_exemplo(self):
        """Empréstimo de exemplo para testes."""
        return Emprestimo(
            id=1,
            livro_id=1,
            pessoa_id=1,
            usuario_id=1,
            data_emprestimo=datetime.now()
        )

    # Testes de cadastro de livro
    def test_cadastrar_livro_sucesso(self, usecase, mock_livro_service, livro_exemplo):
        """Testa cadastro de livro com dados válidos."""
        # Arrange
        mock_livro_service.criar.return_value = livro_exemplo

        # Act
        resultado = usecase.cadastrar_livro("O Senhor dos Anéis", "J.R.R. Tolkien")

        # Assert
        assert resultado == livro_exemplo
        mock_livro_service.criar.assert_called_once()
        # Verifica se o livro foi criado com dados corretos
        args = mock_livro_service.criar.call_args[0][0]
        assert args.titulo == "O Senhor dos Anéis"
        assert args.autor == "J.R.R. Tolkien"
        assert args.disponivel is True

    def test_cadastrar_livro_titulo_invalido_muito_curto(self, usecase, mock_livro_service):
        """Testa cadastro com título muito curto."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            usecase.cadastrar_livro("A", "J.R.R. Tolkien")
        
        assert "titulo" in str(exc_info.value)
        mock_livro_service.criar.assert_not_called()

    def test_cadastrar_livro_titulo_vazio(self, usecase, mock_livro_service):
        """Testa cadastro com título vazio."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.cadastrar_livro("", "J.R.R. Tolkien")
        
        mock_livro_service.criar.assert_not_called()

    def test_cadastrar_livro_titulo_none(self, usecase, mock_livro_service):
        """Testa cadastro com título None."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.cadastrar_livro(None, "J.R.R. Tolkien")
        
        mock_livro_service.criar.assert_not_called()

    def test_cadastrar_livro_autor_invalido_muito_curto(self, usecase, mock_livro_service):
        """Testa cadastro com autor muito curto."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            usecase.cadastrar_livro("O Senhor dos Anéis", "A")
        
        assert "autor" in str(exc_info.value)
        mock_livro_service.criar.assert_not_called()

    def test_cadastrar_livro_autor_vazio(self, usecase, mock_livro_service):
        """Testa cadastro com autor vazio."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.cadastrar_livro("O Senhor dos Anéis", "")
        
        mock_livro_service.criar.assert_not_called()

    def test_cadastrar_livro_autor_none(self, usecase, mock_livro_service):
        """Testa cadastro com autor None."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.cadastrar_livro("O Senhor dos Anéis", None)
        
        mock_livro_service.criar.assert_not_called()

    def test_cadastrar_livro_com_espacos_extras(self, usecase, mock_livro_service, livro_exemplo):
        """Testa cadastro com espaços extras nos campos."""
        # Arrange
        mock_livro_service.criar.return_value = livro_exemplo

        # Act
        resultado = usecase.cadastrar_livro("  O Senhor dos Anéis  ", "  J.R.R. Tolkien  ")

        # Assert
        assert resultado == livro_exemplo
        # Verifica se os espaços foram removidos
        args = mock_livro_service.criar.call_args[0][0]
        assert args.titulo == "O Senhor dos Anéis"
        assert args.autor == "J.R.R. Tolkien"

    # Testes de listagem
    def test_listar_livros(self, usecase, mock_livro_service, livro_exemplo):
        """Testa listagem de todos os livros."""
        # Arrange
        livros = [livro_exemplo, Livro(2, "1984", "George Orwell", True)]
        mock_livro_service.listar.return_value = livros

        # Act
        resultado = usecase.listar_livros()

        # Assert
        assert resultado == livros
        mock_livro_service.listar.assert_called_once()

    def test_listar_livros_paginado(self, usecase, mock_livro_service, livro_exemplo):
        """Testa listagem paginada de livros."""
        # Arrange
        livros = [livro_exemplo]
        total = 10
        mock_livro_service.listar_paginado.return_value = (livros, total)

        # Act
        resultado_livros, resultado_total = usecase.listar_livros_paginado(1, 5)

        # Assert
        assert resultado_livros == livros
        assert resultado_total == total
        mock_livro_service.listar_paginado.assert_called_once_with(1, 5)

    def test_listar_emprestimos_paginado(self, usecase, mock_emprestimo_service, emprestimo_exemplo):
        """Testa listagem paginada de empréstimos."""
        # Arrange
        emprestimos = [emprestimo_exemplo]
        total = 5
        mock_emprestimo_service.listar_paginado.return_value = (emprestimos, total)

        # Act
        resultado_emprestimos, resultado_total = usecase.listar_emprestimos_paginado(1, 10)

        # Assert
        assert resultado_emprestimos == emprestimos
        assert resultado_total == total
        mock_emprestimo_service.listar_paginado.assert_called_once_with(1, 10, EmprestimoStatus.ATIVOS)

    def test_listar_emprestimos_paginado_com_status_especifico(self, usecase, mock_emprestimo_service, emprestimo_exemplo):
        """Testa listagem paginada de empréstimos com status específico."""
        # Arrange
        emprestimos = [emprestimo_exemplo]
        total = 3
        mock_emprestimo_service.listar_paginado.return_value = (emprestimos, total)

        # Act
        resultado_emprestimos, resultado_total = usecase.listar_emprestimos_paginado(
            1, 10, EmprestimoStatus.DEVOLVIDOS
        )

        # Assert
        assert resultado_emprestimos == emprestimos
        assert resultado_total == total
        mock_emprestimo_service.listar_paginado.assert_called_once_with(1, 10, EmprestimoStatus.DEVOLVIDOS)

    # Testes de empréstimo
    def test_emprestar_livro_sucesso(self, usecase, mock_livro_service, mock_pessoa_service, 
                                   mock_emprestimo_service, livro_exemplo, pessoa_exemplo, emprestimo_exemplo):
        """Testa empréstimo de livro com sucesso."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = livro_exemplo
        mock_pessoa_service.buscar_por_id.return_value = pessoa_exemplo
        mock_emprestimo_service.buscar_ativo_por_livro.return_value = None
        mock_emprestimo_service.emprestar.return_value = emprestimo_exemplo

        # Act
        resultado = usecase.emprestar(1, 1, 1)

        # Assert
        assert resultado == emprestimo_exemplo
        mock_livro_service.buscar_por_id.assert_called_once_with(1)
        mock_pessoa_service.buscar_por_id.assert_called_once_with(1)
        mock_emprestimo_service.buscar_ativo_por_livro.assert_called_once_with(1)
        mock_emprestimo_service.emprestar.assert_called_once_with(1, 1, 1)

    def test_emprestar_livro_nao_encontrado(self, usecase, mock_livro_service, mock_pessoa_service, mock_emprestimo_service):
        """Testa empréstimo de livro que não existe."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(LivroNaoEncontradoException) as exc_info:
            usecase.emprestar(999, 1, 1)

        assert "999" in str(exc_info.value)
        mock_livro_service.buscar_por_id.assert_called_once_with(999)
        mock_pessoa_service.buscar_por_id.assert_not_called()
        mock_emprestimo_service.emprestar.assert_not_called()

    def test_emprestar_livro_indisponivel(self, usecase, mock_livro_service, mock_pessoa_service, mock_emprestimo_service):
        """Testa empréstimo de livro indisponível."""
        # Arrange
        livro_indisponivel = Livro(1, "Título", "Autor", False)
        mock_livro_service.buscar_por_id.return_value = livro_indisponivel

        # Act & Assert
        with pytest.raises(LivroIndisponivelException) as exc_info:
            usecase.emprestar(1, 1, 1)

        assert "1" in str(exc_info.value)
        mock_livro_service.buscar_por_id.assert_called_once_with(1)
        mock_pessoa_service.buscar_por_id.assert_not_called()

    def test_emprestar_pessoa_nao_encontrada(self, usecase, mock_livro_service, mock_pessoa_service, 
                                           mock_emprestimo_service, livro_exemplo):
        """Testa empréstimo para pessoa que não existe."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = livro_exemplo
        mock_pessoa_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException) as exc_info:
            usecase.emprestar(1, 999, 1)

        assert "999" in str(exc_info.value)
        mock_pessoa_service.buscar_por_id.assert_called_once_with(999)
        mock_emprestimo_service.emprestar.assert_not_called()

    def test_emprestar_livro_com_emprestimo_ativo(self, usecase, mock_livro_service, mock_pessoa_service, 
                                                 mock_emprestimo_service, livro_exemplo, pessoa_exemplo, emprestimo_exemplo):
        """Testa empréstimo de livro que já tem empréstimo ativo."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = livro_exemplo
        mock_pessoa_service.buscar_por_id.return_value = pessoa_exemplo
        mock_emprestimo_service.buscar_ativo_por_livro.return_value = emprestimo_exemplo

        # Act & Assert
        with pytest.raises(LivroIndisponivelException) as exc_info:
            usecase.emprestar(1, 1, 1)

        assert "1" in str(exc_info.value)
        mock_emprestimo_service.buscar_ativo_por_livro.assert_called_once_with(1)
        mock_emprestimo_service.emprestar.assert_not_called()

    # Testes de devolução
    def test_devolver_livro_sucesso(self, usecase, mock_livro_service, mock_emprestimo_service, 
                                   livro_exemplo, emprestimo_exemplo):
        """Testa devolução de livro com sucesso."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = livro_exemplo
        mock_emprestimo_service.buscar_ativo_por_livro.return_value = emprestimo_exemplo
        emprestimo_devolvido = Emprestimo(1, 1, 1, 1, datetime.now(), datetime.now())
        mock_emprestimo_service.devolver.return_value = emprestimo_devolvido

        # Act
        resultado = usecase.devolver(1)

        # Assert
        assert resultado == emprestimo_devolvido
        mock_livro_service.buscar_por_id.assert_called_once_with(1)
        mock_emprestimo_service.buscar_ativo_por_livro.assert_called_once_with(1)
        mock_emprestimo_service.devolver.assert_called_once_with(1, 1)

    def test_devolver_livro_nao_encontrado(self, usecase, mock_livro_service, mock_emprestimo_service):
        """Testa devolução de livro que não existe."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(LivroNaoEncontradoException) as exc_info:
            usecase.devolver(999)

        assert "999" in str(exc_info.value)
        mock_livro_service.buscar_por_id.assert_called_once_with(999)
        mock_emprestimo_service.buscar_ativo_por_livro.assert_not_called()

    def test_devolver_livro_sem_emprestimo_ativo(self, usecase, mock_livro_service, mock_emprestimo_service, livro_exemplo):
        """Testa devolução de livro sem empréstimo ativo."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = livro_exemplo
        mock_emprestimo_service.buscar_ativo_por_livro.return_value = None

        # Act & Assert
        with pytest.raises(EmprestimoAtivoNaoEncontradoException) as exc_info:
            usecase.devolver(1)

        assert "1" in str(exc_info.value)
        mock_emprestimo_service.buscar_ativo_por_livro.assert_called_once_with(1)
        mock_emprestimo_service.devolver.assert_not_called()

    # Testes de métodos auxiliares privados
    def test_obter_livro_existente_encontrado(self, usecase, mock_livro_service, livro_exemplo):
        """Testa método privado _obter_livro_existente com livro encontrado."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = livro_exemplo

        # Act
        resultado = usecase._obter_livro_existente(1)

        # Assert
        assert resultado == livro_exemplo
        mock_livro_service.buscar_por_id.assert_called_once_with(1)

    def test_obter_livro_existente_nao_encontrado(self, usecase, mock_livro_service):
        """Testa método privado _obter_livro_existente com livro não encontrado."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(LivroNaoEncontradoException):
            usecase._obter_livro_existente(999)

    def test_obter_livro_disponivel_sucesso(self, usecase, mock_livro_service, livro_exemplo):
        """Testa método privado _obter_livro_disponivel com livro disponível."""
        # Arrange
        mock_livro_service.buscar_por_id.return_value = livro_exemplo

        # Act
        resultado = usecase._obter_livro_disponivel(1)

        # Assert
        assert resultado == livro_exemplo

    def test_obter_livro_disponivel_indisponivel(self, usecase, mock_livro_service):
        """Testa método privado _obter_livro_disponivel com livro indisponível."""
        # Arrange
        livro_indisponivel = Livro(1, "Título", "Autor", False)
        mock_livro_service.buscar_por_id.return_value = livro_indisponivel

        # Act & Assert
        with pytest.raises(LivroIndisponivelException):
            usecase._obter_livro_disponivel(1)

    def test_validar_pessoa_existente_sucesso(self, usecase, mock_pessoa_service, pessoa_exemplo):
        """Testa método privado _validar_pessoa_existente com pessoa encontrada."""
        # Arrange
        mock_pessoa_service.buscar_por_id.return_value = pessoa_exemplo

        # Act & Assert - Não deve lançar exceção
        usecase._validar_pessoa_existente(1)
        mock_pessoa_service.buscar_por_id.assert_called_once_with(1)

    def test_validar_pessoa_existente_nao_encontrada(self, usecase, mock_pessoa_service):
        """Testa método privado _validar_pessoa_existente com pessoa não encontrada."""
        # Arrange
        mock_pessoa_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException):
            usecase._validar_pessoa_existente(999)

    def test_garantir_ausencia_de_emprestimo_ativo_sem_emprestimo(self, usecase, mock_emprestimo_service):
        """Testa método privado _garantir_ausencia_de_emprestimo_ativo sem empréstimo ativo."""
        # Arrange
        mock_emprestimo_service.buscar_ativo_por_livro.return_value = None

        # Act & Assert - Não deve lançar exceção
        usecase._garantir_ausencia_de_emprestimo_ativo(1)
        mock_emprestimo_service.buscar_ativo_por_livro.assert_called_once_with(1)

    def test_garantir_ausencia_de_emprestimo_ativo_com_emprestimo(self, usecase, mock_emprestimo_service, emprestimo_exemplo):
        """Testa método privado _garantir_ausencia_de_emprestimo_ativo com empréstimo ativo."""
        # Arrange
        mock_emprestimo_service.buscar_ativo_por_livro.return_value = emprestimo_exemplo

        # Act & Assert
        with pytest.raises(LivroIndisponivelException):
            usecase._garantir_ausencia_de_emprestimo_ativo(1)

    # Testes de orquestração de services
    def test_orquestracao_multiplos_services(self, usecase, mock_livro_service, mock_emprestimo_service, mock_pessoa_service):
        """Testa que o usecase orquestra corretamente múltiplos services."""
        # Arrange
        livros = [Livro(1, "Título", "Autor", True)]
        emprestimos = [Emprestimo(1, 1, 1, 1, datetime.now())]
        mock_livro_service.listar.return_value = livros
        mock_emprestimo_service.listar_paginado.return_value = (emprestimos, 1)

        # Act
        resultado_livros = usecase.listar_livros()
        resultado_emprestimos, total = usecase.listar_emprestimos_paginado(1, 10)

        # Assert
        assert resultado_livros == livros
        assert resultado_emprestimos == emprestimos
        assert total == 1
        mock_livro_service.listar.assert_called_once()
        mock_emprestimo_service.listar_paginado.assert_called_once()

    # Testes de fluxo completo
    def test_fluxo_completo_cadastro_emprestimo_devolucao(self, usecase, mock_livro_service, mock_emprestimo_service, 
                                                         mock_pessoa_service, pessoa_exemplo):
        """Testa fluxo completo de cadastro, empréstimo e devolução."""
        # Arrange
        livro_criado = Livro(1, "Dom Casmurro", "Machado de Assis", True)
        emprestimo_criado = Emprestimo(1, 1, 1, 1, datetime.now())
        emprestimo_devolvido = Emprestimo(1, 1, 1, 1, datetime.now(), datetime.now())

        # Configurar mocks para cadastro
        mock_livro_service.criar.return_value = livro_criado

        # Configurar mocks para empréstimo
        mock_livro_service.buscar_por_id.return_value = livro_criado
        mock_pessoa_service.buscar_por_id.return_value = pessoa_exemplo
        mock_emprestimo_service.buscar_ativo_por_livro.side_effect = [None, emprestimo_criado]
        mock_emprestimo_service.emprestar.return_value = emprestimo_criado

        # Configurar mocks para devolução
        mock_emprestimo_service.devolver.return_value = emprestimo_devolvido

        # Act - Cadastro
        resultado_cadastro = usecase.cadastrar_livro("Dom Casmurro", "Machado de Assis")

        # Act - Empréstimo
        resultado_emprestimo = usecase.emprestar(1, 1, 1)

        # Act - Devolução
        resultado_devolucao = usecase.devolver(1)

        # Assert
        assert resultado_cadastro == livro_criado
        assert resultado_emprestimo == emprestimo_criado
        assert resultado_devolucao == emprestimo_devolvido

        # Verifica se todos os services foram chamados corretamente
        mock_livro_service.criar.assert_called_once()
        mock_emprestimo_service.emprestar.assert_called_once_with(1, 1, 1)
        mock_emprestimo_service.devolver.assert_called_once_with(1, 1)