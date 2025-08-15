from fastapi import Request
from fastapi.responses import JSONResponse
from src.presentation.dto.common import ApiResponse
from src.domain.exceptions import (
	DomainException,
	EmailJaExisteException,
	PessoaNaoEncontradaException,
	DadosInvalidosException
)

def create_exception_handlers():
	async def email_ja_existe_handler(request: Request, exc: EmailJaExisteException) -> JSONResponse:
		return JSONResponse(
			status_code=409,
			content=ApiResponse[None](
				success=False,
				error="EMAIL_ALREADY_EXISTS",
				message=f"Email '{exc.email}' já está cadastrado",
				details={"email": exc.email, "suggestion": "Use um email diferente ou faça login se já tiver conta"}
			).model_dump()
		)
	
	async def pessoa_nao_encontrada_handler(request: Request, exc: PessoaNaoEncontradaException) -> JSONResponse:
		return JSONResponse(
			status_code=404,
			content=ApiResponse[None](
				success=False,
				error="PERSON_NOT_FOUND",
				message=f"Pessoa com ID {exc.pessoa_id} não encontrada",
				details={"pessoa_id": exc.pessoa_id, "suggestion": "Verifique se o ID está correto"}
			).model_dump()
		)
	
	async def dados_invalidos_handler(request: Request, exc: DadosInvalidosException) -> JSONResponse:
		return JSONResponse(
			status_code=400,
			content=ApiResponse[None](
				success=False,
				error="INVALID_DATA",
				message=f"Campo '{exc.campo}' com valor '{exc.valor}' é inválido",
				details={"field": exc.campo, "value": exc.valor, "suggestion": "Verifique o formato e regras do campo"}
			).model_dump()
		)
	
	async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
		return JSONResponse(
			status_code=422,
			content=ApiResponse[None](
				success=False,
				error="DOMAIN_ERROR",
				message=str(exc),
				details={"exception_type": exc.__class__.__name__, "suggestion": "Verifique os dados enviados"}
			).model_dump()
		)
	
	return {
		EmailJaExisteException: email_ja_existe_handler,
		PessoaNaoEncontradaException: pessoa_nao_encontrada_handler,
		DadosInvalidosException: dados_invalidos_handler,
		DomainException: domain_exception_handler,
	} 