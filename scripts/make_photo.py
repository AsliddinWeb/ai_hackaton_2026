#!/usr/bin/env python3
"""Toza rentgendan "negatoskopdagi plyonkaning telefon fotosi" ni sun'iy yasaydi.

Nega kerak. Faza 1.2 (normalizatsiya) aynan yomon fotolarda ishlashi kerak, lekin
qo'lda olingan fotolarda haqiqiy o'zgartirish bizga noma'lum — natijani o'lchab
bo'lmaydi. Bu skript o'zgartirishni O'ZI qo'yadi va burchak koordinatalarini
saqlaydi, shuning uchun normalizatsiya qanchalik to'g'ri tiklaganini aniq
o'lchash mumkin.

Ishlatish:
    python3 scripts/make_photo.py kirish.png chiqish.jpg --seed 7
    python3 scripts/make_photo.py --synthetic chiqish.jpg     # rentgensiz sinov
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import cv2
import numpy as np


def synthetic_xray(w: int = 900, h: int = 1100) -> np.ndarray:
    """Rentgen o'rniga shartli ko'krak qafasi tasviri - quvurni sinash uchun."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h / 2

    def blob(px, py, rx, ry, amp):
        return amp * np.exp(-(((xx - px) / rx) ** 2 + ((yy - py) / ry) ** 2))

    img = np.full((h, w), 70.0, np.float32)
    img += blob(cx, cy * 0.22, w * 0.42, h * 0.16, 70)     # yelka to'qimalari
    img += blob(cx, cy * 0.95, w * 0.05, h * 0.34, 95)     # umurtqa
    img -= blob(cx - w * 0.19, cy * 0.88, w * 0.15, h * 0.24, 60)  # chap o'pka
    img -= blob(cx + w * 0.19, cy * 0.88, w * 0.15, h * 0.24, 60)  # o'ng o'pka
    img += blob(cx, h * 0.80, w * 0.34, h * 0.09, 80)      # diafragma

    for i in range(9):                                      # qovurg'alar
        img += blob(cx, h * (0.22 + i * 0.055), w * 0.46, h * 0.008, 26)

    return np.clip(img, 0, 255).astype(np.uint8)


def make_photo(xray: np.ndarray, rng: random.Random,
               glare_level: float = 1.0) -> tuple[np.ndarray, dict]:
    """Plyonkani negatoskopga qo'yib telefonda suratga olishni taqlid qiladi."""
    h, w = xray.shape[:2]

    # 1. Plyonka atrofida qorong'u fon - negatoskop ramkasi va xona
    pad_x, pad_y = int(w * 0.22), int(h * 0.18)
    canvas_w, canvas_h = w + pad_x * 2, h + pad_y * 2
    canvas = np.full((canvas_h, canvas_w), 14, np.uint8)
    canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
    canvas[pad_y:pad_y + h, pad_x:pad_x + w] = cv2.cvtColor(xray, cv2.COLOR_GRAY2BGR)

    # Plyonka chekkasidagi yorug' hoshiya
    cv2.rectangle(canvas, (pad_x - 3, pad_y - 3), (pad_x + w + 3, pad_y + h + 3),
                  (120, 124, 128), 3)

    # 2. Perspektiv buzilish - telefon tik ushlanmagan
    src = np.float32([[pad_x, pad_y], [pad_x + w, pad_y],
                      [pad_x + w, pad_y + h], [pad_x, pad_y + h]])
    jitter = min(canvas_w, canvas_h) * 0.055
    dst = src + np.float32([[rng.uniform(-jitter, jitter) for _ in range(2)]
                            for _ in range(4)])
    M = cv2.getPerspectiveTransform(src, dst)
    photo = cv2.warpPerspective(canvas, M, (canvas_w, canvas_h),
                                borderValue=(14, 14, 14))

    # 4. Kamera nuqsonlari: yengil xiralik, shovqin, vinyetka
    k = rng.choice([3, 5])
    photo = cv2.GaussianBlur(photo, (k, k), 0)
    photo = np.clip(photo.astype(np.int16) +
                    rng.uniform(2, 6) * np.random.randn(canvas_h, canvas_w, 3),
                    0, 255).astype(np.uint8)

    vy, vx = np.mgrid[0:canvas_h, 0:canvas_w].astype(np.float32)
    r = np.sqrt(((vx - canvas_w / 2) / (canvas_w / 2)) ** 2 +
                ((vy - canvas_h / 2) / (canvas_h / 2)) ** 2)
    vignette = (1 - 0.28 * np.clip(r, 0, 1.4) ** 2)[..., None]
    photo = np.clip(photo.astype(np.float32) * vignette, 0, 255).astype(np.uint8)

    # 5. Yorug'lik aksi - obyektiv oldidagi shishada, shuning uchun vinyetkadan
    # KEYIN qo'yiladi va sensorni to'yintiradi (real fotoda ham shunday)
    glare = np.zeros((canvas_h, canvas_w), np.float32)
    gx = int(rng.uniform(0.18, 0.62) * canvas_w)
    gy = int(rng.uniform(0.15, 0.55) * canvas_h)
    axes = (int(canvas_w * rng.uniform(0.10, 0.18) * glare_level),
            int(canvas_h * rng.uniform(0.07, 0.13) * glare_level))
    cv2.ellipse(glare, (gx, gy), axes, rng.uniform(0, 180), 0, 360, 1.0, -1)
    glare = cv2.GaussianBlur(glare, (0, 0), sigmaX=canvas_w * 0.035)
    photo = np.clip(photo.astype(np.float32) + glare[..., None] * 320,
                    0, 255).astype(np.uint8)

    truth = {
        "corners": dst.tolist(),           # plyonkaning haqiqiy burchaklari
        "glare_center": [gx, gy],
        "canvas": [canvas_w, canvas_h],
        "film": [w, h],
    }
    return photo, truth


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", type=Path, help="Toza rentgen rasmi")
    ap.add_argument("output", type=Path)
    ap.add_argument("--synthetic", action="store_true", help="Rentgensiz shartli tasvir")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--glare", type=float, default=1.0,
                    help="Aks kuchi: 0.3 yengil, 1.0 kuchli")
    args = ap.parse_args()

    if args.synthetic or args.source is None:
        xray = synthetic_xray()
    else:
        xray = cv2.imread(str(args.source), cv2.IMREAD_GRAYSCALE)
        if xray is None:
            print(f"Rasm o'qilmadi: {args.source}")
            return 1

    photo, truth = make_photo(xray, random.Random(args.seed), args.glare)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.output), photo, [cv2.IMWRITE_JPEG_QUALITY, 88])
    args.output.with_suffix(".truth.json").write_text(json.dumps(truth, indent=2))

    print(f"Yozildi: {args.output}  ({photo.shape[1]}x{photo.shape[0]})")
    print(f"Haqiqiy burchaklar: {args.output.with_suffix('.truth.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
