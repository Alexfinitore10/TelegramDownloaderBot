import subprocess
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class Processor:
    @staticmethod
    async def compress_if_needed(file_path, target_size_mb=45):
        current_size = os.path.getsize(file_path)
        if current_size <= target_size_mb * 1024 * 1024:
            return file_path

        output_path = file_path.rsplit('.', 1)[0] + '_compressed.mp4'
        logger.info(f"Compressing {file_path} as it exceeds limit.")
        
        success = await asyncio.to_thread(Processor._compress, file_path, output_path, target_size_mb)
        if success:
            return output_path
        return file_path # Fallback to original if compression fails

    @staticmethod
    def _compress(input_path, output_path, target_size_mb):
        try:
            # Get duration
            cmd_duration = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
            duration = float(subprocess.check_output(cmd_duration).decode().strip())
            
            target_bitrate = (target_size_mb * 1024 * 1024 * 8) / duration
            video_bitrate = target_bitrate - 128000
            if video_bitrate < 100000: video_bitrate = 100000

            # Pass 1
            subprocess.run([
                'ffmpeg', '-y', '-i', input_path,
                '-c:v', 'libx264', '-b:v', str(int(video_bitrate)),
                '-pass', '1', '-an', '-f', 'mp4', '/dev/null'
            ], check=True)
            
            # Pass 2
            subprocess.run([
                'ffmpeg', '-y', '-i', input_path,
                '-c:v', 'libx264', '-b:v', str(int(video_bitrate)),
                '-pass', '2', '-c:a', 'aac', '-b:a', '128k',
                output_path
            ], check=True)
            
            return os.path.exists(output_path)
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return False
        finally:
            # Cleanup ffmpeg2pass log files
            for f in os.listdir('.'):
                if f.startswith('ffmpeg2pass'):
                    os.remove(f)
