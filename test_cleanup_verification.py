import os
import asyncio
from unittest.mock import AsyncMock, MagicMock
from handlers.messages import handle_text_message
from aiogram import types

async def test_cleanup_logic():
    print("Testing cleanup logic...")
    
    # Create a dummy file
    test_file = "downloads/cleanup_test.mp4"
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    with open(test_file, "w") as f:
        f.write("test data")
    
    print(f"Created dummy file: {test_file}")
    
    # Mock Telegram message
    message = AsyncMock(spec=types.Message)
    message.text = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    
    # status_msg should have awaitable methods
    status_msg = AsyncMock(spec=types.Message)
    status_msg.edit_text = AsyncMock()
    status_msg.delete = AsyncMock()
    
    message.reply = AsyncMock(return_value=status_msg)
    message.reply_video = AsyncMock()
    
    # Mock Downloader and Processor to return our dummy file
    import handlers.messages
    handlers.messages.downloader.download = AsyncMock(return_value={
        'filename': test_file,
        'title': 'Test Video',
        'duration': 10,
        'filesize': 100
    })
    handlers.messages.Processor.compress_if_needed = AsyncMock(return_value=test_file)
    
    # Run the handler
    await handle_text_message(message)
    
    # Verify cleanup
    if not os.path.exists(test_file):
        print("SUCCESS: Dummy file was automatically deleted after processing.")
    else:
        print("FAILURE: Dummy file still exists.")
        os.remove(test_file)

if __name__ == "__main__":
    asyncio.run(test_cleanup_logic())
