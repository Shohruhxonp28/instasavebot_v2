# Telegram Media Downloader Bot

Ushbu loyiha **Aiogram 3.x** va **universalDownloader (Node.js)** integratsiyasi asosida yaratilgan universal media yuklovchi Telegram botdir.

Bot quyidagi platformalardan video, rasm, karusel albom va musiqalarni eng yuqori sifatda yuklab beradi hamda videolardagi fon musiqasini **FFmpeg** + **ACRCloud** yordamida avtomatik aniqlaydi.

---

## 📌 Qo'llab-quvvatlanadigan platformalar

- **Instagram**: Reels, Postlar (rasmlar), Karusel (albomlar)
- **Pinterest**: Rasmlar (asl yuqori sifatda) va Videolar
- **TikTok & Douyin**: Suv belgisiz (watermark-free) videolar va fotolar
- **Threads**: Rasmlar va videolar
- **Spotify & SoundCloud**: Audio treklar (MP3)
- **Snapchat & CapCut**: Videolar
- **TeraBox**: To'g'ridan-to'g'ri fayllar va videolar
- **YouTube, Facebook, Twitter (X)**: Videolar
- **Reddit, Bluesky, Dailymotion, Tumblr, LinkedIn**

---

## 🚀 Asosiy imkoniyatlar

1. **Gibrid yuklash tizimi (yt-dlp + universalDownloader)**:
   - Instagram uchun Snapsave API birlamchi qilib sozlangan, zaxira sifatida `yt-dlp` ishlaydi.
   - Har bir platforma uchun eng tezkor va ishonchli usul tanlanadi.
2. **Karusel (Albom) yuborish**:
   - Bir nechta rasm va videolarni Telegram albom ko'rinishida guruhlab yuboradi.
