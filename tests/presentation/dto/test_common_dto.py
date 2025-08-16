"""
Testes para os DTOs comuns.
"""
import pytest
from datetime import datetime
from src.presentation.dto.common import PaginationMeta, PaginatedResponse, ApiResponse


class TestPaginationMeta:
    """Testes para PaginationMeta."""
    
    def test_criar_paginacao_valida(self):
        """Teste de criação de paginação com dados válidos."""
        # Arrange & Act
        pagination = PaginationMeta(
            page=1,
            size=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_previous=False
        )
        
        # Assert
        assert pagination.page == 1
        assert pagination.size == 10
        assert pagination.total == 100
        assert pagination.total_pages == 10
        assert pagination.has_next is True
        assert pagination.has_previous is False
    
    def test_criar_paginacao_primeira_pagina(self):
        """Teste de criação de paginação para primeira página."""
        # Arrange & Act
        pagination = PaginationMeta(
            page=1,
            size=20,
            total=50,
            total_pages=3,
            has_next=True,
            has_previous=False
        )
        
        # Assert
        assert pagination.page == 1
        assert pagination.size == 20
        assert pagination.total == 50
        assert pagination.total_pages == 3
        assert pagination.has_next is True
        assert pagination.has_previous is False
    
    def test_criar_paginacao_pagina_meio(self):
        """Teste de criação de paginação para página do meio."""
        # Arrange & Act
        pagination = PaginationMeta(
            page=5,
            size=15,
            total=150,
            total_pages=10,
            has_next=True,
            has_previous=True
        )
        
        # Assert
        assert pagination.page == 5
        assert pagination.size == 15
        assert pagination.total == 150
        assert pagination.total_pages == 10
        assert pagination.has_next is True
        assert pagination.has_previous is True
    
    def test_criar_paginacao_ultima_pagina(self):
        """Teste de criação de paginação para última página."""
        # Arrange & Act
        pagination = PaginationMeta(
            page=10,
            size=25,
            total=250,
            total_pages=10,
            has_next=False,
            has_previous=True
        )
        
        # Assert
        assert pagination.page == 10
        assert pagination.size == 25
        assert pagination.total == 250
        assert pagination.total_pages == 10
        assert pagination.has_next is False
        assert pagination.has_previous is True
    
    def test_criar_paginacao_sem_dados(self):
        """Teste de criação de paginação sem dados."""
        # Arrange & Act
        pagination = PaginationMeta(
            page=1,
            size=10,
            total=0,
            total_pages=0,
            has_next=False,
            has_previous=False
        )
        
        # Assert
        assert pagination.page == 1
        assert pagination.size == 10
        assert pagination.total == 0
        assert pagination.total_pages == 0
        assert pagination.has_next is False
        assert pagination.has_previous is False
    
    def test_metodo_create_paginacao(self):
        """Teste do método create para criar paginação."""
        # Arrange & Act
        pagination = PaginationMeta.create(page=2, size=10, total=25)
        
        # Assert
        assert pagination.page == 2
        assert pagination.size == 10
        assert pagination.total == 25
        assert pagination.total_pages == 3  # (25 + 10 - 1) // 10 = 34 // 10 = 3
        assert pagination.has_next is True  # 2 < 3
        assert pagination.has_previous is True  # 2 > 1
    
    def test_metodo_create_primeira_pagina(self):
        """Teste do método create para primeira página."""
        # Arrange & Act
        pagination = PaginationMeta.create(page=1, size=10, total=25)
        
        # Assert
        assert pagination.page == 1
        assert pagination.size == 10
        assert pagination.total == 25
        assert pagination.total_pages == 3
        assert pagination.has_next is True  # 1 < 3
        assert pagination.has_previous is False  # 1 > 1 = False
    
    def test_metodo_create_ultima_pagina(self):
        """Teste do método create para última página."""
        # Arrange & Act
        pagination = PaginationMeta.create(page=3, size=10, total=25)
        
        # Assert
        assert pagination.page == 3
        assert pagination.size == 10
        assert pagination.total == 25
        assert pagination.total_pages == 3
        assert pagination.has_next is False  # 3 < 3 = False
        assert pagination.has_previous is True  # 3 > 1
    
    def test_metodo_create_pagina_exata(self):
        """Teste do método create quando total é múltiplo exato do size."""
        # Arrange & Act
        pagination = PaginationMeta.create(page=2, size=10, total=20)
        
        # Assert
        assert pagination.page == 2
        assert pagination.size == 10
        assert pagination.total == 20
        assert pagination.total_pages == 2  # (20 + 10 - 1) // 10 = 29 // 10 = 2
        assert pagination.has_next is False  # 2 < 2 = False
        assert pagination.has_previous is True  # 2 > 1
    
    def test_serializacao_paginacao(self):
        """Teste de serialização da paginação."""
        # Arrange
        pagination = PaginationMeta(
            page=1,
            size=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_previous=False
        )
        
        # Act
        dados = pagination.model_dump()
        
        # Assert
        assert dados["page"] == 1
        assert dados["size"] == 10
        assert dados["total"] == 100
        assert dados["total_pages"] == 10
        assert dados["has_next"] is True
        assert dados["has_previous"] is False
    
    def test_serializacao_json(self):
        """Teste de serialização para JSON."""
        # Arrange
        pagination = PaginationMeta(
            page=1,
            size=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_previous=False
        )
        
        # Act
        dados_json = pagination.model_dump(mode="json")
        
        # Assert
        assert dados_json["page"] == 1
        assert dados_json["size"] == 10
        assert dados_json["total"] == 100
        assert dados_json["total_pages"] == 10
        assert dados_json["has_next"] is True
        assert dados_json["has_previous"] is False


