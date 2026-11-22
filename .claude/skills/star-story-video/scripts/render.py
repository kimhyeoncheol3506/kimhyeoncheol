# -*- coding: utf-8 -*-
"""스타 서사 영상 렌더러. 프로젝트 폴더의 config.json + script.txt + lines/*.wav + img/*.png + clips.json + music.json -> out/final.mp4 script.txt + lines/*.wav + img/*.png + clips.json -> out/final.mp4
사용: python render_full.py [--preview N초] [--only 챕터번호]"""
import hashlib, json, math, os, re, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else os.getcwd()); os.chdir(HERE)
B = '_b'; os.makedirs(B, exist_ok=True); os.makedirs(os.path.join(B, 'seg'), exist_ok=True)
CFG = json.load(open('config.json', encoding='utf-8'))
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(SKILL, 'assets', 'fonts')
WSRC = os.path.join(HERE, 'src')
BGM = os.path.join(HERE, 'bgm')
for f in ('Pretendard-Bold.otf', 'Pretendard-ExtraBold.otf', 'Pretendard-Medium.otf'):
    shutil.copy(os.path.join(SRC, f), os.path.join(B, f))
W, H, FPS = 1920, 1080, 30
BOLD, XB, MED = 'Pretendard-Bold.otf', 'Pretendard-ExtraBold.otf', 'Pretendard-Medium.otf'
GOLD, NAVY = '0xFFD24A', '0x0E1020'
GAP, LEAD, TAIL = 1.0, 0.7, 0.9
CLIPS = json.load(open('clips.json', encoding='utf-8')) if os.path.exists('clips.json') else {}
ARGS = sys.argv[1:]
ONLY = int(ARGS[ARGS.index('--only') + 1]) if '--only' in ARGS else None
PRESET = 'veryfast'

def run(args, cwd=B):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y'] + args, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise SystemExit('ffmpeg fail: ' + ' '.join(args)[:600] + '\n' + r.stderr[-2000:])

def dur(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True)
    return float(r.stdout.strip())

_tc = [0]
def T(text):
    _tc[0] += 1
    n = 'txt/%s.txt' % hashlib.md5(text.encode('utf-8')).hexdigest()[:16]
    os.makedirs(os.path.join(B, 'txt'), exist_ok=True)
    open(os.path.join(B, n), 'w', encoding='utf-8').write(text)
    return n

def fa(a, b=None, f=0.35):
    if b is None:
        return "alpha='if(lt(t,%.2f),0,if(lt(t,%.2f),(t-%.2f)/%.2f,1))'" % (a, a + f, a, f)
    return ("alpha='if(lt(t,%.2f),0,if(lt(t,%.2f),(t-%.2f)/%.2f,if(lt(t,%.2f),1,if(lt(t,%.2f),(%.2f-t)/%.2f,0))))'"
            % (a, a + f, a, f, b - f, b, b, f))

def dt(text, font, size, x, y, color='white', extra=''):
    return "drawtext=fontfile=%s:textfile=%s:expansion=none:fontsize=%d:fontcolor=%s:x=%s:y=%s%s" % (font, T(text), size, color, x, y, (':' + extra) if extra else '')

def tw(s, size):
    return sum(size * (0.98 if ord(c) > 0x2E80 else 0.56) for c in s)

def wrap(s, size, maxw):
    words, lines, cur = s.split(' '), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if tw(t, size) > maxw and cur:
            lines.append(cur); cur = w_
        else:
            cur = t
    if cur: lines.append(cur)
    return lines

def block(text, font, size, cy, color, extra, maxw=1500, lh=1.35):
    ls = wrap(text, size, maxw)
    y0 = cy - (len(ls) * size * lh) / 2
    return [dt(l, font, size, '(w-tw)/2', '%d' % (y0 + i * size * lh), color, extra) for i, l in enumerate(ls)]

def subs(lines_at, D):
    out = []
    for a, b, text in lines_at:
        ls = wrap(text, 46, 1500)
        n = len(ls)
        for k, l in enumerate(ls):
            y = H - 120 - (n - k) * 64
            out.append(dt(l, BOLD, 46, '(w-tw)/2', '%d' % y, 'white', 'box=1:boxcolor=black@0.55:boxborderw=14:' + fa(a, min(b, D), 0.15)))
    return out

