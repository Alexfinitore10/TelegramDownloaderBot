# Telegram Video Downloader Bot

A professional Telegram bot that automatically detects, downloads, and optimizes video links from multiple platforms (YouTube, Instagram, TikTok, Facebook, and more) using a Local Telegram Bot API server for high-capacity uploads.

## Key Features

- **Multi-Platform Support**: Powered by `yt-dlp` to support 1000+ sites.
- **Smart Compression**: 
  - Dynamic bitrate calculation to fit a **100MB** target.
  - Bitrate pre-check: skips compression if the original is already optimized.
  - GPU (NVENC) and CPU (VP9) support.
- **Robustness**:
  - Handles long filenames automatically using video IDs.
  - 30-minute duration limit.
  - Access control for Owner and specific Groups.
- **Production Ready**:
  - Local Telegram Bot API integration for bypassing the 50MB limit.
  - Automated Bug Reporting: sends crash details directly to the owner.
  - Persistent logging (`logs/bot.log` and `logs/bugs.log`).

## Setup & Deployment

### 1. Requirements
- Docker and Docker Compose
- Telegram Bot Token (from @BotFather)
- Telegram API ID & Hash (from my.telegram.org)

### 2. Configuration
Create a `.env` file in the root directory:
```env
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
OWNER_ID=your_numeric_telegram_id
ALLOWED_GROUPS=-100123456789, -100987654321
MAX_FILE_SIZE_MB=100
DOWNLOAD_DIR=downloads
```

### 3. Deployment
```bash
sudo docker compose up -d --build
```

### 4. Monitoring
- View logs: `sudo docker compose logs -f bot`
- Persistent logs are stored in the `./logs` directory.

## Project Structure
- `core/`: Core logic for extraction, downloading, and processing.
- `handlers/`: Telegram message handlers.
- `logs/`: Persistent log files.
- `main.py`: Entry point and bug reporting system.
- `config.py`: Environment configuration loader.
```