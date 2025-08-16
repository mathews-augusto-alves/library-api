"""
Testes para o MetricsMiddleware e endpoint de métricas.
"""
import pytest
from src.infrastructure.monitoring.metrics import (
    MetricsMiddleware,
    http_requests_total,
    get_metrics,
)


@pytest.mark.asyncio
async def test_metrics_middleware_increments_counters():
    async def simple_app(scope, receive, send):
        if scope["type"] == "http":
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"OK"})

    middleware = MetricsMiddleware(simple_app)

    scope = {"type": "http", "method": "GET", "path": "/teste"}

    async def dummy_receive():
        return {"type": "http.request"}

    async def dummy_send(message):
        pass

    labels = http_requests_total.labels(method="GET", route="/teste", status_code=200)
    before = labels._value.get()

    await middleware(scope, dummy_receive, dummy_send)

    after = labels._value.get()
    assert after == before + 1


def test_get_metrics_returns_response():
    resp = get_metrics()
    assert resp.status_code == 200
    assert resp.media_type.startswith("text/plain") 