# ---------------- parse ----------------
def hk(line):
    return hashlib.md5(line.encode('utf-8')).hexdigest()[:12]

shots, chapter = [], 0
cur = None
def new_shot(kind, arg, **kw):
    global cur
    cur = dict(kind=kind, arg=arg, ch=chapter, items=[], **kw); shots.append(cur); return cur
for raw in open('script.txt', encoding='utf-8').read().splitlines():
    s = raw.strip()
    if not s: continue
    if s.startswith('## '):
        p = s[3:].split('|'); chapter = int(p[0])
        if chapter > 0: new_shot('chapter', p, fixed=7.5)
        cur = None if chapter == 0 else cur
        continue
    if s.startswith('> '):
        if cur is None or cur['kind'] in ('chapter', 'dday', 'cmt', 'title', 'end'):
            new_shot('hold', None)
        cur['items'].append(('line', s[2:].strip()))
        continue
    m = re.match(r'\[(\w+)\s*(.*)\]$', s)
    if not m: continue
    tag, arg = m.group(1), m.group(2)
    if tag == 'pause':
        if cur is None: new_shot('black', 'ㅤ|')
        cur['items'].append(('pause', float(arg)))
    elif tag == 'cmt':
        if cur is not None and cur['kind'] == 'cmt' and len(cur['arg']) < 3:
            cur['arg'].append(arg.split('|'))
        else:
            new_shot('cmt', [arg.split('|')])
    elif tag == 'dday': new_shot('dday', arg.split('|'), fixed=4.2)
    elif tag == 'title': new_shot('title', None, fixed=5.0)
    elif tag == 'end': new_shot('end', None, fixed=12.0)
    elif tag == 'clip':
        if arg in CLIPS: new_shot('clip', arg)
        else: print('  (clip 없음, 건너뜀)', arg)
    else:
        new_shot(tag, arg)

# hold = continue previous visual (re-use the last visual shot spec)
last_vis = None
for sh in shots:
    if sh['kind'] == 'hold':
        if last_vis: sh['kind'], sh['arg'] = last_vis
        else: sh['kind'], sh['arg'] = 'black', 'ㅤ|'
    elif sh['kind'] in ('img', 'card', 'quote', 'promise', 'rank', 'clip', 'split', 'black'):
        last_vis = (sh['kind'], sh['arg'])

# split clip shots: clip only as long as the clip itself, then cut to an AI image (no freeze-frames)
AFTER = {}

def item_d(it):
    if it[0] == 'pause': return it[1]
    wav = os.path.join('lines', hk(it[1]) + '.wav')
    return (dur(wav) if os.path.exists(wav) else max(1.5, len(it[1]) / 6.9)) + GAP
_ns = []
for sh in shots:
    _ns.append(sh)
    if sh['kind'] == 'clip' and sh['items']:
        c = CLIPS[sh['arg']]; cap = (c['to'] - c['ss']) * 1.25 + 0.6
        t = LEAD; keep, rest = [], []
        for it in sh['items']:
            d = item_d(it)
            if not rest and (t + d <= cap or not keep):
                keep.append(it); t += d
            else:
                rest.append(it)
        sh['items'] = keep
        if rest:
            alt = c.get('after') or CFG.get('after_default', 'mic_empty')
            _ns.append(dict(kind='img', arg=alt, ch=sh['ch'], items=rest))
shots = _ns

# long image shots: change picture every ~18s (pool per chapter) so the screen never sits still too long
POOL = {int(k): v for k, v in CFG.get('pool', {}).items()}

