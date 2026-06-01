import subprocess
import os

def compress_video(input_path, output_path, target_size_mb):
    print(f"Compressing {input_path} to ~{target_size_mb}MB...")
    
    # Get duration
    cmd_duration = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
    duration = float(subprocess.check_output(cmd_duration).decode().strip())
    
    # Calculate target bitrate (bits per second)
    # size = bitrate * duration
    # bitrate = size / duration
    target_bitrate = (target_size_mb * 1024 * 1024 * 8) / duration
    
    # Subtract some for audio (roughly 128k)
    video_bitrate = target_bitrate - 128000
    if video_bitrate < 100000: video_bitrate = 100000 # Minimum 100kbps
    
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264', '-b:v', str(int(video_bitrate)),
        '-pass', '1', '-f', 'mp4', '/dev/null'
    ]
    subprocess.run(cmd)
    
    cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264', '-b:v', str(int(video_bitrate)),
        '-pass', '2', '-c:a', 'aac', '-b:a', '128k',
        output_path
    ]
    subprocess.run(cmd)
    
    if os.path.exists(output_path):
        new_size = os.path.getsize(output_path)
        print(f"SUCCESS: Compressed to {new_size / 1024 / 1024:.2f} MB")
        return output_path
    return None

if __name__ == "__main__":
    # Find the downloaded file from previous test
    download_dir = 'downloads'
    files = [f for f in os.listdir(download_dir) if f.endswith('.mp4')]
    if files:
        input_file = os.path.join(download_dir, files[0])
        output_file = 'compressed_test.mp4'
        compress_video(input_file, output_file, 5) # Compress to 5MB
    else:
        print("No input file found. Run test_download.py first.")
