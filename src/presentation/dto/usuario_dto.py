from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
import re

class UsuarioCreateRequest(BaseModel):
    nome: str
    email: str
    senha: str

    @field_validator('nome')
    def validar_nome(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()

    @field_validator('email')
    def validar_email(cls, v):
        if not v or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Email inválido')
        return v

    @field_validator('senha')
    def validar_senha(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        return v

class UsuarioUpdateRequest(BaseModel):
    nome: str
    email: str
    senha: str

class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str

class LoginRequest(BaseModel):
    email: str
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str 