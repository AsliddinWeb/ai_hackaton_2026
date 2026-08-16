# API kontrakti

**Asos:** `http://<LAN-IP>:8000` · Format: JSON · Autentifikatsiya: `Authorization: Bearer <token>`

Bu hujjat kelishuv. Yangi endpoint kerak bo’lsa — avval shu yerga yoziladi, keyin kod.
Mobil ilova va panel shu kontrakt bo’yicha **soxta ma’lumot** bilan ishlashni boshlaydi va
backendni kutmaydi.

**Konvensiya:** JSON kalitlari inglizcha, foydalanuvchi ko’radigan yozuvlar o’zbekcha.
Sanalar ISO 8601, vaqt UTC (`2026-08-16T09:41:00Z`).

---

## Asosiy tushunchalar

**Xavf darajasi** — `high` · `medium` · `low` · `pending`. Ilovada mos ranglar: qizil, sariq, yashil, kulrang.

**Topilma (finding)** — modelning bitta xulosasi. Har doim anatomik joy bilan birga:

```json
{ "code": "infiltration", "label": "Infiltrat", "location": "O'ng o'pka, yuqori bo'lak",
  "probability": 0.87, "severity": "high" }
```

**Sifat (quality)** — qurilmada va serverda hisoblangan to’rt ko’rsatkich:

```json
{ "sharpness": 0.94, "glare": 0.02, "angle_deg": 1.4, "lung_field": "full", "passed": true }
```

`passed: false` bo’lsa model **umuman ishlamaydi**. Sifatsiz rasmdan chiqqan ishonchli
ko’rinadigan xato — eng xavfli ssenariy.

**Keys holati** — `draft` · `queued` · `analyzing` · `awaiting_doctor` · `confirmed` · `rejected`.

---

## 0. Salomatlik

### `GET /health`

Autentifikatsiya kerak emas. **Faza 0.4 shu endpoint bilan yopiladi.**

```json
{ "status": "ok", "version": "0.1.0", "time": "2026-08-16T09:41:00Z",
  "services": { "db": "ok", "storage": "ok", "ai": "ok" } }
```

`services` — bog’liq konteynerlar holati. Docker da nima ishlamayotganini darrov ko’rsatadi.

---

## 1. Autentifikatsiya

### `POST /auth/login`

```json
{ "phone": "+998912345678", "code": "12345" }
```

```json
{
  "token": "eyJhbGci...",
  "user": {
    "id": 3, "full_name": "Saidova Nigora", "role": "nurse",
    "facility": { "id": 42, "name": "QVP-042", "district": "Kasbi tumani" }
  }
}
```

`role`: `nurse` · `specialist` · `admin`. Demo rejimida `code` tekshirilmaydi.

### `GET /auth/me` → yuqoridagi `user` obyekti

---

## 2. Bemorlar

### `GET /patients?q=&page=&page_size=`

```json
{
  "items": [
    { "id": 91, "full_name": "Rahmonov Sherzod", "age": 54, "sex": "male",
      "last_case_at": "2026-08-16T09:12:00Z", "last_risk": "high" }
  ],
  "total": 128, "page": 1, "page_size": 20
}
```

### `POST /patients`

```json
{ "full_name": "Rahmonov Sherzod Aliyevich", "birth_date": "1971-04-12",
  "sex": "male", "phone": "+998901112233", "address": "Muglon QFY" }
```

### `GET /patients/{id}` → bemor va uning keyslari ro’yxati

---

## 3. Keyslar

### `POST /cases`

Anamnez bilan yangi keys ochiladi. Rasm keyin yuklanadi.

```json
{
  "patient_id": 91,
  "complaints": ["cough", "night_fever", "sweating"],
  "cough_duration_days": 21,
  "tb_contact": "yes",
  "note": null,
  "client_id": "a3f2-91b7-...-4c8e"
}
```

| Maydon | Qiymatlar |
|---|---|
| `complaints` | `cough` · `night_fever` · `dyspnea` · `weight_loss` · `sweating` · `chest_pain` |
| `tb_contact` | `yes` · `no` · `unknown` |
| `client_id` | UUID, oflayn navbat uchun — takroriy yuborishni oldini oladi |

```json
{ "id": 507, "status": "draft", "patient": { "id": 91, "full_name": "Rahmonov Sherzod" },
  "created_at": "2026-08-16T09:10:00Z" }
```

### `POST /cases/{id}/images`

Rasm yuklash. Katta fayl bo’laklab yuboriladi.

`Content-Type: multipart/form-data`

| Maydon | Nima |
|---|---|
| `file` | Rasm bo’lagi |
| `client_id` | Keysdagi bilan bir xil UUID |
| `chunk_index`, `chunk_total` | Bo’lak raqami. Uzilsa qoldig’idan davom etadi |
| `device_quality` | Qurilmada hisoblangan sifat, JSON matn |

Oxirgi bo’lak kelgach keys `queued` ga o’tadi va AI navbatiga tushadi.

```json
{ "image_id": 880, "case_status": "queued", "received_chunks": 4, "expected_chunks": 4 }
```

### `GET /cases?risk=&status=&page=`

```json
{
  "items": [
    {
      "id": 507,
      "patient": { "id": 91, "full_name": "Rahmonov Sherzod", "age": 54 },
      "risk": "high",
      "risk_score": 0.87,
      "top_finding": "O'ng yuqori sohada infiltrat",
      "status": "awaiting_doctor",
      "created_at": "2026-08-16T09:12:00Z",
      "age_minutes": 12,
      "sla_breached": false,
      "facility": { "id": 42, "name": "QVP-042", "district": "Kasbi tumani" }
    }
  ],
  "total": 43, "page": 1, "page_size": 20
}
```

