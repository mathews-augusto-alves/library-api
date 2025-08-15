import redis
import os
import logging
from typing import Optional
from src.infrastructure.monitoring.metrics import record_redis_command, record_cache_hit, record_cache_miss

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    """Retorna uma instância do cliente Redis"""
    global _redis_client
    
    if _redis_client is None and REDIS_ENABLED:
        try:
            if REDIS_URL:
                _redis_client = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            else:
                _redis_client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
            
            _redis_client.ping()
            logger.info(f"Redis conectado via {'URL' if REDIS_URL else f'{REDIS_HOST}:{REDIS_PORT}'}")
        except Exception as e:
            logger.warning(f"Falha ao conectar com Redis: {e}")
            _redis_client = None
    
    return _redis_client

def cache_get_safe(client: redis.Redis, key: str) -> Optional[str]:
    """Busca um valor do cache de forma segura"""
    if not client or not REDIS_ENABLED:
        return None
    
    try:
        record_redis_command()
        value = client.get(key)
        if value:
            record_cache_hit()
        else:
            record_cache_miss()
        return value
    except Exception as e:
        logger.warning(f"Erro ao buscar cache Redis: {e}")
        return None

def cache_set_safe(client: redis.Redis, key: str, value: str, ttl_seconds: int = 300) -> bool:
    """Define um valor no cache de forma segura"""
    if not client or not REDIS_ENABLED:
        return False
    
    try:
        record_redis_command()
        return client.setex(key, ttl_seconds, value)
    except Exception as e:
        logger.warning(f"Erro ao definir cache Redis: {e}")
        return False

def cache_delete_safe(client: redis.Redis, key: str) -> bool:
    """Remove um valor do cache de forma segura"""
    if not client or not REDIS_ENABLED:
        return False
    
    try:
        record_redis_command()
        return bool(client.delete(key))
    except Exception as e:
        logger.warning(f"Erro ao remover cache Redis: {e}")
        return False

def cache_get(client: redis.Redis, key: str) -> Optional[str]:
    """Busca um valor do cache (versão não segura para compatibilidade)"""
    return cache_get_safe(client, key)

def cache_set(client: redis.Redis, key: str, value: str, ttl_seconds: int = 300) -> bool:
    """Define um valor no cache (versão não segura para compatibilidade)"""
    return cache_set_safe(client, key, value, ttl_seconds) 