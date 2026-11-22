# -*- coding: utf-8 -*-
"""짜깁기 스토리 영상: edl.json -> out/final.mp4
클립(타인 영상 짧게) + 자막 캡션 + 섹션 카드 + 최소 더빙(기존 TTS 재사용) + Statement BGM 크게(대사 때만 살짝 덕킹)"""
import hashlib, json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()); os.chdir(HERE)
FF = r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin'
YT = r'C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\yt-dlp.yt-dlp_Microsoft.Winget.Source_8wekyb3d8bbwe\yt-dlp.exe'
os.environ['PATH'] = FF + os.pathsep + os.environ['PATH']
FONTS = r'C:\Users\Admin\.aside\u\0\skills\user\star-story-video\assets\fonts'
OLD = r'C:\Users\Admin\.aside\u\0\sessions\2026-11-07_8X9mbbpbzFnhB8Tg\tmp\src'
WONI = r'C:\Users\Admin\.aside\u\0\sessions\2026-11-07_OXQgFF9i9xP3w1wi\tmp\woni'
MUSIC = os.environ.get('MUSIC') or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'statement.mp3')
MUSIC_GAIN = float(os.environ.get('MUSIC_GAIN', '2.7'))   # 이전 기본 0.78의 약 3.5배
W, H, FPS = 1920, 1080, 30
for d in ('dl', 'seg', 'txt', 'out'): os.makedirs(d, exist_ok=True)
for f in ('BlackHanSans.ttf', 'Pretendard-ExtraBold.otf', 'Pretendard-Bold.otf', 'Pretendard-Medium.otf'):
    shutil.copy(os.path.join(FONTS, f), f)
BH, XB, BD, MD = 'BlackHanSans.ttf', 'Pretendard-ExtraBold.otf', 'Pretendard-Bold.otf', 'Pretendard-Medium.otf'

