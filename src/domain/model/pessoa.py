from dataclasses import dataclass
from datetime import date

@dataclass
class Pessoa:
    id: int | None
    nome: str
    telefone: str
    data_nascimento: date
    email: str | None = None
