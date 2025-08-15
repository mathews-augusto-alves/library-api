from sqlalchemy.orm import Session
from datetime import datetime
from src.domain.model.emprestimo import Emprestimo
from src.domain.ports.emprestimo_repository import EmprestimoRepositoryPort
from src.infrastructure.persistence.entities.emprestimo_entity import EmprestimoModel
from src.domain.enums.emprestimo_status import EmprestimoStatus
from typing import Tuple
from zoneinfo import ZoneInfo
import os

class EmprestimoRepository(EmprestimoRepositoryPort):
    def __init__(self, db: Session):
        self.db = db
        self._tz = ZoneInfo(os.getenv("APP_TZ", "America/Sao_Paulo"))

    def criar(self, emprestimo: Emprestimo) -> Emprestimo:
        db_emp = EmprestimoModel(**emprestimo.__dict__)
        self.db.add(db_emp)
        self.db.flush()
        return Emprestimo(**emprestimo.__dict__ | {"id": db_emp.id})

    def listar_paginado(self, page: int, size: int, status: EmprestimoStatus = EmprestimoStatus.ATIVOS) -> Tuple[list[Emprestimo], int]:
        offset = (page - 1) * size
        
        query = self.db.query(EmprestimoModel)
        
        if status == EmprestimoStatus.ATIVOS:
            query = query.filter(
                EmprestimoModel.data_emprestimo.isnot(None),
                EmprestimoModel.data_devolucao.is_(None)
            )
        elif status == EmprestimoStatus.DEVOLVIDOS:
            query = query.filter(
                EmprestimoModel.data_emprestimo.isnot(None),
                EmprestimoModel.data_devolucao.isnot(None)
            )
        elif status == EmprestimoStatus.TODOS:
            query = query.filter(EmprestimoModel.data_emprestimo.isnot(None))
        
        total = query.count()
        
        emprestimos = query.offset(offset).limit(size).all()
        
        result = []
        for emp in emprestimos:
            emprestimo = Emprestimo(
                id=emp.id,
                livro_id=emp.livro_id,
                pessoa_id=emp.pessoa_id,
                usuario_id=emp.usuario_id,
                data_emprestimo=emp.data_emprestimo,
                data_devolucao=emp.data_devolucao
            )
            result.append(emprestimo)
        
        return result, total

    def buscar_ativo_por_livro(self, livro_id: int) -> Emprestimo | None:
        r = self.db.query(EmprestimoModel).filter(
            EmprestimoModel.livro_id == livro_id,
            EmprestimoModel.data_devolucao.is_(None)
        ).first()
        return Emprestimo(**r.__dict__) if r else None

    def finalizar(self, emprestimo_id: int) -> Emprestimo | None:
        db_emp = self.db.query(EmprestimoModel).filter(EmprestimoModel.id == emprestimo_id).first()
        if not db_emp:
            return None
        db_emp.data_devolucao = datetime.now(self._tz)
        self.db.flush()
        return Emprestimo(**db_emp.__dict__)