def run(a, cwd=HERE):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y'] + a, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode: raise SystemExit('ffmpeg fail ' + ' '.join(a)[:400] + '\n' + r.stderr[-1500:])
def probe(p, what):
    return subprocess.run(['ffprobe', '-v', 'error'] + what + ['-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip()
def T(s):
    n = 'txt/%s.txt' % hashlib.md5(s.encode('utf-8')).hexdigest()[:12]
    open(n, 'w', encoding='utf-8').write(s); return n
def dt(s, font, size, x, y, color='white', extra=''):
    return "drawtext=fontfile=%s:textfile=%s:expansion=none:fontsize=%d:fontcolor=%s:x=%s:y=%s%s" % (font, T(s), size, color, x, y, (':' + extra) if extra else '')
def tw(s, size): return sum(size * (0.98 if ord(c) > 0x2E80 else 0.56) for c in s)

E = json.load(open('edl.json', encoding='utf-8'))
items = E['items']

# 1) download sections
for it in items:
    if 'id' not in it: continue
    a, b = max(0, it['s'] - 2), it['s'] + it['d'] + 2
    out = 'dl/%s_%d.mp4' % (it['id'], int(it['s']))
    it['file'] = out; it['off'] = it['s'] - a
    if os.path.exists(out) and os.path.getsize(out) > 10000: continue
    print('dl', it['id'], it['s'], flush=True)
    subprocess.run([YT, '-q', '-f', 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]/b', '--merge-output-format', 'mp4',
                    '--download-sections', '*%d-%d' % (a, b), '--force-keyframes-at-cuts', '-o', out, 'https://www.youtube.com/watch?v=' + it['id']])
for it in items:
    if 'local' in it:
        it['file'] = it['local'].replace('OLD/', OLD + os.sep).replace('WONI/', os.path.join(WONI, 'src') + os.sep); it['off'] = it['s']

# 2) segments
segs, voice_events, clip_spans, t = [], [], [], 0.0
def voice_wav(text):
    h = hashlib.md5(text.encode('utf-8')).hexdigest()[:12] + '.wav'
    for d in (os.path.join(HERE, 'lines'), os.path.join(WONI, 'lines')):
        p = os.path.join(d, h)
        if os.path.exists(p): return p
    print('NO VOICE WAV (run tts first):', text[:30]); return None
for i, it in enumerate(items):
    seg = 'seg/%03d.mp4' % i
    if 'sec' in it:                              # 섹션 타이틀 카드
        D = 2.4; txt = it['sec']
        yr, rest = (txt.split(' · ', 1) + [''])[:2]
        vf = ','.join(['noise=alls=4:allf=t', dt(yr, BH, 120, '(w-tw)/2', '(h-th)/2-70', '0xFFE01B', 'borderw=6:bordercolor=black'),
                       dt(rest, XB, 64, '(w-tw)/2', 'h/2+60', 'white'), 'fade=t=in:st=0:d=0.3,fade=t=out:st=%.2f:d=0.3' % (D - 0.3)])
        run(['-f', 'lavfi', '-i', 'color=c=0x08080C:s=%dx%d:r=%d' % (W, H, FPS), '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-vf', vf, '-t', '%.2f' % D,
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-shortest', seg])
    elif 'card' in it:
        D = it['d']; a, b = it['card']
        v = voice_wav(it.get('voice', '')) if it.get('voice') else None
        if v: D = max(D, float(probe(v, ['-show_entries', 'format=duration'])) + 1.2); voice_events.append((t + 0.4, v))
        size = 120 if tw(a, 120) < 1700 else int(1700 / tw(a, 1))
        bsize = 54 if tw(b, 54) < 1750 else int(1750 / tw(b, 1))
        vf = ','.join(['noise=alls=4:allf=t', dt(a, BH, size, '(w-tw)/2', '(h-th)/2-60', 'white', 'borderw=6:bordercolor=black'),
                       dt(b, XB, bsize, '(w-tw)/2', 'h/2+70', '0xFFE01B'), 'fade=t=in:st=0:d=0.4,fade=t=out:st=%.2f:d=0.5' % (D - 0.5)])
        run(['-f', 'lavfi', '-i', 'color=c=black:s=%dx%d:r=%d' % (W, H, FPS), '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-vf', vf, '-t', '%.2f' % D,
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '2', '-shortest', seg])
    else:
        f = it['file']; D = it['d']
        if not os.path.exists(f): print('MISSING', f); continue
        wh = probe(f, ['-select_streams', 'v:0', '-show_entries', 'stream=width,height']).split(',')
        vw, vh = int(wh[0]), int(wh[1])
        has_a = bool(probe(f, ['-select_streams', 'a', '-show_entries', 'stream=index']))
        if vh > vw * 0.9:   # 세로 영상: 흐린 배경 위에 가운데
            fc = ("[0:v]split=2[a][b];[a]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,boxblur=30:3,eq=brightness=-0.15[bg];"
                  "[b]scale=-2:%d[fg];[bg][fg]overlay=(W-w)/2:0" % (W, H, W, H, H))
        else:               # 가로: 살짝 확대(1.06) + 천천히 줌
            fc = ("[0:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,scale=w='trunc(%d*(1.06+0.03*t/%.2f)/2)*2':h=-2:eval=frame,crop=%d:%d"
                  % (W, H, W, H, W, D, W, H))
        yr, cap = (it.get('cap') or ['', ''])[:2]
        over = ['setsar=1', 'fps=%d' % FPS, 'eq=saturation=1.05:contrast=1.03']
        if cap or yr:
            capsize = 58 if tw(cap, 58) < 1500 else int(1500 / tw(cap, 1))
            over.append("drawbox=x=0:y=ih-190:w=iw:h=190:color=black@0.45:t=fill")
            if yr: over.append(dt(yr, BH, 50, '70', 'h-170', '0xFFE01B', 'borderw=4:bordercolor=black'))
            over.append(dt(cap, XB, capsize, '70', 'h-108', 'white', 'borderw=4:bordercolor=black'))
        over.append(dt('출처: ' + it.get('src', ''), MD, 24, 'w-tw-30', '26', 'white@0.85', 'box=1:boxcolor=black@0.4:boxborderw=8'))
        over.append('fade=t=in:st=0:d=0.2,fade=t=out:st=%.2f:d=0.2' % (D - 0.2))
        fc += ',' + ','.join(over) + '[v]'
        ins = ['-ss', '%.2f' % it['off'], '-t', '%.2f' % D, '-i', f]
        if has_a and it.get('a', 0) > 0:
            fc += ';[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.2f,afade=t=in:d=0.15,afade=t=out:st=%.2f:d=0.25,apad[aa]' % (it['a'], D - 0.25)
            amap = '[aa]'; extra = []
        else:
            extra = ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']; amap = '1:a'
        run(ins + extra + ['-filter_complex', fc, '-map', '[v]', '-map', amap, '-t', '%.2f' % D, '-r', str(FPS),
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '2', seg])
        if it.get('a', 0) > 0: clip_spans.append((t, t + D))
        if it.get('voice'):
            v = voice_wav(it['voice'])
            if v: voice_events.append((t + 0.3, v))
    d_real = float(probe(seg, ['-show_entries', 'format=duration']))
    segs.append(seg); t += d_real
    print('seg %d  t=%.1f' % (i, t), flush=True)
TOTAL = t
open('list.txt', 'w', encoding='utf-8').write(''.join("file '%s'\n" % s for s in segs))
run(['-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-ar', '48000', 'out/body.mp4'])

# 3) audio: 원본 대사 + 최소 더빙 + Statement(크게, 대사 때만 살짝 덕킹)
run(['-i', 'out/body.mp4', '-vn', '-ar', '48000', '-ac', '2', 'out/clipaudio.wav'])
vin, vf_ = ['-i', 'out/clipaudio.wav'], []
for k, (at, w) in enumerate(voice_events):
    vin += ['-i', w]; ms = int(at * 1000)
    vf_.append('[%d]aresample=48000,aformat=channel_layouts=stereo,volume=1.6,adelay=%d|%d[v%d]' % (k + 1, ms, ms, k))
mix_in = '[0]' + ''.join('[v%d]' % k for k in range(len(voice_events)))
fc = ';'.join(vf_ + [mix_in + 'amix=inputs=%d:normalize=0[o]' % (len(voice_events) + 1)]) if voice_events else '[0]anull[o]'
run(vin + ['-filter_complex', fc, '-map', '[o]', '-t', '%.2f' % TOTAL, 'out/speech.wav'])
run(['-stream_loop', '-1', '-i', MUSIC, '-t', '%.2f' % TOTAL, '-af', 'loudnorm=I=-18:TP=-2:LRA=11,afade=t=in:d=1.5,afade=t=out:st=%.2f:d=4' % (TOTAL - 4),
     '-ar', '48000', '-ac', '2', 'out/music.wav'])
run(['-i', 'out/speech.wav', '-i', 'out/music.wav', '-filter_complex',
     '[0]asplit=2[s][sc];[1]volume=%.2f[m];[m][sc]sidechaincompress=threshold=0.02:ratio=3:knee=4:attack=80:release=900[md];'
     '[s][md]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[o]' % MUSIC_GAIN, '-map', '[o]', '-ar', '48000', '-ac', '2', 'out/mix.wav'])
run(['-i', 'out/body.mp4', '-i', 'out/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', 'out/final.mp4'])
print('OUT out/final.mp4 %.1f s' % TOTAL)
