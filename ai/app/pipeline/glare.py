"""Yorug'lik aksini aniqlash.

Mutlaq yorqinlik bo'yicha aniqlab bo'lmaydi. Sabab ikkita:
  - foto umuman qorong'u bo'lishi mumkin, lekin bir joyi yonib ketgan
  - suyak to'qimasi ham yorug' - uni aks deb hisoblash xato

To'g'ri belgi: **yorug' VA teksturasi yo'qolgan** soha. Yonib ketgan joyda
sensor to'yingan, shuning uchun u tekis bo'ladi. Suyakda esa tafsilot qoladi.
"""

from __future__ import annotations

import cv2
import numpy as np

# Yorqinlik chegarasi rasmning o'ziga nisbatan hisoblanadi
BRIGHT_FRACTION = 0.82   # median va maksimum orasidagi nuqta
BRIGHT_FLOOR = 150       # bundan pastda aks bo'lishi mumkin emas
FLAT_STD = 5.0           # mahalliy og'ish shundan past bo'lsa - tekstura yo'q
WINDOW = 9               # mahalliy og'ish oynasi

# Tiklash chegarasi. Bundan katta aksni inpaint qayta tiklay olmaydi -
# u to'qima o'rniga tekis yorug' dog' qoldiradi va bu MODELNI CHALG'ITADI.
# Shuning uchun katta aks tiklanmaydi, sifat darvozasi uni rad etadi.
MAX_REPAIRABLE = 0.02


def _local_std(gray: np.ndarray, k: int = WINDOW) -> np.ndarray:
    """Har bir piksel atrofidagi standart og'ish - tekstura o'lchovi."""
    f = gray.astype(np.float32)
    mean = cv2.boxFilter(f, -1, (k, k), normalize=True)
    mean_sq = cv2.boxFilter(f * f, -1, (k, k), normalize=True)
    return np.sqrt(np.clip(mean_sq - mean * mean, 0, None))


def glare_mask(gray: np.ndarray) -> tuple[np.ndarray, float]:
    """Yonib ketgan sohalar maskasi va ularning ulushi."""
    median = float(np.median(gray))
    top = float(np.percentile(gray, 99.7))
    threshold = max(BRIGHT_FLOOR, median + BRIGHT_FRACTION * (top - median))

    bright = gray >= threshold
    flat = _local_std(gray) < FLAT_STD
    mask = (bright & flat).astype(np.uint8) * 255

    # Mayda nuqtalarni olib tashlash - aks har doim blok bo'lib turadi
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

    return mask, float(np.count_nonzero(mask) / mask.size)
