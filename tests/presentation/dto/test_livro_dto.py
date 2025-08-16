"""
Testes para os DTOs de livro.
"""
import pytest
from datetime import date
from src.presentation.dto.livro_dto import LivroCreateRequest, LivroResponse, EmprestimoCreateRequest


class TestLivroCreateRequest:
    """Testes para LivroCreateRequest."""
    
    def test_criar_livro_valido(self):
        """Teste de criação de livro com dados válidos."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien"
        )
        
        # Assert
        assert dto.titulo == "O Senhor dos Anéis"
        assert dto.autor == "J.R.R. Tolkien"
    
    def test_criar_livro_titulo_minimo(self):
        """Teste de criação com título de tamanho mínimo."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="AB",  # 2 caracteres (mínimo)
            autor="Autor Teste"
        )
        
        # Assert
        assert dto.titulo == "AB"
    
    def test_criar_livro_titulo_medio(self):
        """Teste de criação com título de tamanho médio."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="O Senhor dos Anéis - A Sociedade do Anel",
            autor="J.R.R. Tolkien"
        )
        
        # Assert
        assert dto.titulo == "O Senhor dos Anéis - A Sociedade do Anel"
    
    def test_criar_livro_titulo_maximo(self):
        """Teste de criação com título de tamanho máximo."""
        # Arrange & Act
        titulo_maximo = "A" * 200  # 200 caracteres (máximo)
        dto = LivroCreateRequest(
            titulo=titulo_maximo,
            autor="Autor Teste"
        )
        
        # Assert
        assert dto.titulo == titulo_maximo
    
    def test_criar_livro_autor_minimo(self):
        """Teste de criação com autor de tamanho mínimo."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="Título Teste",
            autor="AB"  # 2 caracteres (mínimo)
        )
        
        # Assert
        assert dto.autor == "AB"
    
    def test_criar_livro_autor_medio(self):
        """Teste de criação com autor de tamanho médio."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="Título Teste",
            autor="John Ronald Reuel Tolkien"
        )
        
        # Assert
        assert dto.autor == "John Ronald Reuel Tolkien"
    
    def test_criar_livro_autor_maximo(self):
        """Teste de criação com autor de tamanho máximo."""
        # Arrange & Act
        autor_maximo = "A" * 100  # 100 caracteres (máximo)
        dto = LivroCreateRequest(
            titulo="Título Teste",
            autor=autor_maximo
        )
        
        # Assert
        assert dto.autor == autor_maximo
    
    def test_validacao_titulo_vazio(self):
        """Teste de validação com título vazio."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Título deve ter pelo menos 2 caracteres"):
            LivroCreateRequest(
                titulo="",  # Vazio
                autor="Autor Teste"
            )
    
    def test_validacao_titulo_muito_curto(self):
        """Teste de validação com título muito curto."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Título deve ter pelo menos 2 caracteres"):
            LivroCreateRequest(
                titulo="A",  # 1 caractere
                autor="Autor Teste"
            )
    
    def test_validacao_titulo_apenas_espacos(self):
        """Teste de validação com título apenas com espaços."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Título deve ter pelo menos 2 caracteres"):
            LivroCreateRequest(
                titulo="   ",  # Apenas espaços
                autor="Autor Teste"
            )
    
    def test_validacao_autor_vazio(self):
        """Teste de validação com autor vazio."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Autor deve ter pelo menos 2 caracteres"):
            LivroCreateRequest(
                titulo="Título Teste",
                autor=""  # Vazio
            )
    
    def test_validacao_autor_muito_curto(self):
        """Teste de validação com autor muito curto."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Autor deve ter pelo menos 2 caracteres"):
            LivroCreateRequest(
                titulo="Título Teste",
                autor="A"  # 1 caractere
            )
    
    def test_validacao_autor_apenas_espacos(self):
        """Teste de validação com autor apenas com espaços."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Autor deve ter pelo menos 2 caracteres"):
            LivroCreateRequest(
                titulo="Título Teste",
                autor="   "  # Apenas espaços
            )
    
    def test_criar_livro_com_caracteres_especiais(self):
        """Teste de criação com caracteres especiais."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="1984 - Mil Novecentos e Oitenta e Quatro",
            autor="George Orwell"
        )
        
        # Assert
        assert dto.titulo == "1984 - Mil Novecentos e Oitenta e Quatro"
        assert dto.autor == "George Orwell"
    
    def test_criar_livro_com_acentos(self):
        """Teste de criação com acentos."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="O Pequeno Príncipe",
            autor="Antoine de Saint-Exupéry"
        )
        
        # Assert
        assert dto.titulo == "O Pequeno Príncipe"
        assert dto.autor == "Antoine de Saint-Exupéry"
    
    def test_criar_livro_com_espacos_extras(self):
        """Teste de criação com espaços extras que devem ser removidos."""
        # Arrange & Act
        dto = LivroCreateRequest(
            titulo="  O Senhor dos Anéis  ",
            autor="  J.R.R. Tolkien  "
        )
        
        # Assert - Espaços devem ser removidos pelos validadores
        assert dto.titulo == "O Senhor dos Anéis"
        assert dto.autor == "J.R.R. Tolkien"


class TestLivroResponse:
    """Testes para LivroResponse."""
    
    def test_criar_resposta_valida(self):
        """Teste de criação de resposta com dados válidos."""
        # Arrange & Act
        dto = LivroResponse(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )
        
        # Assert
        assert dto.id == 1
        assert dto.titulo == "O Senhor dos Anéis"
        assert dto.autor == "J.R.R. Tolkien"
        assert dto.disponivel is True
    
    def test_resposta_com_id_zero(self):
        """Teste de resposta com ID zero."""
        # Arrange & Act
        dto = LivroResponse(
            id=0,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )
        
        # Assert
        assert dto.id == 0
        assert dto.titulo == "O Senhor dos Anéis"
        assert dto.autor == "J.R.R. Tolkien"
        assert dto.disponivel is True
    
    def test_resposta_livro_indisponivel(self):
        """Teste de resposta para livro indisponível."""
        # Arrange & Act
        dto = LivroResponse(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=False
        )
        
        # Assert
        assert dto.id == 1
        assert dto.titulo == "O Senhor dos Anéis"
        assert dto.autor == "J.R.R. Tolkien"
        assert dto.disponivel is False
    
    def test_resposta_com_diferentes_tipos_disponibilidade(self):
        """Teste de resposta com diferentes tipos de disponibilidade."""
        # Arrange & Act - Livro disponível
        dto_disponivel = LivroResponse(
            id=1,
            titulo="Livro Disponível",
            autor="Autor Teste",
            disponivel=True
        )
        
        # Assert - Livro disponível
        assert dto_disponivel.disponivel is True
        
        # Arrange & Act - Livro indisponível
        dto_indisponivel = LivroResponse(
            id=2,
            titulo="Livro Indisponível",
            autor="Autor Teste",
            disponivel=False
        )
        
        # Assert - Livro indisponível
        assert dto_indisponivel.disponivel is False
    
    def test_serializacao_dto(self):
        """Teste de serialização do DTO."""
        # Arrange
        dto = LivroResponse(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )
        
        # Act
        dados = dto.model_dump()
        
        # Assert
        assert dados["id"] == 1
        assert dados["titulo"] == "O Senhor dos Anéis"
        assert dados["autor"] == "J.R.R. Tolkien"
        assert dados["disponivel"] is True
    
    def test_serializacao_json(self):
        """Teste de serialização para JSON."""
        # Arrange
        dto = LivroResponse(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )
        
        # Act
        dados_json = dto.model_dump(mode="json")
        
        # Assert
        assert dados_json["id"] == 1
        assert dados_json["titulo"] == "O Senhor dos Anéis"
        assert dados_json["autor"] == "J.R.R. Tolkien"
        assert dados_json["disponivel"] is True


class TestEmprestimoCreateRequest:
    """Testes para EmprestimoCreateRequest."""
    
    def test_criar_emprestimo_valido(self):
        """Teste de criação de empréstimo com dados válidos."""
        # Arrange & Act
        dto = EmprestimoCreateRequest(
            livro_id=1,
            pessoa_id=1
        )
        
        # Assert
        assert dto.livro_id == 1
        assert dto.pessoa_id == 1
    
    def test_criar_emprestimo_com_ids_diferentes(self):
        """Teste de criação com IDs diferentes."""
        # Arrange & Act
        dto = EmprestimoCreateRequest(
            livro_id=5,
            pessoa_id=10
        )
        
        # Assert
        assert dto.livro_id == 5
        assert dto.pessoa_id == 10
    
    def test_criar_emprestimo_com_id_zero(self):
        """Teste de criação com ID zero."""
        # Arrange & Act
        dto = EmprestimoCreateRequest(
            livro_id=0,
            pessoa_id=0
        )
        
        # Assert
        assert dto.livro_id == 0
        assert dto.pessoa_id == 0
    
    def test_emprestimo_com_ids_altos(self):
        """Teste de empréstimo com IDs altos."""
        # Arrange & Act
        dto = EmprestimoCreateRequest(
            livro_id=999999,
            pessoa_id=888888
        )
        
        # Assert
        assert dto.livro_id == 999999
        assert dto.pessoa_id == 888888
    
    def test_serializacao_emprestimo(self):
        """Teste de serialização do DTO de empréstimo."""
        # Arrange
        dto = EmprestimoCreateRequest(
            livro_id=1,
            pessoa_id=1
        )
        
        # Act
        dados = dto.model_dump()
        
        # Assert
        assert dados["livro_id"] == 1
        assert dados["pessoa_id"] == 1
    
    def test_fluxo_completo_criar_livro_emprestar(self):
        """Teste de fluxo completo: criar livro e empréstimo."""
        # Arrange & Act - Criar livro
        livro_dto = LivroCreateRequest(
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien"
        )
        
        # Assert - Criar livro
        assert livro_dto.titulo == "O Senhor dos Anéis"
        assert livro_dto.autor == "J.R.R. Tolkien"
        
        # Arrange & Act - Criar empréstimo
        emprestimo_dto = EmprestimoCreateRequest(
            livro_id=1,
            pessoa_id=1
        )
        
        # Assert - Criar empréstimo
        assert emprestimo_dto.livro_id == 1
        assert emprestimo_dto.pessoa_id == 1
        
        # Arrange & Act - Resposta do livro
        livro_response = LivroResponse(
            id=1,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=False  # Agora indisponível
        )
        
        # Assert - Resposta do livro
        assert livro_response.id == 1
        assert livro_response.titulo == "O Senhor dos Anéis"
        assert livro_response.disponivel is False 