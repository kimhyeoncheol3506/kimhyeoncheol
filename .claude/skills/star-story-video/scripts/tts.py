# -*- coding: utf-8 -*-
"""script.txt 의 '> ' 줄을 여의도여자(Voicebox)로 생성.
Whisper(small)로 받아 적어 원문과 비교해 더듬음/반복/누락이 있으면 시드를 바꿔 재생성.
결과: lines/NNN.wav (무음 정리 + 1.0908배속, 48k mono), tts_log.jsonl"""
import hashlib, difflib, json, os, re, subprocess, sys, time, urllib.request, uuid
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].isdigit() else os.getcwd())
os.chdir(HERE)
sys.argv = [sys.argv[0]] + [x for x in sys.argv[1:] if x.isdigit()]
VB = 'http://127.0.0.1:17493'
SPEED = 1.08 * 1.01
OUT = 'lines'; RAW = 'lines_raw'
os.makedirs(OUT, exist_ok=True); os.makedirs(RAW, exist_ok=True)
INSTRUCT = ("차분하고 또렷한 다큐멘터리 내레이션 톤, 신뢰감 있게, 보통 속도. 쉼표에서 짧게 끊어 읽고 문장 끝은 자연스럽게 내려 닫는다. "
            "숫자와 핵심 낱말은 또박또박 읽는다. 더듬거나 같은 말을 반복하지 않는다. 감정은 절제하되 따뜻하게.")

DIG = '영일이삼사오육칠팔구'
def sino(n):
    n = int(n)
    if n == 0: return '영'
    def under1e4(x):
        s = ''
        for unit, v in (('천', 1000), ('백', 100), ('십', 10)):
            d = x // v; x %= v
            if d: s += ('' if d == 1 else DIG[d]) + unit
        if x: s += DIG[x]
        return s
    parts = []
    for unit, v in (('억', 10**8), ('만', 10**4)):
        d = n // v; n %= v
        if d: parts.append(('' if (d == 1 and unit == '만') else under1e4(d)) + unit)
    if n: parts.append(under1e4(n))
    return ''.join(parts)
NATIVE_H = {1: '한', 2: '두', 3: '세', 4: '네', 5: '다섯', 6: '여섯', 7: '일곱', 8: '여덟', 9: '아홉', 10: '열', 11: '열한', 12: '열두'}
def speak(t):
    t = t.replace('3.26킬로미터', '삼 점 이육 킬로미터')
    t = re.sub(r'(\d+)시(?!간)', lambda m: NATIVE_H.get(int(m.group(1)), sino(m.group(1))) + ' 시', t)
    t = re.sub(r'(?<!\d)6월', '유월', t); t = re.sub(r'(?<!\d)10월', '시월', t)
    t = t.replace('1천만', '천만')
    t = re.sub(r'\d+', lambda m: sino(m.group(0)), t)
    return t
def hangul(s):
    for a_, b_ in (('다섯', '5'), ('여섯', '6'), ('일곱', '7'), ('여덟', '8'), ('아홉', '9'), ('열여섯', '16'), ('스무', '20')): s = s.replace(a_, b_)
    s = re.sub(r'\d+', lambda m: sino(m.group(0)), s)
    return re.sub(r'[^가-힣]', '', s)

def vb(path, body=None, raw=False, timeout=600):
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(VB + path, data=None if body is None else json.dumps(body, ensure_ascii=False).encode('utf-8'),
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    with op.open(req, timeout=timeout) as r:
        d = r.read()
    return d if raw else json.loads(d)
profs = vb('/profiles'); profs = profs.get('profiles', profs) if isinstance(profs, dict) else profs
P = next(x for x in profs if x.get('name') == '여의도여자')
ENG = P.get('default_engine') or 'qwen'

def gen(text, out, seed):
    body = {'profile_id': P['id'], 'text': text, 'language': P.get('language') or 'ko', 'model_size': '1.7B', 'engine': ENG, 'seed': seed}
    if ENG == 'qwen_custom_voice':
        body['instruct'] = INSTRUCT
    gid = vb('/generate', body)['id']
    for _ in range(900):
        h = vb('/history/%s' % gid, timeout=30)
        if h.get('status') == 'completed': break
        if h.get('status') == 'failed': raise RuntimeError(h.get('error'))
        time.sleep(1.5)
    open(out, 'wb').write(vb('/audio/%s' % gid, raw=True))

def transcribe(path):
    r = subprocess.run(['curl.exe', '-s', '-X', 'POST', VB + '/transcribe', '-F', 'file=@' + path, '-F', 'language=ko', '-F', 'model=small', '--max-time', '300'],
                       capture_output=True, timeout=320)
    return json.loads(r.stdout.decode('utf-8'))

def dur(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True)
    return float(r.stdout.strip())

def score(src, hyp, d):
    a, b = hangul(src), hangul(hyp)
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    spc = d / max(1, len(a))   # 원 속도 기준 초/글자
    pen = 0.0
    if spc > 0.40: pen += (spc - 0.40) * 2
    if spc < 0.17: pen += (0.17 - spc) * 2
    # 원문에 없는 2글자 이상 반복(더듬음)
    for m in re.finditer(r'([가-힣]{1,3})\1', b):
        if m.group(0) not in a: pen += 0.08
    if len(b) > len(a) * 1.15: pen += 0.1
    return ratio - pen, ratio, spc

lines = [l[2:].strip() for l in open('script.txt', encoding='utf-8').read().splitlines() if l.startswith('> ')]
log = open('tts_log.jsonl', 'a', encoding='utf-8')
only = set(int(x) for x in sys.argv[1:]) if len(sys.argv) > 1 else None
for i, line in enumerate(lines):
    hk = hashlib.md5(line.encode('utf-8')).hexdigest()[:12]
    fin = os.path.join(OUT, hk + '.wav')
    if os.path.exists(fin) and not only: continue
    if only and i not in only: continue
    text = speak(line)
    best = None
    for k, seed in enumerate((7, 21, 42, 99, 123, 2024)):
        raw = os.path.join(RAW, '%s_s%d.wav' % (hk, seed))
        t0 = time.time()
        if not os.path.exists(raw):
            gen(text, raw, seed)
        d = dur(raw)
        try:
            hyp = transcribe(raw).get('text', '')
        except Exception as e:
            hyp = ''
        sc, ratio, spc = score(text, hyp, d)
        rec = {'i': i, 'seed': seed, 'score': round(sc, 3), 'ratio': round(ratio, 3), 'spc': round(spc, 3), 'dur': round(d, 2), 'hyp': hyp, 'src': text, 'sec': round(time.time() - t0, 1)}
        log.write(json.dumps(rec, ensure_ascii=False) + '\n'); log.flush()
        if best is None or sc > best[0]: best = (sc, raw, rec)
        if sc >= 0.88: break
        if k >= 2 and best[0] >= 0.80: break
    print('[%d/%d] score=%.3f seed=%s %s' % (i + 1, len(lines), best[0], best[2]['seed'], line[:30]), flush=True)
    # 앞뒤 무음 정리 + 1.0908배속
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', best[1], '-af',
                    'silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12,areverse,atempo=%.4f' % SPEED,
                    '-ar', '48000', '-ac', '1', fin], check=True)
print('DONE', len(lines))
