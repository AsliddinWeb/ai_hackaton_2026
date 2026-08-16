"""Faza 1.2 - plyonka fotosini normalizatsiya qilish. Loyihaning texnik yadrosi.

Barcha ochiq modellar toza DICOM bor deb faraz qiladi. Bizda esa telefonda
olingan foto: qiyshiq, yorug'lik aks etgan, fon aralashgan, vinyetkali.

Ketma-ketlik:
    1. Plyonka chegarasini topish        (detect.find_film)
    2. Perspektivni tuzatish             - qiyshiqlikni yo'qotadi
    3. Yorug'lik aksini maskalash        - yonib ketgan sohalarni tiklaydi
    4. Kontrastni normallashtirish       - CLAHE
    5. O'pka sohasini kesish             - modelga faqat kerakli qism boradi
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .detect import Quad, find_film
from .glare import MAX_REPAIRABLE, glare_mask

# Model kirishi. torchxrayvision 224x224 kutadi, lekin biz kattaroq saqlaymiz -
# issiqlik xaritasi aniqroq chiqadi va shifokor kattalashtira oladi.
OUTPUT_SIZE = 1024


@dataclass
class Normalized:
    image: np.ndarray          # tekislangan, kontrasti tuzatilgan kulrang tasvir
    quad: Quad | None          # topilgan plyonka chegarasi
    glare_fixed: float         # tiklangan yorug'lik aksi ulushi
    warped: bool               # perspektiv tuzatildimi


def _target_size(corners: np.ndarray) -> tuple[int, int]:
    """Plyonkaning haqiqiy nisbatini chekka uzunliklaridan hisoblaydi."""
    tl, tr, br, bl = corners
    width = max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl))
    height = max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))
    if width < 1 or height < 1:
        return OUTPUT_SIZE, OUTPUT_SIZE

    ratio = height / width
    if ratio >= 1:
        return int(OUTPUT_SIZE / ratio), OUTPUT_SIZE
    return OUTPUT_SIZE, int(OUTPUT_SIZE * ratio)


def unwarp(image: np.ndarray, quad: Quad) -> np.ndarray:
    """Qiyshiq plyonkani to'g'ri to'rtburchakka keltiradi."""
    w, h = _target_size(quad.corners)
    dst = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
    M = cv2.getPerspectiveTransform(quad.corners, dst)
    return cv2.warpPerspective(image, M, (w, h), flags=cv2.INTER_CUBIC)


def remove_glare(gray: np.ndarray) -> tuple[np.ndarray, float]:
    """Yonib ketgan sohalarni atrofdagi to'qimadan tiklaydi."""
    hot, ratio = glare_mask(gray)
    if ratio < 0.0005:
        return gray, 0.0

    if ratio > MAX_REPAIRABLE:
        # Juda katta - tiklamaymiz. Yolg'on to'qima chizishdan ko'ra rasmni
        # o'z holida qoldirib, sifat darvozasiga rad ettirgan ma'qul.
        return gray, ratio

    # Chekkalarini ham qamrash uchun biroz kengaytiriladi
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    hot = cv2.dilate(hot, k, iterations=2)
    fixed = cv2.inpaint(gray, hot, 7, cv2.INPAINT_TELEA)
    return fixed, ratio


def enhance(gray: np.ndarray) -> np.ndarray:
    """Kontrastni tekislaydi.

    Telefon fotosida yorug'lik notekis tushadi - bir chekka yorug', ikkinchisi
    qorong'u. CLAHE buni mahalliy ravishda tuzatadi va o'pka to'qimasi
    ko'rinadigan bo'ladi.
    """
    # Notekis yoritishni olib tashlash: katta blur bilan bo'lish
    background = cv2.GaussianBlur(gray, (0, 0), sigmaX=gray.shape[1] * 0.06)
    flat = cv2.divide(gray, background, scale=128)

    clahe = cv2.createCLAHE(clipLimit=2.4, tileGridSize=(8, 8))
    return clahe.apply(flat)


def crop_lung_field(gray: np.ndarray, margin: float = 0.04) -> np.ndarray:
    """Plyonka chekkasidagi hoshiya va yozuvlarni kesib tashlaydi."""
    h, w = gray.shape[:2]
    mx, my = int(w * margin), int(h * margin)
    return gray[my:h - my, mx:w - mx]


def normalize(image: np.ndarray, quad: Quad | None = None) -> Normalized:
    """To'liq quvur: foto -> modelga tayyor tasvir."""
    if quad is None:
        quad = find_film(image)

    if quad is not None:
        work = unwarp(image, quad)
        warped = True
    else:
        # Chegara topilmasa ham to'xtamaymiz - qolgan bosqichlar baribir foyda beradi.
        # Lekin sifat darvozasi buni allaqachon belgilagan bo'ladi.
        work = image
        warped = False

    gray = cv2.cvtColor(work, cv2.COLOR_BGR2GRAY) if work.ndim == 3 else work
    gray, glare_fixed = remove_glare(gray)
    gray = enhance(gray)
    gray = crop_lung_field(gray)

    return Normalized(image=gray, quad=quad, glare_fixed=glare_fixed, warped=warped)
