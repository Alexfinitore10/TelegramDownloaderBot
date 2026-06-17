import os
from dotenv import load_dotenv

load_dotenv()

def get_int_env(key, default):
    val = os.getenv(key)
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DOWNLOAD_DIR = os.path.abspath(os.getenv("DOWNLOAD_DIR", "downloads"))
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

MAX_FILE_SIZE_MB = get_int_env("MAX_FILE_SIZE_MB", 100)
OWNER_ID = get_int_env("OWNER_ID", 0)
ALLOWED_GROUPS = [int(x) for x in os.getenv("ALLOWED_GROUPS", "").split(",") if x and x.strip().lstrip('-').isdigit()]
