"""Plyonka chegarasini topish.

Fotoda plyonka qorong'u fon ustida turadi va negatoskop uni orqadan yoritadi.
Shuning uchun eng ishonchli belgi - yorug' to'rtburchak soha.

Bu modul 1.1 (burchakni o'lchash) va 1.2 (perspektivni tuzatish) uchun umumiy.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .glare import glare_mask

# Plyonka kadrning kamida shuncha qismini egallashi kerak.
# Undan kichigi - tasodifiy yorug' dog', plyonka emas.
MIN_AREA_RATIO = 0.12

# Aniqlash uchun rasm shu kenglikka kichraytiriladi - tezlik uchun.
WORK_WIDTH = 900

# Plyonka nisbati shu oraliqda bo'lishi kerak. Aks etish dog'i odatda
# cho'zinchoq yoki juda kichik bo'ladi va shu filtrdan o'tmaydi.
ASPECT_RANGE = (0.55, 1.85)


@dataclass(frozen=True)
class Quad:
    """Plyonkaning to'rt burchagi, asl rasm koordinatalarida."""

    corners: np.ndarray  # (4,2) float32, tartibi: tl, tr, br, bl
    area_ratio: float    # kadrning necha qismini egallaydi
    angle_deg: float     # yuqori chekkaning gorizontalga nisbatan burchagi

    @property
    def as_list(self) -> list[list[float]]:
        return self.corners.tolist()


def order_corners(pts: np.ndarray) -> np.ndarray:
    """Burchaklarni tl, tr, br, bl tartibiga keltiradi."""
    pts = pts.reshape(4, 2).astype(np.float32)
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.float32([
        pts[np.argmin(s)],  # tl - yig'indisi eng kichik
        pts[np.argmin(d)],  # tr - farqi eng kichik
        pts[np.argmax(s)],  # br
        pts[np.argmax(d)],  # bl
    ])


def find_film(image: np.ndarray) -> Quad | None:
    """Fotodagi plyonka to'rtburchagini topadi. Topilmasa None."""
    h, w = image.shape[:2]
    scale = WORK_WIDTH / max(w, 1)
    small = cv2.resize(image, (WORK_WIDTH, int(h * scale))) if scale < 1 else image.copy()
    inv = 1.0 / scale if scale < 1 else 1.0

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY) if small.ndim == 3 else small

    # MUHIM: yorug'lik aksini avval so'ndirish kerak.
    # Aks to'yingan (255) bo'ladi va Otsu chegarasini o'ziga tortadi - natijada
    # detektor plyonka o'rniga aks dog'ini topadi. Shuning uchun aks piksellari
    # rasmning median yorqinligi bilan almashtiriladi.
    hot, hot_ratio = glare_mask(gray)
    if hot_ratio > 0.0005:
        gray = gray.copy()
        gray[hot > 0] = np.uint8(np.median(gray))

    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    # Plyonka fondan yorug'roq - Otsu chegarasi ularni ajratadi
    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Teshiklarni yopish va mayda shovqinni olib tashlash
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    frame_area = small.shape[0] * small.shape[1]
    best: tuple[float, np.ndarray] | None = None

    for c in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        area = cv2.contourArea(c)
        if area / frame_area < MIN_AREA_RATIO:
            break

        # To'rtburchakka yaqinlashtirish
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) != 4:
            # To'rtburchak chiqmasa - minimal aylantirilgan to'rtburchakka tushamiz
            approx = cv2.boxPoints(cv2.minAreaRect(c)).astype(np.int32).reshape(-1, 1, 2)

        if not cv2.isContourConvex(approx.reshape(-1, 2).astype(np.int32)):
            continue

        # Nisbat tekshiruvi - plyonka emas, tasodifiy dog' bo'lmasin
        pts = order_corners(approx.astype(np.float32))
        width = max(np.linalg.norm(pts[1] - pts[0]), np.linalg.norm(pts[2] - pts[3]))
        height = max(np.linalg.norm(pts[3] - pts[0]), np.linalg.norm(pts[2] - pts[1]))
        if width < 1 or height < 1:
            continue
        if not (ASPECT_RANGE[0] <= height / width <= ASPECT_RANGE[1]):
            continue

        best = (area / frame_area, approx)
        break

    if best is None:
        return None

    area_ratio, approx = best
    corners = order_corners(approx.astype(np.float32)) * inv

    # Yuqori chekka burchagi - telefon qanchalik qiyshiq ushlangani
    tl, tr = corners[0], corners[1]
    angle = float(np.degrees(np.arctan2(tr[1] - tl[1], tr[0] - tl[0])))

    return Quad(corners=corners, area_ratio=float(area_ratio), angle_deg=angle)
