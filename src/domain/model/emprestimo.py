from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Emprestimo:
    id: Optional[int]
    livro_id: int
    pessoa_id: int
    usuario_id: int
    data_emprestimo: datetime
    data_devolucao: Optional[datetime] = None 