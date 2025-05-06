from fastapi.testclient import TestClient
from main import app
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi.responses import JSONResponse
from main import (
    select_demo,
    db_schema,
    read_measurements,
    read_config,
    create_config,
    create_measurement
)

client = TestClient(app)

def test_check_db():
    response = client.get("/check-db")
    print(response.text) 
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_select_demo():
    response = client.get("/select-demo")
    print(response.text) 
    assert response.status_code == 200
    assert "result" in response.json()
    
@pytest.mark.asyncio
async def test_check_db():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_row = MagicMock()
    mock_row._mapping = {"now": "2024-03-20 10:00:00"}
    mock_result.fetchone.return_value = mock_row
    
    mock_session.execute.return_value = mock_result
    
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await select_demo()
        
        assert result["status"] == "ok"
        assert result["result"] == {"now": "2024-03-20 10:00:00"}
        mock_session.execute.assert_called_once()

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
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await select_demo()
        
        assert result["status"] == "ok"
        assert result["result"] == {"now": "2024-03-20 10:00:00"}
        mock_session.execute.assert_called_once()

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await select_demo()
        
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
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await db_schema()
        
        assert result["status"] == "ok"
        assert "table1" in result["schema"]
        assert "table2" in result["schema"]
        assert len(result["schema"]["table1"]) == 2

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await db_schema()
        
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
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await read_measurements(config_id=None)
        
        assert "measurements" in result
        assert len(result["measurements"]) == 2
        assert result["measurements"][0]["id"] == 1

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await read_measurements(config_id=None)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_read_config():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(_mapping={"id": 1, "interval": 100}),
        MagicMock(_mapping={"id": 2, "interval": 200})
    ]
    mock_session.execute.return_value = mock_result
    
    # Test successful case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await read_config(config_id=None)
        
        assert "config" in result
        assert len(result["config"]) == 2
        assert result["config"][0]["interval"] == 100

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await read_config(config_id=None)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        assert result.body.decode() == '{"status":"error","message":"DB Error"}'

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
    
    # Test successful case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await create_config(interval=100, frequency=1.5, rgb_camera=True, hsi_camera=False)
        
        assert "config" in result
        assert len(result["config"]) == 1
        assert result["config"][0]["interval"] == 100
        mock_session.commit.assert_called_once()

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await create_config(interval=100)
        
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
    
    # Test successful case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await create_measurement(
            snapshot_rgb_camera="data1",
            snapshot_hsi_camera="data2",
            acustic=50,
            config_id=1
        )
        
        assert "measurement" in result
        assert len(result["measurement"]) == 1
        assert result["measurement"][0]["acustic"] == 50
        mock_session.commit.assert_called_once()

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await create_measurement(snapshot_rgb_camera="data1")
        
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
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await read_measurements(config_id=1)
        
        assert "measurements" in result
        assert len(result["measurements"]) == 2
        assert all(m["config_id"] == 1 for m in result["measurements"])

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await read_measurements(config_id=1)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        assert result.body.decode() == '{"status":"error","message":"DB Error"}'

@pytest.mark.asyncio
async def test_read_measurement_by_id():
    # Mock the session and result
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MagicMock(_mapping={"id": 1, "snapshot_rgb_camera": "data1"})
    ]
    mock_session.execute.return_value = mock_result
    
    # Test successful case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value = mock_session
        result = await read_measurements(config_id=1)
        
        assert "measurements" in result
        assert len(result["measurements"]) == 1
        assert result["measurements"][0]["id"] == 1

    # Test error case
    with patch("main.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value.__aenter__.return_value.execute.side_effect = Exception("DB Error")
        result = await read_measurements(config_id=1)
        
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500
        assert result.body.decode() == '{"status":"error","message":"DB Error"}'