_ns = []
for sh in shots:
    if sh['kind'] != 'img' or not sh['items']:
        _ns.append(sh); continue
    chunks, cur_, t = [], [], LEAD
    for it in sh['items']:
        d = item_d(it)
        if cur_ and t + d > 19.0:
            chunks.append(cur_); cur_, t = [], LEAD
        cur_.append(it); t += d
    if cur_: chunks.append(cur_)
    base = sh['arg'].split()[0]; extra = ' '.join(sh['arg'].split()[1:])
    pool = [x for x in POOL.get(sh['ch'], []) if x != base] or [base]
    pi = (sum(map(ord, base)) % len(pool))
    for k, ch_items in enumerate(chunks):
        name = base if k == 0 else pool[(pi + k) % len(pool)]
        _ns.append(dict(kind='img', arg=(name + ' ' + extra).strip() if k == 0 else name, ch=sh['ch'], items=ch_items))
shots = _ns

# durations from narration
for sh in shots:
    t = LEAD; ats = []
    for it in sh['items']:
        if it[0] == 'line':
            wav = os.path.join('lines', hk(it[1]) + '.wav')
            d = dur(wav) if os.path.exists(wav) else max(1.5, len(it[1]) / 6.9)
            ats.append((t, t + d, it[1], wav)); t += d + GAP
        else:
            t += it[1]
    t = t - (GAP if ats and sh['items'][-1][0] == 'line' else 0) + TAIL
    if sh['kind'] == 'cmt':
        t = 2.0 + 3.2 * len(sh['arg']) + 3.0
    if sh['kind'] == 'clip':
        c = CLIPS[sh['arg']]; cl = c['to'] - c['ss']
        if not sh['items']: t = cl
    if 'fixed' in sh and not sh['items']: t = sh['fixed']
    if sh['kind'] == 'rank' and sh['arg'] in ('climb',): t = max(t, 7.5)
    sh['D'] = round(max(t, 1.2), 3); sh['ats'] = ats

if '--dry' in ARGS:
    from collections import defaultdict
    per = defaultdict(float)
    for s in shots: per[s['ch']] += s['D']
    for k in sorted(per): print('ch', k, '%.1f min' % (per[k] / 60))
    print('TOTAL %.1f min, shots %d' % (sum(per.values()) / 60, len(shots))); sys.exit(0)
if ONLY is not None:
    shots = [s for s in shots if s['ch'] == ONLY]

# ---------------- visuals ----------------
def img_input(name):
    p = os.path.abspath(os.path.join('img', name + '.png'))
    return p

MOVES = ['zin', 'pl', 'zout', 'pr', 'pu']
def v_img(sh, idx, D):
    a = sh['arg'].split(); name = a[0]; bw = 'bw' in a[1:]
    mv = MOVES[idx % len(MOVES)]
    base = "crop=1024:576:0:224,scale=2208:1242:flags=lanczos"
    if mv == 'zin':
        motion = "scale=w='trunc(2208*(1+0.06*t/%.2f)/2)*2':h=-2:eval=frame,crop=1920:1080:(iw-1920)/2:(ih-1080)/2" % D
    elif mv == 'zout':
        motion = "scale=w='trunc(2208*(1.06-0.06*t/%.2f)/2)*2':h=-2:eval=frame,crop=1920:1080:(iw-1920)/2:(ih-1080)/2" % D
    elif mv == 'pl':
        motion = "crop=1920:1080:'(iw-1920)*t/%.2f':(ih-1080)/2" % D
    elif mv == 'pr':
        motion = "crop=1920:1080:'(iw-1920)*(1-t/%.2f)':(ih-1080)/2" % D
    else:
        motion = "crop=1920:1080:(iw-1920)/2:'(ih-1080)*(1-t/%.2f)'" % D
    f = [base, motion, 'setsar=1']
    if bw: f.append('hue=s=0,eq=contrast=1.08')
    f += ['vignette=PI/4.5']
    lab = 'AI 재연 이미지'
    f.append(dt(lab, MED, 22, 'w-tw-36', '30', 'white@0.55'))
    return ['-loop', '1', '-framerate', str(FPS), '-i', img_input(name)], f

def bg(color=NAVY):
    return ['-f', 'lavfi', '-i', 'color=c=%s:s=%dx%d:r=%d' % (color, W, H, FPS)]

