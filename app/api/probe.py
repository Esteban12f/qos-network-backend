from datetime import datetime, timezone

from fastapi import APIRouter, Query, Response

router = APIRouter(
    prefix="/probe",
    tags=["Probe"]
)


@router.get("/ping")
def ping():
    """
    Endpoint liviano para medir latencia desde Angular.
    Angular calcula el tiempo entre enviar la petición y recibir la respuesta.
    """
    return {
        "status": "ok",
        "message": "pong",
        "server_timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/download")
def download_probe(
    size_kb: int = Query(
        default=512,
        ge=64,
        le=5120,
        description="Tamaño del archivo de prueba en KB. Máximo 5120 KB."
    )
):
    """
    Endpoint para prueba de descarga.

    Angular descarga este contenido y calcula el throughput aproximado:
    Mbps = (bytes_descargados * 8) / tiempo_segundos / 1_000_000
    """
    size_bytes = size_kb * 1024
    content = b"0" * size_bytes

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "X-Probe-Size-KB": str(size_kb),
            "Cache-Control": "no-store"
        }
    )