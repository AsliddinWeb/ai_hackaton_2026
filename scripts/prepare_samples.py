#!/usr/bin/env python3
"""Shenzhen (ChinaSet) arxividan teng nisbatda test namunalarini ajratadi.

Ishlatish:
    python3 scripts/prepare_samples.py data/chinaset.zip --count 30

Yorliq fayl nomida turadi: CHNCXR_0001_0.png -> 0 (norma), _1 -> sil belgilari.
Natija data/samples/ ga tushadi va labels.csv yoziladi.
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import zipfile
from pathlib import Path

NAME_RE = re.compile(r"CHNCXR_(\d+)_([01])\.png$", re.IGNORECASE)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path, help="ChinaSet_AllFiles.zip yo'li")
    ap.add_argument("--count", type=int, default=30, help="Nechta rasm (teng bo'linadi)")
    ap.add_argument("--out", type=Path, default=Path("data/samples"))
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    if not args.archive.exists():
        print(f"Arxiv topilmadi: {args.archive}")
        print("Yuklash: curl -L -o data/chinaset.zip "
              "https://openi.nlm.nih.gov/imgs/collections/ChinaSet_AllFiles.zip")
        return 1

    with zipfile.ZipFile(args.archive) as z:
        entries: dict[str, list[str]] = {"0": [], "1": []}
        for name in z.namelist():
            m = NAME_RE.search(name)
            if m:
                entries[m.group(2)].append(name)

        if not entries["0"] or not entries["1"]:
            print("Arxivda kutilgan nomdagi rasmlar topilmadi.")
            print("Fayllar CHNCXR_0001_0.png ko'rinishida bo'lishi kerak.")
            return 1

        rng = random.Random(args.seed)
        half = args.count // 2
        chosen: list[tuple[str, str]] = []
        for label, names in entries.items():
            take = min(half, len(names))
            chosen += [(n, label) for n in rng.sample(sorted(names), take)]
        rng.shuffle(chosen)

        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "photos").mkdir(exist_ok=True)

        rows = []
        for src, label in chosen:
            dst = args.out / Path(src).name
            dst.write_bytes(z.read(src))
            rows.append({"file": dst.name,
                         "label": label,
                         "meaning": "sil belgilari" if label == "1" else "norma"})

    with (args.out / "labels.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "label", "meaning"])
        w.writeheader()
        w.writerows(rows)

    n1 = sum(1 for r in rows if r["label"] == "1")
    print(f"Ajratildi: {len(rows)} ta rasm ({n1} sil, {len(rows) - n1} norma) -> {args.out}")
    print()
    print("KEYINGI QADAM — buni o'tkazib yubormang:")
    print("  Rasmlarni noutbuk ekranida ochib, TELEFONDA suratga oling.")
    print("  Ataylab bir nechtasi qiyshiq, aks etgan va xira bo'lsin.")
    print(f"  Natijani {args.out / 'photos'} ga soling.")
    print("  Faza 1 aynan shu fotolarda sinaladi, toza rasmlarda emas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
