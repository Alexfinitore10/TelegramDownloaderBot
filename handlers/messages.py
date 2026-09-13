from aiogram import types, F
from core.extractor import LinkExtractor
from core.downloader import Downloader
from core.processor import Processor
import config
import os
import logging
import asyncio

logger = logging.getLogger(__name__)
extractor = LinkExtractor()
downloader = Downloader()

# Limit to 1 concurrent video processing to save disk space
processing_semaphore = asyncio.Semaphore(1)

async def handle_text_message(message: types.Message):
    logger.info(f"Received message from {message.from_user.id} in chat {message.chat.id} ({message.chat.type})")
    
    # 0. Access Control
    is_owner = message.from_user.id == config.OWNER_ID
    is_allowed_user = message.from_user.id in config.ALLOWED_USERS
    is_group = message.chat.type in ["group", "supergroup"]
    is_allowed_group = message.chat.id in config.ALLOWED_GROUPS

    logger.debug(f"Access Check: owner={is_owner}, allowed_user={is_allowed_user}, group={is_group}, allowed_group={is_allowed_group}")

    if not (is_owner or is_allowed_user or (is_group and (not config.ALLOWED_GROUPS or is_allowed_group))):
        logger.warning(f"Access denied for user {message.from_user.id}")
        return

    if not message.text:
        logger.info("Message has no text, skipping.")
        return

    links = extractor.extract_links(message.text)
    video_links = extractor.filter_video_links(links)
    
    if not video_links:
        logger.info(f"No video links found in: {message.text[:50]}...")
        return

    logger.info(f"Found {len(video_links)} video links. Processing...")


    for url in video_links:
        # We wait our turn in the queue
        async with processing_semaphore:
            status_msg = await message.reply(f"📥 Media detected! Starting processing...")
            
            try:
                # 1. Download
                await status_msg.edit_text("⏳ Downloading media...")
                media_infos = await downloader.download(url)
                if not media_infos:
                    domain = extractor.get_domain(url)
                    await status_msg.edit_text(f"❌ Could not find any supported media in this {domain} link.")
                    continue
                
                for i, media_info in enumerate(media_infos):
                    temp_files = []
                    try:
                        prefix = f"[{i+1}/{len(media_infos)}] " if len(media_infos) > 1 else ""
                        
                        # Duration Check
                        duration = media_info.get('duration', 0)
                        if duration and duration > 1800: # 30 minutes
                            await message.reply(f"⚠️ {prefix}Video is too long ({int(duration/60)} min). Maximum allowed is 30 minutes.")
                            if os.path.exists(media_info['filename']):
                                os.remove(media_info['filename'])
                            continue

                        temp_files.append(media_info['filename'])
                        
                        # 2. Process/Compress with Progress Bar
                        async def progress_update(percent, status_text=None):
                            bar_length = 10
                            filled_length = int(bar_length * percent / 100)
                            bar = "▣" * filled_length + "▢" * (bar_length - filled_length)
                            text = f"⚙️ {prefix}Optimizing media...\n`[{bar}]` {percent}%\n"
                            if status_text:
                                text += f"_{status_text}_"
                            try:
                                await status_msg.edit_text(text, parse_mode="Markdown")
                            except Exception: pass

                        final_path = await Processor.compress_if_needed(
                            media_info['filename'], 
                            target_size_mb=config.MAX_FILE_SIZE_MB,
                            progress_callback=progress_update
                        )
                        if final_path != media_info['filename']:
                            temp_files.append(final_path)
                        
                        # 3. Upload
                        final_size = os.path.getsize(final_path) / (1024 * 1024)
                        logger.warning(f"File pronto per l'invio: {final_path} ({final_size:.2f}MB)")
                        await status_msg.edit_text(f"📤 {prefix}Uploading to Telegram ({final_size:.2f}MB)...")
                        
                        ext = os.path.splitext(final_path)[1].lower()
                        media_file = types.FSInputFile(final_path)
                        caption = f"✅ {media_info['title']}"
                        
                        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                            await message.reply_photo(
                                photo=media_file,
                                caption=caption
                            )
                            logger.warning(f"✅ Foto inviata con successo: {media_info['title']}")
                        elif ext in ['.gif']:
                            await message.reply_animation(
                                animation=media_file,
                                caption=caption
                            )
                            logger.warning(f"✅ GIF inviata con successo: {media_info['title']}")
                        else:
                            await message.reply_video(
                                video=media_file,
                                caption=caption,
                                supports_streaming=True
                            )
                            logger.warning(f"✅ Video inviato con successo: {media_info['title']}")
                    finally:
                        for f in temp_files:
                            if os.path.exists(f):
                                try: os.remove(f)
                                except: pass
                
                await status_msg.delete()
                    
            except asyncio.CancelledError:
                await status_msg.edit_text("⚠️ Process interrupted (Bot shutting down).")
                raise
            except Exception as e:
                logger.error(f"Error handling link {url}: {e}", exc_info=True)
                # Notify owner of the bug
                from main import notify_owner_of_error
                await notify_owner_of_error(message.bot, f"Link: {url}\nError: {str(e)}")
                
                try:
                    await status_msg.edit_text(f"❌ Error during processing: {str(e)[:100]}")
                except:
                    pass
