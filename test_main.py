import httpx
import asyncio
import pytest
from main import app

@pytest.mark.asyncio
async def test_check_db():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/check-db")
        print(response.text)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_status_codes():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        config_resp = await client.post("/config", json={"interval_value": 1})
        assert config_resp.status_code == 201
        config_id = config_resp.json()["config"][0]["id"]

        measurement_resp = await client.post("/measurements", json={"config_id": config_id})
        assert measurement_resp.status_code == 201
        measurement_id = measurement_resp.json()["measurement"][0]["id"]

        test_cases = [
            ("get",  "/check-db",                  (200, 500)),
            ("get",  "/db-schema",                 200),
            ("get",  "/config",                    200),
            ("get",  "/measurements",              200),
            ("get",  f"/config/{config_id}",       200),
            ("get",  f"/measurement/{measurement_id}", 200),
            ("get",  "/config/999999", 404),
            ("get",  "/measurements/999999", 404),
        ]

        for method, url, expect in test_cases:
            resp = await getattr(client, method)(url)
            if isinstance(expect, tuple):
                assert resp.status_code in expect, f"{url} failed with {resp.status_code}"
            else:
                assert resp.status_code == expect, f"{url} failed with {resp.status_code}"