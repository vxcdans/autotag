import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "22002589"))
API_HASH = os.getenv("API_HASH", "7238067a3532e1501f726a04cdda9f60")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8511887155:AAEyIou13uAf0URxzzW4mtV1_GMtaiumsuc")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "-1002351008445"))
TOPIC_ID = int(os.getenv("TOPIC_ID", "25192"))
DB_PATH = os.environ.get("DB_PATH", "tagall.db")
TARGET_TAGALL_GROUP_ID = int(os.environ.get("TARGET_TAGALL_GROUP_ID", -1002181517971))
OWNER_ID = int(os.getenv("OWNER_ID", "1086812385"))
