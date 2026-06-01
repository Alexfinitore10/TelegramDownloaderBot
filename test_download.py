import yt_dlp
import os

def download_video(url):
    print(f"Downloading: {url}")
    # Small video for testing: a short YouTube video (10-15 seconds)
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'max_filesize': 50 * 1024 * 1024, # 50MB limit for Telegram
    }
    
    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filesize = os.path.getsize(filename)
            print(f"SUCCESS: Downloaded '{filename}' ({filesize / 1024 / 1024:.2f} MB)")
            return filename
    except Exception as e:
        print(f"FAILURE: {str(e)}")
        return None

if __name__ == "__main__":
    # A public domain video or a very reliable short one
    test_url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ" # "Big Buck Bunny" trailer (short)
    download_video(test_url)
