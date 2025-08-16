from src.application.usecase.livro_usecases import LivroUseCase
from src.presentation.dto.livro_dto import LivroCreateRequest, LivroResponse, EmprestimoResponse, LivroBrief, PessoaBrief
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
			livro = self.usecase.obter_livro_por_id(e.livro_id)
			pessoa = self.usecase.obter_pessoa_por_id(e.pessoa_id)
			response_data.append(EmprestimoResponse(
				id=e.id,
				livro_id=e.livro_id,
				pessoa_id=e.pessoa_id,
				usuario_id=e.usuario_id,
				data_emprestimo=e.data_emprestimo.isoformat(),
				data_devolucao=e.data_devolucao.isoformat() if e.data_devolucao else None,
				livro=LivroBrief(id=livro.id, titulo=livro.titulo, autor=livro.autor) if livro else None,
				pessoa=PessoaBrief(id=pessoa.id, nome=pessoa.nome, telefone=pessoa.telefone, email=pessoa.email) if pessoa else None,
			))
		
		cache_payload = {
			"data": [e.model_dump(mode="json") for e in response_data],
			"meta": meta.model_dump()
		}
		cache_set_safe(cache, cache_key, json.dumps(cache_payload), ttl_seconds=self.CACHE_TTL)
		
		return PaginatedResponse(data=response_data, meta=meta)

	def emprestar(self, livro_id: int, pessoa_id: int, usuario_id: int, cache: Redis) -> EmprestimoResponse:
		result = self.usecase.emprestar(livro_id, pessoa_id, usuario_id)
		
		cache_delete_safe(cache, "livros:list")
		cache_delete_safe(cache, f"livros:{livro_id}")
		cache_delete_safe(cache, "emprestimos:list")
		
		livro = self.usecase.obter_livro_por_id(result.livro_id)
		pessoa = self.usecase.obter_pessoa_por_id(result.pessoa_id)
		return EmprestimoResponse(
			id=result.id,
			livro_id=result.livro_id,
			pessoa_id=result.pessoa_id,
			usuario_id=result.usuario_id,
			data_emprestimo=result.data_emprestimo.isoformat(),
			data_devolucao=result.data_devolucao.isoformat() if result.data_devolucao else None,
			livro=LivroBrief(id=livro.id, titulo=livro.titulo, autor=livro.autor) if livro else None,
			pessoa=PessoaBrief(id=pessoa.id, nome=pessoa.nome, telefone=pessoa.telefone, email=pessoa.email) if pessoa else None,
		)

	def devolver(self, livro_id: int, cache: Redis) -> EmprestimoResponse:
		result = self.usecase.devolver(livro_id)
		
		cache_delete_safe(cache, "livros:list")
		cache_delete_safe(cache, f"livros:{livro_id}")
		cache_delete_safe(cache, "emprestimos:list")
		
		livro = self.usecase.obter_livro_por_id(result.livro_id)
		pessoa = self.usecase.obter_pessoa_por_id(result.pessoa_id)
		return EmprestimoResponse(
			id=result.id,
			livro_id=result.livro_id,
			pessoa_id=result.pessoa_id,
			usuario_id=result.usuario_id,
			data_emprestimo=result.data_emprestimo.isoformat(),
			data_devolucao=result.data_devolucao.isoformat() if result.data_devolucao else None,
			livro=LivroBrief(id=livro.id, titulo=livro.titulo, autor=livro.autor) if livro else None,
			pessoa=PessoaBrief(id=pessoa.id, nome=pessoa.nome, telefone=pessoa.telefone, email=pessoa.email) if pessoa else None,
		) 