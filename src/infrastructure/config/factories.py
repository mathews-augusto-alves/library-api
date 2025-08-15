from fastapi import Depends
from sqlalchemy.orm import Session
from src.infrastructure.config.db.dependencies import get_db
from src.infrastructure.cache.redis_client import get_redis_client
from src.infrastructure.config.app.app_factory_contract import ApplicationFactory
from src.infrastructure.config.sqlalchemy_factory import SqlAlchemyFactory

def get_app_factory(db: Session = Depends(get_db)) -> ApplicationFactory:
    return SqlAlchemyFactory(db)

def get_usuario_controller(factory: ApplicationFactory = Depends(get_app_factory)):
    return factory.create_usuario_controller()

def get_pessoa_controller(factory: ApplicationFactory = Depends(get_app_factory)):
    return factory.create_pessoa_controller()

def get_livro_controller(factory: ApplicationFactory = Depends(get_app_factory)):
    return factory.create_livro_controller()

def get_cache():
    return get_redis_client() 