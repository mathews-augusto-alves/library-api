from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator, ConfigDict

class PessoaCreateRequest(BaseModel):
    nome: str
    telefone: str
    data_nascimento: date
    email: Optional[str] = None

    @field_validator('nome')
    def validar_nome(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()

    @field_validator('telefone')
    def validar_telefone(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Telefone deve ter pelo menos 8 caracteres')
        return v

    @field_validator('email')
    def validar_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email deve ser válido')
        return v

class PessoaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    telefone: str
    data_nascimento: date
    email: Optional[str] = None 