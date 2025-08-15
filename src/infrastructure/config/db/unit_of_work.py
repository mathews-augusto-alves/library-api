from src.domain.ports.unit_of_work import UnitOfWorkPort

class SqlAlchemyUnitOfWork(UnitOfWorkPort):
    def __init__(self, session):
        self.session = session

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
