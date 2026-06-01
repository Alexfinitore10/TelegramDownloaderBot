import yt_dlp
import sys

def test_link(url):
    print(f"Testing URL: {url}")
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'simulate': True,
        'force_generic_extractor': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"SUCCESS: Found video '{info.get('title')}' from {info.get('extractor')}")
            return True
    except Exception as e:
        print(f"FAILURE: {str(e)}")
        return False

if __name__ == "__main__":
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", # Rick Astley
        "https://www.instagram.com/reels/C8S6f-yM_q4/", # Random Reel (might fail if private/auth needed)
        "https://www.tiktok.com/@khaby.lame/video/7375685584558230817", # TikTok
    ]
    
    results = [test_link(url) for url in test_urls]
    if all(results):
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
