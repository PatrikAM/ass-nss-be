import os
import httpx
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from fastapi.responses import JSONResponse
from main import (
    app,
    select_demo,
    db_schema,
    read_measurements,
    create_config,
    create_measurement,
    ConfigCreateRequest,
    read_measurement_by_id,
    get_db_session,
)

integration = pytest.mark.skipif(
    os.getenv("RUN_TESTS") != "1",
    reason="Integration tests require RUN_TESTS=1"
)

@integration
@pytest.mark.asyncio
async def test_check_db():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/check-db")
        print(response.text)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@integration
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

@pytest.mark.asyncio
async def test_check_db():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_row = MagicMock()
    mock_row._mapping = {"now": "2024-03-20 10:00:00"}
    mock_result.fetchone.return_value = mock_row

    mock_session.execute.return_value = mock_result

    result = await select_demo(mock_session)

    assert result["status"] == "ok"
    assert result["result"] == {"now": "2024-03-20 10:00:00"}
    mock_session.execute.assert_called_once()

    mock_session.execute.side_effect = Exception("DB Error")
    result = await select_demo(mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_select_demo():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_row = MagicMock()
    mock_row._mapping = {"now": "2024-03-20 10:00:00"}
    mock_result.fetchone.return_value = mock_row

    mock_session.execute.return_value = mock_result

    # Test successful case
    result = await select_demo(mock_session)

    assert result["status"] == "ok"
    assert result["result"] == {"now": "2024-03-20 10:00:00"}
    mock_session.execute.assert_called_once()

    # Test error case
    mock_session.execute.side_effect = Exception("DB Error")
    result = await select_demo(mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_db_schema():
    # Mock the session and results
    mock_session = AsyncMock()
    mock_tables_result = MagicMock()
    mock_tables_result.fetchall.return_value = [("table1",), ("table2",)]

    mock_columns_result = MagicMock()
    mock_columns_result.fetchall.return_value = [
        ("column1", "integer"),
        ("column2", "text")
    ]

    mock_session.execute.side_effect = [mock_tables_result, mock_columns_result, mock_columns_result]

    # Test successful case
    result = await db_schema(mock_session)

    assert result["status"] == "ok"
    assert "table1" in result["schema"]
    assert "table2" in result["schema"]
    assert len(result["schema"]["table1"]) == 2

    # Test error case
    mock_session.execute.side_effect = Exception("DB Error")
    result = await db_schema(mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_read_measurements():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(_mapping={"id": 1, "snapshot_rgb_camera": "data1"}),
        MagicMock(_mapping={"id": 2, "snapshot_rgb_camera": "data2"})
    ]
    mock_session.execute.return_value = mock_result

    # Test successful case
    result = await read_measurements(mock_session)

    assert "measurements" in result
    assert len(result["measurements"]) == 2
    assert result["measurements"][0]["id"] == 1

    # Test error case
    mock_session.execute.side_effect = Exception("DB Error")
    result = await read_measurements(mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_read_config():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(_mapping={"id": 1, "interval": 100}),
        MagicMock(_mapping={"id": 2, "interval": 200})
    ]
    mock_session.execute.return_value = mock_result

    # Override the DB session dependency
    app.dependency_overrides[get_db_session] = lambda: mock_session

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
        assert len(data["config"]) == 2
        assert data["config"][0]["interval"] == 100

    # Test error case
    mock_session.execute.side_effect = Exception("DB Error")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/config")
        assert response.status_code == 500
        assert response.json() == {"status": "error", "message": "DB Error"}

    # Clean up overrides
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_config():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(_mapping={
            "id": 1,
            "interval": 100,
            "frequency": 1.5,
            "rgb_camera": True,
            "hsi_camera": False,
            "created_at": datetime.now()
        })
    ]
    mock_session.execute.return_value = mock_result

    payload = ConfigCreateRequest(interval_value=100, frequency=1.5, rgb_camera=True, hsi_camera=False)
    result = await create_config(payload, mock_session)

    assert "config" in result
    assert len(result["config"]) == 1
    assert result["config"][0]["interval"] == 100
    mock_session.commit.assert_called_once()

    mock_session.execute.side_effect = Exception("DB Error")
    result = await create_config(payload, mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_create_measurement():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(_mapping={
            "id": 1,
            "snapshot_rgb_camera": "data1",
            "snapshot_hsi_camera": "data2",
            "acustic": 50,
            "config_id": 1,
            "created_at": datetime.now()
        })
    ]
    mock_session.execute.return_value = mock_result

    result = await create_measurement(
        snapshot_rgb_camera="data1",
        snapshot_hsi_camera="data2",
        acustic=50,
        config_id=1,
        session=mock_session
    )

    assert "measurement" in result
    assert len(result["measurement"]) == 1
    assert result["measurement"][0]["acustic"] == 50
    mock_session.commit.assert_called_once()

    mock_session.execute.side_effect = Exception("DB Error")
    result = await create_measurement(snapshot_rgb_camera="data1", session=mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_read_measurements_with_config():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(_mapping={"id": 1, "config_id": 1}),
        MagicMock(_mapping={"id": 2, "config_id": 1})
    ]
    mock_session.execute.return_value = mock_result

    # Test successful case
    result = await read_measurements(mock_session)

    assert "measurements" in result
    assert len(result["measurements"]) == 2
    assert all(m["config_id"] == 1 for m in result["measurements"])

    # Test error case
    mock_session.execute.side_effect = Exception("DB Error")
    result = await read_measurements(mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_read_measurement_by_id():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchone.return_value = MagicMock(_mapping={"id": 1, "snapshot_rgb_camera": "data1"})
    mock_session.execute.return_value = mock_result

    # Test successful case
    result = await read_measurement_by_id(1, mock_session)

    assert "measurement" in result
    assert result["measurement"]["id"] == 1

    # Test error case
    mock_session.execute.side_effect = Exception("DB Error")
    result = await read_measurement_by_id(1, mock_session)

    assert isinstance(result, JSONResponse)
    assert result.status_code == 500
    assert result.body.decode() == '{"status":"error","message":"DB Error"}'
