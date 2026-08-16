# ShifokorAI

Qishloqdagi rentgen suratini shifokorga yetkazadi.

Hamshira negatoskopdagi plyonkani oddiy telefon kamerasida suratga oladi → sun’iy intellekt
tasvirni tahlil qilib xavf bo’yicha saralaydi → faqat shubhali holatlar viloyat mutaxassisiga
boradi → yakuniy tashxisni shifokor qo’yadi.

Umummilliy AI Xakaton, Qarshi bosqichi — **13-yo’nalish: Hududiy SI-Mobil Diagnostika**.

Bosqichlar: [PHASE.md](PHASE.md) · API kontrakti: [docs/api.md](docs/api.md)

## Papkalar

| Papka | Nima | Kim |
|---|---|---|
| `api/` | FastAPI backend | 2-kishi |
| `ai/` | Tasvir quvuri: normalizatsiya, model, heatmap | 1-kishi |
| `mobile/` | Hamshira ilovasi — React Native (Expo) | 3-kishi |
| `panel/` | Shifokor paneli — React + Vite | 4-kishi |
| `infra/` | Docker fayllari | 2-kishi |
| `docs/` | API kontrakti va qaror yozuvlari | hamma |
| `data/` | Test rasmlari (git da saqlanmaydi) | 5-kishi |

## Ishga tushirish

### Portlar

Loyiha **18300-18305** blokida ishlaydi. Ular ataylab standart emas — kompyuteringizdagi
boshqa loyihalarga (8000, 8080, 5432, 9000) xalaqit qilmasligi uchun.

| Port | Nima |
|---|---|
| `18300` | Backend (api) |
| `18301` | AI xizmati |
| `18302` | PostgreSQL |
| `18303` | MinIO S3 |
| `18304` | MinIO brauzer konsoli |
| `18305` | Expo Metro bundler |

### 1. Backend, AI, baza va fayl saqlash — Docker

```bash
docker compose up -d
```

Tekshirish:

```bash
curl http://localhost:18300/health
```

### 2. Hamshira ilovasi — Docker emas, to’g’ridan-to’g’ri

Expo Go telefondan Metro bundlerga LAN orqali ulanadi, shuning uchun u konteynerda ishlatilmaydi.

```bash
cd mobile && npm start
```

Port `package.json` da yozilgan (`--port 18305`), qo’lda ko’rsatish shart emas.

### 3. Shifokor paneli

```bash
cd panel && npm run dev
```

Panel Faza 4 da quriladi.

## Telefonni ulash

Telefon `localhost` ni ko’rmaydi — u noutbukning o’zi emas. Noutbukning LAN IP sini oling:

```bash
ipconfig getifaddr en0
```

Chiqqan manzilni `mobile/.env` ga yozing:

```
EXPO_PUBLIC_API_URL=http://192.168.1.42:18300
```

`.env` o’zgarsa Expo ni qayta ishga tushiring — `EXPO_PUBLIC_*` bundle paytida yoziladi.

**Wi-Fi qurilmalar orasini bloklasa:** telefondan hotspot tarqating va noutbukni shunga ulang.
Yoki `npx expo start --port 18305 --tunnel` (sekinroq).

## Qoidalar

- Yangi endpoint qo’shilsa, avval `docs/api.md` yangilanadi, keyin kod yoziladi
- O’zbekcha matnda apostrof faqat `’` (U+2019). `ʻ` (U+02BB) ko’p shriftda buziladi
- Model vaznlari va test rasmlari git ga qo’shilmaydi
- AI hech qachon tashxis qo’ymaydi — u faqat saralaydi, qarorni shifokor qabul qiladi