def v_black(sh, idx, D):
    p = (sh['arg'] or '|').split('|') + ['']
    f = []
    if p[0].strip() and p[0] != 'ㅤ':
        f.append(dt(p[0], XB, 104, '(w-tw)/2', '(h-th)/2-40', 'white', fa(0.25, D, 0.45)))
    if p[1].strip():
        f.append(dt(p[1], MED, 40, '(w-tw)/2', 'h/2+70', '0xBBBBBB', fa(0.6, D, 0.45)))
    return bg('black'), f or ['null']

def v_card(sh, idx, D):
    big, small = (sh['arg'].split('|') + [''])[:2]
    size = 120 if tw(big, 120) < 1700 else int(1700 / tw(big, 1) )
    f = ['noise=alls=3:allf=t', dt(big, XB, size, '(w-tw)/2', '(h-th)/2-60', GOLD, fa(0.2)),
         'drawbox=x=760:y=%d:w=400:h=3:color=white@0.35:t=fill' % (H / 2 + 40)]
    f += block(small, MED, 40, H / 2 + 110, '0xCCCCDD', fa(0.6), 1600)
    return bg(), f

def v_quote(sh, idx, D):
    text, who = (sh['arg'].split('|') + [''])[:2]
    f = ['noise=alls=3:allf=t', dt('“', XB, 220, '(w-tw)/2', '120', GOLD + '@0.85', fa(0.1))]
    qs = 110 if len(text) <= 12 else (84 if len(text) <= 24 else 66)
    f += block(text, BOLD, qs, H / 2 - 10, 'white', fa(0.35), 1500, 1.4)
    f.append(dt('— ' + who, MED, 36, '(w-tw)/2', '%d' % (H - 300), '0xAAAAAA', fa(0.9)))
    return bg('0x0A0A12'), f

PROM = {k: tuple(v) for k, v in CFG.get('promises', {}).items()}

def v_promise(sh, idx, D):
    k = sh['arg']
    if k in PROM:
        d, l1, l2, who = PROM[k]; col = GOLD if k == 'win' else 'white'
        f = ['noise=alls=3:allf=t', dt(d, MED, 40, '(w-tw)/2', '250', '0xAAAAAA', fa(0.2)),
             dt('“' + l1, XB, 76, '(w-tw)/2', '420', col, fa(0.6)), dt(l2 + '”', XB, 76, '(w-tw)/2', '530', col, fa(1.0)),
             dt('— ' + who, BOLD, 42, '(w-tw)/2', '690', '0xCCCCCC', fa(1.5))]
        return bg('0x08080C'), f
    # both
    f = ['noise=alls=3:allf=t', 'drawbox=x=959:y=200:w=2:h=680:color=white@0.25:t=fill']
    for side, kk, x0 in (('L', 'debut', 0), ('R', 'win', 960)):
        d, l1, l2, who = PROM[kk]; col = GOLD if kk == 'win' else 'white'
        dl = 0.3 if side == 'L' else 1.6
        cx = '%d+(960-tw)/2' % x0
        f += [dt(d, MED, 32, cx, '300', '0xAAAAAA', fa(dl)),
              dt('“' + l1, XB, 44, cx, '440', col, fa(dl + 0.3)), dt(l2 + '”', XB, 44, cx, '510', col, fa(dl + 0.5)),
              dt('— ' + who, BOLD, 34, cx, '620', '0xCCCCCC', fa(dl + 0.8))]
    f.append(dt('840일', XB, 40, '(w-tw)/2', '150', GOLD, fa(2.6)))
    return bg('0x08080C'), f

def rank_steps(key, D):
    r = CFG.get('ranks', {}).get(key)
    if r: return r[0], [tuple(x) for x in r[1]]
    return key, [('', key)]

