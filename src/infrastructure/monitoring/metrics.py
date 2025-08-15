from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Métricas de HTTP (Automáticas)
http_requests_total = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'route', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'route']
)

# Métricas de cache Redis
redis_cache_hits_total = Counter('redis_cache_hits_total', 'Total de hits no cache Redis')
redis_cache_misses_total = Counter('redis_cache_misses_total', 'Total de misses no cache Redis')
redis_commands_total = Counter('redis_commands_total', 'Total de comandos Redis executados')

# Métricas de banco de dados
db_connections_active = Gauge('db_connections_active', 'Conexões ativas com o banco')
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Duração das queries em segundos',
    ['operation', 'table']
)

# Métricas de erros
http_errors_total = Counter(
    'http_errors_total',
    'Total de erros HTTP',
    ['method', 'route', 'status_code', 'error_type']
)

# Métricas de performance da aplicação
app_memory_usage_bytes = Gauge('app_memory_usage_bytes', 'Uso de memória da aplicação em bytes')
app_cpu_usage_percent = Gauge('app_cpu_usage_percent', 'Uso de CPU da aplicação em percentual')

class MetricsMiddleware:
    """Middleware para coletar métricas automáticas das requisições HTTP"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            start_time = time.time()
            
            # Capturar método e rota
            method = scope['method']
            route = scope.get('path', 'unknown')
            
            # Processar a requisição
            await self.app(scope, receive, send)
            
            # Calcular duração
            duration = time.time() - start_time
            
            # Determinar status code (simplificado)
            status_code = 200  # Por padrão, assumimos sucesso
            
            # Incrementar contadores
            http_requests_total.labels(method=method, route=route, status_code=status_code).inc()
            http_request_duration_seconds.labels(method=method, route=route).observe(duration)
            
            # Registrar erros se aplicável
            if status_code >= 400:
                error_type = 'client_error' if status_code < 500 else 'server_error'
                http_errors_total.labels(method=method, route=route, status_code=status_code, error_type=error_type).inc()
        
        else:
            await self.app(scope, receive, send)

def get_metrics():
    """Retorna as métricas no formato Prometheus"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

def record_cache_hit():
    """Registra um hit no cache"""
    redis_cache_hits_total.inc()

def record_cache_miss():
    """Registra um miss no cache"""
    redis_cache_misses_total.inc()

def record_redis_command():
    """Registra um comando Redis"""
    redis_commands_total.inc()

def record_db_operation(operation: str, table: str, duration: float):
    """Registra uma operação de banco de dados"""
    db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)

def record_http_error(method: str, route: str, status_code: int, error_type: str):
    """Registra um erro HTTP"""
    http_errors_total.labels(method=method, route=route, status_code=status_code, error_type=error_type).inc()

def update_app_metrics(memory_bytes: int, cpu_percent: float):
    """Atualiza métricas da aplicação (memória, CPU)"""
    app_memory_usage_bytes.set(memory_bytes)
    app_cpu_usage_percent.set(cpu_percent) 