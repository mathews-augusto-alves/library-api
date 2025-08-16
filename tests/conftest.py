"""
Fixtures base para todos os testes da aplicação.
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Importar a aplicação
from src.main import app


@pytest.fixture
def db_session():
	"""Sessão de banco de dados para testes usando SQLite em memória."""
	# Importar Base para criar tabelas
	from src.infrastructure.config.db.database import Base
	# Importar explicitamente todas as entidades para registrar no metadata
	from src.infrastructure.persistence.entities.usuario_entity import UsuarioModel  # noqa: F401
	from src.infrastructure.persistence.entities.pessoa_entity import PessoaModel  # noqa: F401
	from src.infrastructure.persistence.entities.livro_entity import LivroModel  # noqa: F401
	from src.infrastructure.persistence.entities.emprestimo_entity import EmprestimoModel  # noqa: F401
	
	# Criar engine SQLite em memória para testes
	engine = create_engine(
		"sqlite:///:memory:",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	
	# Criar todas as tabelas
	Base.metadata.create_all(bind=engine)
	
	# Criar sessão de teste
	TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
	session = TestingSessionLocal()
	
	try:
		yield session
	finally:
		session.close()


@pytest.fixture
def mock_redis():
	"""Mock do Redis para testes."""
	return Mock()


@pytest.fixture
def client(db_session, mock_redis):
	"""Cliente HTTP para testes de API com overrides de dependências."""
	from src.infrastructure.config.db.dependencies import get_db
	from src.infrastructure.config.factories import get_cache

	def override_get_db():
		try:
			yield db_session
		finally:
			pass

	def override_get_cache():
		return mock_redis

	app.dependency_overrides[get_db] = override_get_db
	app.dependency_overrides[get_cache] = override_get_cache
	return TestClient(app)


@pytest.fixture
def mock_db_session():
	"""Mock da sessão de banco de dados."""
	return Mock(spec=Session)


@pytest.fixture
def usuario_valido():
	"""Dados válidos de usuário para testes."""
	return {
		"nome": "João Silva",
		"email": "joao@email.com",
		"senha": "senha123"
	}


@pytest.fixture
def pessoa_valida():
	"""Dados válidos de pessoa para testes."""
	return {
		"nome": "Maria Santos",
		"email": "maria@email.com",
		"telefone": "11999999999"
	}


@pytest.fixture
def livro_valido():
	"""Dados válidos de livro para testes."""
	return {
		"titulo": "O Senhor dos Anéis",
		"autor": "J.R.R. Tolkien",
		"isbn": "9788533613379",
		"quantidade": 5
	}


@pytest.fixture
def emprestimo_valido():
	"""Dados válidos de empréstimo para testes."""
	return {
		"usuario_id": 1,
		"livro_id": 1,
		"data_emprestimo": "2025-08-15T10:00:00",
		"data_devolucao_prevista": "2025-09-15T10:00:00"
	}


@pytest.fixture
def mock_usuario_service():
	"""Mock do UsuarioService para testes."""
	return Mock()


@pytest.fixture
def mock_livro_service():
	"""Mock do LivroService para testes."""
	return Mock()


@pytest.fixture
def mock_pessoa_service():
	"""Mock do PessoaService para testes."""
	return Mock()


@pytest.fixture
def mock_emprestimo_service():
	"""Mock do EmprestimoService para testes."""
	return Mock()


@pytest.fixture
def mock_usuario_repository():
	"""Mock do UsuarioRepository para testes."""
	return Mock()


@pytest.fixture
def mock_livro_repository():
	"""Mock do LivroRepository para testes."""
	return Mock()


@pytest.fixture
def mock_pessoa_repository():
	"""Mock do PessoaRepository para testes."""
	return Mock()


@pytest.fixture
def mock_emprestimo_repository():
	"""Mock do EmprestimoRepository para testes."""
	return Mock()


@pytest.fixture
def mock_usuario_usecase():
	"""Mock do UsuarioUseCase para testes."""
	return Mock()


@pytest.fixture
def mock_livro_usecase():
	"""Mock do LivroUseCase para testes."""
	return Mock()


@pytest.fixture
def mock_pessoa_usecase():
	"""Mock do PessoaUseCase para testes."""
	return Mock()


@pytest.fixture
def mock_emprestimo_usecase():
	"""Mock do EmprestimoUseCase para testes."""
	return Mock()


@pytest.fixture
def mock_factory():
	"""Mock da factory para testes."""
	return Mock()


@pytest.fixture
def mock_metrics():
	"""Mock das métricas para testes."""
	return Mock()


@pytest.fixture
def mock_auth():
	"""Mock da autenticação para testes."""
	return Mock()


@pytest.fixture
def auth_headers(db_session):
	"""Gera header de Authorization para um usuário real criado no DB de teste."""
	from src.infrastructure.persistence.repository.usuario_repository import UsuarioRepository
	from src.domain.model.usuario import Usuario
	from src.infrastructure.config.security.auth import create_access_token, get_password_hash

	repo = UsuarioRepository(db_session)
	usuario = repo.criar(Usuario(None, "Test User", "testuser@example.com", get_password_hash("senha123")))
	db_session.commit()
	token = create_access_token({"sub": str(usuario.id), "email": usuario.email})
	return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_database_url():
	"""URL do banco de dados de teste."""
	return "sqlite:///:memory:"


@pytest.fixture
def test_redis_url():
	"""URL do Redis de teste."""
	return "redis://localhost:6379/1"


@pytest.fixture
def test_app_config():
	"""Configuração de teste da aplicação."""
	return {
		"DATABASE_URL": "sqlite:///:memory:",
		"REDIS_URL": "redis://localhost:6379/1",
		"JWT_SECRET": "test-secret-key",
		"JWT_EXPIRES_SECONDS": 3600,
		"APP_TZ": "UTC",
		"LOG_LEVEL": "DEBUG"
	} 