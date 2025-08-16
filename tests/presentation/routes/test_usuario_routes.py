"""
Testes de API para as rotas de usuário.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.main import app


class TestUsuarioRoutes:
    """Testes para as rotas de usuário."""

    def test_cadastrar_usuario_sucesso(self, client: TestClient):
        """Testa cadastro de usuário com sucesso."""
        payload = {
            "nome": "João Silva",
            "email": "joao@email.com",
            "senha": "senha123"
        }
        response = client.post("/api/v1/usuarios/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["nome"] == "João Silva"
        assert data["data"]["email"] == "joao@email.com"
        assert "senha" not in data["data"]

    def test_cadastrar_usuario_dados_invalidos(self, client: TestClient):
        payload = {
            "nome": "",
            "email": "email_invalido",
            "senha": "123"
        }
        response = client.post("/api/v1/usuarios/", json=payload)
        assert response.status_code == 422

    def test_login_sucesso(self, client: TestClient):
        # Primeiro cadastra o usuário
        cadastro = client.post(
            "/api/v1/usuarios/",
            json={"nome": "João Silva", "email": "joao@email.com", "senha": "senha123"}
        )
        assert cadastro.status_code == 200
        # Faz login
        response = client.post("/api/v1/auth/login", json={"email": "joao@email.com", "senha": "senha123"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data and "access_token" in data["data"]

    def test_login_credenciais_invalidas(self, client: TestClient):
        # Usuário não existe ou senha incorreta deve retornar 400 (DadosInvalidosException)
        response = client.post("/api/v1/auth/login", json={"email": "nao@existe.com", "senha": "errada"})
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_listar_usuarios_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/usuarios/")
        assert response.status_code == 401

    def test_buscar_usuario_por_id_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/usuarios/1")
        assert response.status_code == 401

    def test_buscar_usuario_por_email_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/usuarios/email/joao@email.com")
        assert response.status_code == 401

    def test_atualizar_usuario_sem_autenticacao(self, client: TestClient):
        payload = {
            "nome": "João Silva Atualizado",
            "email": "joao.novo@email.com",
            "senha": "nova_senha123"
        }
        response = client.put("/api/v1/usuarios/1", json=payload)
        assert response.status_code == 401

    def test_remover_usuario_sem_autenticacao(self, client: TestClient):
        response = client.delete("/api/v1/usuarios/1")
        assert response.status_code == 401

    def test_cadastrar_usuario_campos_obrigatorios(self, client: TestClient):
        response = client.post("/api/v1/usuarios/", json={"email": "joao@email.com", "senha": "senha123"})
        assert response.status_code == 422
        response = client.post("/api/v1/usuarios/", json={"nome": "João Silva", "senha": "senha123"})
        assert response.status_code == 422
        response = client.post("/api/v1/usuarios/", json={"nome": "João Silva", "email": "joao@email.com"})
        assert response.status_code == 422

    def test_login_campos_obrigatorios(self, client: TestClient):
        response = client.post("/api/v1/auth/login", json={"senha": "senha123"})
        assert response.status_code == 422
        response = client.post("/api/v1/auth/login", json={"email": "joao@email.com"})
        assert response.status_code == 422

    def test_cadastrar_usuario_email_duplicado(self, client: TestClient):
        payload = {"nome": "João Silva", "email": "dup@email.com", "senha": "senha123"}
        r1 = client.post("/api/v1/usuarios/", json=payload)
        assert r1.status_code == 200
        r2 = client.post("/api/v1/usuarios/", json=payload)
        # Email duplicado tratato com 409
        assert r2.status_code == 409
        data = r2.json()
        assert data["success"] is False
        assert data["error"] == "EMAIL_ALREADY_EXISTS" 