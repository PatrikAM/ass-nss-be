from datetime import datetime
from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from collections.abc import AsyncGenerator

from settings import DATABASE_URL

def get_engine():
    return create_async_engine(DATABASE_URL, echo=True, future=True)

def get_session():
    engine = get_engine()
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    SessionLocal = get_session()
    async with SessionLocal() as session:
        yield session

app = FastAPI()


class ConfigCreateRequest(BaseModel):
    interval_value: int
    frequency: float | None = None
    rgb_camera: bool | None = None
    hsi_camera: bool | None = None

@app.get("/check-db", status_code=status.HTTP_200_OK)
async def select_demo(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT NOW() as now"))
        row = result.fetchone()
        return {"status": "ok", "result": dict(row._mapping) if row else None}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/db-schema", status_code=status.HTTP_200_OK)
async def db_schema(session: AsyncSession = Depends(get_db_session)):
    try:
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

@app.get("/measurements", status_code=status.HTTP_200_OK)
async def read_measurements(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM measurement"))
        measurements = [dict(row._mapping) for row in result.fetchall()]
        return {"measurements": measurements}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/config", status_code=status.HTTP_200_OK)
async def read_config(session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM config"))
        config = [dict(row._mapping) for row in result.fetchall()]
        return {"config": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/config", status_code=status.HTTP_201_CREATED)
async def create_config(payload: ConfigCreateRequest, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("""
            INSERT INTO config (interval_value, frequency, rgb_camera, hsi_camera, created_at)
            VALUES (:interval_value, :frequency, :rgb_camera, :hsi_camera, :created_at)
            RETURNING *
        """), {
            "interval_value": payload.interval_value,
            "frequency": payload.frequency,
            "rgb_camera": payload.rgb_camera,
            "hsi_camera": payload.hsi_camera,
            "created_at": datetime.now()
        })
        await session.commit()
        config = [dict(row._mapping) for row in result.fetchall()]
        return {"config": config}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/measurements", status_code=status.HTTP_201_CREATED)
async def create_measurement(snapshot_rgb_camera: str | None = None, snapshot_hsi_camera: str | None = None, acustic: int | None = None, config_id: int | None = None, created_at: datetime | None = datetime.now(), session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("INSERT INTO measurement (snapshot_rgb_camera, snapshot_hsi_camera, acustic, config_id, created_at) VALUES (:snapshot_rgb_camera, :snapshot_hsi_camera, :acustic, :config_id, :created_at) RETURNING *"), {"snapshot_rgb_camera": snapshot_rgb_camera, "snapshot_hsi_camera": snapshot_hsi_camera, "acustic": acustic, "config_id": config_id, "created_at": created_at})
        await session.commit()
        measurement = [dict(row._mapping) for row in result.fetchall()]
        return {"measurement": measurement}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/config/{config_id}", status_code=status.HTTP_200_OK)
async def read_config_by_id(config_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM config WHERE id = :config_id"), {"config_id": config_id})
        config = [dict(row._mapping) for row in result.fetchall()]
        if not config:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": f"Config with id {config_id} not found"}
            )
        return {"config": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/measurement/{measurement_id}", status_code=status.HTTP_200_OK)
async def read_measurement_by_id(measurement_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        result = await session.execute(text("SELECT * FROM measurement WHERE id = :measurement_id"), {"measurement_id": measurement_id})
        measurement = result.fetchone()
        if not measurement:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": f"Measurement with id {measurement_id} not found"}
            )
        return {"measurement": dict(measurement._mapping)}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

