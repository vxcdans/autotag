import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "22002589"))
API_HASH = os.getenv("API_HASH", "7238067a3532e1501f726a04cdda9f60")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8662943452:AAH4YIngA46OYXbi4H7HV_tmDCXyrm7nZMA")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "-1001717859584"))
TOPIC_ID = int(os.getenv("TOPIC_ID", "281127"))
DB_PATH = os.environ.get("DB_PATH", "tagall.db")
TARGET_TAGALL_GROUP_ID = int(os.environ.get("TARGET_TAGALL_GROUP_ID", -1001717859584))
OWNER_ID = int(os.getenv("OWNER_ID", "8313412433"))
