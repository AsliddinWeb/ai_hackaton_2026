"""ShifokorAI backend.

Faza 0.3/0.4 uchun skelet: /health bog'liq xizmatlar holatini ham qaytaradi,
shunda Docker da nima ishlamayotgani darrov ko'rinadi.
"""

import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text

VERSION = "0.1.0"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://shifokor:shifokor@db:5432/shifokor")
AI_URL = os.getenv("AI_URL", "http://ai:18301")

app = FastAPI(
    title="ShifokorAI",
    version=VERSION,
    description="Qishloqdagi rentgen suratini shifokorga yetkazadi",
)

# Telefon boshqa qurilma. Pilotdan oldin aniq manzillar bilan almashtiriladi.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    """Barcha xatolar docs/api.md dagi bir xil shaklda qaytadi."""
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": str(exc), "field": None}},
    )


async def _check_db() -> str:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:  # noqa: BLE001 - holat matn sifatida qaytadi
        return f"error: {type(exc).__name__}"


async def _check_ai() -> str:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{AI_URL}/health")
        return "ok" if r.status_code == 200 else f"http {r.status_code}"
    except Exception as exc:  # noqa: BLE001
        return f"error: {type(exc).__name__}"


@app.get("/health", tags=["health"])
async def health() -> dict:
    """Faza 0.4 shu endpoint bilan yopiladi.

    Telefondan tekshirish: brauzerda http://<LAN-IP>:18300/health ni oching.
    """
    return {
        "status": "ok",
        "version": VERSION,
        "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "services": {
            "db": await _check_db(),
            "ai": await _check_ai(),
        },
    }
