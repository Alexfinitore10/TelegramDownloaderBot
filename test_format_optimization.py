import asyncio
from core.downloader import Downloader
import os
import logging

# Set up logging to see what yt-dlp is doing
logging.basicConfig(level=logging.INFO)

async def test_format_selection():
    dl = Downloader()
    # A known high-res video (4K)
    url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ" # Big Buck Bunny 4K
    
    print(f"Testing format selection for: {url}")
    result = await dl.download(url)
    
    if result:
        size_mb = result['filesize'] / (1024 * 1024)
        print(f"SUCCESS: Downloaded '{result['filename']}'")
        print(f"Final Size: {size_mb:.2f} MB")
        
        # Cleanup
        if os.path.exists(result['filename']):
            os.remove(result['filename'])
            print("File cleaned up.")
    else:
        print("FAILURE: Download failed.")

if __name__ == "__main__":
    asyncio.run(test_format_selection())
