"""
Testes para UsuarioRepository - Fase 2 do plano de testes.
Testa operações CRUD, queries complexas, paginação e tratamento de erros.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.infrastructure.persistence.repository.usuario_repository import UsuarioRepository
from src.domain.model.usuario import Usuario


class TestUsuarioRepository:
    """Testes para a classe UsuarioRepository."""

    def test_criar_usuario_sucesso(self, db_session: Session):
        """Testa criação de usuário com dados válidos."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario = Usuario(
            id=None,
            nome="João Silva",
            email="joao@email.com",
            senha_hash="hash123"
        )
        
        # Act
        resultado = repository.criar(usuario)
        db_session.commit()
        
        # Assert
        assert resultado.id is not None
        assert resultado.nome == "João Silva"
        assert resultado.email == "joao@email.com"
        assert resultado.senha_hash == "hash123"

    def test_criar_usuario_email_duplicado_falha(self, db_session: Session):
        """Testa que não é possível criar usuário com email duplicado."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario1 = Usuario(None, "João Silva", "joao@email.com", "hash123")
        usuario2 = Usuario(None, "Maria Silva", "joao@email.com", "hash456")
        
        # Act & Assert
        repository.criar(usuario1)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            repository.criar(usuario2)
            db_session.commit()

    def test_buscar_por_id_encontrado(self, db_session: Session):
        """Testa busca por ID quando usuário existe."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario = Usuario(None, "João Silva", "joao@email.com", "hash123")
        usuario_criado = repository.criar(usuario)
        db_session.commit()
        
        # Act
        resultado = repository.buscar_por_id(usuario_criado.id)
        
        # Assert
        assert resultado is not None
        assert resultado.id == usuario_criado.id
        assert resultado.nome == "João Silva"
        assert resultado.email == "joao@email.com"

    def test_buscar_por_id_nao_encontrado(self, db_session: Session):
        """Testa busca por ID quando usuário não existe."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Act
        resultado = repository.buscar_por_id(999)
        
        # Assert
        assert resultado is None

    def test_buscar_por_email_encontrado(self, db_session: Session):
        """Testa busca por email quando usuário existe."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario = Usuario(None, "João Silva", "joao@email.com", "hash123")
        repository.criar(usuario)
        db_session.commit()
        
        # Act
        resultado = repository.buscar_por_email("joao@email.com")
        
        # Assert
        assert resultado is not None
        assert resultado.nome == "João Silva"
        assert resultado.email == "joao@email.com"

    def test_buscar_por_email_nao_encontrado(self, db_session: Session):
        """Testa busca por email quando usuário não existe."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Act
        resultado = repository.buscar_por_email("naoexiste@email.com")
        
        # Assert
        assert resultado is None

    def test_listar_usuarios_vazio(self, db_session: Session):
        """Testa listagem quando não há usuários."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Act
        resultado = repository.listar()
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0

    def test_listar_usuarios_com_dados(self, db_session: Session):
        """Testa listagem quando há usuários cadastrados."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario1 = Usuario(None, "João Silva", "joao@email.com", "hash123")
        usuario2 = Usuario(None, "Maria Santos", "maria@email.com", "hash456")
        
        repository.criar(usuario1)
        repository.criar(usuario2)
        db_session.commit()
        
        # Act
        resultado = repository.listar()
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 2
        nomes = [u.nome for u in resultado]
        assert "João Silva" in nomes
        assert "Maria Santos" in nomes

    def test_listar_paginado_primeira_pagina(self, db_session: Session):
        """Testa paginação na primeira página."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Criar 5 usuários
        for i in range(5):
            usuario = Usuario(None, f"Usuário {i}", f"usuario{i}@email.com", f"hash{i}")
            repository.criar(usuario)
        db_session.commit()
        
        # Act
        usuarios, total = repository.listar_paginado(page=1, size=3)
        
        # Assert
        assert len(usuarios) == 3
        assert total == 5
        assert all(isinstance(u, Usuario) for u in usuarios)

    def test_listar_paginado_segunda_pagina(self, db_session: Session):
        """Testa paginação na segunda página."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Criar 5 usuários
        for i in range(5):
            usuario = Usuario(None, f"Usuário {i}", f"usuario{i}@email.com", f"hash{i}")
            repository.criar(usuario)
        db_session.commit()
        
        # Act
        usuarios, total = repository.listar_paginado(page=2, size=3)
        
        # Assert
        assert len(usuarios) == 2  # Restantes na segunda página
        assert total == 5

    def test_listar_paginado_pagina_vazia(self, db_session: Session):
        """Testa paginação quando página não tem dados."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Act
        usuarios, total = repository.listar_paginado(page=1, size=10)
        
        # Assert
        assert len(usuarios) == 0
        assert total == 0

    def test_atualizar_usuario_existente(self, db_session: Session):
        """Testa atualização de usuário existente."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario_original = Usuario(None, "João Silva", "joao@email.com", "hash123")
        usuario_criado = repository.criar(usuario_original)
        db_session.commit()
        
        usuario_atualizado = Usuario(
            usuario_criado.id,
            "João Santos",
            "joao.santos@email.com",
            "novoHash456"
        )
        
        # Act
        resultado = repository.atualizar(usuario_criado.id, usuario_atualizado)
        db_session.commit()
        
        # Assert
        assert resultado is not None
        assert resultado.id == usuario_criado.id
        assert resultado.nome == "João Santos"
        assert resultado.email == "joao.santos@email.com"
        assert resultado.senha_hash == "novoHash456"

    def test_atualizar_usuario_inexistente(self, db_session: Session):
        """Testa atualização de usuário que não existe."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario_inexistente = Usuario(999, "João Silva", "joao@email.com", "hash123")
        
        # Act
        resultado = repository.atualizar(999, usuario_inexistente)
        
        # Assert
        assert resultado is None

    def test_remover_usuario_existente(self, db_session: Session):
        """Testa remoção de usuário existente."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario = Usuario(None, "João Silva", "joao@email.com", "hash123")
        usuario_criado = repository.criar(usuario)
        db_session.commit()
        
        # Act
        resultado = repository.remover(usuario_criado.id)
        db_session.commit()
        
        # Assert
        assert resultado is True
        
        # Verificar que foi removido
        usuario_removido = repository.buscar_por_id(usuario_criado.id)
        assert usuario_removido is None

    def test_remover_usuario_inexistente(self, db_session: Session):
        """Testa remoção de usuário que não existe."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Act
        resultado = repository.remover(999)
        
        # Assert
        assert resultado is False

    def test_email_unico_constraint(self, db_session: Session):
        """Testa que email deve ser único no banco."""
        # Arrange
        repository = UsuarioRepository(db_session)
        usuario1 = Usuario(None, "João", "teste@email.com", "hash1")
        usuario2 = Usuario(None, "Maria", "teste@email.com", "hash2")
        
        # Act & Assert
        repository.criar(usuario1)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            repository.criar(usuario2)
            db_session.commit()

    def test_campos_obrigatorios(self, db_session: Session):
        """Testa que campos obrigatórios não podem ser None."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Act & Assert - Nome None
        with pytest.raises((IntegrityError, TypeError)):
            usuario_sem_nome = Usuario(None, None, "test@email.com", "hash")
            repository.criar(usuario_sem_nome)
            db_session.commit()

    def test_operacoes_consecutivas_mesma_sessao(self, db_session: Session):
        """Testa múltiplas operações na mesma sessão de banco."""
        # Arrange
        repository = UsuarioRepository(db_session)
        
        # Act - Criar usuário
        usuario = Usuario(None, "João Silva", "joao@email.com", "hash123")
        usuario_criado = repository.criar(usuario)
        db_session.flush()
        
        # Act - Buscar usuário criado
        usuario_encontrado = repository.buscar_por_id(usuario_criado.id)
        
        # Act - Atualizar usuário
        usuario_atualizado = Usuario(usuario_criado.id, "João Santos", "joao@email.com", "hash123")
        resultado_atualizacao = repository.atualizar(usuario_criado.id, usuario_atualizado)
        db_session.flush()
        
        # Act - Listar usuários
        lista_usuarios = repository.listar()
        
        # Assert
        assert usuario_encontrado is not None
        assert resultado_atualizacao is not None
        assert resultado_atualizacao.nome == "João Santos"
        assert len(lista_usuarios) == 1
        assert lista_usuarios[0].nome == "João Santos"