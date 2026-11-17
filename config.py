import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "22002589"))
API_HASH = os.getenv("API_HASH", "7238067a3532e1501f726a04cdda9f60")
BOT_TOKEN = os.getenv("BOT_TOKEN", ":9186491495:AAGYw0D81y47rWHJWjIQEw-iR-IeKzuTCA4")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "-1002161668563")
TOPIC_ID = int(os.getenv("TOPIC_ID", "217532"))
DB_PATH = os.environ.get("DB_PATH", "tagall.db")
TARGET_TAGALL_GROUP_ID = int(os.environ.get("TARGET_TAGALL_GROUP_ID", "-1002358617599"))
OWNER_ID = int(os.getenv("OWNER_ID", "8033557981"))
