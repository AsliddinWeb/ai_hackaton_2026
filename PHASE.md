# ShifokorAI — ishlab chiqish bosqichlari

**Vazifa:** Umummilliy AI Xakaton, Qarshi bosqichi — **13-yo’nalish: "Hududiy SI-Mobil Diagnostika (AI Mobile Clinic for Remote Villages)"**.

**Mahsulot:** Hamshira negatoskopdagi rentgen plyonkasini oddiy telefon kamerasida suratga oladi → sun’iy intellekt tasvirni tahlil qilib xavf bo’yicha saralaydi → faqat shubhali holatlar viloyat mutaxassisiga boradi → yakuniy tashxisni shifokor qo’yadi.

**Asosiy g’oya:** mutaxassisni qishloqqa olib borish emas, **uning vaqtini ko’paytirish**. Yangi apparat sotib olinmaydi — mavjud rentgen va telefon yetarli.

---

## Texnologiyalar

| Qism | Texnologiya | Konteynerda? |
|---|---|---|
| Hamshira ilovasi | **React Native + Expo**, demo **Expo Go** orqali | ❌ yo’q |
| Backend | FastAPI (Python) | ✅ ha |
| AI xizmati | Python, OpenCV, PyTorch | ✅ ha |
| Ma’lumotlar bazasi | PostgreSQL | ✅ ha |
| Fayl saqlash | MinIO | ✅ ha |
| Shifokor paneli | React + Vite | 🟡 ishlab chiqishda yo’q, demoda ha |

**Nega mobil ilova Docker da emas.** Expo Go telefondan Metro bundlerga LAN orqali ulanadi. Bundlerni konteynerga solsangiz, telefon uni ko’rishi uchun qo’shimcha port va tarmoq sozlamalari kerak bo’ladi — foydasi yo’q, muammosi ko’p. `npx expo start` noutbukda to’g’ridan-to’g’ri ishlaydi.

**Nega panel ishlab chiqishda Docker da emas.** Vite ning hot reload i konteynerda sekinlashadi. Demo kunida `docker compose` ga qo’shiladi.

---

## Allaqachon tayyor

Bu ikkisi qayta qilinmaydi, faqat ishlatiladi:

| Nima | Qayerda |
|---|---|
| 12 ta ekran dizayni va vizual til | `design/screens.html` |
| 10 slaydlik taqdimot (16:9 PDF) | `pitch/ShifokorAI.pdf`, manba `pitch/deck.html` |

---

## Kritik yo’l

Eng riskli qism — **AI zanjiri**, backend emas. Telefonda olingan plyonka fotosidan model mazmunli natija bermasa, qolgan hamma narsa bezakka aylanadi.

```
0.3  Docker muhiti ko'tarildi
      ↓
0.4  Telefon backendni ko'radi
      ↓
1.2  Plyonka fotosi normalizatsiyasi  ← ENG RISKLI
      ↓
1.3  Model mazmunli natija beradi
      ↓
2.3  Backend AI ni chaqiradi
      ↓
3.5  Ilovada surat olinadi  →  4.1  Panelda ko'rinadi
```

**Faza 1 birinchi bo’lib yopiladi.** U ishlamasa, yo’nalishni o’zgartirish kerak — buni birinchi kunda bilish kerak, oxirgi kunda emas.

---

## FAZA 0 — Poydevor

| # | Sub-faza | Tayyor mezoni |
|---|---|---|
| 0.1 | Repo va papka tuzilmasi | `api/ ai/ mobile/ panel/ infra/ docs/` yaratilgan, hamma clone qilgan |
| 0.2 | API kontrakti | `docs/api.md` da endpointlar va JSON shakllari yozilgan, hamma rozi |
| 0.3 | **Docker muhiti** | `docker compose up` bitta buyruq bilan `db`, `minio`, `api`, `ai` ni ko’taradi |
| 0.4 | **Telefon ↔ backend ulanishi** | Expo Go dagi ilova noutbukdagi `/health` ga so’rov yuborib javob oldi |
| 0.5 | Test rasmlari | 20-30 ta ko’krak qafasi rentgeni, natijasi ma’lum |

### 0.3 — Docker haqida bilish kerak bo’lganlar

