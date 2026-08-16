# Test rasmlari (Faza 0.5)

Bu papka **git da saqlanmaydi** (`.gitignore` da). Har bir jamoa a’zosi o’zi tayyorlaydi.

## Qaysi to’plam

**Shenzhen (ChinaSet)** — NLM ning ochiq ko’krak qafasi rentgeni to’plami, 662 ta rasm.
Yorliq fayl nomida turadi:

```
CHNCXR_0001_0.png    →  _0  norma
CHNCXR_0327_1.png    →  _1  sil belgilari bor
```

Yaʼni "natijasi ma’lum" sharti bajariladi va model aniqligini o’lchash mumkin.

```bash
curl -L -o chinaset.zip https://openi.nlm.nih.gov/imgs/collections/ChinaSet_AllFiles.zip
```

Muqobil: **Montgomery** (138 rasm) va **NIH ChestX-ray14** (umumiy patologiya, ancha katta).

## Namuna tayyorlash

```bash
python3 scripts/prepare_samples.py data/chinaset.zip --count 30
```

Skript teng nisbatda (yarmi norma, yarmi sil) `data/samples/` ga chiqaradi va
`data/samples/labels.csv` yozadi.

## ⚠️ Eng muhim qadam — rasmlarni telefonda suratga oling

Yuklangan rasmlar **toza raqamli tasvirlar**. Bizning mahsulotimiz esa ular bilan
ishlamaydi — u **negatoskopdagi plyonkaning telefon fotosi** bilan ishlaydi.

Shuning uchun Faza 1 aynan quyidagicha tayyorlangan rasmlarda sinaladi:

1. Rasmni noutbuk ekranida to’liq ochib, xonani biroz qorong’ilashtiring
2. Telefonda suratga oling — **ataylab ideal qilmang**:
   - bir nechtasini qiyshiq oling
   - bir nechtasida ekran yorug’ligi aks etsin
   - bir nechtasi biroz xira chiqsin
3. Natijani `data/samples/photos/` ga soling, nomini asl fayl bilan bir xil qoldiring

**Nega bu shart.** Barcha ochiq modellar toza DICOM bor deb faraz qiladi. Faza 1.2
(plyonka fotosi normalizatsiyasi) — loyihaning texnik yadrosi va u aynan shu
"yomon" rasmlarda ishlashi kerak. Toza rasmlarda sinasangiz, xakatonda hammasi
ishlaydi, real sharoitda esa yiqiladi.

Kamida **10 tasi qiyshiq va aks etgan** bo’lsin. Ular eng qimmatli test namunalari.

## Papka tuzilmasi

```
data/
├── chinaset.zip          yuklangan arxiv
├── samples/              ajratilgan toza rasmlar
│   ├── labels.csv        fayl nomi, yorliq
│   └── *.png
└── samples/photos/       telefonda olingan fotolar  ← Faza 1 shular bilan ishlaydi
```
