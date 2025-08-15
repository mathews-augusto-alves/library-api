from sqlalchemy.orm import Session
from src.infrastructure.config.app.app_factory_contract import ApplicationFactory
from src.infrastructure.config.db.unit_of_work import SqlAlchemyUnitOfWork
from zoneinfo import ZoneInfo
import os

class SqlAlchemyFactory(ApplicationFactory):
    def __init__(self, db: Session):
        self.db = db
        self.uow = SqlAlchemyUnitOfWork(db)
        self.tz = ZoneInfo(os.getenv("APP_TZ", "America/Sao_Paulo"))

    def _build_module(self, repository_cls, service_cls, usecase_cls, controller_cls, extra_service_args=None):
        repo = repository_cls(self.db)
        service = service_cls(repo, self.uow, *(extra_service_args or []))
        usecase = usecase_cls(service)
        return controller_cls(usecase)

    def create_usuario_controller(self):
        from src.infrastructure.persistence.repository.usuario_repository import UsuarioRepository
        from src.application.service.usuario.usuario_service import UsuarioService
        from src.application.usecase.usuario_usecases import UsuarioUseCase
        from src.presentation.controllers.usuario_controllers import UsuarioControllers

        return self._build_module(UsuarioRepository, UsuarioService, UsuarioUseCase, UsuarioControllers)

    def create_pessoa_controller(self):
        from src.infrastructure.persistence.repository.pessoa_repository import PessoaRepository
        from src.application.service.pessoa.pessoa_service import PessoaService
        from src.application.usecase.pessoa_usecases import PessoaUseCase
        from src.presentation.controllers.pessoa_controllers import PessoaControllers

        return self._build_module(PessoaRepository, PessoaService, PessoaUseCase, PessoaControllers)

    def create_livro_controller(self):
        from src.infrastructure.persistence.repository.livro_repository import LivroRepository
        from src.infrastructure.persistence.repository.emprestimo_repository import EmprestimoRepository
        from src.infrastructure.persistence.repository.pessoa_repository import PessoaRepository
        from src.application.service.livro.livro_service import LivroService
        from src.application.service.livro.emprestimo_service import EmprestimoService
        from src.application.service.pessoa.pessoa_service import PessoaService
        from src.application.usecase.livro_usecases import LivroUseCase
        from src.presentation.controllers.livro_controllers import LivroControllers

        livro_repo = LivroRepository(self.db)
        emp_repo = EmprestimoRepository(self.db)
        pessoa_repo = PessoaRepository(self.db)

        livro_service = LivroService(livro_repo, self.uow)
        emp_service = EmprestimoService(emp_repo, livro_repo, self.uow, self.tz)
        pessoa_service = PessoaService(pessoa_repo, self.uow)

        usecase = LivroUseCase(livro_service, emp_service, pessoa_service)
        return LivroControllers(usecase)
