import asyncio
import logging
import signal
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from config import TELEGRAM_TOKEN
from handlers.messages import handle_text_message

# Setup logging
import os
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create handlers
file_handler = logging.FileHandler("logs/bot.log")
bug_handler = logging.FileHandler("logs/bugs.log")
bug_handler.setLevel(logging.ERROR)
stream_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        file_handler,
        bug_handler,
        stream_handler
    ]
)
logger = logging.getLogger(__name__)

async def notify_owner_of_error(bot: Bot, error_msg: str):
    from config import OWNER_ID
    if OWNER_ID:
        try:
            await bot.send_message(OWNER_ID, f"🚨 **BUG REPORTED**\n\n🕒 Time: `{logging.Formatter('%(asctime)s').format(logging.LogRecord(None, None, None, None, None, None, None))}`\n\n❌ Error:\n`{error_msg[:3000]}`")
        except:
            pass

async def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in environment variables!")
        return

    # Initialize bot with Local API Server support
    from aiogram.client.telegram import TelegramAPIServer
    from aiogram.client.session.aiohttp import AiohttpSession
    
    local_server = TelegramAPIServer.from_base("http://telegram-bot-api:8081")
    bot = Bot(token=TELEGRAM_TOKEN, session=AiohttpSession(api=local_server))
    dp = Dispatcher()

    # Register handlers
    dp.message.register(handle_text_message, F.text)
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("👋 Hi! I'm your automatic video downloader.\n\nJust send a link from YouTube, Instagram, TikTok, etc., and I'll send you the video back!")

    # Graceful shutdown handling
    def signal_handler():
        logger.info("Shutdown signal received...")
        asyncio.create_task(dp.stop_polling())

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    logger.info("Bot started and listening...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot session closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
