#!/usr/bin/env python3
"""Faza 1.1/1.2 sinovi.

Sun'iy fotolarda quvurni ishga tushiradi va normalizatsiya haqiqiy burchaklarni
qanchalik to'g'ri tiklaganini o'lchaydi (truth.json bilan solishtirib).
"""
import json, sys
from pathlib import Path

sys.path.insert(0, "/app")

import cv2
import numpy as np
from app.pipeline import assess, find_film, normalize

out = Path("/data/test/out"); out.mkdir(parents=True, exist_ok=True)

for photo in sorted(Path("/data/test").glob("*.jpg")):
    img = cv2.imread(str(photo))
    quad = find_film(img)
    norm = normalize(img, quad)
    q = assess(norm)

    # Aniqlangan burchaklarni haqiqiysi bilan solishtirish
    err = "—"
    truth_file = photo.with_suffix(".truth.json")
    if quad is not None and truth_file.exists():
        truth = np.float32(json.loads(truth_file.read_text())["corners"])
        # truth tartibi tl,tr,br,bl - detect ham shunday qaytaradi
        d = np.linalg.norm(quad.corners - truth, axis=1)
        err = f"{d.mean():.1f} px (max {d.max():.1f})"

    cv2.imwrite(str(out / f"{photo.stem}_norm.png"), norm.image)

    print(f"\n{photo.name}")
    print(f"  plyonka topildi : {'ha' if quad else 'YO`Q'}"
          + (f"  ({quad.area_ratio:.0%} kadr, {quad.angle_deg:+.1f}°)" if quad else ""))
    print(f"  burchak xatosi  : {err}")
    print(f"  o'tkirlik       : {q.sharpness}")
    print(f"  yorug'lik aksi  : {q.glare:.4f}")
    print(f"  o'pka maydoni   : {q.lung_field}")
    print(f"  tiklangan aks   : {norm.glare_fixed:.4f}")
    print(f"  natija          : {'O`TDI' if q.passed else 'RAD: ' + '; '.join(q.reasons)}")
    print(f"  chiqish         : {norm.image.shape[1]}x{norm.image.shape[0]}")