def v_rank(sh, idx, D):
    title, steps = rank_steps(sh['arg'], D)
    n = len(steps); st = 0.4
    span = max(0.6, min(1.6, (D - 1.5) / max(1, n)))
    f = [dt(title, BOLD, 44, '(w-tw)/2', '150', '0xE8E8F0'), 'drawbox=x=360:y=760:w=1200:h=12:color=white@0.15:t=fill']
    ticks = []
    for i, (lab, val) in enumerate(steps):
        s0 = st + i * span; s1 = st + (i + 1) * span if i < n - 1 else D + 1
        ticks.append(s0)
        en = "enable='between(t,%.2f,%.2f)'" % (s0, s1)
        last = (i == n - 1)
        col = GOLD if val in CFG.get('rank_gold', ['1위']) else ('0x888899' if val in CFG.get('rank_dim', ['차트 밖']) else 'white')
        size = 260 if val == '1위' else (190 if tw(val, 190) < 1500 else 150)
        f.append(dt(val, XB, size, '(w-tw)/2', '(h-th)/2-40', col, en))
        f.append(dt(lab, MED, 42, '(w-tw)/2', '650', '0xBBBBCC', en))
        frac = (i + 1) / n
        f.append("drawbox=x=360:y=760:w=%d:h=12:color=%s:t=fill:%s" % (int(1200 * frac), col, en))
    if steps[-1][1] == '1위':
        fl = ticks[-1]
        f.append("drawbox=x=0:y=0:w=iw:h=ih:color=white@0.6:t=fill:enable='between(t,%.2f,%.2f)'" % (fl, fl + 0.12))
    f.append(dt(CFG.get('rank_source', '자료: 언론 보도 종합'), MED, 22, '40', 'h-50', 'white@0.45'))
    sh['ticks'] = ticks
    return bg(), f

def v_dday(sh, idx, D):
    a, b = (sh['arg'] + ['', ''])[:2] if isinstance(sh['arg'], list) else (sh['arg'], '')
    f = ['noise=alls=4:allf=t', dt(a, XB, 150, '(w-tw)/2', '(h-th)/2-50', 'white', fa(0.15)),
         dt(b, MED, 46, '(w-tw)/2', 'h/2+90', GOLD, fa(0.5))]
    sh['ticks'] = [0.15]
    return bg('black'), f

def v_chapter(sh, idx, D):
    p = sh['arg'] + ['', '', '']
    f = ['noise=alls=3:allf=t', dt('CHAPTER %s' % p[0], BOLD, 36, '(w-tw)/2', '360', GOLD, fa(0.2, D, 0.5)),
         dt(p[1], XB, 96, '(w-tw)/2', '(h-th)/2', 'white', fa(0.5, D, 0.5)),
         'drawbox=x=810:y=640:w=300:h=2:color=white@0.4:t=fill',
         dt(p[2], MED, 40, '(w-tw)/2', '680', '0xBBBBBB', fa(1.0, D, 0.5)), 'fade=t=in:st=0:d=0.5']
    return bg('0x050508'), f

def likes(n):
    try:
        n = int(str(n).replace(',', '').strip())
    except ValueError:
        return str(n)
    return ('%.1f만' % (n / 10000)).replace('.0만', '만') if n >= 10000 else ('%.1f천' % (n / 1000)).replace('.0천', '천') if n >= 1000 else str(n)

def v_cmt(sh, idx, D):
    cs = sh['arg']; n = len(cs)
    f = ['noise=alls=3:allf=t', dt('그때, 사람들이 남긴 말', BOLD, 38, '(w-tw)/2', '110', GOLD, fa(0.1))]
    y = 220
    for i, c in enumerate(cs):
        text, lk, src = (c + ['', '', ''])[:3]
        ls = wrap(text, 44, 1380)
        h = 70 + len(ls) * 58 + 40
        a = 0.8 + i * 3.2
        f.append("drawbox=x=250:y=%d:w=1420:h=%d:color=white@0.07:t=fill:enable='gte(t,%.2f)'" % (y, h, a))
        f.append("drawbox=x=250:y=%d:w=6:h=%d:color=%s:t=fill:enable='gte(t,%.2f)'" % (y, h, GOLD, a))
        for k, l in enumerate(ls):
            f.append(dt(l, BOLD, 44, '290', '%d' % (y + 36 + k * 58), 'white', fa(a)))
        f.append(dt('♥ %s   ·   %s' % (likes(lk), src), MED, 28, '290', '%d' % (y + 36 + len(ls) * 58 + 8), '0x9999AA', fa(a)))
        y += h + 34
    f.append(dt('유튜브 실제 댓글 (작성자명 비공개, 좋아요 수는 2026년 11월 기준)', MED, 22, '(w-tw)/2', 'h-60', 'white@0.4'))
    return bg('0x0A0A12'), f

