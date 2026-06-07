import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 100))
OWNER_ID = int(os.getenv("OWNER_ID", 0))
ALLOWED_GROUPS = [int(x) for x in os.getenv("ALLOWED_GROUPS", "").split(",") if x]
