import os
import time
import jwt
from passlib.hash import pbkdf2_sha256
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.infrastructure.config.db.dependencies import get_db
from src.infrastructure.persistence.repository.usuario_repository import UsuarioRepository
from src.application.service.usuario.usuario_service import UsuarioService
from src.infrastructure.config.db.unit_of_work import SqlAlchemyUnitOfWork

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_SECONDS = int(os.getenv("JWT_EXPIRES_SECONDS", "3600"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str) -> str:
    return pbkdf2_sha256.hash(password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, password_hash)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": int(time.time()) + JWT_EXPIRES_SECONDS})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub")) if payload.get("sub") else None
        email = payload.get("email")
        if user_id is None or email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    uow = SqlAlchemyUnitOfWork(db)
    service = UsuarioService(UsuarioRepository(db), uow)
    usuario = service.buscar_por_id(user_id)
    if not usuario or usuario.email != email:
        raise credentials_exception
    return {"id": usuario.id, "email": usuario.email, "nome": usuario.nome} 