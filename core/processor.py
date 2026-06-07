import subprocess
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class Processor:
    @staticmethod
    async def compress_if_needed(file_path, target_size_mb=100, progress_callback=None):
        current_size = os.path.getsize(file_path)
        if current_size <= target_size_mb * 1024 * 1024:
            return file_path

        output_path = file_path.rsplit('.', 1)[0] + '_compressed.mp4'
        logger.info(f"Compressing {file_path} as it exceeds limit ({current_size/1024/1024:.2f}MB).")
        
        # Now calling the async _compress directly
        success = await Processor._compress(file_path, output_path, target_size_mb, progress_callback)
        if success and os.path.exists(output_path):
            if os.path.getsize(output_path) < current_size:
                return output_path
            else:
                logger.info("Compressed file is larger than original. Keeping original.")
                try: os.remove(output_path)
                except: pass
        return file_path

    @staticmethod
    def _has_nvenc():
        try:
            # Simple check, can stay synchronous as it's only called once at start or during logic
            result = subprocess.run(
                ['ffmpeg', '-encoders'], 
                capture_output=True, text=True, check=True
            )
            return 'h264_nvenc' in result.stdout
        except:
            return False

    @staticmethod
    async def _compress(input_path, output_path, target_size_mb, progress_callback=None):
        try:
            # Get duration and bitrate using ffprobe
            cmd_probe = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration,bit_rate', '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
            probe_proc = await asyncio.create_subprocess_exec(*cmd_probe, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, _ = await probe_proc.communicate()
            probe_data = stdout.decode().strip().split('\n')
            
            duration = float(probe_data[0])
            try:
                original_bitrate_kbps = int(probe_data[1]) / 1000
            except:
                original_bitrate_kbps = 0
            
            # Calculate target bitrate to fit target_size_mb
            # We subtract a bit for safety and audio
            target_bitrate_kbps = int((target_size_mb * 0.95 * 8192) / duration)
            video_bitrate_kbps = min(10000, target_bitrate_kbps - 192) # Max 10Mbps for high quality
            if video_bitrate_kbps < 400: video_bitrate_kbps = 400 # Min 400kbps
            
            # PRE-CHECK: If original bitrate is already lower than target, don't compress
            if original_bitrate_kbps > 0 and original_bitrate_kbps <= video_bitrate_kbps * 1.1:
                logger.info(f"Original bitrate ({original_bitrate_kbps:.0f}kbps) is already near or below target ({video_bitrate_kbps}kbps). Skipping compression.")
                return True

            logger.info(f"Target bitrate: {video_bitrate_kbps}kbps for {target_size_mb}MB target. Original: {original_bitrate_kbps:.0f}kbps.")
            
            # Check available encoders
            encoders_proc = await asyncio.create_subprocess_exec('ffmpeg', '-encoders', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, _ = await encoders_proc.communicate()
            encoders = stdout.decode()
            
            common_args = ['-y', '-hide_banner', '-loglevel', 'info', '-stats', '-i', input_path]

            if 'hevc_nvenc' in encoders:
                logger.info("Using GPU HEVC (H.265) with high-quality settings.")
                cmd = common_args + [
                    '-c:v', 'hevc_nvenc', '-rc', 'vbr', '-b:v', f'{video_bitrate_kbps}k',
                    '-maxrate', f'{int(video_bitrate_kbps * 1.5)}k', '-bufsize', f'{video_bitrate_kbps * 2}k',
                    '-preset', 'p4', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', output_path
                ]
            else:
                logger.info("Using CPU (VP9) with High Quality settings.")
                cmd = common_args + [
                    '-c:v', 'libvpx-vp9', '-b:v', f'{video_bitrate_kbps}k', 
                    '-crf', '30', '-deadline', 'good', '-cpu-used', '2', '-row-mt', '1',
                    '-pix_fmt', 'yuv420p', '-c:a', 'libopus', '-b:a', '128k', output_path
                ]

            success = await Processor._run_ffmpeg_with_progress(cmd, duration, progress_callback)
            
            # Fallback if GPU failed or file is empty
            if not success or not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                if 'nvenc' in str(cmd):
                    logger.warning("GPU failed or produced empty file, falling back to HQ CPU...")
                    if progress_callback: await progress_callback(0, "GPU failed, switching to CPU...")
                    cmd_cpu = common_args + [
                        '-c:v', 'libvpx-vp9', '-crf', '31', '-b:v', '0',
                        '-deadline', 'realtime', '-cpu-used', '4', '-row-mt', '1',
                        '-pix_fmt', 'yuv420p', '-c:a', 'libopus', '-b:a', '128k', output_path
                    ]
                    success = await Processor._run_ffmpeg_with_progress(cmd_cpu, duration, progress_callback)

            return success
        except Exception as e:
            logger.error(f"Compression manager error: {e}")
            return False
        finally:
            # Cleanup ffmpeg2pass log files if any
            for f in os.listdir('.'):
                if f.startswith('ffmpeg2pass'):
                    try: os.remove(f)
                    except: pass

    @staticmethod
    async def _run_ffmpeg_with_progress(cmd, total_duration, progress_callback):
        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                'ffmpeg', *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            last_update_time = 0
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                line_str = line.decode().strip()
                if "time=" in line_str and progress_callback:
                    try:
                        time_part = line_str.split("time=")[1].split(" ")[0]
                        h, m, s = time_part.split(':')
                        current_time = int(h)*3600 + int(m)*60 + float(s)
                        
                        progress = min(100, int((current_time / total_duration) * 100))
                        
                        now = asyncio.get_event_loop().time()
                        if now - last_update_time > 2.5:
                            logger.info(f"Compression progress: {progress}%")
                            await progress_callback(progress)
                            last_update_time = now
                    except:
                        continue

            await process.wait()
            return process.returncode == 0
        except asyncio.CancelledError:
            if process:
                try:
                    process.terminate()
                    logger.info("FFmpeg process terminated due to cancellation.")
                except: pass
            raise
        except Exception as e:
            logger.error(f"FFmpeg execution error: {e}")
            return False