def v_clip(sh, idx, D):
    c = CLIPS[sh['arg']]
    src = c['file'] if os.path.isabs(c['file']) else (os.path.join(HERE, c['file']) if os.path.exists(os.path.join(HERE, c['file'])) else os.path.join(WSRC, c['file']))
    cl = c['to'] - c['ss']
    slow = min(1.25, max(1.0, D / cl))
    f = ['setpts=%.3f*(PTS-STARTPTS)' % slow, 'scale=%d:%d:force_original_aspect_ratio=decrease' % (W, H), 'pad=%d:%d:(ow-iw)/2:(oh-ih)/2:black' % (W, H),
         'setsar=1', 'fps=%d' % FPS, 'tpad=stop_mode=clone:stop_duration=%.2f' % max(0, D - cl * slow + 0.5), 'eq=saturation=0.9',
         dt('출처: ' + c['label'], MED, 26, 'w-tw-36', '30', 'white@0.85', 'box=1:boxcolor=black@0.45:boxborderw=10')]
    if c.get('bw'): f.insert(4, 'hue=s=0')
    return ['-ss', '%.2f' % c['ss'], '-t', '%.2f' % cl, '-i', src], f

def v_split(sh, idx, D):
    a, b = sh['arg'].split()
    ins = ['-loop', '1', '-framerate', str(FPS), '-i', img_input(a), '-loop', '1', '-framerate', str(FPS), '-i', img_input(b)]
    fc = ("[0:v]crop=512:576:256:224,scale=960:1080,hue=s=0[l];"
          "[1:v]crop=512:576:256:224,scale=960:1080[r];[l][r]hstack=inputs=2,setsar=1,format=yuv420p,"
          "scale=w='trunc(1920*(1+0.03*t/%.2f)/2)*2':h=-2:eval=frame,crop=1920:1080:(iw-1920)/2:(ih-1080)/2," % D)
    f = [fc.rstrip(','), 'drawbox=x=958:y=0:w=4:h=ih:color=black:t=fill',
         dt('2024  ·  초등학교 운동장', BOLD, 40, '(960-tw)/2', '120', 'white', 'box=1:boxcolor=black@0.5:boxborderw=12:' + fa(0.3)),
         dt('2026  ·  서울월드컵경기장', BOLD, 40, '960+(960-tw)/2', '120', GOLD, 'box=1:boxcolor=black@0.5:boxborderw=12:' + fa(1.0)),
         dt('AI 재연 이미지', MED, 22, 'w-tw-36', '30', 'white@0.55')]
    return ins, f

def v_title(sh, idx, D):
    f = ['noise=alls=2:allf=t', dt(CFG['title'], XB, 170 if tw(CFG['title'], 170) < 1700 else int(1700 / tw(CFG['title'], 1)), '(w-tw)/2', '(h-th)/2-80', 'white', fa(0.2, D + 5, 0.8)),
         dt(CFG['subtitle'], MED, 50, '(w-tw)/2', 'h/2+80', '0xCCCCCC', fa(1.0, D + 5, 0.8)),
         dt(CFG['tagline'], BOLD, 40, '(w-tw)/2', 'h/2+160', GOLD, fa(1.6, D + 5, 0.8)), 'fade=t=out:st=%.2f:d=0.8' % (D - 0.8)]
    return bg('black'), f

def v_end(sh, idx, D):
    L = ['자료 출처'] + CFG['credits']
    f = ['noise=alls=2:allf=t']
    for i, l in enumerate(L):
        f.append(dt(l, BOLD if i == 0 else MED, 48 if i == 0 else min(30, int(1780 / max(1, tw(l, 1)))), '(w-tw)/2', '%d' % (250 + i * 80 + (30 if i else 0)), GOLD if i == 0 else '0xCCCCCC', fa(0.3 + i * 0.25)))
    f.append(dt(CFG['title'], XB, 60, '(w-tw)/2', '880', 'white', fa(2.5)))
    f.append('fade=t=out:st=%.2f:d=1.5' % (D - 1.5))
    return bg('black'), f

