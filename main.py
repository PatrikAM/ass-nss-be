import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
async def create_config(interval: int | None = None, frequency: float | None = None, rgb_camera: bool | None = None, hsi_camera: bool | None = None):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("INSERT INTO config (interval, frequency, rgb_camera, hsi_camera, created_at) VALUES (:interval, :frequency, :rgb_camera, :hsi_camera, :created_at) RETURNING *"), {"interval": interval, "frequency": frequency, "rgb_camera": rgb_camera, "hsi_camera": hsi_camera, "created_at": datetime.now()})
            await session.commit()
            config = [dict(row._mapping) for row in result.fetchall()]
        return {"config": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/measurements")
async def create_measurement(snapshot_rgb_camera: str | None = None, snapshot_hsi_camera: str | None = None, acustic: int | None = None, config_id: int | None = None, created_at: datetime | None = datetime.now()):
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("INSERT INTO measurement (snapshot_rgb_camera, snapshot_hsi_camera, acustic, config_id, created_at) VALUES (:snapshot_rgb_camera, :snapshot_hsi_camera, :acustic, :config_id, :created_at) RETURNING *"), {"snapshot_rgb_camera": snapshot_rgb_camera, "snapshot_hsi_camera": snapshot_hsi_camera, "acustic": acustic, "config_id": config_id, "created_at": created_at})
            await session.commit()
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
