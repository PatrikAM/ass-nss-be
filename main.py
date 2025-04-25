import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

app = FastAPI()

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@app.get("/check-db")
async def select_demo():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT NOW() as now"))
            row = result.fetchone()
        return {"status": "ok", "result": dict(row._mapping) if row else None}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/db-schema")
async def db_schema():
    try:
        async with AsyncSessionLocal() as session:
            # Get all table names in the public schema
            tables_result = await session.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """))
            table_names = [row[0] for row in tables_result.fetchall()]

            schema = {}
            for table in table_names:
                columns_result = await session.execute(text(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = :table
                """), {"table": table})
                columns = [
                    {"name": col[0], "type": col[1]} for col in columns_result.fetchall()
                ]
                schema[table] = columns
        return {"status": "ok", "schema": schema}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/measurements")
async def read_measurements():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT * FROM measurement"))
            measurements = [dict(row._mapping) for row in result.fetchall()]
        return {"measurements": measurements}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/config")
async def read_config():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT * FROM config"))
            config = [dict(row._mapping) for row in result.fetchall()]
        return {"config": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/config")
async def create_config(interval: int, frequency: float, rgb_camera: bool, hsi_camera: bool):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("INSERT INTO config (interval, frequency, rgb_camera, hsi_camera) VALUES (:interval, :frequency, :rgb_camera, :hsi_camera) RETURNING *"), {"interval": interval, "frequency": frequency, "rgb_camera": rgb_camera, "hsi_camera": hsi_camera})
            config = [dict(row._mapping) for row in result.fetchall()]
        return {"config": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/measurements")
async def create_measurement(snapshot_rgb_camera: str, snapshot_hsi_camera: str, acustic: int, config_id: int):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("INSERT INTO measurement (snapshot_rgb_camera, snapshot_hsi_camera, acustic, config_id) VALUES (:snapshot_rgb_camera, :snapshot_hsi_camera, :acustic, :config_id) RETURNING *"), {"snapshot_rgb_camera": snapshot_rgb_camera, "snapshot_hsi_camera": snapshot_hsi_camera, "acustic": acustic, "config_id": config_id})
            measurement = [dict(row._mapping) for row in result.fetchall()]
        return {"measurement": measurement}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    
@app.get("/config/{config_id}")
async def read_config(config_id: int):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT * FROM config WHERE id = :config_id"), {"config_id": config_id})
            config = [dict(row._mapping) for row in result.fetchall()]
        return {"config": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/measurements/{config_id}")
async def read_measurements(config_id: int):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT * FROM measurement WHERE config_id = :config_id"), {"config_id": config_id})
            measurements = [dict(row._mapping) for row in result.fetchall()]
        return {"measurements": measurements}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/measurements/{measurement_id}")
async def read_measurement(measurement_id: int):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT * FROM measurement WHERE id = :measurement_id"), {"measurement_id": measurement_id})
            measurement = [dict(row._mapping) for row in result.fetchall()]
        return {"measurement": measurement}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

