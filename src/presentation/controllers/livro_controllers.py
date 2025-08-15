from src.application.usecase.livro_usecases import LivroUseCase
from src.presentation.dto.livro_dto import LivroCreateRequest, LivroResponse, EmprestimoResponse
from src.presentation.dto.common import PaginationParams, PaginationMeta, PaginatedResponse
from src.domain.enums.emprestimo_status import EmprestimoStatus
import json
from redis import Redis
from src.infrastructure.cache.redis_client import cache_get_safe, cache_set_safe, cache_delete_safe

class LivroControllers:
	def __init__(self, usecase: LivroUseCase):
		self.usecase = usecase
		self.CACHE_TTL = 120

	def cadastrar(self, request: LivroCreateRequest, cache: Redis):
		result = self.usecase.cadastrar_livro(request.titulo, request.autor)
		
		cache_delete_safe(cache, "livros:list")
		cache_delete_safe(cache, f"livros:{result.id}")
		
		return result

	def listar(self):
		return self.usecase.listar_livros()

	def listar_paginado(self, page: int, size: int, cache: Redis) -> PaginatedResponse[LivroResponse]:
		pagination = PaginationParams(page=page, size=size)
		pagination.validate_page_size()
		
		cache_key = f"livros:list:page:{pagination.page}:size:{pagination.size}"
		
		cached = cache_get_safe(cache, cache_key)
		if cached:
			cached_data = json.loads(cached)
			return PaginatedResponse(
				data=[LivroResponse(**p) for p in cached_data["data"]],
				meta=PaginationMeta(**cached_data["meta"])
			)
		
		livros, total = self.usecase.listar_livros_paginado(pagination.page, pagination.size)
		
		meta = PaginationMeta.create(pagination.page, pagination.size, total)
		response_data = [LivroResponse.model_validate(l) for l in livros]
		
		cache_payload = {
			"data": [l.model_dump(mode="json") for l in response_data],
			"meta": meta.model_dump()
		}
		cache_set_safe(cache, cache_key, json.dumps(cache_payload), ttl_seconds=self.CACHE_TTL)
		
		return PaginatedResponse(data=response_data, meta=meta)

	def listar_emprestimos_paginado(self, page: int, size: int, status: EmprestimoStatus, cache: Redis) -> PaginatedResponse[EmprestimoResponse]:
		pagination = PaginationParams(page=page, size=size)
		pagination.validate_page_size()
		
		cache_key = f"emprestimos:list:status:{status.value}:page:{pagination.page}:size:{pagination.size}"
		
		cached = cache_get_safe(cache, cache_key)
		if cached:
			cached_data = json.loads(cached)
			return PaginatedResponse(
				data=[EmprestimoResponse(**p) for p in cached_data["data"]],
				meta=PaginationMeta(**cached_data["meta"])
			)
		
		emprestimos, total = self.usecase.listar_emprestimos_paginado(pagination.page, pagination.size, status)
		
		meta = PaginationMeta.create(pagination.page, pagination.size, total)
		response_data = []
		
		for e in emprestimos:
			response_data.append(EmprestimoResponse(
				id=e.id,
				livro_id=e.livro_id,
				pessoa_id=e.pessoa_id,
				usuario_id=e.usuario_id,
				data_emprestimo=e.data_emprestimo.isoformat(),
				data_devolucao=e.data_devolucao.isoformat() if e.data_devolucao else None,
			))
		
		cache_payload = {
			"data": [e.model_dump(mode="json") for e in response_data],
			"meta": meta.model_dump()
		}
		cache_set_safe(cache, cache_key, json.dumps(cache_payload), ttl_seconds=self.CACHE_TTL)
		
		return PaginatedResponse(data=response_data, meta=meta)

	def emprestar(self, livro_id: int, pessoa_id: int, usuario_id: int, cache: Redis):
		result = self.usecase.emprestar(livro_id, pessoa_id, usuario_id)
		
		cache_delete_safe(cache, "livros:list")
		cache_delete_safe(cache, f"livros:{livro_id}")
		cache_delete_safe(cache, "emprestimos:list")
		
		return result

	def devolver(self, livro_id: int, cache: Redis):
		result = self.usecase.devolver(livro_id)
		
		cache_delete_safe(cache, "livros:list")
		cache_delete_safe(cache, f"livros:{livro_id}")
		cache_delete_safe(cache, "emprestimos:list")
		
		return result 