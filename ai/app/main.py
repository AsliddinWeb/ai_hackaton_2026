"""ShifokorAI - tasvir quvuri xizmati.

Faza 0.3 uchun skelet. Haqiqiy quvur Faza 1 da to'ldiriladi:
  1.1 sifat darvozasi
  1.2 plyonka fotosi normalizatsiyasi
  1.3 patologiya modeli
  1.4 issiqlik xaritasi
  1.5 anatomik joy

Hozircha /predict kontrakt shaklini qaytaradi, lekin natijalar to'ldirilmagan -
mobil ilova va panel shu shakl bo'yicha ishlashni boshlay oladi.
"""

import os
from datetime import datetime, timezone

import cv2
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

VERSION = "0.1.0"
MODEL_CACHE = os.getenv("MODEL_CACHE", "/models")

app = FastAPI(title="ShifokorAI - tasvir quvuri", version=VERSION)


class PredictRequest(BaseModel):
    image_path: str
    case_id: int | None = None


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {
        "status": "ok",
        "version": VERSION,
        "time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "opencv": cv2.__version__,
        "numpy": np.__version__,
        "model_cache": MODEL_CACHE,
        "model_loaded": False,  # Faza 1.3 da True bo'ladi
    }


@app.post("/predict", tags=["ai"])
async def predict(req: PredictRequest) -> dict:
    """docs/api.md dagi shakl. Faza 1 gacha natijalar bo'sh."""
    return {
        "quality": None,
        "normalized_path": None,
        "heatmap_path": None,
        "risk": None,
        "risk_score": None,
        "findings": [],
        "model": {"name": "not_loaded", "version": VERSION},
        "elapsed_ms": 0,
        "reason": "pipeline_not_implemented",
    }