class TestPaginatedResponse:
    """Testes para PaginatedResponse."""
    
    def test_criar_resposta_paginada_valida(self):
        """Teste de criação de resposta paginada com dados válidos."""
        # Arrange
        meta = PaginationMeta(
            page=1,
            size=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_previous=False
        )
        
        # Act
        response = PaginatedResponse(
            data=["item1", "item2", "item3"],
            meta=meta
        )
        
        # Assert
        assert response.data == ["item1", "item2", "item3"]
        assert response.meta == meta
        assert response.meta.page == 1
        assert response.meta.size == 10
        assert response.meta.total == 100
    
    def test_criar_resposta_paginada_vazia(self):
        """Teste de criação de resposta paginada vazia."""
        # Arrange
        meta = PaginationMeta(
            page=1,
            size=10,
            total=0,
            total_pages=0,
            has_next=False,
            has_previous=False
        )
        
        # Act
        response = PaginatedResponse(
            data=[],
            meta=meta
        )
        
        # Assert
        assert response.data == []
        assert response.meta == meta
        assert response.meta.total == 0
        assert response.meta.total_pages == 0
    
    def test_criar_resposta_paginada_com_dados_complexos(self):
        """Teste de criação de resposta paginada com dados complexos."""
        # Arrange
        meta = PaginationMeta(
            page=2,
            size=5,
            total=25,
            total_pages=5,
            has_next=True,
            has_previous=True
        )
        
        dados_complexos = [
            {"id": 1, "nome": "Item 1"},
            {"id": 2, "nome": "Item 2"},
            {"id": 3, "nome": "Item 3"},
            {"id": 4, "nome": "Item 4"},
            {"id": 5, "nome": "Item 5"}
        ]
        
        # Act
        response = PaginatedResponse(
            data=dados_complexos,
            meta=meta
        )
        
        # Assert
        assert len(response.data) == 5
        assert response.data[0]["id"] == 1
        assert response.data[0]["nome"] == "Item 1"
        assert response.meta.page == 2
        assert response.meta.size == 5
        assert response.meta.total == 25
        assert response.meta.total_pages == 5
    
    def test_validacao_resposta_dados_none(self):
        """Teste de validação com dados None."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            PaginatedResponse(
                data=None,
                meta=PaginationMeta(
                    page=1,
                    size=10,
                    total=100,
                    total_pages=10,
                    has_next=True,
                    has_previous=False
                )
            )
    
    def test_validacao_resposta_meta_none(self):
        """Teste de validação com meta None."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            PaginatedResponse(
                data=["item1", "item2"],
                meta=None
            )
    
    def test_serializacao_resposta_paginada(self):
        """Teste de serialização da resposta paginada."""
        # Arrange
        meta = PaginationMeta(
            page=1,
            size=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_previous=False
        )
        
        response = PaginatedResponse(
            data=["item1", "item2", "item3"],
            meta=meta
        )
        
        # Act
        dados = response.model_dump()
        
        # Assert
        assert dados["data"] == ["item1", "item2", "item3"]
        assert dados["meta"]["page"] == 1
        assert dados["meta"]["size"] == 10
        assert dados["meta"]["total"] == 100
        assert dados["meta"]["total_pages"] == 10
        assert dados["meta"]["has_next"] is True
        assert dados["meta"]["has_previous"] is False
    
    def test_serializacao_json(self):
        """Teste de serialização para JSON."""
        # Arrange
        meta = PaginationMeta(
            page=1,
            size=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_previous=False
        )
        
        response = PaginatedResponse(
            data=["item1", "item2", "item3"],
            meta=meta
        )
        
        # Act
        dados_json = response.model_dump(mode="json")
        
        # Assert
        assert dados_json["data"] == ["item1", "item2", "item3"]
        assert dados_json["meta"]["page"] == 1
        assert dados_json["meta"]["size"] == 10
        assert dados_json["meta"]["total"] == 100
        assert dados_json["meta"]["total_pages"] == 10
        assert dados_json["meta"]["has_next"] is True
        assert dados_json["meta"]["has_previous"] is False