### `GET /cases/{id}`

```json
{
  "id": 507,
  "patient": { "id": 91, "full_name": "Rahmonov Sherzod", "age": 54, "sex": "male" },
  "anamnesis": {
    "complaints": ["cough", "night_fever", "sweating"],
    "cough_duration_days": 21, "tb_contact": "yes"
  },
  "images": [
    { "id": 880,
      "original_url": "/files/880/original.jpg",
      "normalized_url": "/files/880/normalized.png",
      "heatmap_url": "/files/880/heatmap.png",
      "quality": { "sharpness": 0.94, "glare": 0.02, "angle_deg": 1.4,
                   "lung_field": "full", "passed": true } }
  ],
  "risk": "high",
  "risk_score": 0.87,
  "findings": [
    { "code": "infiltration", "label": "Infiltrat", "location": "O'ng o'pka, yuqori bo'lak",
      "probability": 0.87, "severity": "high" },
    { "code": "effusion", "label": "Plevral suyuqlik", "location": "Aniqlanmadi",
      "probability": 0.09, "severity": "low" }
  ],
  "model": { "name": "densenet121-chest", "version": "0.3.1" },
  "status": "awaiting_doctor",
  "verdict": null,
  "created_at": "2026-08-16T09:12:00Z"
}
```

**`model` maydoni majburiy.** Har bir natija qaysi model versiyasi bilan chiqarilgani
yoziladi. Bir yildan keyin "u paytda qaysi model edi" degan savolga javob bo’lishi shart.

`findings` va `risk` Faza 1 gacha `null` bo’ladi — mijoz buni ushlashi shart.

### `POST /cases/{id}/verdict`

Faqat `specialist` roli.

```json
{ "action": "confirmed", "note": "Ftiziatrga yo'llandi" }
```

| `action` | Ma’nosi | Yangi holat |
|---|---|---|
| `confirmed` | Tasdiqlayman | `confirmed` |
| `rejected` | Patologiya yo’q | `rejected` |
| `needs_more` | Qo’shimcha tekshiruv kerak | `awaiting_doctor` |

```json
{ "case_id": 507, "status": "confirmed", "verdict": {
  "action": "confirmed", "note": "Ftiziatrga yo'llandi",
  "by": { "id": 7, "full_name": "Rasulova Dilnoza" },
  "at": "2026-08-16T09:53:00Z" } }
```

---

## 4. Real vaqt

### `GET /events`

Server-Sent Events. Panel yangi keys kelganda o’zi yangilanadi.

```
event: case.ready
data: { "case_id": 507, "risk": "high", "patient": "Rahmonov Sherzod" }

event: case.verdict
data: { "case_id": 507, "status": "confirmed" }
```

---

## 5. Statistika

### `GET /stats`

```json
{
  "by_risk": { "high": 14, "medium": 96, "low": 412, "pending": 3 },
  "awaiting_doctor": 5,
  "sla_breached": 1,
  "by_facility": [
    { "facility": "QVP-042", "district": "Kasbi tumani", "total": 43, "high": 3 }
  ]
}
```

---

## 6. AI xizmati (ichki)

Backend chaqiradi, tashqaridan ochiq emas. Alohida konteyner: `http://ai:9000`.

### `POST /predict`

```json
{ "image_path": "/data/880/original.jpg", "case_id": 507 }
```

```json
{
  "quality": { "sharpness": 0.94, "glare": 0.02, "angle_deg": 1.4,
               "lung_field": "full", "passed": true },
  "normalized_path": "/data/880/normalized.png",
  "heatmap_path": "/data/880/heatmap.png",
  "risk": "high",
  "risk_score": 0.87,
  "findings": [ /* Topilma obyektlari */ ],
  "model": { "name": "densenet121-chest", "version": "0.3.1" },
  "elapsed_ms": 2140
}
```

**Sifat o’tmasa model ishlamaydi:**

```json
{ "quality": { "sharpness": 0.31, "glare": 0.44, "angle_deg": 14.2,
               "lung_field": "partial", "passed": false },
  "risk": null, "findings": [], "reason": "quality_gate_failed" }
```

---

## Xatolar

Barcha xatolar bir xil shaklda:

```json
{ "error": { "code": "validation_error", "message": "Rasm sifati yetarli emas",
             "field": "file" } }
```

| Kod | Holat | Qachon |
|---|---|---|
| `unauthorized` | 401 | Token yo’q yoki eskirgan |
| `forbidden` | 403 | Rol yetarli emas (masalan hamshira verdikt bermoqchi) |
| `not_found` | 404 | Obyekt topilmadi |
| `validation_error` | 422 | Maydon noto’g’ri |
| `quality_gate_failed` | 422 | Rasm sifati past, model ishlamadi |
| `conflict` | 409 | `client_id` takrorlandi — javobda mavjud yozuv qaytadi |
| `ai_unavailable` | 503 | AI konteyneri javob bermayapti |

---

## Mijoz uchun eslatmalar

1. `findings`, `risk` va `heatmap_url` Faza 1 gacha `null` — mijoz buni ushlashi shart
2. Xavf darajasi faqat backendda hisoblanadi, mijoz o’zi hisoblamaydi
3. Oflayn navbatdagi har bir keysga `client_id` beriladi va qayta yuborishda **o’zgarmaydi**
4. Qurilmada hisoblangan sifat serverda **qayta tekshiriladi** — telefonga ishonilmaydi
