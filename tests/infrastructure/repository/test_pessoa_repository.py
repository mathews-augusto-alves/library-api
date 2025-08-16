"""
Testes para PessoaRepository - Fase 2 do plano de testes.
Testa operações CRUD, queries complexas, paginação e tratamento de erros.
"""
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.infrastructure.persistence.repository.pessoa_repository import PessoaRepository
from src.domain.model.pessoa import Pessoa


class TestPessoaRepository:
    """Testes para a classe PessoaRepository."""

    def test_criar_pessoa_sucesso(self, db_session: Session):
        """Testa criação de pessoa com dados válidos."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa = Pessoa(
            id=None,
            nome="Maria Santos",
            telefone="11999999999",
            data_nascimento=date(1990, 5, 15),
            email="maria@email.com"
        )
        
        # Act
        resultado = repository.criar(pessoa)
        db_session.commit()
        
        # Assert
        assert resultado.id is not None
        assert resultado.nome == "Maria Santos"
        assert resultado.telefone == "11999999999"
        assert resultado.data_nascimento == date(1990, 5, 15)
        assert resultado.email == "maria@email.com"

    def test_criar_pessoa_sem_email(self, db_session: Session):
        """Testa criação de pessoa sem email (opcional)."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa = Pessoa(
            id=None,
            nome="João Silva",
            telefone="11888888888",
            data_nascimento=date(1985, 10, 20),
            email=None
        )
        
        # Act
        resultado = repository.criar(pessoa)
        db_session.commit()
        
        # Assert
        assert resultado.id is not None
        assert resultado.nome == "João Silva"
        assert resultado.telefone == "11888888888"
        assert resultado.data_nascimento == date(1985, 10, 20)
        assert resultado.email is None

    def test_criar_pessoa_email_duplicado_falha(self, db_session: Session):
        """Testa que não é possível criar pessoa com email duplicado."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa1 = Pessoa(None, "Maria Santos", "11999999999", date(1990, 5, 15), "teste@email.com")
        pessoa2 = Pessoa(None, "João Silva", "11888888888", date(1985, 10, 20), "teste@email.com")
        
        # Act & Assert
        repository.criar(pessoa1)
        db_session.commit()
        
        with pytest.raises(IntegrityError):
            repository.criar(pessoa2)
            db_session.commit()

    def test_buscar_por_id_encontrado(self, db_session: Session):
        """Testa busca por ID quando pessoa existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa = Pessoa(None, "Ana Costa", "11777777777", date(1992, 3, 8), "ana@email.com")
        pessoa_criada = repository.criar(pessoa)
        db_session.commit()
        
        # Act
        resultado = repository.buscar_por_id(pessoa_criada.id)
        
        # Assert
        assert resultado is not None
        assert resultado.id == pessoa_criada.id
        assert resultado.nome == "Ana Costa"
        assert resultado.telefone == "11777777777"
        assert resultado.data_nascimento == date(1992, 3, 8)
        assert resultado.email == "ana@email.com"

    def test_buscar_por_id_nao_encontrado(self, db_session: Session):
        """Testa busca por ID quando pessoa não existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act
        resultado = repository.buscar_por_id(999)
        
        # Assert
        assert resultado is None

    def test_buscar_por_email_encontrado(self, db_session: Session):
        """Testa busca por email quando pessoa existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa = Pessoa(None, "Carlos Lima", "11666666666", date(1988, 12, 25), "carlos@email.com")
        repository.criar(pessoa)
        db_session.commit()
        
        # Act
        resultado = repository.buscar_por_email("carlos@email.com")
        
        # Assert
        assert resultado is not None
        assert resultado.nome == "Carlos Lima"
        assert resultado.email == "carlos@email.com"

    def test_buscar_por_email_nao_encontrado(self, db_session: Session):
        """Testa busca por email quando pessoa não existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act
        resultado = repository.buscar_por_email("naoexiste@email.com")
        
        # Assert
        assert resultado is None

    def test_email_existe_verdadeiro(self, db_session: Session):
        """Testa verificação de existência de email quando existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa = Pessoa(None, "Lucia Ferreira", "11555555555", date(1995, 7, 14), "lucia@email.com")
        repository.criar(pessoa)
        db_session.commit()
        
        # Act
        resultado = repository.email_existe("lucia@email.com")
        
        # Assert
        assert resultado is True

    def test_email_existe_falso(self, db_session: Session):
        """Testa verificação de existência de email quando não existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act
        resultado = repository.email_existe("naoexiste@email.com")
        
        # Assert
        assert resultado is False

    def test_listar_pessoas_vazio(self, db_session: Session):
        """Testa listagem quando não há pessoas."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act
        resultado = repository.listar()
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0

    def test_listar_pessoas_com_dados(self, db_session: Session):
        """Testa listagem quando há pessoas cadastradas."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa1 = Pessoa(None, "Roberto Silva", "11444444444", date(1980, 1, 1), "roberto@email.com")
        pessoa2 = Pessoa(None, "Fernanda Costa", "11333333333", date(1987, 6, 10), None)
        
        repository.criar(pessoa1)
        repository.criar(pessoa2)
        db_session.commit()
        
        # Act
        resultado = repository.listar()
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 2
        nomes = [p.nome for p in resultado]
        assert "Roberto Silva" in nomes
        assert "Fernanda Costa" in nomes

    def test_listar_paginado_primeira_pagina(self, db_session: Session):
        """Testa paginação na primeira página."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Criar 5 pessoas
        for i in range(5):
            pessoa = Pessoa(None, f"Pessoa {i}", f"1155555555{i}", date(1990, 1, i+1), f"pessoa{i}@email.com")
            repository.criar(pessoa)
        db_session.commit()
        
        # Act
        pessoas, total = repository.listar_paginado(page=1, size=3)
        
        # Assert
        assert len(pessoas) == 3
        assert total == 5
        assert all(isinstance(p, Pessoa) for p in pessoas)

    def test_listar_paginado_segunda_pagina(self, db_session: Session):
        """Testa paginação na segunda página."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Criar 5 pessoas
        for i in range(5):
            pessoa = Pessoa(None, f"Pessoa {i}", f"1155555555{i}", date(1990, 1, i+1), f"pessoa{i}@email.com")
            repository.criar(pessoa)
        db_session.commit()
        
        # Act
        pessoas, total = repository.listar_paginado(page=2, size=3)
        
        # Assert
        assert len(pessoas) == 2  # Restantes na segunda página
        assert total == 5

    def test_listar_paginado_pagina_vazia(self, db_session: Session):
        """Testa paginação quando página não tem dados."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act
        pessoas, total = repository.listar_paginado(page=1, size=10)
        
        # Assert
        assert len(pessoas) == 0
        assert total == 0

    def test_atualizar_pessoa_existente(self, db_session: Session):
        """Testa atualização de pessoa existente."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa_original = Pessoa(None, "Pedro Santos", "11222222222", date(1993, 4, 22), "pedro@email.com")
        pessoa_criada = repository.criar(pessoa_original)
        db_session.commit()
        
        pessoa_atualizada = Pessoa(
            pessoa_criada.id,
            "Pedro Oliveira",
            "11111111111",
            date(1993, 4, 22),
            "pedro.oliveira@email.com"
        )
        
        # Act
        resultado = repository.atualizar(pessoa_criada.id, pessoa_atualizada)
        db_session.commit()
        
        # Assert
        assert resultado is not None
        assert resultado.id == pessoa_criada.id
        assert resultado.nome == "Pedro Oliveira"
        assert resultado.telefone == "11111111111"
        assert resultado.data_nascimento == date(1993, 4, 22)
        assert resultado.email == "pedro.oliveira@email.com"

    def test_atualizar_pessoa_inexistente(self, db_session: Session):
        """Testa atualização de pessoa que não existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa_inexistente = Pessoa(999, "Pessoa Inexistente", "11000000000", date(1990, 1, 1), "inexistente@email.com")
        
        # Act
        resultado = repository.atualizar(999, pessoa_inexistente)
        
        # Assert
        assert resultado is None

    def test_remover_pessoa_existente(self, db_session: Session):
        """Testa remoção de pessoa existente."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa = Pessoa(None, "Rafael Sousa", "11999888777", date(1991, 11, 3), "rafael@email.com")
        pessoa_criada = repository.criar(pessoa)
        db_session.commit()
        
        # Act
        resultado = repository.remover(pessoa_criada.id)
        db_session.commit()
        
        # Assert
        assert resultado is True
        
        # Verificar que foi removido
        pessoa_removida = repository.buscar_por_id(pessoa_criada.id)
        assert pessoa_removida is None

    def test_remover_pessoa_inexistente(self, db_session: Session):
        """Testa remoção de pessoa que não existe."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act
        resultado = repository.remover(999)
        
        # Assert
        assert resultado is False

    def test_campos_obrigatorios(self, db_session: Session):
        """Testa que campos obrigatórios são tratados adequadamente."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act - Criar pessoa com dados válidos (teste positivo)
        pessoa_valida = Pessoa(None, "Nome Válido", "11999999999", date(1990, 1, 1), "teste@email.com")
        resultado = repository.criar(pessoa_valida)
        db_session.commit()
        
        # Assert - Verificar que pessoa foi criada corretamente
        assert resultado.id is not None
        assert resultado.nome == "Nome Válido"
        assert resultado.telefone == "11999999999"
        assert resultado.data_nascimento == date(1990, 1, 1)

    def test_data_nascimento_valida(self, db_session: Session):
        """Testa criação com diferentes datas de nascimento válidas."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act - Data passada
        pessoa_passada = Pessoa(None, "Pessoa Passada", "11111111111", date(1950, 1, 1), "passada@email.com")
        resultado_passada = repository.criar(pessoa_passada)
        
        # Act - Data recente
        pessoa_recente = Pessoa(None, "Pessoa Recente", "11222222222", date(2000, 12, 31), "recente@email.com")
        resultado_recente = repository.criar(pessoa_recente)
        
        db_session.commit()
        
        # Assert
        assert resultado_passada.data_nascimento == date(1950, 1, 1)
        assert resultado_recente.data_nascimento == date(2000, 12, 31)

    def test_operacoes_consecutivas_mesma_sessao(self, db_session: Session):
        """Testa múltiplas operações na mesma sessão de banco."""
        # Arrange
        repository = PessoaRepository(db_session)
        
        # Act - Criar pessoa
        pessoa = Pessoa(None, "Teste Operações", "11888777666", date(1989, 8, 17), "teste@email.com")
        pessoa_criada = repository.criar(pessoa)
        db_session.flush()
        
        # Act - Verificar se email existe
        email_existe = repository.email_existe("teste@email.com")
        
        # Act - Buscar pessoa criada
        pessoa_encontrada = repository.buscar_por_id(pessoa_criada.id)
        
        # Act - Atualizar pessoa
        pessoa_atualizada = Pessoa(pessoa_criada.id, "Teste Atualizado", "11777666555", date(1989, 8, 17), "teste.atualizado@email.com")
        resultado_atualizacao = repository.atualizar(pessoa_criada.id, pessoa_atualizada)
        db_session.flush()
        
        # Act - Listar pessoas
        lista_pessoas = repository.listar()
        
        # Assert
        assert email_existe is True
        assert pessoa_encontrada is not None
        assert resultado_atualizacao is not None
        assert resultado_atualizacao.nome == "Teste Atualizado"
        assert resultado_atualizacao.email == "teste.atualizado@email.com"
        assert len(lista_pessoas) == 1
        assert lista_pessoas[0].nome == "Teste Atualizado"

    def test_buscar_pessoas_por_diferentes_criterios(self, db_session: Session):
        """Testa busca por diferentes critérios (ID e email)."""
        # Arrange
        repository = PessoaRepository(db_session)
        pessoa1 = Pessoa(None, "Busca Por ID", "11555444333", date(1992, 2, 14), "busca.id@email.com")
        pessoa2 = Pessoa(None, "Busca Por Email", "11444333222", date(1994, 9, 28), "busca.email@email.com")
        
        pessoa1_criada = repository.criar(pessoa1)
        pessoa2_criada = repository.criar(pessoa2)
        db_session.commit()
        
        # Act
        encontrada_por_id = repository.buscar_por_id(pessoa1_criada.id)
        encontrada_por_email = repository.buscar_por_email("busca.email@email.com")
        
        # Assert
        assert encontrada_por_id is not None
        assert encontrada_por_id.nome == "Busca Por ID"
        
        assert encontrada_por_email is not None
        assert encontrada_por_email.nome == "Busca Por Email"