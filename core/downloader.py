import yt_dlp
import os
import asyncio
import logging
import requests

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
        try:
            return await asyncio.to_thread(self._extract_info, url, ydl_opts)
        except Exception as e:
            # Se yt-dlp fallisce l'estrazione info (comune su TikTok senza login),
            # restituiamo None e lasciamo che il metodo download provi il fallback
            if "tiktok" in url.lower():
                logger.info(f"yt-dlp info extraction skipped/failed for TikTok (normal behavior): {e}")
            else:
                logger.warning(f"Info extraction failed for {url}: {e}")
            return None

    def _extract_info(self, url, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)

    async def _tiktok_fallback(self, url):
        """Metodo di fallback per TikTok usando TikWM API"""
        logger.info(f"Attempting TikTok fallback for {url}")
        from config import DOWNLOAD_DIR
        api_url = "https://www.tikwm.com/api/"
        
        try:
            res = await asyncio.to_thread(lambda: requests.post(api_url, data={"url": url}, timeout=15).json())
            if res.get("code") != 0:
                logger.error(f"TikWM API error: {res.get('msg')}")
                return None
            
            data = res["data"]
            video_url = data["play"]
            if not video_url.startswith("http"):
                video_url = "https://www.tikwm.com" + video_url
            
            video_id = data["id"]
            title = data.get("title", f"TikTok_{video_id}")
            filename = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
            
            # Download effettivo
            def _do_download():
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get(video_url, headers=headers, stream=True, timeout=30)
                if r.status_code == 200:
                    with open(filename, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return True
                return False

            success = await asyncio.to_thread(_do_download)
            if success:
                return [{
                    'filename': filename,
                    'title': title,
                    'duration': data.get("duration"),
                    'filesize': os.path.getsize(filename)
                }]
        except Exception as e:
            logger.error(f"TikTok fallback failed: {e}")
        return None

    async def download(self, url):
        from config import DOWNLOAD_DIR
        
        # Otteniamo info per decidere la qualità in base alla durata
        info = await self.get_info(url)
        duration = 0
        if info:
            duration = info.get('duration') or 0
        
        # Strategia: alta qualità per video brevi, degradazione graduale per video lunghi
        if duration == 0:
            fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' # Preferiamo MP4 nativi
        elif duration < 300: # < 5 minuti: Massima qualità
            fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif duration < 900: # < 15 minuti: Fino a 1080p
            fmt = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
        elif duration < 1800: # < 30 minuti: Fino a 720p
            fmt = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
        else: # > 30 minuti: 480p
            fmt = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'

        ydl_opts = {
            'format': fmt,
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
            'js_runtime': 'node',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        try:
            return await asyncio.to_thread(self._download, url, ydl_opts)
        except Exception as e:
            # Rilevamento specifico per TikTok (login required o errori di estrazione)
            if ("tiktok" in url.lower()) and ("login" in str(e).lower() or "extraction" in str(e).lower() or not info):
                logger.info(f"yt-dlp failed for TikTok (login required), trying fallback...")
                return await self._tiktok_fallback(url)
            
            logger.error(f"Download failed for {url}: {e}")
            return None

    def _download(self, url, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:
                # It's a playlist or multi-video post
                results = []
                for entry in info['entries']:
                    if not entry:
                        continue
                    filename = ydl.prepare_filename(entry)
                    if os.path.exists(filename):
                        results.append({
                            'filename': filename,
                            'title': entry.get('title') or info.get('title'),
                            'duration': entry.get('duration'),
                            'filesize': os.path.getsize(filename)
                        })
                return results
            else:
                # It's a single video
                filename = ydl.prepare_filename(info)
                return [{
                    'filename': filename,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'filesize': os.path.getsize(filename)
                }]
