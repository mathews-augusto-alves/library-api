from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional

class LivroCreateRequest(BaseModel):
    titulo: str
    autor: str

    @field_validator('titulo')
    def validar_titulo(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Título deve ter pelo menos 2 caracteres')
        return v.strip()

    @field_validator('autor')
    def validar_autor(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Autor deve ter pelo menos 2 caracteres')
        return v.strip()

class LivroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titulo: str
    autor: str
    disponivel: bool

class EmprestimoCreateRequest(BaseModel):
    livro_id: int
    pessoa_id: int

class LivroBrief(BaseModel):
    id: int
    titulo: str
    autor: str

class PessoaBrief(BaseModel):
    id: int
    nome: str
    telefone: str
    email: Optional[str] = None

class EmprestimoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    livro_id: int
    pessoa_id: int
    usuario_id: int
    data_emprestimo: str
    data_devolucao: str | None
    livro: Optional[LivroBrief] = None
    pessoa: Optional[PessoaBrief] = None 