<h2 align="center">
    ──「 LIVE CHAT BOT PRIVATE ADMIN 」──
</h2>

<p align="center">
  <img src="[https://te.legra.ph/file/07e5b7d11e3a834ad3826.jpg](https://files.catbox.moe/9bn194.jpg)">
</p>

# 🤖 Livegram Bot (Pyrogram)

Bot Telegram dua arah menggunakan Pyrogram. Pengguna mengirim pesan ke bot, pesan masuk ke grup admin di topik tertentu, dan admin dapat membalas cukup dengan reply.

## ✨ Fitur
- User kirim pesan → masuk ke grup admin (dalam topik/forum)
- Admin balas via reply → pesan langsung dikirim ke user
- Otomatis menyimpan pemetaan pesan → user ID
- Tidak perlu sortir manual, mendukung banyak admin

## ⚙️ Cara Pakai

### 1. Clone dan Masuk Folder
```bash
git clone https://github.com/yourusername/livegram-bot.git
cd livegram-bot
```

### 2. Siapkan `.env`
```bash
cp .env.example .env
```
Edit `.env` dan isi dengan data dari [my.telegram.org](https://my.telegram.org) dan @BotFather

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Bot
```bash
python3 bot.py
```

## 📚 Contoh `.env`
```
API_ID=123456
API_HASH=your_api_hash
BOT_TOKEN=123456:ABCDEF-yourbottoken
ADMIN_GROUP_ID=-1001234567890
TOPIC_ID=55
```

## 📁 Struktur File
```
livegram-bot/
├── bot.py
├── config.py
├── .env.example
├── data.json
├── requirements.txt
└── README.md
```

## ✍️ Credit
Made with ❤️ by @fsyrl9
Visit : https://t.me/FerdiStore
