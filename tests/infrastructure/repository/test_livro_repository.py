"""
Testes para LivroRepository - Fase 2 do plano de testes.
Testa operações CRUD, queries complexas, paginação e tratamento de erros.
"""
import pytest
from sqlalchemy.orm import Session

from src.infrastructure.persistence.repository.livro_repository import LivroRepository
from src.domain.model.livro import Livro


class TestLivroRepository:
    """Testes para a classe LivroRepository."""

    def test_criar_livro_sucesso(self, db_session: Session):
        """Testa criação de livro com dados válidos."""
        # Arrange
        repository = LivroRepository(db_session)
        livro = Livro(
            id=None,
            titulo="O Senhor dos Anéis",
            autor="J.R.R. Tolkien",
            disponivel=True
        )
        
        # Act
        resultado = repository.criar(livro)
        db_session.commit()
        
        # Assert
        assert resultado.id is not None
        assert resultado.titulo == "O Senhor dos Anéis"
        assert resultado.autor == "J.R.R. Tolkien"
        assert resultado.disponivel is True

    def test_criar_livro_indisponivel(self, db_session: Session):
        """Testa criação de livro marcado como indisponível."""
        # Arrange
        repository = LivroRepository(db_session)
        livro = Livro(
            id=None,
            titulo="1984",
            autor="George Orwell",
            disponivel=False
        )
        
        # Act
        resultado = repository.criar(livro)
        db_session.commit()
        
        # Assert
        assert resultado.id is not None
        assert resultado.titulo == "1984"
        assert resultado.autor == "George Orwell"
        assert resultado.disponivel is False

    def test_buscar_por_id_encontrado(self, db_session: Session):
        """Testa busca por ID quando livro existe."""
        # Arrange
        repository = LivroRepository(db_session)
        livro = Livro(None, "Dune", "Frank Herbert", True)
        livro_criado = repository.criar(livro)
        db_session.commit()
        
        # Act
        resultado = repository.buscar_por_id(livro_criado.id)
        
        # Assert
        assert resultado is not None
        assert resultado.id == livro_criado.id
        assert resultado.titulo == "Dune"
        assert resultado.autor == "Frank Herbert"
        assert resultado.disponivel is True

    def test_buscar_por_id_nao_encontrado(self, db_session: Session):
        """Testa busca por ID quando livro não existe."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Act
        resultado = repository.buscar_por_id(999)
        
        # Assert
        assert resultado is None

    def test_listar_livros_vazio(self, db_session: Session):
        """Testa listagem quando não há livros."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Act
        resultado = repository.listar()
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0

    def test_listar_livros_com_dados(self, db_session: Session):
        """Testa listagem quando há livros cadastrados."""
        # Arrange
        repository = LivroRepository(db_session)
        livro1 = Livro(None, "1984", "George Orwell", True)
        livro2 = Livro(None, "Brave New World", "Aldous Huxley", False)
        
        repository.criar(livro1)
        repository.criar(livro2)
        db_session.commit()
        
        # Act
        resultado = repository.listar()
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 2
        titulos = [l.titulo for l in resultado]
        assert "1984" in titulos
        assert "Brave New World" in titulos

    def test_listar_paginado_primeira_pagina(self, db_session: Session):
        """Testa paginação na primeira página."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Criar 5 livros
        for i in range(5):
            livro = Livro(None, f"Livro {i}", f"Autor {i}", i % 2 == 0)
            repository.criar(livro)
        db_session.commit()
        
        # Act
        livros, total = repository.listar_paginado(page=1, size=3)
        
        # Assert
        assert len(livros) == 3
        assert total == 5
        assert all(isinstance(l, Livro) for l in livros)

    def test_listar_paginado_segunda_pagina(self, db_session: Session):
        """Testa paginação na segunda página."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Criar 5 livros
        for i in range(5):
            livro = Livro(None, f"Livro {i}", f"Autor {i}", True)
            repository.criar(livro)
        db_session.commit()
        
        # Act
        livros, total = repository.listar_paginado(page=2, size=3)
        
        # Assert
        assert len(livros) == 2  # Restantes na segunda página
        assert total == 5

    def test_listar_paginado_pagina_vazia(self, db_session: Session):
        """Testa paginação quando página não tem dados."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Act
        livros, total = repository.listar_paginado(page=1, size=10)
        
        # Assert
        assert len(livros) == 0
        assert total == 0

    def test_atualizar_disponibilidade_para_indisponivel(self, db_session: Session):
        """Testa atualização de disponibilidade para falso."""
        # Arrange
        repository = LivroRepository(db_session)
        livro = Livro(None, "Fahrenheit 451", "Ray Bradbury", True)
        livro_criado = repository.criar(livro)
        db_session.commit()
        
        # Act
        resultado = repository.atualizar_disponibilidade(livro_criado.id, False)
        db_session.commit()
        
        # Assert
        assert resultado is not None
        assert resultado.id == livro_criado.id
        assert resultado.titulo == "Fahrenheit 451"
        assert resultado.autor == "Ray Bradbury"
        assert resultado.disponivel is False

    def test_atualizar_disponibilidade_para_disponivel(self, db_session: Session):
        """Testa atualização de disponibilidade para verdadeiro."""
        # Arrange
        repository = LivroRepository(db_session)
        livro = Livro(None, "Neuromancer", "William Gibson", False)
        livro_criado = repository.criar(livro)
        db_session.commit()
        
        # Act
        resultado = repository.atualizar_disponibilidade(livro_criado.id, True)
        db_session.commit()
        
        # Assert
        assert resultado is not None
        assert resultado.id == livro_criado.id
        assert resultado.titulo == "Neuromancer"
        assert resultado.autor == "William Gibson"
        assert resultado.disponivel is True

    def test_atualizar_disponibilidade_livro_inexistente(self, db_session: Session):
        """Testa atualização de disponibilidade de livro que não existe."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Act
        resultado = repository.atualizar_disponibilidade(999, True)
        
        # Assert
        assert resultado is None

    def test_campos_obrigatorios_titulo_autor(self, db_session: Session):
        """Testa que título e autor são tratados adequadamente."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Act - Criar livro com dados válidos (teste positivo)
        livro_valido = Livro(None, "Título Válido", "Autor Válido", True)
        resultado = repository.criar(livro_valido)
        db_session.commit()
        
        # Assert - Verificar que livro foi criado corretamente
        assert resultado.id is not None
        assert resultado.titulo == "Título Válido"
        assert resultado.autor == "Autor Válido"

    def test_disponibilidade_default_true(self, db_session: Session):
        """Testa que disponibilidade padrão é True."""
        # Arrange
        repository = LivroRepository(db_session)
        livro = Livro(None, "Blade Runner", "Philip K. Dick")  # Sem especificar disponivel
        
        # Act
        resultado = repository.criar(livro)
        db_session.commit()
        
        # Assert
        assert resultado.disponivel is True

    def test_operacoes_consecutivas_mesma_sessao(self, db_session: Session):
        """Testa múltiplas operações na mesma sessão de banco."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Act - Criar livro
        livro = Livro(None, "Foundation", "Isaac Asimov", True)
        livro_criado = repository.criar(livro)
        db_session.flush()
        
        # Act - Buscar livro criado
        livro_encontrado = repository.buscar_por_id(livro_criado.id)
        
        # Act - Atualizar disponibilidade
        resultado_atualizacao = repository.atualizar_disponibilidade(livro_criado.id, False)
        db_session.flush()
        
        # Act - Listar livros
        lista_livros = repository.listar()
        
        # Assert
        assert livro_encontrado is not None
        assert livro_encontrado.disponivel is True  # Antes da atualização
        assert resultado_atualizacao is not None
        assert resultado_atualizacao.disponivel is False  # Após a atualização
        assert len(lista_livros) == 1
        assert lista_livros[0].disponivel is False

    def test_buscar_e_atualizar_livro_especifico(self, db_session: Session):
        """Testa busca e atualização de um livro específico entre vários."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Criar 3 livros
        livros_criados = []
        for i in range(3):
            livro = Livro(None, f"Livro {i}", f"Autor {i}", True)
            livro_criado = repository.criar(livro)
            livros_criados.append(livro_criado)
        db_session.commit()
        
        # Act - Buscar o livro do meio
        livro_meio = repository.buscar_por_id(livros_criados[1].id)
        
        # Act - Atualizar disponibilidade apenas do livro do meio
        repository.atualizar_disponibilidade(livros_criados[1].id, False)
        db_session.commit()
        
        # Act - Verificar estado de todos os livros
        todos_livros = repository.listar()
        
        # Assert
        assert livro_meio is not None
        assert livro_meio.titulo == "Livro 1"
        
        # Verificar que apenas o livro do meio foi atualizado
        livros_indisponiveis = [l for l in todos_livros if not l.disponivel]
        assert len(livros_indisponiveis) == 1
        assert livros_indisponiveis[0].titulo == "Livro 1"

    def test_filtrar_livros_por_disponibilidade(self, db_session: Session):
        """Testa filtragem implícita por disponibilidade através da listagem."""
        # Arrange
        repository = LivroRepository(db_session)
        
        # Criar livros com diferentes disponibilidades
        livro1 = Livro(None, "Disponível 1", "Autor 1", True)
        livro2 = Livro(None, "Indisponível 1", "Autor 2", False)
        livro3 = Livro(None, "Disponível 2", "Autor 3", True)
        
        repository.criar(livro1)
        repository.criar(livro2)
        repository.criar(livro3)
        db_session.commit()
        
        # Act
        todos_livros = repository.listar()
        livros_disponiveis = [l for l in todos_livros if l.disponivel]
        livros_indisponiveis = [l for l in todos_livros if not l.disponivel]
        
        # Assert
        assert len(todos_livros) == 3
        assert len(livros_disponiveis) == 2
        assert len(livros_indisponiveis) == 1
        
        titulos_disponiveis = [l.titulo for l in livros_disponiveis]
        assert "Disponível 1" in titulos_disponiveis
        assert "Disponível 2" in titulos_disponiveis
        
        assert livros_indisponiveis[0].titulo == "Indisponível 1"