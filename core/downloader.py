import yt_dlp
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, download_dir='downloads'):
        self.download_dir = download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    async def get_info(self, url):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'simulate': True,
        }
        return await asyncio.to_thread(self._extract_info, url, ydl_opts)

    def _extract_info(self, url, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    async def download(self, url):
        ydl_opts = {
            # Prefer MP4s under 50MB natively.
            # If unavailable, prefer MP4s <= 720p resolution.
            # Fallback to general best format if the above criteria aren't met.
            'format': 'best[ext=mp4][filesize<50M]/best[ext=mp4][height<=720]/best[ext=mp4]/best',
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'max_filesize': 50 * 1024 * 1024, # yt-dlp will still abort if it picks a format > 50MB
            # Use node as JS runtime if available for extraction
            'js_runtime': 'node',
        }
        
        try:
            return await asyncio.to_thread(self._download, url, ydl_opts)
        except Exception as e:
            logger.error(f"Download failed for {url}: {e}")
            return None

    def _download(self, url, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return {
                'filename': filename,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'filesize': os.path.getsize(filename)
            }
