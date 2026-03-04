import asyncio
import random
import html
from typing import Dict

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait

import database
from config import ADMIN_GROUP_ID, TOPIC_ID

# ================= CONFIG =================
MAX_MENTION_TEXT = 10
MAX_MENTION_MEDIA = 5

TAGALL_DURATION_SECONDS = 300   # auto cancel 5 menit
AUTO_CLEAR_SECONDS = 60         # auto clear 1 menit
DELAY_RANGE = (3, 5)

_pending: Dict[int, Dict] = {}
_running: Dict[int, asyncio.Task] = {}
app = None


# ================= UTIL =================

def esc(t: str) -> str:
    return html.escape(t or "")


def make_mention(u) -> str:
    if u.username:
        return f"@{u.username}"
    name = u.first_name or u.last_name or str(u.id)
    return f'<a href="tg://user?id={u.id}">{esc(name)}</a>'


def keep_original_text(text: str) -> str:
    return esc(text) if text else ""


# === PATCH: REMOVE BOT HEADER ===
def extract_user_text(text: str) -> str:
    if not text:
        return ""

    # Format bot:
    # 📩 Pesan dari:
    # Nama: ...
    # ID: ...
    #
    # ISI PESAN USER
    parts = text.split("\n\n", 1)

    if len(parts) == 2:
        return parts[1].strip()

    return text.strip()


def format_mentions(mentions):
    lines = ["┌ ✨"]
    for m in mentions:
        lines.append(f"│ • {m}")
    lines.append("└ ✨")
    return "\n".join(lines)


async def gather_members(client, chat_id: int):
    users = []
    async for m in client.get_chat_members(chat_id):
        if not m.user.is_bot:
            users.append(m.user)
    return users


# ================= TIMER =================

async def auto_cancel(gid: int):
    await asyncio.sleep(TAGALL_DURATION_SECONDS)
    if database.is_session_active(gid):
        database.stop_session(gid)
        await app.send_message(
            ADMIN_GROUP_ID,
            f"⛔ Tagall AUTO-CANCEL (5 menit) di grup {gid}",
            message_thread_id=TOPIC_ID
        )
        asyncio.create_task(auto_clear(gid))


async def auto_clear(gid: int):
    await asyncio.sleep(AUTO_CLEAR_SECONDS)
    database.stop_session(gid)
    _running.pop(gid, None)


# ================= SEND =================

async def safe_send(target, original: Message, text: str):
    try:
        if original and original.media:
            return await app.copy_message(
                target,
                original.chat.id,
                original.id,
                caption=text,
                parse_mode=ParseMode.HTML
            )
        return await app.send_message(
            target,
            text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
    except Exception:
        pass


# ================= SETUP =================

def setup(client):
    global app
    app = client

    # ================= /cancel =================
    @app.on_message(filters.chat(ADMIN_GROUP_ID) & filters.command("cancel"))
    async def cancel_all(_, m: Message):
        for gid, task in list(_running.items()):
            task.cancel()
            database.stop_session(gid)
            asyncio.create_task(auto_clear(gid))
        _running.clear()
        _pending.clear()
        await m.reply("⛔ Semua tagall dihentikan.")

    # ================= /tagall =================
    @app.on_message(filters.chat(ADMIN_GROUP_ID) & filters.command("tagall"))
    async def remote_tagall(_, m: Message):
        if not m.is_topic_message or m.message_thread_id != TOPIC_ID:
            return await m.reply("🔒 Gunakan /tagall di topic yang ditentukan.")

        reply = m.reply_to_message
        _pending[m.id] = {
            "text": " ".join(m.text.split()[1:]),
            "reply_chat": reply.chat.id if reply else None,
            "reply_id": reply.id if reply else None
        }

        kb, row = [], []
        for gid, title in database.list_groups():
            row.append(
                InlineKeyboardButton(
                    title or str(gid),
                    callback_data=f"tg:{gid}:{m.id}"
                )
            )
            if len(row) == 2:
                kb.append(row)
                row = []
        if row:
            kb.append(row)

        await m.reply("Pilih grup target:", reply_markup=InlineKeyboardMarkup(kb))

    # ================= CALLBACK =================
    @app.on_callback_query(filters.regex("^tg:"))
    async def cb(_, cq):
        _, gid_s, src_s = cq.data.split(":")
        gid = int(gid_s)
        src_id = int(src_s)

        data = _pending.get(src_id)
        if not data:
            return await cq.answer("Kadaluarsa", show_alert=True)

        await cq.answer("🚀 Tagall dimulai")

        users = await gather_members(app, gid)
        if not users:
            return await app.send_message(cq.from_user.id, "❌ Gagal ambil member")

        database.start_session(gid)
        _running[gid] = asyncio.create_task(auto_cancel(gid))

        original = None
        if data["reply_chat"]:
            original = await app.get_messages(
                data["reply_chat"],
                data["reply_id"]
            )

        mentions = [make_mention(u) for u in users]
        per_chunk = MAX_MENTION_MEDIA if original and original.media else MAX_MENTION_TEXT

        for i in range(0, len(mentions), per_chunk):
            if not database.is_session_active(gid):
                break

            chunk = mentions[i:i + per_chunk]

            body = []
            if original:
                clean = extract_user_text(original.caption or original.text)
                body.append(keep_original_text(clean))

            if data["text"]:
                body.append(keep_original_text(data["text"]))

            body.append(format_mentions(chunk))
            final = "\n\n".join(filter(None, body))

            await safe_send(gid, original, final)
            await asyncio.sleep(random.uniform(*DELAY_RANGE))

        asyncio.create_task(auto_clear(gid))

        await app.send_message(
            ADMIN_GROUP_ID,
            f"✅ Tagall selesai di grup {gid}",
            message_thread_id=TOPIC_ID
        )
