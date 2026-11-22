# -*- coding: utf-8 -*-
"""여의도여자 나레이션 생성 (여러 프로젝트가 동시에 불러도 Voicebox는 한 번에 하나씩).
사용: python tts_queue.py <proj>
 - <proj>/edl.json 의 모든 "voice" 문장을 <proj>/script.txt('> ' 줄)로 쓰고
 - 전역 잠금(tmp/tts.lock)을 잡은 뒤 star-story-video/scripts/tts.py <proj> 실행 -> <proj>/lines/<md5 12>.wav
 - 끝나면 'TTS DONE n' 출력."""
import json, os, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')
proj = os.path.abspath(sys.argv[1])
E = json.load(open(os.path.join(proj, 'edl.json'), encoding='utf-8'))
lines = [it['voice'].strip() for it in E['items'] if it.get('voice')]
open(os.path.join(proj, 'script.txt'), 'w', encoding='utf-8').write(''.join('> %s\n' % l for l in lines))
LOCK = r'C:\Users\Admin\.aside\u\0\sessions\2026-11-07_OXQgFF9i9xP3w1wi\tmp\tts.lock'
TTS = r'C:\Users\Admin\.aside\u\0\skills\user\star-story-video\scripts\tts.py'
FF = r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin'
os.environ['PATH'] = FF + os.pathsep + os.environ['PATH']; os.environ['PYTHONIOENCODING'] = 'utf-8'
while True:
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, proj.encode()); os.close(fd); break
    except FileExistsError:
        try:
            if time.time() - os.path.getmtime(LOCK) > 3 * 3600: os.remove(LOCK); continue
        except OSError: pass
        print('waiting for Voicebox lock...', flush=True); time.sleep(30)
try:
    r = subprocess.run([sys.executable, TTS, proj], cwd=proj)
finally:
    os.remove(LOCK)
print('TTS DONE', len(lines), 'rc', r.returncode)