3. **Musiqani aniqlash (Shazam analogi)**:
   - Videodagi fon musiqasi ACRCloud orqali aniqlanadi (qo'shiq nomi, ijrochi, albom).
4. **Majburiy kanallarga obuna tizimi**:
   - Botdan foydalanishdan oldin kanallarga a'zo bo'lishni talab qilish ("✅ Obunani tekshirish" tugmasi bilan).
5. **To'liq Telegram Admin Panel (`/admin`)**:
   - 👥 Foydalanuvchilar (jami soni, ID bo'yicha qidirish, bloklash/blokdan chiqarish)
   - 📊 Statistika (har bir platforma bo'yicha yuklashlar soni, musiqa qidiruvlari)
   - 📢 Xabar tarqatish (Broadcast - matn, rasm, video, hujjat, oldindan ko'rish va tasdiqlash)
   - 📺 Majburiy kanallar (qo'shish, o'chirish, yoqish/o'chirish)
   - 👑 Admin sozlamalari (majburiy obunani yoqish/o'chirish)

---

## 📂 Loyiha tuzilishi

```text
instasavebot_v2/
│
├── bot/
│   ├── handlers/       # Foydalanuvchi handlerlari (start, downloader)
│   ├── admin/          # Admin panel handlerlari
│   ├── keyboards/      # Tugmalar (inline keyboards)
│   ├── services/       # yt-dlp, universalDownloader ko'prigi, ACRCloud
│   ├── database/       # SQLite ma'lumotlar bazasi va so'rovlar
│   ├── utils/          # FSM holatlari, admin filterlar
│   ├── config.py       # Sozlamalar va muhit o'zgaruvchilari
│   └── main.py         # Botning asosiy kirish nuqtasi
│
├── universalDownloader/ # Node.js ko'p platformali scraper dvigateli
│   ├── services/       # Alohida servislar (Threads, Spotify, CapCut va h.k.)
│   ├── controllers/    # API kontrollerlari
│   ├── routes/         # Express yo'nalishlari
│   ├── cli.js          # Python bilan integratsiya uchun CLI ko'prik
│   └── index.js        # Mustaqil Express API serveri
│
├── downloads/          # Vaqtinchalik yuklangan fayllar (avtomatik tozalanadi)
├── media/              # Vaqtinchalik audio fayllar (avtomatik tozalanadi)
├── cookies.txt         # yt-dlp uchun cookie fayli
├── requirements.txt    # Python kutubxonalari
├── .env.example        # Sozlamalar namunasi
└── README.md
```

---

## 🛠 Tizim talablari

- **Python**: 3.10 yoki undan yuqori
- **Node.js**: 18 yoki undan yuqori (va `npm`)
- **FFmpeg**: Tizimda o'rnatilgan bo'lishi kerak
- **Telegram Bot Token**: [@BotFather](https://t.me/BotFather) dan olingan token

---

## 📥 O'rnatish va Ishga tushirish bo'yicha to'liq qo'llanma

### 1-qadam. Loyihani yuklab olish va unga kirish

```bash
cd ~/www/instasavebot/instasavebot_v2
```

---

### 2-qadam. FFmpeg ni sozlash

#### A variant: Oddiy VPS / Ubuntu / Debian (Root huquqi bo'lsa):
```bash
sudo apt update
sudo apt install -y ffmpeg
```

#### B variant: PaaS / Shared Hosting (Root yoki `sudo` huquqi bo'lmaganda):
Agar serveringizda `sudo` ishlamasa, statik FFmpeg binary faylini to'g'ridan-to'g'ri o'zingizning katalogingizga yuklab oling:
```bash
mkdir -p ~/bin
cd ~/bin
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz --strip-components=1
rm ffmpeg-release-amd64-static.tar.xz
```
Tekshirish:
```bash
~/bin/ffmpeg -version
```
*(Bunday holda `.env` faylida `FFMPEG_PATH=/home/username/bin/ffmpeg` deb ko'rsatiladi).*

---

### 3-qadam. universalDownloader (Node.js) paketlarini o'rnatish

Loyiha papkasida turib:
```bash
cd universalDownloader
npm install
cd ..
```

---

### 4-qadam. Python Virtual Muhit (venv) va kutubxonalarni o'rnatish

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5-qadam. `.env` faylini sozlash

Namuna asosida `.env` faylini yarating:
```bash
cp .env.example .env
nano .env
```

Quyidagi parametrlarni to'ldiring:
```env
# @BotFather dan olingan bot tokeni
BOT_TOKEN=123456789:ABCDEF_sizning_bot_tokeningiz

# Admin(lar)ning Telegram ID raqamlari (vergul bilan ajratilgan)
ADMIN_IDS=123456789

# ACRCloud ma'lumotlari (musiqa aniqlash uchun kerak bo'lsa)
ACR_HOST=identify-eu-west-1.acrcloud.com
ACR_ACCESS_KEY=sizning_access_key
ACR_ACCESS_SECRET=sizning_access_secret

# Instagram hisob ma'lumotlari (yopiq/yosh chegarasi bor postlar uchun)
INSTAGRAM_USERNAME=uzbekchakinolarx
INSTAGRAM_PASSWORD=S14159265s

# Ma'lumotlar bazasi fayli
DB_PATH=bot_database.db

# Telegram orqali yuklash hajmi chegarasi (MB da)
MAX_VIDEO_SIZE_MB=50

# FFmpeg to'liq yo'li (agar sudo bilan o'rnatilgan bo'lsa bo'sh qoldiring, aks holda ko'rsating)
# Masalan: /home/duovel/bin/ffmpeg
FFMPEG_PATH=
```
*Saqlash uchun: `Ctrl + O`, `Enter`. Chiqish uchun: `Ctrl + X`.*

---

### 6-qadam. Botni ishga tushirish

#### 1. Sinov uchun to'g'ridan-to'g'ri ishga tushirish:
```bash
source venv/bin/activate
python3 -m bot.main
```
*(To'xtatish uchun: `Ctrl + C`).*

#### 2. Serverda orqa fonda (doimiy) ishlatish:

**A variant: `nohup` orqali (eng osoni):**
```bash
nohup python3 -m bot.main > bot.log 2>&1 &
```
- Botning ishlash jarayonini (loglarni) kuzatish:
  ```bash
  tail -f bot.log
  ```
- Botni to'xtatish kerak bo'lsa:
  ```bash
  pkill -f "python3 -m bot.main"
  ```

**B variant: `screen` orqali:**
```bash
screen -S instabot
python3 -m bot.main
```
- Ekranni orqa fonga o'tkazish: `Ctrl + A`, keyin `D`.
- Qaytadan ekranga kirish: `screen -r instabot`.

---

## 📺 Majburiy kanallarni sozlash

1. Botingizni kanalingizga **Administrator** (Admin) qilib qo'shing.
2. Telegram orqali botingizga `/admin` buyrug'ini yuboring.
3. **📺 Required Channels → ➕ Add channel** bo'limiga kiring.
4. Kanal username'ini (masalan `@mening_kanalim`) yoki ID raqamini yuboring.
5. Bot a'zolikni avtomatik tekshiradigan holatga keladi.

---

## ⚙️ universalDownloader qanday ishlaydi?

- **Bot uchun alohida ishga tushirish SHART EMAS!**
  Sizdan talab qilinadigan yagona narsa — serverda bir marta uning paketlarini o'rnatish:
  ```bash
  cd universalDownloader
  npm install
  cd ..
  ```
  Foydalanuvchi Telegram orqali havola yuborganida, Python boti fon rejimida `cli.js` orqali universalDownloader dvigatelini **avtomatik ravishda o'zi chaqiradi**, mediani yuklab oladi va foydalanuvchiga yuboradi. Ya'ni alohida server yoki port ochib yurishingiz shart emas.

- **Mustaqil Web API server sifatida ishlatish (Ixtiyoriy):**
  Agar ushbu API'dan botdan tashqari, o'zingizning veb-saytingiz yoki boshqa ilovalaringiz uchun alohida HTTP API sifatida foydalanmoqchi bo'lsangiz:
  ```bash
  cd universalDownloader
  npm start
  ```
  Standart holda `http://localhost:3000` portida ishga tushadi.

---

## ⚠️ Muhim eslatmalar

- **Telegram Bot API limiti**: Telegram botlar to'g'ridan-to'g'ri maksimal **50 MB** gacha bo'lgan fayllarni yubora oladi. `MAX_VIDEO_SIZE_MB` dan katta fayllar foydalanuvchiga ogohlantirish bilan rad etiladi.
- **Xotirani tozalash**: Har bir so'rov bajarilgandan so'ng vaqtinchalik yuklangan barcha videolar, fotosuratlar va audio fayllar darhol o'chiriladi. Server diskida ortiqcha fayllar saqlanmaydi.