class TestApiResponse:
    """Testes para ApiResponse."""
    
    def test_criar_resposta_api_sucesso(self):
        """Teste de criação de resposta de API com sucesso."""
        # Arrange & Act
        response = ApiResponse(
            success=True,
            data={"id": 1, "nome": "João Silva"},
            message="Usuário criado com sucesso"
        )
        
        # Assert
        assert response.success is True
        assert response.data["id"] == 1
        assert response.data["nome"] == "João Silva"
        assert response.message == "Usuário criado com sucesso"
        assert response.error is None
        assert response.details is None
    
    def test_criar_resposta_api_erro(self):
        """Teste de criação de resposta de API com erro."""
        # Arrange & Act
        response = ApiResponse(
            success=False,
            data=None,
            message="Erro ao criar usuário",
            error="Email já existe"
        )
        
        # Assert
        assert response.success is False
        assert response.data is None
        assert response.message == "Erro ao criar usuário"
        assert response.error == "Email já existe"
        assert response.details is None
    
    def test_criar_resposta_api_sem_mensagem(self):
        """Teste de criação de resposta de API sem mensagem."""
        # Arrange & Act
        response = ApiResponse(
            success=True,
            data={"id": 1, "nome": "João Silva"}
        )
        
        # Assert
        assert response.success is True
        assert response.data["id"] == 1
        assert response.data["nome"] == "João Silva"
        assert response.message is None
        assert response.error is None
        assert response.details is None
    
    def test_criar_resposta_api_sem_erro(self):
        """Teste de criação de resposta de API sem erro."""
        # Arrange & Act
        response = ApiResponse(
            success=True,
            data={"id": 1, "nome": "João Silva"},
            message="Usuário criado com sucesso"
        )
        
        # Assert
        assert response.success is True
        assert response.data["id"] == 1
        assert response.data["nome"] == "João Silva"
        assert response.message == "Usuário criado com sucesso"
        assert response.error is None
        assert response.details is None
    
    def test_criar_resposta_api_com_dados_complexos(self):
        """Teste de criação de resposta de API com dados complexos."""
        # Arrange & Act
        dados_complexos = {
            "usuarios": [
                {"id": 1, "nome": "João Silva"},
                {"id": 2, "nome": "Maria Santos"}
            ],
            "total": 2,
            "pagina": 1
        }
        
        response = ApiResponse(
            success=True,
            data=dados_complexos,
            message="Usuários listados com sucesso"
        )
        
        # Assert
        assert response.success is True
        assert len(response.data["usuarios"]) == 2
        assert response.data["usuarios"][0]["nome"] == "João Silva"
        assert response.data["usuarios"][1]["nome"] == "Maria Santos"
        assert response.data["total"] == 2
        assert response.data["pagina"] == 1
        assert response.message == "Usuários listados com sucesso"
    
    def test_criar_resposta_api_com_details(self):
        """Teste de criação de resposta de API com detalhes."""
        # Arrange & Act
        response = ApiResponse(
            success=False,
            data=None,
            message="Erro de validação",
            error="Campos obrigatórios não preenchidos",
            details={"campos_faltando": ["nome", "email"]}
        )
        
        # Assert
        assert response.success is False
        assert response.data is None
        assert response.message == "Erro de validação"
        assert response.error == "Campos obrigatórios não preenchidos"
        assert response.details["campos_faltando"] == ["nome", "email"]
    
    def test_resposta_api_padrao(self):
        """Teste de criação de resposta de API com valores padrão."""
        # Arrange & Act
        response = ApiResponse()
        
        # Assert
        assert response.success is True
        assert response.data is None
        assert response.message is None
        assert response.error is None
        assert response.details is None
    
    def test_serializacao_resposta_api(self):
        """Teste de serialização da resposta de API."""
        # Arrange
        response = ApiResponse(
            success=True,
            data={"id": 1, "nome": "João Silva"},
            message="Usuário criado com sucesso"
        )
        
        # Act
        dados = response.model_dump()
        
        # Assert
        assert dados["success"] is True
        assert dados["data"]["id"] == 1
        assert dados["data"]["nome"] == "João Silva"
        assert dados["message"] == "Usuário criado com sucesso"
        assert dados["error"] is None
        assert dados["details"] is None
    
    def test_serializacao_json(self):
        """Teste de serialização para JSON."""
        # Arrange
        response = ApiResponse(
            success=True,
            data={"id": 1, "nome": "João Silva"},
            message="Usuário criado com sucesso"
        )
        
        # Act
        dados_json = response.model_dump(mode="json")
        
        # Assert
        assert dados_json["success"] is True
        assert dados_json["data"]["id"] == 1
        assert dados_json["data"]["nome"] == "João Silva"
        assert dados_json["message"] == "Usuário criado com sucesso"
        assert dados_json["error"] is None
        assert dados_json["details"] is None
    
    def test_fluxo_completo_sucesso_erro(self):
        """Teste de fluxo completo: sucesso e erro."""
        # Arrange & Act - Resposta de sucesso
        success_response = ApiResponse(
            success=True,
            data={"id": 1, "nome": "João Silva"},
            message="Usuário criado com sucesso"
        )
        
        # Assert - Resposta de sucesso
        assert success_response.success is True
        assert success_response.data["id"] == 1
        assert success_response.message == "Usuário criado com sucesso"
        
        # Arrange & Act - Resposta de erro
        error_response = ApiResponse(
            success=False,
            data=None,
            message="Erro ao criar usuário",
            error="Email já existe"
        )
        
        # Assert - Resposta de erro
        assert error_response.success is False
        assert error_response.data is None
        assert error_response.message == "Erro ao criar usuário"
        assert error_response.error == "Email já existe" 