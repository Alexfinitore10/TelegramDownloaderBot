from aiogram import types, F
from core.extractor import LinkExtractor
from core.downloader import Downloader
from core.processor import Processor
import os
import logging
import asyncio

logger = logging.getLogger(__name__)
extractor = LinkExtractor()
downloader = Downloader()

async def handle_text_message(message: types.Message):
    links = extractor.extract_links(message.text)
    video_links = extractor.filter_video_links(links)
    
    if not video_links:
        return

    for url in video_links:
        status_msg = await message.reply(f"🎬 Video detected! Starting download...")
        
        try:
            # 1. Download
            media_info = await downloader.download(url)
            if not media_info:
                await status_msg.edit_text("❌ Failed to download video. It might be too large or restricted.")
                continue
            
            # 2. Process/Compress
            await status_msg.edit_text("⚙️ Processing video...")
            final_path = await Processor.compress_if_needed(media_info['filename'])
            
            # 3. Upload
            await status_msg.edit_text("📤 Uploading to Telegram...")
            video = types.FSInputFile(final_path)
            await message.reply_video(
                video=video,
                caption=f"✅ {media_info['title']}",
                supports_streaming=True
            )
            
            await status_msg.delete()
            
            # 4. Cleanup
            if os.path.exists(media_info['filename']):
                os.remove(media_info['filename'])
            if final_path != media_info['filename'] and os.path.exists(final_path):
                os.remove(final_path)
                
        except Exception as e:
            logger.error(f"Error handling link {url}: {e}")
            await status_msg.edit_text(f"❌ Error: {str(e)}")
