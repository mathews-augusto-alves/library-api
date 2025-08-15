from fastapi import Depends
from sqlalchemy.orm import Session
from src.infrastructure.config.db.database import SessionLocal

def get_db():
    """Dependency para injetar a sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 