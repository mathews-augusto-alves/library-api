from src.application.usecase.usuario_usecases import UsuarioUseCase
from src.presentation.dto.usuario_dto import UsuarioCreateRequest, UsuarioUpdateRequest, UsuarioResponse
from src.presentation.dto.common import PaginationParams, PaginationMeta, PaginatedResponse
import json
from redis import Redis
from src.infrastructure.cache.redis_client import cache_get_safe, cache_set_safe, cache_delete_safe

class UsuarioControllers:
	def __init__(self, usecase: UsuarioUseCase):
		self.usecase = usecase
		self.CACHE_TTL = 120

	def cadastrar(self, request: UsuarioCreateRequest):
		return self.usecase.cadastrar(request.nome, request.email, request.senha)

	def login(self, email: str, senha: str):
		return self.usecase.login(email, senha)

	def listar(self):
		return self.usecase.listar()

	def listar_paginado(self, page: int, size: int, cache: Redis) -> PaginatedResponse[UsuarioResponse]:
		pagination = PaginationParams(page=page, size=size)
		pagination.validate_page_size()
		
		cache_key = f"usuarios:list:page:{pagination.page}:size:{pagination.size}"
		
		cached = cache_get_safe(cache, cache_key)
		if cached:
			cached_data = json.loads(cached)
			return PaginatedResponse(
				data=[UsuarioResponse(**p) for p in cached_data["data"]],
				meta=PaginationMeta(**cached_data["meta"])
			)
		
		usuarios, total = self.usecase.listar_paginado(pagination.page, pagination.size)
		
		meta = PaginationMeta.create(pagination.page, pagination.size, total)
		response_data = [UsuarioResponse.model_validate(u) for u in usuarios]
		
		cache_payload = {
			"data": [u.model_dump(mode="json") for u in response_data],
			"meta": meta.model_dump()
		}
		cache_set_safe(cache, cache_key, json.dumps(cache_payload), ttl_seconds=self.CACHE_TTL)
		
		return PaginatedResponse(data=response_data, meta=meta)

	def buscar_por_id(self, usuario_id: int, cache: Redis) -> UsuarioResponse:
		key = f"usuarios:{usuario_id}"
		cached = cache_get_safe(cache, key)
		if cached:
			return UsuarioResponse(**json.loads(cached))
		
		usuario = self.usecase.buscar_por_id(usuario_id)
		resp = UsuarioResponse.model_validate(usuario)
		cache_set_safe(cache, key, resp.model_dump_json(), ttl_seconds=self.CACHE_TTL)
		return resp

	def buscar_por_email(self, email: str, cache: Redis) -> UsuarioResponse:
		key = f"usuarios:email:{email}"
		cached = cache_get_safe(cache, key)
		if cached:
			return UsuarioResponse(**json.loads(cached))
		
		usuario = self.usecase.buscar_por_email(email)
		if not usuario:
			return None
		
		resp = UsuarioResponse.model_validate(usuario)
		cache_set_safe(cache, key, resp.model_dump_json(), ttl_seconds=self.CACHE_TTL)
		return resp

	def atualizar(self, usuario_id: int, request: UsuarioUpdateRequest, cache: Redis) -> UsuarioResponse:
		result = self.usecase.atualizar(usuario_id, request.nome, request.email, request.senha)
		
		cache_delete_safe(cache, f"usuarios:{usuario_id}")
		cache_delete_safe(cache, "usuarios:list")
		if request.email:
			cache_delete_safe(cache, f"usuarios:email:{request.email}")
		
		return UsuarioResponse.model_validate(result)

	def remover(self, usuario_id: int, cache: Redis) -> None:
		self.usecase.remover(usuario_id)
		
		cache_delete_safe(cache, f"usuarios:{usuario_id}")
		cache_delete_safe(cache, "usuarios:list") 