VIS = dict(img=v_img, black=v_black, card=v_card, quote=v_quote, promise=v_promise, rank=v_rank, dday=v_dday,
           chapter=v_chapter, cmt=v_cmt, clip=v_clip, split=v_split, title=v_title, end=v_end)

# ---------------- render segments ----------------
t_abs = 0.0; seglist = []; voice_events = []; sfx_events = []; chap_starts = {}
for i, sh in enumerate(shots):
    D = sh['D']
    chap_starts.setdefault(sh['ch'], t_abs)
    ins, f = VIS[sh['kind']](sh, i, D)
    if sh['kind'] not in ('title', 'chapter', 'end'):
        f += subs([(a, b, tx) for a, b, tx, _ in sh['ats']], D)
    if sh['kind'] in ('img', 'clip', 'split') and i > 0 and shots[i - 1]['kind'] != sh['kind']:
        f.append('fade=t=in:st=0:d=0.35')
    name = 'seg/%04d.mp4' % i
    key = hashlib.md5(json.dumps([ins, f, D], ensure_ascii=False).encode()).hexdigest()[:10]
    stamp = os.path.join(B, name + '.' + key)
    if not os.path.exists(stamp):
        vf = ','.join(f)
        if sh['kind'] == 'split':
            run(ins + ['-filter_complex', vf + '[v]', '-map', '[v]', '-t', '%.3f' % D, '-r', str(FPS), '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', PRESET, '-crf', '21', '-video_track_timescale', '15360', '-an', name])
        else:
            run(ins + ['-vf', vf, '-t', '%.3f' % D, '-r', str(FPS), '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', PRESET, '-crf', '21', '-video_track_timescale', '15360', '-an', name])
        for old in [x for x in os.listdir(os.path.join(B, 'seg')) if x.startswith('%04d.mp4.' % i)]:
            os.remove(os.path.join(B, 'seg', old))
        open(stamp, 'w').close()
    real = dur(os.path.join(B, name))
    seglist.append(name)
    for a, b, tx, wav in sh['ats']:
        if os.path.exists(wav): voice_events.append((t_abs + a, os.path.abspath(wav)))
    for tk in sh.get('ticks', []):
        sfx_events.append((t_abs + tk, 'tick'))
    if sh['kind'] == 'rank' and rank_steps(sh['arg'], D)[1][-1][1] == '1위':
        sfx_events.append((t_abs + sh['ticks'][-1], 'boom'))
    if sh['kind'] == 'chapter': sfx_events.append((t_abs + 0.1, 'swish'))
    if sh['kind'] == 'black' and (sh['arg'] or '').startswith(tuple(CFG.get('boom_prefixes', ['840']))): sfx_events.append((t_abs, 'boom'))
    t_abs += real
    if i % 20 == 0: print('seg %d/%d  t=%.1f' % (i, len(shots), t_abs), flush=True)
TOTAL = t_abs
print('TOTAL video %.1f s (%.1f min)' % (TOTAL, TOTAL / 60), flush=True)

with open(os.path.join(B, 'list.txt'), 'w', encoding='utf-8') as fh:
    for n in seglist: fh.write("file '%s'\n" % n)
