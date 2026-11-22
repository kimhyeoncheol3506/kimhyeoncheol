# -*- coding: utf-8 -*-
"""보조 도구. 사용: python tools.py <명령> <프로젝트폴더> [인자]
  base-img <proj>                 기본 AI 재연 이미지 42장(assets 경로 or 원본 세션)을 proj/img 로 복사
  prep-img <proj> <genpaths.json> imagegen 결과 PNG들을 렌더러용 1024x1024(가운데 띠)로 맞춰 proj/img/<이름>.png 저장
  sheet <proj> <video.mp4> [n]    영상에서 n(기본20)장 프레임 + 타임코드 시트 -> proj/src/sheet_<이름>.jpg
  dl <proj> <id> <name> <start> <end>   유튜브 구간만 다운로드 -> proj/src/<name>.mp4 (explorer.exe 로 띄운 bat 안에서 실행 권장)
  bgm <proj>                      proj/bgm/*.mp3 를 -18 LUFS wav 로 정규화
  thumb <proj>                    proj/thumb/thumb.json 대로 1280x720 썸네일 생성
"""
import json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(SKILL, 'assets', 'fonts')
FF = r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin'
YT = r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\yt-dlp.yt-dlp_Microsoft.Winget.Source_8wekyb3d8bbwe\yt-dlp.exe'
BASE_IMG = r'C:\Users\Admin\.aside\u\0\sessions\2026-11-07_8X9mbbpbzFnhB8Tg\tmp\full\img'
os.environ['PATH'] = FF + os.pathsep + os.environ['PATH']

def ff(args, cwd=None):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y'] + args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode: raise SystemExit(r.stderr[-1500:])

def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip())

cmd, proj = sys.argv[1], os.path.abspath(sys.argv[2])
for d in ('img', 'src', 'bgm', 'thumb', 'out'): os.makedirs(os.path.join(proj, d), exist_ok=True)

if cmd == 'base-img':
    src = os.path.join(SKILL, 'assets', 'img') if os.path.isdir(os.path.join(SKILL, 'assets', 'img')) else BASE_IMG
    for f in os.listdir(src):
        if f.endswith('.png'): shutil.copy(os.path.join(src, f), os.path.join(proj, 'img', f))
    print('copied', len(os.listdir(os.path.join(proj, 'img'))))
elif cmd == 'prep-img':
    g = json.load(open(sys.argv[3], encoding='utf-8'))
    for name, p in g.items():
        ff(['-i', p, '-vf', "scale=1024:-2,crop=1024:'min(ih,1024)',pad=1024:1024:0:(1024-ih)/2:black", os.path.join(proj, 'img', name + '.png')])
        print('img', name)
elif cmd == 'sheet':
    v = sys.argv[3]; n = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    shutil.copy(os.path.join(FONTS, 'Pretendard-Bold.otf'), os.path.join(proj, 'src', 'pb.otf'))
    step = max(1.0, round(dur(v) / n, 1))
    out = os.path.join(proj, 'src', 'sheet_' + os.path.splitext(os.path.basename(v))[0] + '.jpg')
    ff(['-i', v, '-vf', "fps=1/%s,scale=384:-2,drawtext=fontfile=pb.otf:text='%%{pts\\:hms}':fontsize=26:fontcolor=yellow:box=1:boxcolor=black@0.7:x=6:y=6,tile=5x4" % step, '-frames:v', '1', out], cwd=os.path.join(proj, 'src'))
    print(out, 'step', step)
elif cmd == 'dl':
    vid, name, a, b = sys.argv[3:7]
    subprocess.run([YT, '-q', '-f', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b', '--merge-output-format', 'mp4', '--download-sections', '*%s-%s' % (a, b),
                    '--force-keyframes-at-cuts', '-o', name + '.%(ext)s', 'https://www.youtube.com/watch?v=' + vid], cwd=os.path.join(proj, 'src'))
    print('dl', name)
elif cmd == 'bgm':
    d = os.path.join(proj, 'bgm')
    for f in os.listdir(d):
        if f.lower().endswith('.mp3'):
            out = os.path.join(d, os.path.splitext(f)[0].split(' - ')[0].replace(' ', '').lower() + '.wav')
            ff(['-i', os.path.join(d, f), '-af', 'loudnorm=I=-18:TP=-2:LRA=11', '-ar', '48000', '-ac', '2', out])
            print(os.path.basename(out), round(dur(out), 1))
elif cmd == 'thumb':
    # thumb.json: {"left": "img/xxx.png", "right": "thumb/face.png", "right_crop": "w:h:x:y",
    #              "title": "...", "left_text": "...", "right_text": "...", "out": "thumb_A.jpg"}  (variants: list of these)
    td = os.path.join(proj, 'thumb')
    for f in ('BlackHanSans.ttf', 'Pretendard-ExtraBold.otf'): shutil.copy(os.path.join(FONTS, f), os.path.join(td, f))
    cfg = json.load(open(os.path.join(td, 'thumb.json'), encoding='utf-8'))
    for k, c in enumerate(cfg if isinstance(cfg, list) else [cfg]):
        def T(n, s):
            open(os.path.join(td, n), 'w', encoding='utf-8').write(s); return n
        T('t%d_title.txt' % k, c['title']); T('t%d_l.txt' % k, c['left_text']); T('t%d_r.txt' % k, c['right_text']); T('t_arrow.txt', '→')
        def tx(f, size, x, y, col='white'):
            return "drawtext=fontfile=BlackHanSans.ttf:textfile=%s:fontsize=%d:fontcolor=%s:borderw=10:bordercolor=black:x=%s:y=%s" % (f, size, col, x, y)
        ls = 70 if len(c['left_text']) > 7 else 96
        rs = 104 if len(c['right_text']) <= 6 else 84
        fc = ("[0:v]crop=1024:1024:0:0,scale=720:720,crop=640:720:40:0,hue=s=0,eq=contrast=1.12:brightness=-0.06[l];"
              "[1:v]crop=%s,scale=640:720,eq=saturation=1.08:contrast=1.04[r];[l][r]hstack=inputs=2,format=rgb24,"
              "drawbox=x=0:y=0:w=1280:h=170:color=black@0.55:t=fill,drawbox=x=0:y=540:w=1280:h=180:color=black@0.45:t=fill,"
              "drawbox=x=637:y=170:w=6:h=370:color=white@0.9:t=fill," % c['right_crop']
              + tx('t%d_title.txt' % k, 132 if len(c['title']) <= 8 else 104, '(w-tw)/2', '22') + ','
              + tx('t%d_l.txt' % k, ls, '(640-tw)/2', '590' if ls == 70 else '575') + ','
              + "drawtext=fontfile=Pretendard-ExtraBold.otf:textfile=t_arrow.txt:fontsize=96:fontcolor=0xFFE01B:borderw=8:bordercolor=black:x=(w-tw)/2:y=572,"
              + tx('t%d_r.txt' % k, rs, '640+(640-tw)/2', '572' if rs == 104 else '588', '0xFFE01B') + ','
              + "drawtext=fontfile=Pretendard-ExtraBold.otf:text='AI 재연':fontsize=18:fontcolor=white@0.6:x=12:y=182")
        ff(['-i', os.path.join(proj, c['left']), '-i', os.path.join(proj, c['right']), '-filter_complex', fc, '-frames:v', '1', '-q:v', '2', c.get('out', 'thumb_%d.jpg' % k)], cwd=td)
        print('thumb', c.get('out'))
