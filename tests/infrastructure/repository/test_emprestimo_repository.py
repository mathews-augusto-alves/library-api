"""
Testes para EmprestimoRepository - Fase 2 do plano de testes.
Testa operações CRUD, queries complexas, paginação e tratamento de erros.
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

from src.infrastructure.persistence.repository.emprestimo_repository import EmprestimoRepository
from src.infrastructure.persistence.repository.usuario_repository import UsuarioRepository
from src.infrastructure.persistence.repository.livro_repository import LivroRepository
from src.infrastructure.persistence.repository.pessoa_repository import PessoaRepository
from src.domain.model.emprestimo import Emprestimo
from src.domain.model.usuario import Usuario
from src.domain.model.livro import Livro
from src.domain.model.pessoa import Pessoa
from src.domain.enums.emprestimo_status import EmprestimoStatus
from datetime import date


class TestEmprestimoRepository:
    """Testes para a classe EmprestimoRepository."""

    @pytest.fixture
    def setup_data(self, db_session: Session):
        """Setup de dados básicos para os testes."""
        # Criar repositórios
        usuario_repo = UsuarioRepository(db_session)
        livro_repo = LivroRepository(db_session)
        pessoa_repo = PessoaRepository(db_session)
        
        # Criar dados de teste
        usuario = usuario_repo.criar(Usuario(None, "Admin", "admin@email.com", "hash123"))
        livro = livro_repo.criar(Livro(None, "Livro Teste", "Autor Teste", True))
        pessoa = pessoa_repo.criar(Pessoa(None, "Pessoa Teste", "11999999999", date(1990, 1, 1), "pessoa@email.com"))
        
        db_session.commit()
        
        return {
            "usuario_id": usuario.id,
            "livro_id": livro.id,
            "pessoa_id": pessoa.id
        }

    def test_criar_emprestimo_sucesso(self, db_session: Session, setup_data):
        """Testa criação de empréstimo com dados válidos."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        data_emprestimo = datetime.now(tz)
        
        emprestimo = Emprestimo(
            id=None,
            livro_id=setup_data["livro_id"],
            pessoa_id=setup_data["pessoa_id"],
            usuario_id=setup_data["usuario_id"],
            data_emprestimo=data_emprestimo,
            data_devolucao=None
        )
        
        # Act
        resultado = repository.criar(emprestimo)
        db_session.commit()
        
        # Assert
        assert resultado.id is not None
        assert resultado.livro_id == setup_data["livro_id"]
        assert resultado.pessoa_id == setup_data["pessoa_id"]
        assert resultado.usuario_id == setup_data["usuario_id"]
        assert resultado.data_emprestimo == data_emprestimo
        assert resultado.data_devolucao is None

    def test_criar_emprestimo_ja_devolvido(self, db_session: Session, setup_data):
        """Testa criação de empréstimo que já foi devolvido."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        data_emprestimo = datetime.now(tz)
        data_devolucao = datetime.now(tz)
        
        emprestimo = Emprestimo(
            id=None,
            livro_id=setup_data["livro_id"],
            pessoa_id=setup_data["pessoa_id"],
            usuario_id=setup_data["usuario_id"],
            data_emprestimo=data_emprestimo,
            data_devolucao=data_devolucao
        )
        
        # Act
        resultado = repository.criar(emprestimo)
        db_session.commit()
        
        # Assert
        assert resultado.id is not None
        assert resultado.data_emprestimo == data_emprestimo
        assert resultado.data_devolucao == data_devolucao

    def test_buscar_ativo_por_livro_encontrado(self, db_session: Session, setup_data):
        """Testa busca de empréstimo ativo por livro quando existe."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        emprestimo = Emprestimo(
            id=None,
            livro_id=setup_data["livro_id"],
            pessoa_id=setup_data["pessoa_id"],
            usuario_id=setup_data["usuario_id"],
            data_emprestimo=datetime.now(tz),
            data_devolucao=None
        )
        
        repository.criar(emprestimo)
        db_session.commit()
        
        # Act
        resultado = repository.buscar_ativo_por_livro(setup_data["livro_id"])
        
        # Assert
        assert resultado is not None
        assert resultado.livro_id == setup_data["livro_id"]
        assert resultado.data_devolucao is None

    def test_buscar_ativo_por_livro_nao_encontrado(self, db_session: Session, setup_data):
        """Testa busca de empréstimo ativo por livro quando não existe."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        
        # Act
        resultado = repository.buscar_ativo_por_livro(999)
        
        # Assert
        assert resultado is None

    def test_buscar_ativo_por_livro_apenas_devolvidos(self, db_session: Session, setup_data):
        """Testa que busca ativa não retorna empréstimos devolvidos."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        emprestimo = Emprestimo(
            id=None,
            livro_id=setup_data["livro_id"],
            pessoa_id=setup_data["pessoa_id"],
            usuario_id=setup_data["usuario_id"],
            data_emprestimo=datetime.now(tz),
            data_devolucao=datetime.now(tz)  # Já devolvido
        )
        
        repository.criar(emprestimo)
        db_session.commit()
        
        # Act
        resultado = repository.buscar_ativo_por_livro(setup_data["livro_id"])
        
        # Assert
        assert resultado is None

    def test_finalizar_emprestimo_existente(self, db_session: Session, setup_data):
        """Testa finalização de empréstimo existente."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        emprestimo = Emprestimo(
            id=None,
            livro_id=setup_data["livro_id"],
            pessoa_id=setup_data["pessoa_id"],
            usuario_id=setup_data["usuario_id"],
            data_emprestimo=datetime.now(tz),
            data_devolucao=None
        )
        
        emprestimo_criado = repository.criar(emprestimo)
        db_session.commit()
        
        # Act
        resultado = repository.finalizar(emprestimo_criado.id)
        db_session.commit()
        
        # Assert
        assert resultado is not None
        assert resultado.id == emprestimo_criado.id
        assert resultado.data_devolucao is not None
        assert isinstance(resultado.data_devolucao, datetime)

    def test_finalizar_emprestimo_inexistente(self, db_session: Session):
        """Testa finalização de empréstimo que não existe."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        
        # Act
        resultado = repository.finalizar(999)
        
        # Assert
        assert resultado is None

    def test_listar_paginado_status_ativos(self, db_session: Session, setup_data):
        """Testa listagem paginada de empréstimos ativos."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        # Criar empréstimo ativo
        emprestimo_ativo = Emprestimo(
            None, setup_data["livro_id"], setup_data["pessoa_id"], 
            setup_data["usuario_id"], datetime.now(tz), None
        )
        repository.criar(emprestimo_ativo)
        db_session.commit()
        
        # Act
        emprestimos, total = repository.listar_paginado(page=1, size=10, status=EmprestimoStatus.ATIVOS)
        
        # Assert
        assert len(emprestimos) == 1
        assert total == 1
        assert emprestimos[0].data_devolucao is None

    def test_listar_paginado_status_devolvidos(self, db_session: Session, setup_data):
        """Testa listagem paginada de empréstimos devolvidos."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        # Criar empréstimo devolvido
        emprestimo_devolvido = Emprestimo(
            None, setup_data["livro_id"], setup_data["pessoa_id"], 
            setup_data["usuario_id"], datetime.now(tz), datetime.now(tz)
        )
        repository.criar(emprestimo_devolvido)
        db_session.commit()
        
        # Act
        emprestimos, total = repository.listar_paginado(page=1, size=10, status=EmprestimoStatus.DEVOLVIDOS)
        
        # Assert
        assert len(emprestimos) == 1
        assert total == 1
        assert emprestimos[0].data_devolucao is not None

    def test_listar_paginado_status_todos(self, db_session: Session, setup_data):
        """Testa listagem paginada de todos os empréstimos."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        # Criar empréstimo ativo
        emprestimo_ativo = Emprestimo(
            None, setup_data["livro_id"], setup_data["pessoa_id"], 
            setup_data["usuario_id"], datetime.now(tz), None
        )
        repository.criar(emprestimo_ativo)
        
        # Criar outro usuário, livro e pessoa para segundo empréstimo
        usuario_repo = UsuarioRepository(db_session)
        livro_repo = LivroRepository(db_session)
        pessoa_repo = PessoaRepository(db_session)
        
        usuario2 = usuario_repo.criar(Usuario(None, "Admin2", "admin2@email.com", "hash456"))
        livro2 = livro_repo.criar(Livro(None, "Livro 2", "Autor 2", True))
        pessoa2 = pessoa_repo.criar(Pessoa(None, "Pessoa 2", "11888888888", date(1985, 5, 5), "pessoa2@email.com"))
        
        # Criar empréstimo devolvido
        emprestimo_devolvido = Emprestimo(
            None, livro2.id, pessoa2.id, 
            usuario2.id, datetime.now(tz), datetime.now(tz)
        )
        repository.criar(emprestimo_devolvido)
        db_session.commit()
        
        # Act
        emprestimos, total = repository.listar_paginado(page=1, size=10, status=EmprestimoStatus.TODOS)
        
        # Assert
        assert len(emprestimos) == 2
        assert total == 2

    def test_listar_paginado_paginacao(self, db_session: Session, setup_data):
        """Testa paginação na listagem de empréstimos."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        usuario_repo = UsuarioRepository(db_session)
        livro_repo = LivroRepository(db_session)
        pessoa_repo = PessoaRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        # Criar 5 empréstimos ativos
        for i in range(5):
            usuario = usuario_repo.criar(Usuario(None, f"Usuario {i}", f"usuario{i}@email.com", f"hash{i}"))
            livro = livro_repo.criar(Livro(None, f"Livro {i}", f"Autor {i}", True))
            pessoa = pessoa_repo.criar(Pessoa(None, f"Pessoa {i}", f"1188888888{i}", date(1990, 1, i+1), f"pessoa{i}@email.com"))
            
            emprestimo = Emprestimo(None, livro.id, pessoa.id, usuario.id, datetime.now(tz), None)
            repository.criar(emprestimo)
        
        db_session.commit()
        
        # Act - Primeira página
        emprestimos_p1, total_p1 = repository.listar_paginado(page=1, size=3, status=EmprestimoStatus.ATIVOS)
        
        # Act - Segunda página
        emprestimos_p2, total_p2 = repository.listar_paginado(page=2, size=3, status=EmprestimoStatus.ATIVOS)
        
        # Assert
        assert len(emprestimos_p1) == 3
        assert total_p1 == 5
        assert len(emprestimos_p2) == 2
        assert total_p2 == 5

    def test_listar_paginado_sem_dados(self, db_session: Session):
        """Testa listagem paginada quando não há empréstimos."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        
        # Act
        emprestimos, total = repository.listar_paginado(page=1, size=10, status=EmprestimoStatus.TODOS)
        
        # Assert
        assert len(emprestimos) == 0
        assert total == 0

    def test_timezone_configuracao(self, db_session: Session, setup_data):
        """Testa configuração de timezone."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        emprestimo = Emprestimo(
            None, setup_data["livro_id"], setup_data["pessoa_id"], 
            setup_data["usuario_id"], datetime.now(tz), None
        )
        
        emprestimo_criado = repository.criar(emprestimo)
        db_session.commit()
        
        # Act - Finalizar empréstimo (deve usar timezone configurado)
        resultado = repository.finalizar(emprestimo_criado.id)
        db_session.commit()
        
        # Assert
        assert resultado is not None
        assert resultado.data_devolucao is not None
        # Verificar que a data de devolução tem timezone info
        assert resultado.data_devolucao.tzinfo is not None

    def test_operacoes_consecutivas_mesma_sessao(self, db_session: Session, setup_data):
        """Testa múltiplas operações na mesma sessão de banco."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        # Act - Criar empréstimo
        emprestimo = Emprestimo(
            None, setup_data["livro_id"], setup_data["pessoa_id"], 
            setup_data["usuario_id"], datetime.now(tz), None
        )
        emprestimo_criado = repository.criar(emprestimo)
        db_session.flush()
        
        # Act - Buscar empréstimo ativo
        emprestimo_ativo = repository.buscar_ativo_por_livro(setup_data["livro_id"])
        
        # Act - Listar empréstimos ativos
        emprestimos_ativos, total_ativos = repository.listar_paginado(page=1, size=10, status=EmprestimoStatus.ATIVOS)
        
        # Act - Finalizar empréstimo
        emprestimo_finalizado = repository.finalizar(emprestimo_criado.id)
        db_session.flush()
        
        # Act - Verificar que não há mais empréstimos ativos para o livro
        emprestimo_ativo_apos = repository.buscar_ativo_por_livro(setup_data["livro_id"])
        
        # Act - Listar empréstimos devolvidos
        emprestimos_devolvidos, total_devolvidos = repository.listar_paginado(page=1, size=10, status=EmprestimoStatus.DEVOLVIDOS)
        
        # Assert
        assert emprestimo_ativo is not None
        assert len(emprestimos_ativos) == 1
        assert total_ativos == 1
        assert emprestimo_finalizado is not None
        assert emprestimo_finalizado.data_devolucao is not None
        assert emprestimo_ativo_apos is None
        assert len(emprestimos_devolvidos) == 1
        assert total_devolvidos == 1

    def test_multiplos_emprestimos_mesmo_livro(self, db_session: Session, setup_data):
        """Testa comportamento com múltiplos empréstimos do mesmo livro."""
        # Arrange
        repository = EmprestimoRepository(db_session)
        pessoa_repo = PessoaRepository(db_session)
        tz = ZoneInfo("America/Sao_Paulo")
        
        # Criar segunda pessoa
        pessoa2 = pessoa_repo.criar(Pessoa(None, "Pessoa 2", "11777777777", date(1985, 5, 5), "pessoa2@email.com"))
        db_session.commit()
        
        # Criar primeiro empréstimo e devolver
        emprestimo1 = Emprestimo(
            None, setup_data["livro_id"], setup_data["pessoa_id"], 
            setup_data["usuario_id"], datetime.now(tz), None
        )
        emp1_criado = repository.criar(emprestimo1)
        repository.finalizar(emp1_criado.id)
        
        # Criar segundo empréstimo (ativo)
        emprestimo2 = Emprestimo(
            None, setup_data["livro_id"], pessoa2.id, 
            setup_data["usuario_id"], datetime.now(tz), None
        )
        repository.criar(emprestimo2)
        db_session.commit()
        
        # Act
        emprestimo_ativo = repository.buscar_ativo_por_livro(setup_data["livro_id"])
        emprestimos_todos, total_todos = repository.listar_paginado(page=1, size=10, status=EmprestimoStatus.TODOS)
        
        # Assert
        assert emprestimo_ativo is not None
        assert emprestimo_ativo.pessoa_id == pessoa2.id  # Deve ser o segundo empréstimo
        assert len(emprestimos_todos) == 2
        assert total_todos == 2