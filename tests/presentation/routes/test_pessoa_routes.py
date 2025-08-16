"""
Testes de API para as rotas de pessoa.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date


class TestPessoaRoutes:
    """Testes para as rotas de pessoa."""

    def test_criar_pessoa_sucesso(self, client: TestClient, auth_headers):
        payload = {
            "nome": "Maria Santos",
            "telefone": "11999999999",
            "data_nascimento": "1990-01-01",
            "email": "maria@email.com"
        }
        response = client.post("/api/v1/pessoas/", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["nome"] == "Maria Santos"
        assert data["data"]["telefone"] == "11999999999"
        assert data["data"]["data_nascimento"] == "1990-01-01"

    def test_criar_pessoa_sem_email(self, client: TestClient, auth_headers):
        payload = {"nome": "João Silva", "telefone": "11988888888", "data_nascimento": "1985-05-15"}
        response = client.post("/api/v1/pessoas/", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] is None

    def test_criar_pessoa_dados_invalidos(self, client: TestClient, auth_headers):
        payload = {"nome": "", "telefone": "123", "data_nascimento": "1990-01-01", "email": "email_invalido"}
        response = client.post("/api/v1/pessoas/", json=payload, headers=auth_headers)
        # Erros de validação do DTO (Pydantic) retornam 422
        assert response.status_code == 422

    def test_criar_pessoa_campos_obrigatorios(self, client: TestClient, auth_headers):
        r = client.post("/api/v1/pessoas/", json={"telefone": "11999999999", "data_nascimento": "1990-01-01", "email": "x@y.com"}, headers=auth_headers)
        assert r.status_code == 422
        r = client.post("/api/v1/pessoas/", json={"nome": "Maria Santos", "data_nascimento": "1990-01-01", "email": "x@y.com"}, headers=auth_headers)
        assert r.status_code == 422
        r = client.post("/api/v1/pessoas/", json={"nome": "Maria Santos", "telefone": "11999999999", "email": "x@y.com"}, headers=auth_headers)
        assert r.status_code == 422

    def test_listar_pessoas_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/pessoas/")
        assert response.status_code == 401

    def test_buscar_pessoa_por_id_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/pessoas/1")
        assert response.status_code == 401

    def test_buscar_pessoa_por_email_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/pessoas/email/maria@email.com")
        assert response.status_code == 401

    def test_atualizar_pessoa_sem_autenticacao(self, client: TestClient):
        payload = {"nome": "Maria Santos Atualizada", "telefone": "11977777777", "data_nascimento": "1990-01-01", "email": "maria.nova@email.com"}
        response = client.put("/api/v1/pessoas/1", json=payload)
        assert response.status_code == 401

    def test_remover_pessoa_sem_autenticacao(self, client: TestClient):
        response = client.delete("/api/v1/pessoas/1")
        assert response.status_code == 401

    def test_validacao_paginacao(self, client: TestClient, auth_headers):
        response = client.get("/api/v1/pessoas/", params={"page": 0, "size": 10}, headers=auth_headers)
        assert response.status_code == 422
        response = client.get("/api/v1/pessoas/", params={"page": 1, "size": 25}, headers=auth_headers)
        assert response.status_code == 422

    def test_criar_pessoa_email_duplicado(self, client: TestClient, auth_headers):
        payload = {"nome": "Maria Santos", "telefone": "11999999999", "data_nascimento": "1990-01-01", "email": "dup@exemplo.com"}
        r1 = client.post("/api/v1/pessoas/", json=payload, headers=auth_headers)
        assert r1.status_code == 200
        r2 = client.post("/api/v1/pessoas/", json=payload, headers=auth_headers)
        assert r2.status_code == 409

    def test_validacao_data_nascimento(self, client: TestClient, auth_headers):
        r = client.post("/api/v1/pessoas/", json={"nome": "Maria", "telefone": "11999999999", "data_nascimento": "1990/01/01", "email": "m@e.com"}, headers=auth_headers)
        assert r.status_code == 422
        r = client.post("/api/v1/pessoas/", json={"nome": "Maria", "telefone": "11999999999", "data_nascimento": "1990-13-45", "email": "m@e.com"}, headers=auth_headers)
        assert r.status_code == 422 