**Bazaviy obrazlarni birinchi kuni tortib oling.** AI konteyneri PyTorch va OpenCV bilan 3-5 GB keladi. Xakaton Wi-Fi sida buni yuklash yarim soat ketishi mumkin. `docker pull` ni ish boshida, hamma bir vaqtda internetga urilmasdan oldin qiling.

**Model vaznlari obraz ichiga qo’shilmaydi.** Ular hajmni ikki barobar oshiradi va har bir qayta qurishda qaytadan yoziladi. Volume ga mount qilinadi va bir marta yuklanadi.

**Kod volume orqali ulanadi.** Har o’zgarishda obrazni qayta qurmaslik uchun `./api:/app` ko’rinishida mount qilinadi va `--reload` bilan ishlatiladi.

**macOS da `--network host` ishlamaydi.** Portlar aniq ko’rsatiladi: `8000:8000`. Konteyner ichidan noutbukka murojaat kerak bo’lsa — `host.docker.internal`.

**GPU yo’q.** macOS da Docker GPU bermaydi, model CPU da ishlaydi. Bizning modelimiz uchun yetarli, lekin javob vaqti sekinroq — demoda buni hisobga oling.

### 0.4 — telefon ulanishi

Telefon `localhost` ni ko’rmaydi. Konteyner portni `0.0.0.0` ga chiqaradi (`-p 8000:8000` shuni qiladi), telefon esa **noutbukning LAN IP** siga ulanadi:

```
ipconfig getifaddr en0        →  masalan 192.168.1.42
mobile/.env:  EXPO_PUBLIC_API_URL=http://192.168.1.42:8000
```

Xakaton Wi-Fi si qurilmalar orasini bloklasa — telefondan hotspot tarqating va noutbukni shunga ulang. **Buni demodan oldin, tinch paytda sinang.**

### 0.5 — test rasmlari

Ochiq to’plamlar: sil bo’yicha Montgomery va Shenzhen, umumiy patologiya bo’yicha NIH ChestX-ray14. Bir qismini **ekrandan yoki chop etib telefonda suratga oling** — Faza 1 aynan shunday "plyonka fotosi" da sinaladi, toza DICOM da emas.

---

## FAZA 1 — AI zanjiri ← eng riskli, birinchi

Maqsad: telefonda olingan sifatsiz fotodan model mazmunli natija berishini **isbotlash**.

| # | Sub-faza | Tayyor mezoni |
|---|---|---|
| 1.1 | Sifat darvozasi | Rasm rentgenmi, xiralik, yorug’lik aksi va burchak baholanadi; to’rt raqam qaytadi |
| 1.2 | **Plyonka fotosi normalizatsiyasi** | Qiyshiq, aks etgan foto → tekislangan, kontrasti tuzatilgan tasvir |
| 1.3 | Patologiya modeli | Tayyor model ishga tushdi, patologiya ehtimollari qaytadi |
| 1.4 | Issiqlik xaritasi | Grad-CAM PNG chiqadi, model qayerga qaraganini ko’rsatadi |
| 1.5 | Anatomik joy | Topilma "o’ng o’pka, yuqori bo’lak" ko’rinishida beriladi, dog’ sifatida emas |
| 1.6 | Xizmat interfeysi | `POST /predict` → sifat, topilmalar, xavf bali, heatmap manzili |

**1.2 — loyihaning texnik yadrosi.** Barcha ochiq modellar DICOM bor deb faraz qiladi. Bizda esa telefonda olingan plyonka fotosi: qiyshiq, yorug’lik aks etgan, fon aralashgan. Ketma-ketlik: kontur aniqlash → perspektiv tuzatish → aks etishni maskalash → kontrast normalizatsiyasi → o’pka sohasini kesish.

**Modelni o’qitmang.** Tayyor pretrained model ishlatiladi. 4 kunda o’qitilgan model tayyoridan yomonroq chiqadi va vaqtni yeydi.

**1.1 xavfsizlik qoidasi.** Sifat past bo’lsa model **javob bermaydi**. Yomon fotodan chiqqan ishonchli ko’rinadigan xato — eng xavfli ssenariy.

**Docker eslatmasi.** AI xizmati alohida konteyner. Uni backenddan ajratish shart: model og’ir, backend yengil bo’lishi kerak, va AI ni qayta ishga tushirganda backend uzilmasligi kerak.

---

## FAZA 2 — Backend

