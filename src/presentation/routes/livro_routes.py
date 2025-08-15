from fastapi import APIRouter, Depends, Query
from src.infrastructure.config.security.auth import get_current_user
from src.infrastructure.config.factories import get_livro_controller, get_cache
from src.presentation.controllers.livro_controllers import LivroControllers
from src.presentation.dto.livro_dto import LivroCreateRequest, LivroResponse, EmprestimoCreateRequest, EmprestimoResponse
from src.presentation.dto.common import ApiResponse, PaginatedResponse
from src.domain.enums.emprestimo_status import EmprestimoStatus
from redis import Redis

router = APIRouter(tags=["Livros"], dependencies=[Depends(get_current_user)], prefix="/livros")

emprestimo_router = APIRouter(tags=["Emprestimos"], dependencies=[Depends(get_current_user)], prefix="/emprestimos")

@router.post("/", response_model=ApiResponse[LivroResponse])
def cadastrar_livro(request: LivroCreateRequest, controller: LivroControllers = Depends(get_livro_controller), cache: Redis = Depends(get_cache)):
    result = controller.cadastrar(request, cache)
    return ApiResponse(data=LivroResponse.model_validate(result))

@router.get("/", response_model=ApiResponse[PaginatedResponse[LivroResponse]])
def listar_livros(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=20, description="Tamanho da página (máx: 20)"),
    controller: LivroControllers = Depends(get_livro_controller), 
    cache: Redis = Depends(get_cache)
):
    result = controller.listar_paginado(page, size, cache)
    return ApiResponse(data=result)

@router.post("/emprestimos", response_model=ApiResponse[EmprestimoResponse])
def emprestar(request: EmprestimoCreateRequest, current_user = Depends(get_current_user), controller: LivroControllers = Depends(get_livro_controller), cache: Redis = Depends(get_cache)):
    result = controller.emprestar(request.livro_id, request.pessoa_id, current_user["id"], cache)
    return ApiResponse(data=EmprestimoResponse(
        id=result.id,
        livro_id=result.livro_id,
        pessoa_id=result.pessoa_id,
        usuario_id=result.usuario_id,
        data_emprestimo=result.data_emprestimo.isoformat(),
        data_devolucao=result.data_devolucao.isoformat() if result.data_devolucao else None,
    ))

@router.put("/{livro_id}/devolver", response_model=ApiResponse[EmprestimoResponse])
def devolver(livro_id: int, controller: LivroControllers = Depends(get_livro_controller), cache: Redis = Depends(get_cache)):
    result = controller.devolver(livro_id, cache)
    return ApiResponse(data=EmprestimoResponse(
        id=result.id,
        livro_id=result.livro_id,
        pessoa_id=result.pessoa_id,
        usuario_id=result.usuario_id,
        data_emprestimo=result.data_emprestimo.isoformat(),
        data_devolucao=result.data_devolucao.isoformat() if result.data_devolucao else None,
    ))

# Rotas de Empréstimos
@emprestimo_router.get("/", response_model=ApiResponse[PaginatedResponse[EmprestimoResponse]])
def listar_emprestimos(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=20, description="Tamanho da página (máx: 20)"),
    status: EmprestimoStatus = Query(EmprestimoStatus.ATIVOS, description="Filtrar por status: ativos, devolvidos ou todos"),
    controller: LivroControllers = Depends(get_livro_controller), 
    cache: Redis = Depends(get_cache)
):
    result = controller.listar_emprestimos_paginado(page, size, status, cache)
    return ApiResponse(data=result) 