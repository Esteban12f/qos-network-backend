import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.measurements    import router as measurements_router
from app.api.metrics         import router as metrics_router
from app.api.probe           import router as probe_router
from app.api.queue           import router as queue_router
from app.api.recommendations import router as recommendations_router
from app.api.statistics      import router as statistics_router
from app.api.system          import router as system_router
from app.core.config         import get_settings
from app.core.database       import create_tables, ensure_user_id_column

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        ensure_user_id_column()
    except Exception:
        logger.warning(
            "No se pudo conectar a la base de datos al iniciar. "
            "El servidor seguirá activo, pero las operaciones que usen la base de datos fallarán "
            "hasta que DATABASE_URL sea válida.",
            exc_info=True,
        )
    yield

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(system_router)
app.include_router(probe_router)
app.include_router(measurements_router)
app.include_router(metrics_router)
app.include_router(statistics_router)
app.include_router(queue_router)
app.include_router(recommendations_router)

@app.get("/")
def root():
    return {"message": "QoS Network Monitor API running", "docs": "/docs"}