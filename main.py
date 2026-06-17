import asyncio
import logging
import signal
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from config import TELEGRAM_TOKEN
from handlers.messages import handle_text_message

from datetime import datetime, time, timedelta

# Setup logging
import os
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create handlers
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler("logs/bot.log", maxBytes=1024*1024, backupCount=5)
bug_handler = RotatingFileHandler("logs/bugs.log", maxBytes=1024*1024, backupCount=5)
bug_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.WARNING, # Solo Errori e Warning per non bloattare il file
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        bug_handler,
        stream_handler
    ]
)
logger = logging.getLogger(__name__)

async def countdown_task(bot: Bot):
    import zoneinfo
    from config import ALLOWED_GROUPS, OWNER_ID
    target_date = datetime(2026, 6, 24).date()
    rome_tz = zoneinfo.ZoneInfo("Europe/Rome")
    
    # Lista destinatari: Gruppi + Owner
    recipients = list(ALLOWED_GROUPS)
    if OWNER_ID and OWNER_ID not in recipients:
        recipients.append(OWNER_ID)
    
    last_sent_hour = -1
    last_sent_date = None

    while True:
        now = datetime.now(rome_tz)
        today = now.date()
        current_hour = now.hour
        
        # 1. Giorno dell'uscita: 24 Giugno
        if today == target_date:
            # Messaggio delle 00:00
            if current_hour == 0 and last_sent_date != today:
                for chat_id in recipients:
                    try:
                        msg = await bot.send_message(chat_id, "DELTARUNE TODAY")
                        await bot.pin_chat_message(chat_id, msg.message_id)
                    except Exception as e:
                        logger.error(f"Errore countdown TODAY: {e}")
                last_sent_date = today

            # Messaggio delle 17:00
            if current_hour == 17 and last_sent_hour != 17:
                for chat_id in recipients:
                    try:
                        await bot.send_message(chat_id, "DELTARUNE CAPITOLO 5 OUT")
                    except Exception as e:
                        logger.error(f"Errore countdown OUT: {e}")
                last_sent_hour = 17
                # Dopo le 17 del 24 possiamo chiudere il task
                if current_hour >= 17:
                    break

        # 2. Giorno prima: 23 Giugno (Ogni ora)
        elif today == (target_date - timedelta(days=1)):
            if current_hour != last_sent_hour:
                for chat_id in recipients:
                    try:
                        await bot.send_message(chat_id, "TOMORROW")
                    except Exception as e:
                        logger.error(f"Errore countdown TOMORROW: {e}")
                last_sent_hour = current_hour
                last_sent_date = today

        # 3. Giorni precedenti (Solo a mezzanotte)
        elif today < (target_date - timedelta(days=1)):
            if current_hour == 0 and last_sent_date != today:
                days_left = (target_date - today).days
                text = f"Mancano {days_left} tomorrows a Deltarune"
                for chat_id in recipients:
                    try:
                        msg = await bot.send_message(chat_id, text)
                        await bot.pin_chat_message(chat_id, msg.message_id)
                    except Exception as e:
                        logger.error(f"Errore countdown daily: {e}")
                last_sent_date = today

        # 4. Fine countdown
        elif today > target_date:
            break

        # Aspettiamo un minuto prima di ricontrollare (per non martellare la CPU)
        await asyncio.sleep(60)

async def notify_owner_of_error(bot: Bot, error_msg: str):
    from config import OWNER_ID
    if OWNER_ID:
        try:
            await bot.send_message(OWNER_ID, f"🚨 **BUG REPORTED**\n\n🕒 Time: `{logging.Formatter('%(asctime)s').format(logging.LogRecord(None, None, None, None, None, None, None))}`\n\n❌ Error:\n`{error_msg[:3000]}`")
        except:
            pass

async def check_and_notify_update(bot: Bot):
    import config
    version_file = "version.txt"
    last_version_file = "logs/last_version.txt"
    changelog_file = "CHANGELOG.md"

    if not os.path.exists(version_file):
        return

    with open(version_file, "r") as f:
        current_version = f.read().strip()

    last_version = ""
    if os.path.exists(last_version_file):
        with open(last_version_file, "r") as f:
            last_version = f.read().strip()

    if current_version != last_version:
        logger.info(f"New version detected: {current_version}. Sending update notification.")
        
        # Read changelog
        changelog_text = "Nuovo aggiornamento disponibile!"
        if os.path.exists(changelog_file):
            with open(changelog_file, "r") as f:
                content = f.read()
                # Try to extract the first section (the most recent update)
                import re
                match = re.search(r"## \[[^\]]+\] - \d{4}-\d{2}-\d{2}\n(.*?)(?=\n## |$)", content, re.DOTALL)
                if match:
                    changelog_text = match.group(1).strip()
                else:
                    changelog_text = content[:4000] # Fallback to first 4k chars

        msg = f"🚀 **Bot Aggiornato alla v{current_version}**\n\nCosa c'è di nuovo:\n{changelog_text}"
        
        # Notify owner
        if config.OWNER_ID:
            try: await bot.send_message(config.OWNER_ID, msg, parse_mode="Markdown")
            except Exception as e: logger.error(f"Failed to notify owner: {e}")

        # Notify allowed groups
        for group_id in config.ALLOWED_GROUPS:
            try: await bot.send_message(group_id, msg, parse_mode="Markdown")
            except Exception as e: logger.error(f"Failed to notify group {group_id}: {e}")

        # Save current version as last version
        with open(last_version_file, "w") as f:
            f.write(current_version)

async def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in environment variables!")
        return

    # Initialize bot with Local API Server support
    from aiogram.client.telegram import TelegramAPIServer
    from aiogram.client.session.aiohttp import AiohttpSession
    from aiohttp import ClientTimeout
    
    # Abilitiamo la VERA modalità locale: il bot passerà il percorso del file invece dei byte HTTP
    local_server = TelegramAPIServer.from_base("http://telegram-bot-api:8081", is_local=True)
    
    # Impostiamo il timeout globale della sessione a 5 minuti
    session = AiohttpSession(
        api=local_server,
        timeout=300
    )
    bot = Bot(token=TELEGRAM_TOKEN, session=session)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(handle_text_message, F.text)
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("👋 Hi! I'm your automatic video downloader.\n\nJust send a link from YouTube, Instagram, TikTok, etc., and I'll send you the video back!")

    @dp.message(Command("test_deltarune"))
    async def cmd_test_deltarune(message: types.Message):
        from config import OWNER_ID
        if message.from_user.id != OWNER_ID:
            return
            
        target_date = datetime(2026, 6, 24).date()
        days_left = (target_date - datetime.now().date()).days
        text = f"TEST: Mancano {days_left} tomorrows a Deltarune"
        if days_left == 0: text = "TEST: Deltarune TODAY!"
        
        try:
            msg = await message.answer(text)
            await bot.pin_chat_message(message.chat.id, msg.message_id)
            await message.answer("✅ Test completato: Messaggio inviato e pinnato!")
        except Exception as e:
            await message.answer(f"❌ Errore durante il test di pinning: {e}")

    # Check for updates and notify
    await check_and_notify_update(bot)

    # Avvio task del countdown
    asyncio.create_task(countdown_task(bot))

    logger.warning("🤖 BOT AVVIATO - v0.2.0 è online e operativa!")

    # Graceful shutdown handling
    def signal_handler():
        logger.warning("📥 Segnale di spegnimento ricevuto...")
        asyncio.create_task(dp.stop_polling())

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    logger.info("Bot started and listening...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.warning("🔌 Bot session closed. Sistema spento.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
