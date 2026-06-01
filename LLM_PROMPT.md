# LLM Handover Prompt: Telegram Video Downloader Bot

## Context
You are a senior Python developer tasked with finalizing a Telegram Bot that automatically detects video links (YouTube, Instagram, TikTok, etc.) and re-uploads the media to the chat. The project skeleton is already built using `aiogram 3.x`, `yt-dlp`, and `ffmpeg`.

## Current Project Structure
- `main.py`: Entry point using `aiogram`'s `Dispatcher`.
- `config.py`: Configuration loader via `python-dotenv`.
- `core/extractor.py`: Uses `urlextract` to find and filter video links.
- `core/downloader.py`: Asynchronous wrapper for `yt-dlp`.
- `core/processor.py`: Uses `ffmpeg` for 2-pass compression to fit Telegram's 50MB Bot API limit.
- `handlers/messages.py`: Main logic pipeline (Download -> Compress -> Upload -> Cleanup).

## Your Task
1. **API Integration**: Integrate the user-provided Telegram Bot Token into the `.env` file and verify connection.
2. **Enhanced Error Handling**: Implement more granular error handling in `core/downloader.py` for specific `yt-dlp` exceptions (e.g., private videos, region locks).
3. **Cookie Support**: Add a mechanism to load `cookies.txt` for `yt-dlp` to allow downloading from restricted platforms like Instagram and TikTok.
4. **User Feedback**: Improve the bot's messaging to provide progress updates (e.g., "Downloading 50%...", "Compressing...").
5. **Sustainability**: Implement a command (e.g., `/update`) to trigger `pip install -U yt-dlp` to keep the extractor up to date.
6. **Robust Cleanup**: Ensure that even on crash, the `downloads/` directory is purged of partially downloaded files.

## Technical Specifications
- **Language**: Python 3.10+
- **Framework**: aiogram 3.x
- **Extraction Engine**: yt-dlp (must be updated frequently)
- **Processing Engine**: ffmpeg (required for muxing and compression)
- **Deployment**: Must be suitable for long-running server processes (background/systemd).

## Constraints
- **File Limits**: Telegram Bot API has a hard limit of 50MB for uploads. Use the provided compression logic in `processor.py` to ensure videos fit.
- **Concurrency**: The bot must handle multiple links and multiple users simultaneously without blocking the main event loop.

Please review the existing codebase and implement these enhancements to make the bot production-ready.
