# Agents.md - Telegram Downloader Bot Implementation Plan

## Overview
A Python-based Telegram bot that monitors chats for video hyperlinks, downloads the media using `yt-dlp`, and re-uploads it directly to the chat.

## Phase 1: Research & Discovery - [COMPLETED]
- [x] **Library Selection**: aiogram 3.x, yt-dlp, ffmpeg, urlextract.
- [x] **Feasibility Testing**: Verified YT download and FFmpeg compression.

## Phase 2: Core Module Development - [COMPLETED]
- [x] **Link Detection & Extraction**: Implemented in `core/extractor.py`.
- [x] **Media Downloader (`downloader.py`)**: Implemented async wrapper for `yt-dlp`.
- [x] **Media Processor (`processor.py`)**: Implemented 2-pass bitrate-based compression.

## Phase 3: Bot Pipeline Integration - [COMPLETED]
- [x] **Async Queue System**: Handled by `aiogram`'s polling and `asyncio.to_thread`.
- [x] **State & Cleanup**: Automatic cleanup of downloads and temp files in `handlers/messages.py`.

## Phase 4: Reliability & Sustainability - [COMPLETED]
- [x] **Format Optimization**: Implemented smart resolution selection to prioritize <50MB MP4s.
- [x] **Update Strategy**: User should run `pip install -U yt-dlp` periodically.
- [x] **Logging & Monitoring**: Basic logging implemented in `main.py`.

## Phase 5: Finalization - [IN PROGRESS]
- [x] Implementation of full project skeleton.
- [x] Verified auto-cleanup mechanism in handlers.
- [x] Successfully tested extraction, download, and compression modules.
- [x] Write the comprehensive prompt for LLM handoff (`LLM_PROMPT.md`).
- [ ] Final end-to-end integration tests (requires Token).

