from fastapi import APIRouter, Depends, Query
from src.infrastructure.config.factories import get_usuario_controller, get_cache
from src.presentation.controllers.usuario_controllers import UsuarioControllers
from src.presentation.dto.usuario_dto import (
    UsuarioCreateRequest, UsuarioUpdateRequest, UsuarioResponse, LoginRequest, TokenResponse
)
from src.presentation.dto.common import ApiResponse, PaginatedResponse
from src.infrastructure.config.security.auth import get_current_user
from redis import Redis

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# Rotas públicas
@router.post("/", response_model=ApiResponse[UsuarioResponse])
def cadastrar_usuario(request: UsuarioCreateRequest, controller: UsuarioControllers = Depends(get_usuario_controller)):
    u = controller.cadastrar(request)
    return ApiResponse(data=UsuarioResponse.model_validate(u))

@auth_router.post("/login", response_model=ApiResponse[TokenResponse])
def login(request: LoginRequest, controller: UsuarioControllers = Depends(get_usuario_controller)):
    token = controller.login(request.email, request.senha)
    return ApiResponse(data=token)

# Rotas protegidas
@router.get("/", response_model=ApiResponse[PaginatedResponse[UsuarioResponse]], dependencies=[Depends(get_current_user)])
def listar_usuarios(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=20, description="Tamanho da página (máx: 20)"),
    controller: UsuarioControllers = Depends(get_usuario_controller), 
    cache: Redis = Depends(get_cache)
):
    result = controller.listar_paginado(page, size, cache)
    return ApiResponse(data=result)

@router.get("/{usuario_id}", response_model=ApiResponse[UsuarioResponse], dependencies=[Depends(get_current_user)])
def buscar_usuario(usuario_id: int, controller: UsuarioControllers = Depends(get_usuario_controller), cache: Redis = Depends(get_cache)):
    result = controller.buscar_por_id(usuario_id, cache)
    return ApiResponse(data=result)

@router.get("/email/{email}", response_model=ApiResponse[UsuarioResponse], dependencies=[Depends(get_current_user)])
def buscar_usuario_por_email(email: str, controller: UsuarioControllers = Depends(get_usuario_controller), cache: Redis = Depends(get_cache)):
    result = controller.buscar_por_email(email, cache)
    return ApiResponse(data=result)

@router.put("/{usuario_id}", response_model=ApiResponse[UsuarioResponse], dependencies=[Depends(get_current_user)])
def atualizar_usuario(usuario_id: int, request: UsuarioUpdateRequest, controller: UsuarioControllers = Depends(get_usuario_controller), cache: Redis = Depends(get_cache)):
    result = controller.atualizar(usuario_id, request, cache)
    return ApiResponse(data=result)

@router.delete("/{usuario_id}", response_model=ApiResponse[None], dependencies=[Depends(get_current_user)])
def remover_usuario(usuario_id: int, controller: UsuarioControllers = Depends(get_usuario_controller), cache: Redis = Depends(get_cache)):
    controller.remover(usuario_id, cache)
    return ApiResponse(message="Usuário removido com sucesso") 