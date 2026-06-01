import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from config import TELEGRAM_TOKEN
from handlers.messages import handle_text_message

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in environment variables!")
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(handle_text_message, F.text)
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("👋 Hi! I'm your automatic video downloader.\n\nJust send a link from YouTube, Instagram, TikTok, etc., and I'll send you the video back!")

    logger.info("Bot started and listening...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
