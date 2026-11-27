# -*- coding: utf-8 -*-
"""7개 프로젝트 script.txt -> 여의도여자 문장별 TTS -> voice.wav(목표 158초로 atempo) + timings.json"""
import json, os, re, subprocess, sys, time, urllib.request
try:  # 발음 사전(ko-tts-pronounce): 음성에 넣는 문장만 읽는 대로 바꾼다. KO_TTS_RAW=1이면 끔
    for _kp in (os.path.join(os.path.expanduser("~"), ".orca", "bots", "bot", "skills", "ko-tts-pronounce"),  # PC 원본 사전
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ko-tts-pronounce")):  # 저장소/클라우드: .claude/skills/ko-tts-pronounce
        if os.path.isdir(_kp): sys.path.insert(0, _kp); break
    from ko_tts import normalize as _ko_norm
    if os.environ.get("KO_TTS_RAW") == "1": raise ImportError
except Exception:
    _ko_norm = lambda s: s


URL = "http://127.0.0.1:17493"
INSTRUCT = ("역사 다큐멘터리 내레이터 톤. 차분하지만 긴장감 있게, 약간 빠른 속도. "
            "숫자와 핵심 낱말은 또박또박 힘주어 읽고, 마지막 문장은 여운을 남기며 닫는다.")
INSTRUCT = os.environ.get("INSTRUCT") or INSTRUCT
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJS = ["v1_lee", "v2_sejong", "v3_yi", "v4_seonjo", "v5_daewongun", "v6_uija", "v7_chunchu"]
if len(sys.argv) > 1:
    PROJS = sys.argv[1].split(",")
TARGET = float(os.environ.get("TARGET", "158"))  # 목표 음성 길이(초). 더 길면 atempo 로 줄임, 짧으면 그대로
# 사용: python make_voice_pc.py <프로젝트폴더(절대경로 가능)>[,<폴더2>...]
GAP = 0.30
FF = "ffmpeg"


def vb(path, body=None, raw=False, timeout=600):
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(URL + path, data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with op.open(req, timeout=timeout) as r:
        d = r.read()
    return d if raw else json.loads(d.decode("utf-8"))


PROFILE = None


def tts(text, out, seed=11):
    global PROFILE
    if PROFILE is None:
        PROFILE = next(x for x in vb("/profiles") if x["name"] == os.environ.get("TTS_VOICE", "여의도여자"))["id"]
    body = {"profile_id": PROFILE, "text": _ko_norm(text), "language": "ko", "model_size": "1.7B",
            "engine": "qwen_custom_voice", "seed": seed, "instruct": INSTRUCT}
    gid = vb("/generate", body)["id"]
    for _ in range(1200):
        h = vb("/history/%s" % gid, timeout=30)
        if h.get("status") == "completed":
            break
        if h.get("status") == "failed":
            raise RuntimeError(h.get("error"))
        time.sleep(1.5)
    open(out, "wb").write(vb("/audio/%s" % gid, raw=True))


def dur_of(wav):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav], capture_output=True, text=True)
    return float(r.stdout.strip())


def speech_bounds(wav):
    r = subprocess.run([FF, "-i", wav, "-af", "silencedetect=n=-40dB:d=0.08", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    dur = dur_of(wav)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    a = ends[0] if starts and starts[0] < 0.02 and ends else 0.0
    b = starts[-1] if starts and (not ends or starts[-1] > ends[-1]) else dur
    return max(0, a - 0.03), min(dur, b + 0.08)


def syl(w):
    n = len(re.findall(r"[가-힣A-Za-z]", w)) + 2 * len(re.findall(r"\d", w))
    return max(1, n)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


for name in PROJS:
    d = os.path.join(ROOT, name)
    if os.path.exists(os.path.join(d, "voice.wav")) and os.path.exists(os.path.join(d, "timings.json")):
        log(name, "already done"); continue
    lines = [l.strip() for l in open(os.path.join(d, "script.txt"), encoding="utf-8").read().splitlines() if l.strip()]
    vd = os.path.join(d, "vo"); os.makedirs(vd, exist_ok=True)
    parts, words, t = [], [], 0.0
    for i, line in enumerate(lines):
        raw = os.path.join(vd, "s%02d_raw.wav" % i)
        if not os.path.exists(raw):
            t0 = time.time()
            for attempt in range(3):
                try:
                    tts(line, raw + ".tmp.wav"); os.replace(raw + ".tmp.wav", raw); break
                except Exception as e:
                    log(name, i, "retry", e); time.sleep(5)
            log(name, i, "/", len(lines), "tts %.0fs" % (time.time() - t0))
        a, b = speech_bounds(raw)
        cut = os.path.join(vd, "s%02d.wav" % i)
        subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-ss", "%.3f" % a, "-to", "%.3f" % b, "-ar", "48000", "-ac", "1", cut], check=True)
        L = b - a
        toks = line.split()
        tot = sum(syl(w) for w in toks)
        c = t
        for w in toks:
            dw = L * syl(w) / tot
            words.append({"word": w, "start": c, "end": c + dw * 0.92})
            c += dw
        parts.append(cut); t += L
        if i < len(lines) - 1:
            t += GAP
    gap = os.path.join(vd, "gap.wav")
    subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(GAP), gap], check=True)
    lst = os.path.join(vd, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for i, p in enumerate(parts):
            f.write("file '%s'\n" % p.replace("\\", "/"))
            if i < len(parts) - 1:
                f.write("file '%s'\n" % gap.replace("\\", "/"))
    raw1x = os.path.join(d, "voice_1x.wav")
    subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "48000", "-ac", "1", raw1x], check=True)
    D = dur_of(raw1x)
    f = max(1.0, D / TARGET)
    subprocess.run([FF, "-v", "error", "-y", "-i", raw1x, "-af", "atempo=%.5f" % f, "-ar", "48000", "-ac", "1", os.path.join(d, "voice.wav")], check=True)
    for w in words:
        w["start"] = round(w["start"] / f, 3); w["end"] = round(w["end"] / f, 3)
    json.dump(words, open(os.path.join(d, "timings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    log(name, "DONE raw %.1fs tempo %.3f -> %.1fs, %d words" % (D, f, dur_of(os.path.join(d, "voice.wav")), len(words)))
log("ALL DONE")
