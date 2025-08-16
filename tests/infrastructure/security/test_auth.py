"""
Testes para o módulo de autenticação (hash, verificação, tokens, fluxos inválidos).
"""
import pytest
from fastapi import HTTPException
from src.infrastructure.config.security import auth


class TestAuth:
    def test_password_hash_and_verify(self):
        senha = "minha_senha_secreta"
        hash_ = auth.get_password_hash(senha)
        assert hash_ and isinstance(hash_, str)
        assert auth.verify_password(senha, hash_) is True
        assert auth.verify_password("outra_senha", hash_) is False

    def test_create_access_token_contains_claims(self):
        token = auth.create_access_token({"sub": "1", "email": "user@email.com"})
        assert isinstance(token, str)
        payload = auth.jwt.decode(token, auth.JWT_SECRET, algorithms=[auth.JWT_ALGORITHM])
        assert payload["sub"] == "1"
        assert payload["email"] == "user@email.com"
        assert payload["exp"] > 0

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_raises(self, mock_db_session):
        with pytest.raises(HTTPException) as exc:
            await auth.get_current_user(token="token_invalido", db=mock_db_session)
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_missing_claims_raises(self, mock_db_session):
        token = auth.create_access_token({})
        with pytest.raises(HTTPException) as exc:
            await auth.get_current_user(token=token, db=mock_db_session)
        assert exc.value.status_code == 401 