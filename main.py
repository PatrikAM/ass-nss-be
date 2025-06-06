from datetime import datetime
from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from collections.abc import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware

from settings import DATABASE_URL

def get_engine():
    """
    Create and return an async SQLAlchemy engine instance.
    
    Returns:
        AsyncEngine: A SQLAlchemy async engine instance configured with the database URL.
    """
    return create_async_engine(DATABASE_URL, echo=True, future=True)

def get_session():
    """
    Create and return a session factory for database operations.
    
    Returns:
        sessionmaker: A SQLAlchemy session factory configured with an async session class.
    """
    engine = get_engine()
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that creates and yields a database session.
    
    Yields:
        AsyncSession: An async database session that will be automatically closed after use.
        
    Note:
        This is designed to be used as a FastAPI dependency for route handlers.
    """
    SessionLocal = get_session()
    async with SessionLocal() as session:
        yield session

app = FastAPI(
    title="Measurement API",
    description="API for managing measurements and configurations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfigCreateRequest(BaseModel):
    """
    Pydantic model for creating a new configuration.
    
    Attributes:
        interval_value (int): The interval value for the configuration.
        frequency (float, optional): The frequency setting. Defaults to None.
        rgb_camera (bool, optional): Whether RGB camera is enabled. Defaults to None.
        hsi_camera (bool, optional): Whether HSI camera is enabled. Defaults to None.
    """
    interval_value: int
    frequency: float | None = None
    rgb_camera: bool | None = None
    hsi_camera: bool | None = None

@app.get("/check-db", status_code=status.HTTP_200_OK)
async def select_demo(session: AsyncSession = Depends(get_db_session)):
    """
    Check if the database is accessible by executing a simple query.
    
    Args:
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing the status and the current database timestamp.
        
    Raises:
        HTTPException: If there's an error connecting to the database.
    """
    try:
        result = await session.execute(text("SELECT NOW() as now"))
        row = result.fetchone()
        return {"status": "ok", "result": dict(row._mapping) if row else None}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/db-schema", status_code=status.HTTP_200_OK)
async def db_schema(session: AsyncSession = Depends(get_db_session)):
    """
    Retrieve the complete database schema including all tables and their columns.
    
    Args:
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing the database schema with table names as keys
              and their column definitions as values.
              
    Raises:
        HTTPException: If there's an error retrieving the database schema.
    """
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
    """
    Retrieve all measurements from the database.
    
    Args:
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing a list of all measurements.
        
    Raises:
        HTTPException: If there's an error retrieving the measurements.
    """
    try:
        result = await session.execute(text("SELECT * FROM measurement"))
        measurements = [dict(row._mapping) for row in result.fetchall()]
        return {"measurements": measurements}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/config", status_code=status.HTTP_200_OK)
async def read_config(session: AsyncSession = Depends(get_db_session)):
    """
    Retrieve all configuration entries from the database.
    
    Args:
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing a list of all configuration entries.
        
    Raises:
        HTTPException: If there's an error retrieving the configurations.
    """
    try:
        result = await session.execute(text("SELECT * FROM config"))
        config = [dict(row._mapping) for row in result.fetchall()]
        return {"config": config}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.post("/config", status_code=status.HTTP_201_CREATED)
async def create_config(payload: ConfigCreateRequest, session: AsyncSession = Depends(get_db_session)):
    """
    Create a new configuration entry in the database.
    
    Args:
        payload (ConfigCreateRequest): The configuration data to be created.
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing the created configuration.
        
    Raises:
        HTTPException: If there's an error creating the configuration.
    """
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
async def create_measurement(
    snapshot_rgb_camera: str | None = None, 
    snapshot_hsi_camera: str | None = None, 
    acustic: int | None = None, 
    config_id: int | None = None, 
    created_at: datetime | None = datetime.now(), 
    session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new measurement entry in the database.
    
    Args:
        snapshot_rgb_camera (str, optional): Base64 encoded RGB camera snapshot. Defaults to None.
        snapshot_hsi_camera (str, optional): Base64 encoded HSI camera snapshot. Defaults to None.
        acustic (int, optional): Acoustic measurement value. Defaults to None.
        config_id (int, optional): ID of the associated configuration. Defaults to None.
        created_at (datetime, optional): Timestamp of the measurement. Defaults to current time.
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing the created measurement.
        
    Raises:
        HTTPException: If there's an error creating the measurement.
    """
    try:
        snapshot_hsi_camera_preprocessed = snapshot_hsi_camera
        if snapshot_hsi_camera == "None":
            snapshot_hsi_camera_preprocessed = None
        snapshot_rgb_camera_preprocessed = snapshot_rgb_camera
        if snapshot_rgb_camera == "None":
            snapshot_rgb_camera_preprocessed = None
        date = datetime.now()
        result = await session.execute(text("INSERT INTO measurement (snapshot_rgb_camera, snapshot_hsi_camera, acustic, config_id, created_at) VALUES (:snapshot_rgb_camera, :snapshot_hsi_camera, :acustic, :config_id, :created_at) RETURNING *"), {"snapshot_rgb_camera": snapshot_rgb_camera_preprocessed, "snapshot_hsi_camera": snapshot_hsi_camera_preprocessed, "acustic": acustic, "config_id": config_id, "created_at": date})
        await session.commit()
        measurement = [dict(row._mapping) for row in result.fetchall()]
        return {"measurement": measurement}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/config/{config_id}", status_code=status.HTTP_200_OK)
async def read_config_by_id(config_id: int, session: AsyncSession = Depends(get_db_session)):
    """
    Retrieve a specific configuration by its ID.
    
    Args:
        config_id (int): The ID of the configuration to retrieve.
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing the requested configuration.
        
    Raises:
        HTTPException: 404 if the configuration is not found.
        HTTPException: 500 if there's an error retrieving the configuration.
    """
    try:
        result = await session.execute(text("SELECT * FROM config WHERE id = :config_id"), {"config_id": config_id})
        config = [dict(row._mapping) for row in result.fetchall()][0]
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
    """
    Retrieve a specific measurement by its ID.
    
    Args:
        measurement_id (int): The ID of the measurement to retrieve.
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing the requested measurement.
        
    Raises:
        HTTPException: 404 if the measurement is not found.
        HTTPException: 500 if there's an error retrieving the measurement.
    """
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

@app.get("/measurement/config/{config_id}", status_code=status.HTTP_200_OK)
async def read_measurement_by_config_id(config_id: int, session: AsyncSession = Depends(get_db_session)):
    """
    Retrieve all measurements associated with a specific configuration ID.
    
    Args:
        config_id (int): The ID of the configuration to get measurements for.
        session (AsyncSession): The database session dependency.
        
    Returns:
        dict: A dictionary containing a list of measurements for the specified configuration.
        
    Raises:
        HTTPException: 404 if no measurements are found for the configuration.
        HTTPException: 500 if there's an error retrieving the measurements.
    """
    try:
        result = await session.execute(text("SELECT * FROM measurement WHERE config_id = :config_id"), {"config_id": config_id})
        measurement = result.fetchall()
        if not measurement:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": f"Measurement with config id {config_id} not found"}
            )
        return {"measurement": [dict(row._mapping) for row in measurement]}
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})