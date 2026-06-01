import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F

# This is a skeleton. Real token will be provided by user later.
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello! I'm a Video Downloader Bot. Send me a link and I'll try to download it.")

@dp.message(F.text)
async def handle_message(message: types.Message):
    # This will be integrated with link extraction logic
    text = message.text
    await message.answer(f"I received your message: {text}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
