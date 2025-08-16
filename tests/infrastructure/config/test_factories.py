"""
Testes para as factories (SqlAlchemyFactory) criando controllers.
"""
from src.infrastructure.config.sqlalchemy_factory import SqlAlchemyFactory
from src.presentation.controllers.usuario_controllers import UsuarioControllers
from src.presentation.controllers.pessoa_controllers import PessoaControllers
from src.presentation.controllers.livro_controllers import LivroControllers


class TestFactories:
    def test_create_usuario_controller(self, db_session):
        factory = SqlAlchemyFactory(db_session)
        controller = factory.create_usuario_controller()
        assert isinstance(controller, UsuarioControllers)
    
    def test_create_pessoa_controller(self, db_session):
        factory = SqlAlchemyFactory(db_session)
        controller = factory.create_pessoa_controller()
        assert isinstance(controller, PessoaControllers)
    
    def test_create_livro_controller(self, db_session):
        factory = SqlAlchemyFactory(db_session)
        controller = factory.create_livro_controller()
        assert isinstance(controller, LivroControllers) 