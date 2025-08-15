from dataclasses import dataclass
from typing import Optional

@dataclass
class Livro:
    id: Optional[int]
    titulo: str
    autor: str
    disponivel: bool = True 