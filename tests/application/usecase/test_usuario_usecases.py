"""
Testes para UsuarioUseCase - Fase 4 do plano de testes.
Testa execução de regras de negócio, validações de domínio, orquestração de services,
tratamento de exceções e fluxos de sucesso e erro.
"""
import pytest
from unittest.mock import Mock, patch

from src.application.usecase.usuario_usecases import UsuarioUseCase
from src.application.service.usuario.usuario_service import UsuarioService
from src.domain.model.usuario import Usuario
from src.domain.exceptions import (
    DadosInvalidosException,
    EmailJaExisteException,
    PessoaNaoEncontradaException
)


class TestUsuarioUseCase:
    """Testes para a classe UsuarioUseCase."""

    @pytest.fixture
    def mock_service(self):
        """Mock do UsuarioService."""
        return Mock(spec=UsuarioService)

    @pytest.fixture
    def usecase(self, mock_service):
        """Instância do usecase para testes."""
        return UsuarioUseCase(mock_service)

    @pytest.fixture
    def usuario_exemplo(self):
        """Usuário de exemplo para testes."""
        return Usuario(
            id=1,
            nome="João Silva",
            email="joao@email.com",
            senha_hash="$2b$12$hashexemplo"
        )

    # Testes de validação de email
    def test_validar_email_valido(self, usecase):
        """Testa validação de email válido."""
        # Arrange & Act & Assert - Não deve lançar exceção
        usecase._validar_email("joao@email.com")
        usecase._validar_email("maria.silva@empresa.com.br")
        usecase._validar_email("teste123@dominio.org")

    def test_validar_email_invalido(self, usecase):
        """Testa validação de email inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            usecase._validar_email("email_invalido")
        assert "email" in str(exc_info.value)

        with pytest.raises(DadosInvalidosException):
            usecase._validar_email("@dominio.com")

        with pytest.raises(DadosInvalidosException):
            usecase._validar_email("email@")

        with pytest.raises(DadosInvalidosException):
            usecase._validar_email("")

        with pytest.raises(DadosInvalidosException):
            usecase._validar_email(None)

    # Testes de validação de nome
    def test_validar_nome_valido(self, usecase):
        """Testa validação de nome válido."""
        # Arrange & Act & Assert - Não deve lançar exceção
        usecase._validar_nome("João Silva")
        usecase._validar_nome("Maria")
        usecase._validar_nome("  Nome com espaços  ")

    def test_validar_nome_invalido(self, usecase):
        """Testa validação de nome inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            usecase._validar_nome("A")
        assert "nome" in str(exc_info.value)

        with pytest.raises(DadosInvalidosException):
            usecase._validar_nome("")

        with pytest.raises(DadosInvalidosException):
            usecase._validar_nome("   ")

        with pytest.raises(DadosInvalidosException):
            usecase._validar_nome(None)

    # Testes de validação de senha
    def test_validar_senha_valida(self, usecase):
        """Testa validação de senha válida."""
        # Arrange & Act & Assert - Não deve lançar exceção
        usecase._validar_senha("123456")
        usecase._validar_senha("senhaSegura123")
        usecase._validar_senha("minhasenha")

    def test_validar_senha_invalida(self, usecase):
        """Testa validação de senha inválida."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            usecase._validar_senha("12345")
        assert "senha" in str(exc_info.value)

        with pytest.raises(DadosInvalidosException):
            usecase._validar_senha("")

        with pytest.raises(DadosInvalidosException):
            usecase._validar_senha(None)

    # Testes de cadastro
    @patch('src.application.usecase.usuario_usecases.get_password_hash')
    def test_cadastrar_usuario_sucesso(self, mock_hash, usecase, mock_service, usuario_exemplo):
        """Testa cadastro de usuário com sucesso."""
        # Arrange
        mock_service.buscar_por_email.return_value = None
        mock_service.criar.return_value = usuario_exemplo
        mock_hash.return_value = "$2b$12$hashexemplo"

        # Act
        resultado = usecase.cadastrar("João Silva", "joao@email.com", "senha123")

        # Assert
        assert resultado == usuario_exemplo
        mock_service.buscar_por_email.assert_called_once_with("joao@email.com")
        mock_service.criar.assert_called_once()
        mock_hash.assert_called_once_with("senha123")

    @patch('src.application.usecase.usuario_usecases.get_password_hash')
    def test_cadastrar_usuario_email_ja_existe(self, mock_hash, usecase, mock_service, usuario_exemplo):
        """Testa cadastro com email que já existe."""
        # Arrange
        mock_service.buscar_por_email.return_value = usuario_exemplo

        # Act & Assert
        with pytest.raises(EmailJaExisteException) as exc_info:
            usecase.cadastrar("João Silva", "joao@email.com", "senha123")

        assert "joao@email.com" in str(exc_info.value)
        mock_service.buscar_por_email.assert_called_once_with("joao@email.com")
        mock_service.criar.assert_not_called()
        mock_hash.assert_not_called()

    def test_cadastrar_usuario_nome_invalido(self, usecase, mock_service):
        """Testa cadastro com nome inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.cadastrar("A", "joao@email.com", "senha123")

        mock_service.buscar_por_email.assert_not_called()
        mock_service.criar.assert_not_called()

    def test_cadastrar_usuario_email_invalido(self, usecase, mock_service):
        """Testa cadastro com email inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.cadastrar("João Silva", "email_invalido", "senha123")

        mock_service.buscar_por_email.assert_not_called()
        mock_service.criar.assert_not_called()

    def test_cadastrar_usuario_senha_invalida(self, usecase, mock_service):
        """Testa cadastro com senha inválida."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.cadastrar("João Silva", "joao@email.com", "123")

        mock_service.buscar_por_email.assert_not_called()
        mock_service.criar.assert_not_called()

    # Testes de atualização
    @patch('src.application.usecase.usuario_usecases.get_password_hash')
    def test_atualizar_usuario_sucesso(self, mock_hash, usecase, mock_service, usuario_exemplo):
        """Testa atualização de usuário com sucesso."""
        # Arrange
        usuario_atualizado = Usuario(1, "João Santos", "joao.santos@email.com", "$2b$12$newhash")
        mock_service.buscar_por_id.return_value = usuario_exemplo
        mock_service.buscar_por_email.return_value = None
        mock_service.atualizar.return_value = usuario_atualizado
        mock_hash.return_value = "$2b$12$newhash"

        # Act
        resultado = usecase.atualizar(1, "João Santos", "joao.santos@email.com", "novasenha123")

        # Assert
        assert resultado == usuario_atualizado
        mock_service.buscar_por_id.assert_called_once_with(1)
        mock_service.buscar_por_email.assert_called_once_with("joao.santos@email.com")
        mock_service.atualizar.assert_called_once()
        mock_hash.assert_called_once_with("novasenha123")

    @patch('src.application.usecase.usuario_usecases.get_password_hash')
    def test_atualizar_usuario_mesmo_email(self, mock_hash, usecase, mock_service, usuario_exemplo):
        """Testa atualização mantendo o mesmo email."""
        # Arrange
        usuario_atualizado = Usuario(1, "João Santos", "joao@email.com", "$2b$12$newhash")
        mock_service.buscar_por_id.return_value = usuario_exemplo
        mock_service.buscar_por_email.return_value = usuario_exemplo  # Mesmo usuário
        mock_service.atualizar.return_value = usuario_atualizado
        mock_hash.return_value = "$2b$12$newhash"

        # Act
        resultado = usecase.atualizar(1, "João Santos", "joao@email.com", "novasenha123")

        # Assert
        assert resultado == usuario_atualizado
        mock_service.atualizar.assert_called_once()

    def test_atualizar_usuario_nao_encontrado(self, usecase, mock_service):
        """Testa atualização de usuário que não existe."""
        # Arrange
        mock_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException) as exc_info:
            usecase.atualizar(999, "João Silva", "joao@email.com", "senha123")

        assert "999" in str(exc_info.value)
        mock_service.buscar_por_id.assert_called_once_with(999)
        mock_service.buscar_por_email.assert_not_called()
        mock_service.atualizar.assert_not_called()

    def test_atualizar_usuario_email_ja_existe_outro_usuario(self, usecase, mock_service, usuario_exemplo):
        """Testa atualização com email de outro usuário."""
        # Arrange
        outro_usuario = Usuario(2, "Maria Silva", "maria@email.com", "$2b$12$hash")
        mock_service.buscar_por_id.return_value = usuario_exemplo
        mock_service.buscar_por_email.return_value = outro_usuario

        # Act & Assert
        with pytest.raises(EmailJaExisteException):
            usecase.atualizar(1, "João Santos", "maria@email.com", "senha123")

        mock_service.atualizar.assert_not_called()

    # Testes de remoção
    def test_remover_usuario_sucesso(self, usecase, mock_service, usuario_exemplo):
        """Testa remoção de usuário com sucesso."""
        # Arrange
        mock_service.buscar_por_id.return_value = usuario_exemplo
        mock_service.remover.return_value = True

        # Act
        resultado = usecase.remover(1)

        # Assert
        assert resultado is True
        mock_service.buscar_por_id.assert_called_once_with(1)
        mock_service.remover.assert_called_once_with(1)

    def test_remover_usuario_nao_encontrado(self, usecase, mock_service):
        """Testa remoção de usuário que não existe."""
        # Arrange
        mock_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException):
            usecase.remover(999)

        mock_service.buscar_por_id.assert_called_once_with(999)
        mock_service.remover.assert_not_called()

    # Testes de listagem
    def test_listar_usuarios(self, usecase, mock_service, usuario_exemplo):
        """Testa listagem de usuários."""
        # Arrange
        usuarios = [usuario_exemplo, Usuario(2, "Maria", "maria@email.com", "$2b$12$hash")]
        mock_service.listar.return_value = usuarios

        # Act
        resultado = usecase.listar()

        # Assert
        assert resultado == usuarios
        mock_service.listar.assert_called_once()

    def test_listar_paginado(self, usecase, mock_service, usuario_exemplo):
        """Testa listagem paginada de usuários."""
        # Arrange
        usuarios = [usuario_exemplo]
        total = 10
        mock_service.listar_paginado.return_value = (usuarios, total)

        # Act
        resultado_usuarios, resultado_total = usecase.listar_paginado(1, 5)

        # Assert
        assert resultado_usuarios == usuarios
        assert resultado_total == total
        mock_service.listar_paginado.assert_called_once_with(1, 5)

    # Testes de busca
    def test_buscar_por_id_encontrado(self, usecase, mock_service, usuario_exemplo):
        """Testa busca por ID quando usuário existe."""
        # Arrange
        mock_service.buscar_por_id.return_value = usuario_exemplo

        # Act
        resultado = usecase.buscar_por_id(1)

        # Assert
        assert resultado == usuario_exemplo
        mock_service.buscar_por_id.assert_called_once_with(1)

    def test_buscar_por_id_nao_encontrado(self, usecase, mock_service):
        """Testa busca por ID quando usuário não existe."""
        # Arrange
        mock_service.buscar_por_id.return_value = None

        # Act & Assert
        with pytest.raises(PessoaNaoEncontradaException):
            usecase.buscar_por_id(999)

        mock_service.buscar_por_id.assert_called_once_with(999)

    def test_buscar_por_email_encontrado(self, usecase, mock_service, usuario_exemplo):
        """Testa busca por email quando usuário existe."""
        # Arrange
        mock_service.buscar_por_email.return_value = usuario_exemplo

        # Act
        resultado = usecase.buscar_por_email("joao@email.com")

        # Assert
        assert resultado == usuario_exemplo
        mock_service.buscar_por_email.assert_called_once_with("joao@email.com")

    def test_buscar_por_email_nao_encontrado(self, usecase, mock_service):
        """Testa busca por email quando usuário não existe."""
        # Arrange
        mock_service.buscar_por_email.return_value = None

        # Act
        resultado = usecase.buscar_por_email("joao@email.com")

        # Assert
        assert resultado is None
        mock_service.buscar_por_email.assert_called_once_with("joao@email.com")

    def test_buscar_por_email_invalido(self, usecase, mock_service):
        """Testa busca por email com formato inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.buscar_por_email("email_invalido")

        mock_service.buscar_por_email.assert_not_called()

    # Testes de login
    @patch('src.application.usecase.usuario_usecases.create_access_token')
    @patch('src.application.usecase.usuario_usecases.verify_password')
    def test_login_sucesso(self, mock_verify, mock_token, usecase, mock_service, usuario_exemplo):
        """Testa login com credenciais válidas."""
        # Arrange
        mock_service.buscar_por_email.return_value = usuario_exemplo
        mock_verify.return_value = True
        mock_token.return_value = "jwt_token_exemplo"

        # Act
        resultado = usecase.login("joao@email.com", "senha123")

        # Assert
        assert resultado["access_token"] == "jwt_token_exemplo"
        assert resultado["token_type"] == "bearer"
        mock_service.buscar_por_email.assert_called_once_with("joao@email.com")
        mock_verify.assert_called_once_with("senha123", "$2b$12$hashexemplo")
        mock_token.assert_called_once()

    @patch('src.application.usecase.usuario_usecases.verify_password')
    def test_login_usuario_nao_encontrado(self, mock_verify, usecase, mock_service):
        """Testa login com usuário que não existe."""
        # Arrange
        mock_service.buscar_por_email.return_value = None

        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            usecase.login("joao@email.com", "senha123")

        assert "credenciais" in str(exc_info.value)
        mock_service.buscar_por_email.assert_called_once_with("joao@email.com")
        mock_verify.assert_not_called()

    @patch('src.application.usecase.usuario_usecases.verify_password')
    def test_login_senha_incorreta(self, mock_verify, usecase, mock_service, usuario_exemplo):
        """Testa login com senha incorreta."""
        # Arrange
        mock_service.buscar_por_email.return_value = usuario_exemplo
        mock_verify.return_value = False

        # Act & Assert
        with pytest.raises(DadosInvalidosException) as exc_info:
            usecase.login("joao@email.com", "senha_errada")

        assert "credenciais" in str(exc_info.value)
        mock_verify.assert_called_once_with("senha_errada", "$2b$12$hashexemplo")

    def test_login_email_invalido(self, usecase, mock_service):
        """Testa login com email inválido."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.login("email_invalido", "senha123")

        mock_service.buscar_por_email.assert_not_called()

    def test_login_senha_vazia(self, usecase, mock_service):
        """Testa login com senha vazia."""
        # Act & Assert
        with pytest.raises(DadosInvalidosException):
            usecase.login("joao@email.com", "")

        mock_service.buscar_por_email.assert_not_called()

    # Testes de fluxos completos
    @patch('src.application.usecase.usuario_usecases.get_password_hash')
    @patch('src.application.usecase.usuario_usecases.create_access_token')
    @patch('src.application.usecase.usuario_usecases.verify_password')
    def test_fluxo_completo_cadastro_login(self, mock_verify, mock_token, mock_hash, usecase, mock_service):
        """Testa fluxo completo de cadastro seguido de login."""
        # Arrange
        usuario_criado = Usuario(1, "João Silva", "joao@email.com", "$2b$12$hash")
        mock_service.buscar_por_email.side_effect = [None, usuario_criado]  # Cadastro, depois login
        mock_service.criar.return_value = usuario_criado
        mock_hash.return_value = "$2b$12$hash"
        mock_verify.return_value = True
        mock_token.return_value = "jwt_token"

        # Act - Cadastro
        resultado_cadastro = usecase.cadastrar("João Silva", "joao@email.com", "senha123")

        # Act - Login
        resultado_login = usecase.login("joao@email.com", "senha123")

        # Assert
        assert resultado_cadastro == usuario_criado
        assert resultado_login["access_token"] == "jwt_token"
        assert mock_service.buscar_por_email.call_count == 2
        mock_service.criar.assert_called_once()

    def test_orquestracao_service_metodos(self, usecase, mock_service):
        """Testa que o usecase orquestra corretamente os métodos do service."""
        # Arrange
        mock_service.buscar_por_email.return_value = None
        mock_service.listar.return_value = []

        # Act
        usecase.listar()
        usecase.buscar_por_email("test@email.com")

        # Assert
        mock_service.listar.assert_called_once()
        mock_service.buscar_por_email.assert_called_once_with("test@email.com")