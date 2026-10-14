"""Generate public-domain test media; never use purchased material in fixtures."""
import subprocess
from pathlib import Path

folder = Path('/fixtures/Verification Course')
folder.mkdir(parents=True, exist_ok=True)
video = folder / '01 Test lesson.mp4'
if not video.exists():
    subprocess.run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                    'color=c=blue:s=160x90:d=3', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(video)], check=True)
(folder / '01 Test lesson.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\nTest captions\n', encoding='utf-8')
(folder / '01 Test lesson.txt').write_text('Generated verification resource', encoding='utf-8')
print('Created generated verification media at', folder)