| # | Sub-faza | Tayyor mezoni |
|---|---|---|
| 2.1 | Ma’lumotlar modeli | Bemor, keys, tasvir, topilma, verdikt, audit jadvallari |
| 2.2 | Fayl yuklash | Katta rasm bo’laklab yuboriladi, uzilsa qoldig’idan davom etadi |
| 2.3 | Navbat va AI chaqiruvi | Yuklangan rasm navbatga tushadi, AI konteyneri ishlaydi, natija saqlanadi |
| 2.4 | Verdikt va audit | Shifokor qarori yoziladi; har bir AI chiqishi va kim ko’rgani o’chmas logda |
| 2.5 | Real vaqt xabarnoma | Yangi qizil keys paydo bo’lsa panel o’zi yangilanadi |

**2.4 haqida.** Har bir verdikt qaysi model versiyasi bilan chiqarilgani yoziladi. Bir yildan keyin "u paytda qaysi model edi" degan savolga javob bo’lishi shart.

---

## FAZA 3 — Hamshira ilovasi (React Native + Expo)

Maqsad: qishloqda, oflayn, bir qo’lda ishlaydigan kiritish. **Dizayn tayyor** — `design/screens.html` dagi 12 ta ekran.

| # | Sub-faza | Ekranlar | Tayyor mezoni |
|---|---|---|---|
| 3.1 | Skelet va tokenlar | — | `expo-router` navigatsiyasi ishlaydi, rang va tipografika tokenlari kodda |
| 3.2 | Kirish | 01-03 | Telefon raqami va kod bilan kiriladi |
| 3.3 | Bosh ekran va bemorlar | 04-06 | Keyslar ro’yxati, qidiruv, yangi bemor |
| 3.4 | Anamnez | 07 | Shikoyat chiplari va davomiylik kiritiladi |
| 3.5 | **Guided capture** | 08 | Kamera ustida ramka, real vaqt sifat nazorati |
| 3.6 | Sifat va yuborish | 09-10 | Sifat natijasi ko’rsatiladi, keys yuboriladi |
| 3.7 | Natija va profil | 11-12 | AI topilmalari, heatmap, sinxronizatsiya holati |
| 3.8 | Oflayn navbat | — | Aloqa yo’qda saqlanadi, tiklanganda o’zi yuboriladi |

**3.5 — ilovaning eng murakkab qismi.** Kamera oqimi ustida ramka qoplamasi, qurilmada soniyasiga besh marta sifat tekshiruvi (xiralik, aks etish, burchak). Sifat yashil bo’lmaguncha deklanshator ochilmaydi.

**3.8 demo uchun kuchli moment.** Wi-Fi o’chiriladi, keys kiritiladi, yoqiladi — o’zi ketadi. Buni hakamlarga ko’rsatish kerak.

### Expo Go cheklovlari

| Cheklov | Bizga ta’siri |
|---|---|
| Faqat Expo SDK ichidagi kutubxonalar, native modul qo’shib bo’lmaydi | Muammo emas: `expo-camera`, `expo-sqlite`, `expo-router`, `react-native-svg` yetadi |
| Masofaviy push xabarnoma ishlamaydi | Muammo emas: xabarnoma panelga boradi, telefonga emas |
| Telefon va noutbuk bitta tarmoqda bo’lishi shart | Zaxira: telefondan hotspot yoki `npx expo start --tunnel` |
| `.env` o’zgarsa qayta ishga tushirish kerak | `EXPO_PUBLIC_*` bundle paytida yoziladi, ish paytida o’qilmaydi |

---

## FAZA 4 — Shifokor paneli (React + Vite)

| # | Sub-faza | Tayyor mezoni |
|---|---|---|
| 4.1 | Keys navbati | Xavf bo’yicha saralangan, qizil tepada |
| 4.2 | Tasvir ko’ruvchi | Zoom, yorqinlik, original ↔ issiqlik xaritasi almashuvi |
| 4.3 | Topilmalar va verdikt | AI topilmalari ro’yxati va uchta tugma: tasdiqlash, rad etish, qo’shimcha tekshiruv |
| 4.4 | Real vaqt | Yangi keys kelganda ro’yxat o’zi yangilanadi |
| 4.5 | Javobsiz holat | Belgilangan vaqtda javob bo’lmasa, keys tepaga ko’tariladi |