run(['-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'video.mp4'])

# ---------------- audio ----------------
# 1) narration track
def place_track(events, out, total, vol=1.0):
    # chunked mixing to avoid huge filter graphs
    chunk = 40; parts = []
    if not events:
        run(['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono', '-t', '%.2f' % total, out]); return
    for c in range(0, len(events), chunk):
        ev = events[c:c + chunk]
        ins, fl, lab = [], [], []
        for k, (at, wav) in enumerate(ev):
            ins += ['-i', wav]; ms = int(at * 1000)
            fl.append('[%d]aresample=48000,aformat=channel_layouts=mono,adelay=%d|%d[a%d]' % (k, ms, ms, k)); lab.append('[a%d]' % k)
        pn = 'part%03d.wav' % (c // chunk)
        run(ins + ['-filter_complex', ';'.join(fl) + ';' + ''.join(lab) + 'amix=inputs=%d:normalize=0,apad=whole_dur=%.2f[o]' % (len(lab), total), '-map', '[o]', '-t', '%.2f' % total, '-ar', '48000', '-ac', '1', pn])
        parts.append(pn)
    if len(parts) == 1:
        shutil.copy(os.path.join(B, parts[0]), os.path.join(B, out)); return
    ins = sum([['-i', p] for p in parts], [])
    run(ins + ['-filter_complex', ''.join('[%d]' % k for k in range(len(parts))) + 'amix=inputs=%d:normalize=0[o]' % len(parts), '-map', '[o]', '-ar', '48000', '-ac', '1', out])
place_track(voice_events, 'voice.wav', TOTAL)

# 2) music: YouTube Audio Library tracks per section, crossfaded
MUSIC = json.load(open('music.json', encoding='utf-8'))   # [[chapter, file, gain], ...]
chs = sorted(chap_starts)
spans = []
for k, (c, fn, gain) in enumerate(MUSIC):
    st = chap_starts.get(c, 0.0)
    nxt = [chap_starts[x] for x, _, _ in MUSIC[k + 1:] if x in chap_starts]
    en = nxt[0] if nxt else TOTAL
    spans.append((st, en, fn, gain))
pads = []
for k, (st, en, fn, gain) in enumerate(spans):
    d = en - st + 2.5
    pn = 'bgm%02d.wav' % k
    run(['-stream_loop', '-1', '-i', os.path.join(BGM, fn), '-t', '%.2f' % d, '-af',
         'volume=%.3f,afade=t=in:d=2.0,afade=t=out:st=%.2f:d=2.5,aformat=channel_layouts=mono' % (gain, max(0, d - 2.5)), '-ar', '48000', pn])
    pads.append((max(0, st - 1.0), os.path.abspath(os.path.join(B, pn))))
place_track(pads, 'music.wav', TOTAL)
# 3) sfx
run(['-f', 'lavfi', '-i', "aevalsrc='0.9*sin(2*PI*55*t)*exp(-4*t)+0.3*sin(2*PI*110*t)*exp(-6*t)':s=48000:d=1.6", '-ac', '1', 'boom.wav'])
run(['-f', 'lavfi', '-i', "aevalsrc='0.35*sin(2*PI*1320*t)*exp(-30*t)':s=48000:d=0.25", '-ac', '1', 'tick.wav'])
run(['-f', 'lavfi', '-i', 'anoisesrc=d=1.2:c=pink:a=0.25:r=48000', '-af', 'lowpass=f=2500,highpass=f=300,afade=t=in:d=0.5,afade=t=out:st=0.6:d=0.6', '-ac', '1', 'swish.wav'])
place_track([(a, os.path.abspath(os.path.join(B, k + '.wav'))) for a, k in sfx_events], 'sfx.wav', TOTAL)
# 4) mix: music ducked under voice
run(['-i', 'voice.wav', '-i', 'music.wav', '-i', 'sfx.wav', '-filter_complex',
     '[0]asplit=2[v][sc];[1]volume=%.2f[m];[m][sc]sidechaincompress=threshold=0.015:ratio=%.1f:knee=4:attack=120:release=1400[md];' % (CFG.get('music_gain', 0.78), CFG.get('duck_ratio', 4.0)) +
     '[v][md][2]amix=inputs=3:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[o]', '-map', '[o]', '-ar', '48000', '-ac', '2', 'mix.wav'])
os.makedirs('out', exist_ok=True)
outp = os.path.abspath('out/final.mp4' if ONLY is None else 'out/ch%d.mp4' % ONLY)
run(['-i', 'video.mp4', '-i', 'mix.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', outp])
# chapter timestamps for YouTube description
with open('out/chapters.txt', 'w', encoding='utf-8') as fh:
    for c in chs:
        s = int(chap_starts[c]); fh.write('%d:%02d %s\n' % (s // 60, s % 60, c))
print('OUT', outp, '%.1f min' % (TOTAL / 60))
