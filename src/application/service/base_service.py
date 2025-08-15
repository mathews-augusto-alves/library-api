from typing import Callable, TypeVar, Generic
from src.domain.ports.unit_of_work import UnitOfWorkPort

T = TypeVar("T")

class BaseService(Generic[T]):
    def __init__(self, uow: UnitOfWorkPort):
        self.uow = uow

    def _executar_transacao(self, acao: Callable[[], T]) -> T:
        try:
            resultado = acao()
            self.uow.commit()
            return resultado
        except Exception:
            self.uow.rollback()
            raise