**4.5 haqida.** Tizim xabar yuborib, hech kim javob bermay qolishi — real deploymentdagi eng ko’p uchraydigan nosozlik.

---

## FAZA 5 — Demo va taqdimot

| # | Sub-faza | Tayyor mezoni |
|---|---|---|
| 5.1 | Demo ma’lumotlari | 15-20 ta bemor, turli xavf darajalarida |
| 5.2 | Demo ssenariysi | Quyidagi 6 qadam uzluksiz o’tadi |
| 5.3 | Taqdimot | ✅ tayyor — `pitch/ShifokorAI.pdf`, ismlar va raqamlar to’ldiriladi |
| 5.4 | Bitta buyruqli ishga tushirish | Panel ham compose ga qo’shiladi, `docker compose up` hammasini ko’taradi |
| 5.5 | Zaxira reja | Internet yo’q bo’lsa nima qilamiz — yozilgan va sinalgan |

**Demo ssenariysi:**

1. Telefonda plyonka suratga olinadi — ramka yashil bo’lguncha kutiladi
2. Sifat ekrani: aniqlik 0.94, yorug’lik aksi 0.02, burchak 1.4°
3. Wi-Fi o’chiq — keys qurilmada saqlanadi
4. Wi-Fi yoqiladi, keys o’zi ketadi
5. Panelda keys tepaga chiqadi, heatmap bilan
6. Shifokor tasdiqlaydi, holat yopiladi

**5.4 haqida.** Demo kuni "menda ishlayapti" degan holat bo’lmasligi kerak. Backend, AI, baza, fayl saqlash va panel — bitta `docker compose up` bilan ko’tariladi. Faqat Expo alohida: `npx expo start`.

**5.5 haqida.** Backend noutbukda, telefon hotspot orqali ulangan — tashqi internet kerak emas.

---

## FAZA 6 — Xakatondan keyin

Xakatonda bajarilmaydi, lekin taqdimotda aytiladi.

| # | Sub-faza | Mazmuni |
|---|---|---|
| 6.1 | Lokal ma’lumot to’plash | Natijasi ma’lum mahalliy rentgenlar bazasi — asosiy aktiv |
| 6.2 | Retrospektiv validatsiya | Modelni o’z populyatsiyamizda o’lchash |
| 6.3 | Huquqiy asos | AI — tashxis emas, saralash vositasi. Ma’lumot lokalizatsiyasi, rozilik, audit |
| 6.4 | Shadow mode | Tizim ishlaydi, lekin hech kimning qaroriga ta’sir qilmaydi. Bemor uchun nol risk |
| 6.5 | Bitta tumanda pilot | Real foydalanish va boshlang’ich ko’rsatkichlar bilan solishtirish |

---

## Rollar

| Kishi | Zona | Fazalar |
|---|---|---|
| 1 | AI | 1.1 – 1.6 |
| 2 | Backend va Docker | 0.3, 2.1 – 2.5, 5.4 |
| 3 | Mobil ilova (Expo) | 3.1 – 3.8 |
| 4 | Web panel | 4.1 – 4.5 |
| 5 | Soha, demo, taqdimot | 0.5, 5.1 – 5.3, 5.5 |

**Parallel ishlash sharti:** 0.2 (API kontrakti) birinchi soatda kelishiladi. Shundan keyin mobil va panel **soxta ma’lumot** bilan ishlashni boshlaydi va backendni kutmaydi.

---

## Bajarilish tartibi

```
0.1 → 0.2 → 0.3 → 0.4 ────────┐
       0.5 ──────┐             │
                 ▼             │
        1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 1.6
                              │       │
                              ▼       ▼
                        2.1 → 2.2 → 2.3 → 2.4 → 2.5
                              │              │
                 ┌────────────┴──────┬───────┘
                 ▼                   ▼
          3.1 → ... → 3.8      4.1 → ... → 4.5
                 └────────┬──────────┘
                          ▼
                    5.1 → ... → 5.5
```

**Vaqt yetmasa shu tartibda qisqartiriladi:** avval 4.5, keyin 3.7, keyin 1.5, keyin 2.5.

**Hech qachon qisqartirilmaydi:** Faza 1 (1.2 va 1.3) va demo zanjiri `3.5 → 3.6 → 4.1`. Bularsiz ko’rsatadigan narsa qolmaydi.
