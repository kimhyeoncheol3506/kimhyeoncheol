#!/usr/bin/env python3
"""ReachMora 편 문장 다시 녹음 2판(영상은 다시 렌더하지 않음).
  QWEN_TTS_HOME=... python3 tools/rm_retake.py <P> [--takes 4]
<P>/rerecord.json {"say_as": {...}, "sentences": [i, ...]} 의 문장마다
  1) 시드를 바꿔 여러 번 녹음하고(속도 1.15),
  2) 받아쓰기(faster-whisper small)가 대본과 가장 가까운 녹음을 고른다(숫자 오독 거르기),
  3) 원래 길이보다 길면 자르지 않고 뒤의 문장 사이 쉼(0.45초) 안으로 넘긴다(최대 0.38초; 더 길면 속도를 올린 녹음 중에서 고름).
tts/NNNN.wav 는 원래 길이로 두고(timing.json·영상 싱크 그대로) 온전한 녹음은 tts_full/NNNN.wav 에 둔다.
ko_timing --wavs 로 voice.wav 를 다시 이은 뒤, 온전한 녹음을 제자리에 덮어써 넘친 꼬리를 살린다.
결과: <P>/tts/retake_report.json (문장별 후보 받아쓰기·선택)."""
import sys, os, re, json, difflib, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "shorts"))
from facetube import audio as A, textnorm
from facetube.voice import Voice
from facetube.textnorm import to_speech
from faster_whisper import WhisperModel

P = Path(sys.argv[1]).resolve()
NT = int(sys.argv[sys.argv.index("--takes") + 1]) if "--takes" in sys.argv else 4
cfg = json.load(open(P / "rerecord.json", encoding="utf-8"))
sa = P / "say_as.json"
if sa.exists(): textnorm.SAY_AS.update(json.load(open(sa, encoding="utf-8")))
textnorm.SAY_AS.update(cfg.get("say_as", {}))
T = json.load(open(P / "timing.json", encoding="utf-8")); S = {s["i"]: s for s in T["sentences"]}
W = None if "--overlay-only" in sys.argv else WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
MAXOVER = 0.38

def norm(s): return re.sub(r"[^가-힣0-9a-zA-Z]", "", s)
def cer(a, b): return 1 - difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()
def hear(x, sr):
    n = int(len(x) * 16000 / sr); a = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype("float32")
    return " ".join(s.text for s in W.transcribe(a, language="ko", beam_size=3)[0]).strip()

OVERLAY_ONLY = "--overlay-only" in sys.argv
v = Voice(backend="voicebox", voice=["여의도여자", "엠마"], speed=1.15, cer_retry=0.35)   # 고르기는 받아쓰기로 하므로 안쪽 재시도는 줄임
full = P / "tts_full"; full.mkdir(exist_ok=True); rep = []
for i in ([] if OVERLAY_ONLY else cfg["sentences"]):
    f = P / "tts" / f"{i:04d}.wav"; old, sr = sf.read(f, dtype="float32"); L = len(old)
    if sr != A.SR: raise SystemExit("sample rate mismatch")
    text = S[i]["text"]; cands = []
    for k in range(NT):
        sp = 1.15 if k < NT - 1 else 1.22
        v.speed = sp; v.seed_base = 101 + 17 * k
        x, info = v.say(text)
        h = hear(x, sr); e = min(cer(text, h), cer(to_speech(text), h)); over = (len(x) - L) / sr
        cands.append(dict(x=x, heard=h, w_cer=round(e, 3), over=round(over, 2), speed=sp))
        print(f"  [{i}] 후보{k + 1} 받아쓰기오차={e:.3f} 넘침={over:+.2f}초 | {h}", flush=True)
        mu = cfg.get("must", {}).get(str(i))
        if over <= MAXOVER and (e == 0 if not mu else any(norm(m) in norm(h) for m in mu)): break
    must = cfg.get("must", {}).get(str(i))      # 받아쓰기에 꼭 들려야 하는 숫자 표기(여러 표기 중 하나), 예 ["9천 91억", "9,091억"]
    pool = [c for c in cands if not must or any(norm(m) in norm(c["heard"]) for m in must)] or cands
    ok = [c for c in pool if c["over"] <= MAXOVER] or sorted(pool, key=lambda c: c["over"])[:1]
    best = min(ok, key=lambda c: (c["w_cer"], c["over"]))
    x = best["x"]
    if len(x) > L + int(MAXOVER * sr):          # 어떤 후보도 쉼 안에 안 들어가면 자르지 않고 살짝 빠르게(atempo, 음높이 그대로)
        import tempfile
        tgt = L + int(MAXOVER * sr); r = len(x) / tgt
        with tempfile.TemporaryDirectory() as td:
            a, b = os.path.join(td, "a.wav"), os.path.join(td, "b.wav"); sf.write(a, x, sr)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", f"atempo={r:.4f}", "-ar", str(sr), b], check=True)
            x, _ = sf.read(b, dtype="float32")
        x = x[:tgt]; print(f"  [{i}] 쉼에 안 들어가 {r:.3f}배 빠르게 맞춤", flush=True)
    sf.write(full / f"{i:04d}.wav", x, sr)
    y = np.concatenate([x, np.zeros(max(0, L - len(x)), dtype=np.float32)])[:L]
    sf.write(f, y, sr)
    rep.append(dict(i=i, text=text, chosen=next(k for k, c in enumerate(cands) if c is best) + 1, heard=best["heard"], w_cer=best["w_cer"], over=best["over"],
                    candidates=[{k: c[k] for k in ("heard", "w_cer", "over", "speed")} for c in cands]))
    print(f"[{i}] 선택 후보{next(k for k, c in enumerate(cands) if c is best) + 1} 오차={best['w_cer']} 넘침={best['over']:+.2f}초 | {text}", flush=True)
if not OVERLAY_ONLY: json.dump(rep, open(P / "tts" / "retake_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# voice.wav 다시 잇기 → 온전한 녹음을 제자리에 덮어쓰기(넘친 꼬리는 다음 쉼 안)
subprocess.run([sys.executable, str(ROOT.parent / ".claude/skills/reachmora-2d-longform/tools/ko_timing.py"), str(P), "--wavs", str(P / "tts")], check=True)
sr = A.SR
vw = P / "voice.wav"; V, vsr = sf.read(vw, dtype="float32")
from math import gcd
from scipy.signal import resample_poly
g = gcd(vsr, sr)
T = json.load(open(P / "timing.json", encoding="utf-8")); S = {s["i"]: s for s in T["sentences"]}
for ff in sorted(full.glob("*.wav")):
    i = int(ff.stem); x, _ = sf.read(ff, dtype="float32")
    if vsr != sr: x = resample_poly(x, vsr // g, sr // g).astype("float32")
    a = int(round((S[i]["start"] + (0.06 if S[i]["start"] > 0 else 0)) * vsr)); b = min(len(V), a + len(x))
    V[a:b] = x[:b - a]
sf.write(vw, V, vsr); print("DONE")
