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
from app.core.database       import create_tables

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
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