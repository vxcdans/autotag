from database import *
import os
from config import *
from pyrogram import Client, filters
from pyrogram.types import Message
from tagall import setup as tagall_setup

import shutil
import asyncio
from datetime import datetime, timedelta


DB_PATH = "tagall.db"


# ====== IMPORT DATABASE ======
from database import (
    save_message_map,
    get_user_by_admin_message
)

app = Client(
    "livegram_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ====== LOAD TAGALL MODULE ======
tagall_setup(app)
print("Module TagAll Loaded.")


# ============================
# /start
# ============================
@app.on_message(filters.private & filters.command("start"))
async def start_command(_, message: Message):
    await message.reply(
        "👋 Halo! Selamat datang.\n\n"
        "Silakan kirim pesan melalui chat ini.\n"
        "Admin akan membalas secepat mungkin 😊"
    )

# ============================
# User mengirim pesan
# ============================
@app.on_message(filters.private & ~filters.command(["start"]))
async def handle_user_message(_, message: Message):
    user = message.from_user

    caption = (
        f"📩 Pesan dari:\n"
        f"Nama: {user.first_name} (@{user.username or 'tidak_ada'})\n"
        f"ID: {user.id}\n\n"
    )

    sent = None
    try:
        # === kirim sesuai tipe ===
        if message.photo:
            sent = await app.send_photo(
                ADMIN_GROUP_ID,
                message.photo.file_id,
                caption=caption + (message.caption or ""),
                message_thread_id=TOPIC_ID
            )

        elif message.video:
            sent = await app.send_video(
                ADMIN_GROUP_ID,
                message.video.file_id,
                caption=caption + (message.caption or ""),
                message_thread_id=TOPIC_ID
            )

        elif message.voice:
            sent = await app.send_voice(
                ADMIN_GROUP_ID,
                message.voice.file_id,
                caption=caption + (message.caption or ""),
                message_thread_id=TOPIC_ID
            )

        elif message.audio:
            sent = await app.send_audio(
                ADMIN_GROUP_ID,
                message.audio.file_id,
                caption=caption + (message.caption or ""),
                message_thread_id=TOPIC_ID
            )

        elif message.document:
            sent = await app.send_document(
                ADMIN_GROUP_ID,
                message.document.file_id,
                caption=caption + (message.caption or ""),
                message_thread_id=TOPIC_ID
            )

        elif message.animation:
            sent = await app.send_animation(
                ADMIN_GROUP_ID,
                message.animation.file_id,
                caption=caption + (message.caption or ""),
                message_thread_id=TOPIC_ID
            )

        elif message.sticker:
            if getattr(message.sticker, "is_premium", False):
                return await message.reply("❗ Stiker premium tidak bisa dikirim ke admin.")

            sent = await app.send_sticker(
                ADMIN_GROUP_ID,
                message.sticker.file_id,
                message_thread_id=TOPIC_ID
            )

        elif message.text:
            sent = await app.send_message(
                ADMIN_GROUP_ID,
                caption + message.text,
                message_thread_id=TOPIC_ID
            )

        else:
            return await message.reply("❗ Jenis pesan ini belum didukung.")

        # === SIMPAN KE DATABASE ===
        save_message_map(sent.id, user.id)

        await message.reply("📨 Pesanmu telah dikirim ke admin. Tunggu balasannya ya!")

    except Exception as e:
        print("ERROR:", e)
        await message.reply(f"❗ Gagal mengirim ke admin.\n{e}")

# ============================
# Admin membalas pesan
# ============================
@app.on_message(filters.chat(ADMIN_GROUP_ID) & filters.reply)
async def handle_admin_reply(_, message: Message):
    replied = message.reply_to_message

    if not replied or not replied.from_user or not replied.from_user.is_self:
        return

    if replied.message_thread_id != TOPIC_ID:
        return

    # === Ambil user dari database ===
    user_id = get_user_by_admin_message(replied.id)

    if not user_id:
        return await message.reply("⚠️ Data user tidak ditemukan.")

    try:
        if message.text:
            await app.send_message(user_id, f"💬 Balasan admin:\n\n{message.text}")

        elif message.sticker:
            await app.send_sticker(user_id, message.sticker.file_id)

        elif message.photo:
            await app.send_photo(
                user_id,
                message.photo.file_id,
                caption=message.caption or ""
            )

        elif message.video:
            await app.send_video(
                user_id,
                message.video.file_id,
                caption=message.caption or ""
            )

        elif message.voice:
            await app.send_voice(
                user_id,
                message.voice.file_id,
                caption=message.caption or ""
            )

        elif message.audio:
            await app.send_audio(
                user_id,
                message.audio.file_id,
                caption=message.caption or ""
            )

        elif message.document:
            await app.send_document(
                user_id,
                message.document.file_id,
                caption=message.caption or ""
            )

        elif message.animation:
            await app.send_animation(
                user_id,
                message.animation.file_id,
                caption=message.caption or ""
            )

        else:
            await message.reply("❗ Jenis pesan ini belum bisa diteruskan ke user.")

    except Exception as e:
        await message.reply(f"❗ Gagal mengirim ke user.\n{e}")


@app.on_message(filters.command("backup"))
async def cmd_backup(client, message: Message):
    if getattr(message.from_user, "id", None) != OWNER_ID:
        return

    # Pastikan file DB ada
    if not os.path.exists(DB_PATH):
        return await message.reply("❗ Database tidak ditemukan.")

    try:
        await message.reply_document(
            document=DB_PATH,
            caption="📦 Backup database saat ini."
        )
    except Exception as e:
        await message.reply(f"❗ Gagal mengirim backup:\n`{e}`")


@app.on_message(filters.command("restore"))
async def cmd_restore(client, message: Message):
    if getattr(message.from_user, "id", None) != OWNER_ID:
        return

    # Harus reply file .db
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("❗ Balas file `.db` dengan command ini.")

    doc = message.reply_to_message.document

    # Hanya file .db
    if not doc.file_name.lower().endswith(".db"):
        return await message.reply("❗ File harus berformat `.db`.")

    try:
        # Unduh dulu
        temp_file = await message.reply_to_message.download(file_name="restore_temp.db")

        # Overwrite database lama
        shutil.copy(temp_file, DB_PATH)

        await message.reply(
            "✅ Database berhasil di-restore.\n"
            "🔄 Silakan *restart bot* untuk menerapkan perubahan.\n"
            "Gunakan `/reboot` jika ingin restart otomatis."
        )

    except Exception as e:
        await message.reply(f"❗ Gagal restore:\n`{e}`")

@app.on_message(filters.command("reboot"))
async def cmd_reboot(client, message: Message):
    if getattr(message.from_user, "id", None) != OWNER_ID:
        return

    await message.reply("🔄 Bot sedang restart...")

    # Restart script menggunakan start.sh
    os.execvp("bash", ["bash", "start.sh"])

# Auto-backup at midnight (00:00) -> sends DB to OWNER
async def auto_backup_task():
    await asyncio.sleep(5)  # allow bot to start
    while True:
        now = datetime.now()
        # next midnight
        tomorrow = now + timedelta(days=1)
        next_midnight = datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        wait = (next_midnight - now).total_seconds()
        print(f"[AUTO BACKUP] waiting {wait} seconds until midnight...")
        await asyncio.sleep(wait)
        try:
            await app.send_document(OWNER_ID, DB_PATH, caption="📦 Auto-backup database (00:00)")
            print("[AUTO BACKUP] sent backup to owner")
        except Exception as e:
            print("[AUTO BACKUP ERROR]", e)
        # loop to next day
asyncio.get_event_loop().create_task(auto_backup_task())

print("🤖 Bot LiveChat aktif...")
app.run()
