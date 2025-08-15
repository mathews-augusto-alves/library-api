from enum import Enum

class EmprestimoStatus(Enum):
    """Enum para status de empréstimos"""
    ATIVOS = "ativos"           # Apenas empréstimos não devolvidos
    DEVOLVIDOS = "devolvidos"   # Apenas empréstimos devolvidos
    TODOS = "todos"             # Todos os empréstimos 