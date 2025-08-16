from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.config.exception_handlers import create_exception_handlers
from src.presentation.routes.pessoa_routes import router as pessoa_router
from src.presentation.routes.usuario_routes import router as usuario_router, auth_router
from src.presentation.routes.livro_routes import router as livro_router, emprestimo_router
from src.infrastructure.monitoring.metrics import get_metrics, MetricsMiddleware
from src.infrastructure.config.logging_config import setup_logging, get_logger
from fastapi.openapi.utils import get_openapi


def create_app() -> FastAPI:
	setup_logging()
	logger = get_logger(__name__)
	
	app = FastAPI(
		title="API Library - Clean Architecture",
		description="API RESTful para gerenciamento de biblioteca seguindo Clean Architecture",
		version="1.0.0",
		docs_url="/docs",
		redoc_url="/redoc"
	)
	
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)
	
	app.add_middleware(MetricsMiddleware)
	
	exception_handlers = create_exception_handlers()
	for exception_class, handler in exception_handlers.items():
		app.add_exception_handler(exception_class, handler)

	@app.get("/metrics")
	async def metrics():
		return get_metrics()

	@app.get("/health")
	async def health():
		return {"status": "healthy", "service": "api-library"}

	api_router = APIRouter(prefix="/api/v1")
	api_router.include_router(auth_router)
	api_router.include_router(usuario_router)
	api_router.include_router(pessoa_router)
	api_router.include_router(livro_router)
	api_router.include_router(emprestimo_router)

	app.include_router(api_router)

	def custom_openapi():
		if app.openapi_schema:
			return app.openapi_schema
		schema = get_openapi(
			title=app.title,
			version=app.version,
			description=app.description,
			routes=app.routes,
		)
		security_schemes = schema.get("components", {}).get("securitySchemes", {})
		if "OAuth2PasswordBearer" in security_schemes:
			security_schemes["OAuth2PasswordBearer"] = {
				"type": "http",
				"scheme": "bearer",
				"bearerFormat": "JWT",
			}
		app.openapi_schema = schema
		return app.openapi_schema

	app.openapi = custom_openapi
	
	logger.info("Aplicação configurada com sucesso!")
	return app 