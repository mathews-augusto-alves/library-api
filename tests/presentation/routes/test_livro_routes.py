"""
Testes de API para as rotas de livro e empréstimo.
"""
import pytest
from fastapi.testclient import TestClient


class TestLivroRoutes:
    """Testes para as rotas de livro."""

    def test_cadastrar_livro_sucesso(self, client: TestClient, auth_headers):
        payload = {"titulo": "O Senhor dos Anéis", "autor": "J.R.R. Tolkien"}
        response = client.post("/api/v1/livros/", json=payload, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["titulo"] == "O Senhor dos Anéis"
        assert data["data"]["autor"] == "J.R.R. Tolkien"
        assert data["data"]["disponivel"] is True

    def test_cadastrar_livro_dados_invalidos(self, client: TestClient, auth_headers):
        payload = {"titulo": "", "autor": "A"}
        response = client.post("/api/v1/livros/", json=payload, headers=auth_headers)
        assert response.status_code == 422

    def test_cadastrar_livro_campos_obrigatorios(self, client: TestClient, auth_headers):
        response = client.post("/api/v1/livros/", json={"autor": "J.R.R. Tolkien"}, headers=auth_headers)
        assert response.status_code == 422
        response = client.post("/api/v1/livros/", json={"titulo": "O Senhor dos Anéis"}, headers=auth_headers)
        assert response.status_code == 422

    def test_listar_livros_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/livros/")
        assert response.status_code == 401

    def test_validacao_paginacao_livros(self, client: TestClient, auth_headers):
        response = client.get("/api/v1/livros/", params={"page": 0, "size": 10}, headers=auth_headers)
        assert response.status_code == 422
        response = client.get("/api/v1/livros/", params={"page": 1, "size": 25}, headers=auth_headers)
        assert response.status_code == 422


class TestEmprestimoRoutes:
    """Testes para as rotas de empréstimo."""

    def test_emprestar_livro_sucesso(self, client: TestClient, auth_headers):
        # Criar livro e pessoa previamente
        livro = client.post("/api/v1/livros/", json={"titulo": "Livro X", "autor": "Autor Y"}, headers=auth_headers)
        assert livro.status_code == 200
        pessoa = client.post("/api/v1/pessoas/", json={"nome": "Pessoa A", "telefone": "11999999999", "data_nascimento": "1990-01-01", "email": "pessoa@a.com"}, headers=auth_headers)
        assert pessoa.status_code == 200
        # Empréstimo
        response = client.post("/api/v1/livros/emprestimos", json={"livro_id": 1, "pessoa_id": 1}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["livro_id"] == 1
        assert data["data"]["pessoa_id"] == 1

    def test_emprestar_livro_dados_invalidos(self, client: TestClient, auth_headers):
        response = client.post("/api/v1/livros/emprestimos", json={"livro_id": -1, "pessoa_id": 0}, headers=auth_headers)
        assert response.status_code == 422

    def test_emprestar_livro_campos_obrigatorios(self, client: TestClient, auth_headers):
        response = client.post("/api/v1/livros/emprestimos", json={"pessoa_id": 1}, headers=auth_headers)
        assert response.status_code == 422
        response = client.post("/api/v1/livros/emprestimos", json={"livro_id": 1}, headers=auth_headers)
        assert response.status_code == 422

    def test_devolver_livro_sem_autenticacao(self, client: TestClient):
        response = client.put("/api/v1/livros/1/devolver")
        assert response.status_code == 401

    def test_listar_emprestimos_sem_autenticacao(self, client: TestClient):
        response = client.get("/api/v1/emprestimos/")
        assert response.status_code == 401

    def test_validacao_paginacao_emprestimos(self, client: TestClient, auth_headers):
        response = client.get("/api/v1/emprestimos/", params={"page": 0, "size": 10}, headers=auth_headers)
        assert response.status_code == 422
        response = client.get("/api/v1/emprestimos/", params={"page": 1, "size": 25}, headers=auth_headers)
        assert response.status_code == 422

    def test_validacao_status_emprestimo(self, client: TestClient, auth_headers):
        response = client.get("/api/v1/emprestimos/", params={"page": 1, "size": 10, "status": "INVALIDO"}, headers=auth_headers)
        assert response.status_code == 422

    def test_emprestar_livro_inexistente(self, client: TestClient, auth_headers):
        # Criar pessoa válida
        pessoa = client.post("/api/v1/pessoas/", json={"nome": "Pessoa A", "telefone": "11999999999", "data_nascimento": "1990-01-01", "email": "pessoa@a.com"}, headers=auth_headers)
        assert pessoa.status_code == 200
        # Tentar emprestar livro inexistente
        response = client.post("/api/v1/livros/emprestimos", json={"livro_id": 999999, "pessoa_id": 1}, headers=auth_headers)
        # LivroNaoEncontradoException -> 422 via DomainException handler
        assert response.status_code == 422

    def test_emprestar_livro_indisponivel(self, client: TestClient, auth_headers):
        # Criar livro e pessoa
        livro = client.post("/api/v1/livros/", json={"titulo": "Livro X", "autor": "Autor Y"}, headers=auth_headers)
        assert livro.status_code == 200
        pessoa = client.post("/api/v1/pessoas/", json={"nome": "Pessoa A", "telefone": "11999999999", "data_nascimento": "1990-01-01", "email": "pessoa@a.com"}, headers=auth_headers)
        assert pessoa.status_code == 200
        # Primeiro empréstimo
        r1 = client.post("/api/v1/livros/emprestimos", json={"livro_id": 1, "pessoa_id": 1}, headers=auth_headers)
        assert r1.status_code == 200
        # Segundo empréstimo do mesmo livro -> LivroIndisponivelException -> 422
        r2 = client.post("/api/v1/livros/emprestimos", json={"livro_id": 1, "pessoa_id": 1}, headers=auth_headers)
        assert r2.status_code == 422 