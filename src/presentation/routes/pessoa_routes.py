from fastapi import APIRouter, Depends, Query

from src.presentation.dto.pessoa_dto import PessoaCreateRequest, PessoaResponse
from src.infrastructure.config.security.auth import get_current_user
from src.infrastructure.config.factories import get_pessoa_controller, get_cache
from src.presentation.controllers.pessoa_controllers import PessoaControllers
from src.presentation.dto.common import ApiResponse, PaginatedResponse
from redis import Redis

router = APIRouter(prefix="/pessoas", tags=["Pessoas"], dependencies=[Depends(get_current_user)])

@router.post("/", response_model=ApiResponse[PessoaResponse])
def criar_pessoa(
    request: PessoaCreateRequest,
    controller: PessoaControllers = Depends(get_pessoa_controller),
    cache: Redis = Depends(get_cache)
):
    pessoa = controller.criar(request, cache)
    return ApiResponse(data=PessoaResponse.model_validate(pessoa))

@router.get("/", response_model=ApiResponse[PaginatedResponse[PessoaResponse]])
def listar_pessoas(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=20, description="Tamanho da página (máx: 20)"),
    controller: PessoaControllers = Depends(get_pessoa_controller), 
    cache: Redis = Depends(get_cache)
):
    result = controller.listar_paginado(page, size, cache)
    return ApiResponse(data=result)

@router.get("/{pessoa_id}", response_model=ApiResponse[PessoaResponse])
def buscar_por_id(
    pessoa_id: int,
    controller: PessoaControllers = Depends(get_pessoa_controller),
    cache: Redis = Depends(get_cache)
):
    result = controller.buscar_por_id(pessoa_id, cache)
    return ApiResponse(data=result)

@router.get("/email/{email}", response_model=ApiResponse[PessoaResponse])
def buscar_pessoa_por_email(
    email: str,
    controller: PessoaControllers = Depends(get_pessoa_controller),
    cache: Redis = Depends(get_cache)
):
    result = controller.buscar_por_email(email, cache)
    return ApiResponse(data=result)

@router.put("/{pessoa_id}", response_model=ApiResponse[PessoaResponse])
def atualizar_pessoa(
    pessoa_id: int,
    request: PessoaCreateRequest,
    controller: PessoaControllers = Depends(get_pessoa_controller),
    cache: Redis = Depends(get_cache)
):
    result = controller.atualizar(pessoa_id, request, cache)
    return ApiResponse(data=result)

@router.delete("/{pessoa_id}", response_model=ApiResponse[None])
def remover_pessoa(
    pessoa_id: int,
    controller: PessoaControllers = Depends(get_pessoa_controller),
    cache: Redis = Depends(get_cache)
):
    controller.remover_pessoa(pessoa_id, cache)
    return ApiResponse(message="Pessoa removida com sucesso") 