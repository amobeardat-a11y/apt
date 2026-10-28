import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_owasp_security_headers(client: AsyncClient):
    """Verifies that all recommended OWASP Security Headers are present on responses."""
    res = await client.get("/")
    assert res.status_code == 200

    headers = res.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in headers
    assert "strict-origin-when-cross-origin" in headers.get("Referrer-Policy", "")
    assert "X-Process-Time-Ms" in headers


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "UP"
    assert data["database"]["status"] == "HEALTHY"

