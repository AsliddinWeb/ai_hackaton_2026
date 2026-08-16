"""Faza 1.1 - sifat darvozasi.

Qoida: sifat past bo'lsa model UMUMAN ishlamaydi. Yomon fotodan chiqqan
ishonchli ko'rinadigan xato - eng xavfli ssenariy.

Chiqish shakli docs/api.md dagi `quality` obyektiga mos keladi.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import cv2
import numpy as np

from .glare import MAX_REPAIRABLE
from .normalize import Normalized

# Chegaralar. Real fotolarda kalibrovka qilinadi (Faza 1 oxirida).
MIN_SHARPNESS = 0.35   # undan past - xira
MAX_GLARE = MAX_REPAIRABLE   # tiklab bo'lmaydigan aks - rad etiladi
MAX_ANGLE = 12.0       # gradus
MIN_FILM_AREA = 0.12   # plyonka kadrning shuncha qismini egallashi kerak


@dataclass
class Quality:
    sharpness: float
    glare: float
    angle_deg: float
    lung_field: str          # "full" | "partial" | "none"
    passed: bool
    reasons: list[str]       # nega o'tmadi - foydalanuvchiga ko'rsatiladi

    def to_dict(self) -> dict:
        return asdict(self)


def measure_sharpness(gray: np.ndarray) -> float:
    """Laplasian dispersiyasi - klassik xiralik o'lchovi.

    Qiymat 0..1 ga keltiriladi. 500 - tajribaviy to'yinish nuqtasi:
    undan yuqorisi inson ko'zi uchun baribir "o'tkir".
    """
    var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return float(min(var / 500.0, 1.0))


def measure_glare(gray: np.ndarray) -> float:
    """Yonib ketgan sohalar ulushi.

    Faqat yorug' piksellar emas - ular BLOK bo'lib turishi kerak.
    Aks holda oq suyak to'qimasi ham "aks etish" deb hisoblanardi.
    """
    _, hot = cv2.threshold(gray, 246, 255, cv2.THRESH_BINARY)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    hot = cv2.morphologyEx(hot, cv2.MORPH_OPEN, k)
    return float(np.count_nonzero(hot) / hot.size)


def measure_lung_field(gray: np.ndarray) -> str:
    """O'pka maydonlari kadr ichidami.

    O'pka - havoli, ya'ni rentgenda QORONG'U. Rasm o'rtasining chap va o'ng
    choragida qorong'u sohalar bo'lishi kerak. Bu qo'pol tekshiruv;
    aniq segmentatsiya Faza 1.5 da.
    """
    h, w = gray.shape[:2]
    band = gray[int(h * 0.25):int(h * 0.70), :]
    left = band[:, int(w * 0.12):int(w * 0.42)]
    right = band[:, int(w * 0.58):int(w * 0.88)]

    mid = float(np.median(gray))
    found = sum(1 for side in (left, right) if float(np.median(side)) < mid * 0.92)

    return {2: "full", 1: "partial", 0: "none"}[found]


def assess(norm: Normalized) -> Quality:
    """Normalizatsiyadan KEYINGI tasvirni baholaydi.

    Nega keyin. Xom fotoda o'lchov noto'g'ri chiqadi: kadrning yarmi qorong'u
    fon, yorug'lik notekis, plyonka qiyshiq. Bularning hammasi normalizatsiyada
    yo'qoladi va shundan keyingina "bu tasvir modelga yaroqlimi" degan savolga
    javob berish mumkin.

    Yorug'lik aksi esa normalizatsiya ichida O'LCHANADI va tiklanadi - shuning
    uchun u tayyor qiymat sifatida keladi.
    """
    gray = norm.image
    quad = norm.quad

    sharpness = measure_sharpness(gray)
    glare = norm.glare_fixed
    lung = measure_lung_field(gray)
    angle = abs(quad.angle_deg) if quad else 0.0

    reasons: list[str] = []
    if quad is None:
        reasons.append("Plyonka chegarasi topilmadi")
    elif quad.area_ratio < MIN_FILM_AREA:
        reasons.append("Plyonka juda kichik - yaqinroq keling")
    if sharpness < MIN_SHARPNESS:
        reasons.append("Rasm xira - telefonni qimirlatmasdan qayta oling")
    if glare > MAX_GLARE:
        reasons.append("Yorug'lik aks etyapti - telefonni chapga suring")
    if angle > MAX_ANGLE:
        reasons.append("Telefon qiyshiq - to'g'ri ushlang")
    if lung == "none":
        reasons.append("O'pka maydoni topilmadi")

    return Quality(
        sharpness=round(sharpness, 3),
        glare=round(glare, 4),
        angle_deg=round(quad.angle_deg if quad else 0.0, 1),
        lung_field=lung,
        passed=not reasons,
        reasons=reasons,
    )
