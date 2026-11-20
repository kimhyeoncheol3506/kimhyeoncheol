#!/usr/bin/env python3
"""ReachMora 편 다시 녹음(영상은 다시 렌더하지 않음).  QWEN_TTS_HOME=... python3 tools/rm_rerecord.py <P>
<P>/rerecord.json {"say_as": {...}, "sentences": [i, ...]} → 해당 문장만 새 읽기로 다시 만들고,
원래 길이에 맞춰(짧으면 뒤에 무음, 길면 문장 사이 쉼 0.45초 안에서만 허용 — 넘으면 속도를 올려 다시) <P>/tts/NNNN.wav 를 바꾼 뒤
ko_timing --wavs 와 같은 순서로 voice.wav 를 다시 잇는다(timing.json 은 그대로 = 영상과 싱크 유지)."""
import sys, os, json, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "shorts"))
from facetube import audio as A, textnorm
from facetube.voice import Voice
P = Path(sys.argv[1]).resolve(); cfg = json.load(open(P / "rerecord.json", encoding="utf-8"))
sa = P / "say_as.json"
if sa.exists(): textnorm.SAY_AS.update(json.load(open(sa, encoding="utf-8")))
textnorm.SAY_AS.update(cfg["say_as"])
T = json.load(open(P / "timing.json", encoding="utf-8")); S = {s["i"]: s for s in T["sentences"]}
v = Voice(backend="voicebox", voice=["여의도여자", "엠마"], speed=1.15, cer_retry=0.12)
for i in cfg["sentences"]:
    f = P / "tts" / f"{i:04d}.wav"; old, sr = sf.read(f, dtype="float32"); L = len(old)
    for sp in (1.15, 1.25, 1.35):
        v.speed = sp; x, info = v.say(S[i]["text"])
        if sr != A.SR: raise SystemExit("sample rate mismatch")
        if len(x) <= L + int(0.35 * sr): break
    if len(x) < L: x = np.concatenate([x, np.zeros(L - len(x), dtype=np.float32)])
    x = x[:L + int(0.35 * sr)]
    if len(x) > L:   # 쉼 안으로 조금 넘친 만큼은 다음 쉼에서 빼도록 원래 길이로 자르되 끝을 0.03초 페이드
        extra = len(x) - L; x = x[:L]; fade = min(int(0.03 * sr), L); x[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
        print(f"  [{i}] {extra / sr:.2f}초 넘침 → 끝을 잘라 맞춤 (확인 필요)")
    sf.write(f, x, sr); print(f"[{i}] 다시 녹음 cer={info.get('cer')} speed={sp} {S[i]['text'][:40]}", flush=True)
# voice.wav 다시 잇기 (ko_timing.py --wavs 와 같은 방식)
subprocess.run([sys.executable, str(ROOT.parent / ".claude/skills/reachmora-2d-longform/tools/ko_timing.py"), str(P), "--wavs", str(P / "tts")], check=True)
print("DONE")
