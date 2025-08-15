from fastapi import HTTPException
from src.application.usecase.pessoa_usecases import PessoaUseCase
from src.presentation.dto.pessoa_dto import PessoaCreateRequest, PessoaResponse
from src.domain.model.pessoa import Pessoa
from src.presentation.dto.common import PaginationParams, PaginationMeta, PaginatedResponse
import json
from redis import Redis
from src.infrastructure.cache.redis_client import cache_get_safe, cache_set_safe, cache_delete_safe

class PessoaControllers:
	def __init__(self, usecase: PessoaUseCase):
		self.usecase = usecase
		self.CACHE_TTL = 120

	def criar(self, request: PessoaCreateRequest, cache: Redis) -> Pessoa:
		pessoa = Pessoa(None, request.nome, request.telefone, request.data_nascimento, request.email)
		result = self.usecase.criar_pessoa(pessoa)
		
		cache_delete_safe(cache, "pessoas:list")
		if result.email:
			cache_delete_safe(cache, f"pessoas:email:{result.email}")
		cache_delete_safe(cache, f"pessoas:{result.id}")
		
		return result

	def listar(self) -> list[Pessoa]:
		return self.usecase.listar_pessoas()

	def listar_paginado(self, page: int, size: int, cache: Redis) -> PaginatedResponse[PessoaResponse]:
		pagination = PaginationParams(page=page, size=size)
		pagination.validate_page_size()
		
		cache_key = f"pessoas:list:page:{pagination.page}:size:{pagination.size}"
		
		cached = cache_get_safe(cache, cache_key)
		if cached:
			cached_data = json.loads(cached)
			return PaginatedResponse(
				data=[PessoaResponse(**p) for p in cached_data["data"]],
				meta=PaginationMeta(**cached_data["meta"])
			)
		
		pessoas, total = self.usecase.listar_pessoas_paginado(pagination.page, pagination.size)
		
		meta = PaginationMeta.create(pagination.page, pagination.size, total)
		response_data = [PessoaResponse.model_validate(p) for p in pessoas]
		
		cache_payload = {
			"data": [p.model_dump(mode="json") for p in response_data],
			"meta": meta.model_dump()
		}
		cache_set_safe(cache, cache_key, json.dumps(cache_payload), ttl_seconds=self.CACHE_TTL)
		
		return PaginatedResponse(data=response_data, meta=meta)

	def buscar_por_id(self, pessoa_id: int, cache: Redis) -> PessoaResponse:
		key = f"pessoas:{pessoa_id}"
		cached = cache_get_safe(cache, key)
		if cached:
			return PessoaResponse(**json.loads(cached))
		
		pessoa = self.usecase.buscar_por_id(pessoa_id)
		resp = PessoaResponse.model_validate(pessoa)
		cache_set_safe(cache, key, resp.model_dump_json(), ttl_seconds=self.CACHE_TTL)
		return resp

	def buscar_por_email(self, email: str, cache: Redis) -> PessoaResponse:
		key = f"pessoas:email:{email}"
		cached = cache_get_safe(cache, key)
		if cached:
			return PessoaResponse(**json.loads(cached))
		
		pessoa = self.usecase.buscar_pessoa_por_email(email)
		if not pessoa:
			raise HTTPException(status_code=404, detail=f"Pessoa com email '{email}' não encontrada")
		
		resp = PessoaResponse.model_validate(pessoa)
		cache_set_safe(cache, key, resp.model_dump_json(), ttl_seconds=self.CACHE_TTL)
		return resp

	def atualizar(self, pessoa_id: int, request: PessoaCreateRequest, cache: Redis) -> PessoaResponse:
		pessoa = Pessoa(None, request.nome, request.telefone, request.data_nascimento, request.email)
		result = self.usecase.atualizar_pessoa(pessoa_id, pessoa)
		
		cache_delete_safe(cache, "pessoas:list")
		cache_delete_safe(cache, f"pessoas:{pessoa_id}")
		if pessoa.email:
			cache_delete_safe(cache, f"pessoas:email:{pessoa.email}")
		
		return PessoaResponse.model_validate(result)

	def remover_pessoa(self, pessoa_id: int, cache: Redis) -> None:
		self.usecase.remover_pessoa(pessoa_id)
		
		cache_delete_safe(cache, "pessoas:list")
		cache_delete_safe(cache, f"pessoas:{pessoa_id}") 