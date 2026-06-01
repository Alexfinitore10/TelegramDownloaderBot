import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
