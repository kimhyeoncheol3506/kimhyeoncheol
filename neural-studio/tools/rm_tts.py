#!/usr/bin/env python3
"""ReachMora(v2 카툰) 편용 문장별 여의도 녹음.
  QWEN_TTS_HOME=~/.cache/yeouido-tts python3 tools/rm_tts.py <P> [--speed 1.15] [--voice 여의도여자]
<P>/script.txt 의 문장(엔진 sentences 와 같은 분할)마다 <P>/tts/NNNN.wav 를 만든다(내용 해시 캐시, 끊겨도 이어짐).
<P>/say_as.json 이 있으면 화면 표기 → 읽는 소리 대체를 적용한다. 결과 요약은 <P>/tts/report.json (문장별 CER)."""
import sys, os, json, hashlib, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "shorts"))
import soundfile as sf
from facetube import audio as A, textnorm
from facetube.voice import Voice
sys.path.insert(0, str(ROOT.parent / ".claude/skills/reachmora-2d-longform"))
from engine.timing import sentences

P = Path(sys.argv[1]).resolve(); a = sys.argv[2:]
get = lambda k, d: a[a.index(k) + 1] if k in a else d
speed = float(get("--speed", "1.15")); name = get("--voice", "여의도여자")
sa = P / "say_as.json"
if sa.exists(): textnorm.SAY_AS.update(json.load(open(sa, encoding="utf-8")))
ss = sentences(open(P / "script.txt", encoding="utf-8").read())
out = P / "tts"; cache = P / "tts_cache"; out.mkdir(exist_ok=True); cache.mkdir(exist_ok=True)
v = Voice(backend="voicebox", voice=[name, "엠마"], speed=speed, cer_retry=0.18)
rep = []
for i, s in enumerate(ss):
    key = hashlib.md5(f"{name}|{speed}|{s}|{textnorm.to_speech(s)}".encode()).hexdigest()[:16]
    w, m = cache / f"{key}.wav", cache / f"{key}.json"
    if not (w.exists() and m.exists()):
        x, info = v.say(s); sf.write(w, x, A.SR); json.dump(info, open(m, "w", encoding="utf-8"), ensure_ascii=False)
    info = json.load(open(m, encoding="utf-8"))
    shutil.copy(w, out / f"{i:04d}.wav")
    rep.append({"i": i, "text": s, "cer": info.get("cer"), "asr": info.get("asr"), "tries": info.get("tries")})
    print(f"[{i + 1}/{len(ss)}] cer={info.get('cer')} {s[:40]}", flush=True)
for f in out.glob("*.wav"):
    if int(f.stem) >= len(ss): f.unlink()
json.dump(rep, open(out / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE", len(ss))
