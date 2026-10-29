# -*- coding: utf-8 -*-
"""문장별 음성을 Whisper로 받아 적어 대본(음성용 글)과 비교. 숫자는 한글로 바꿔 맞춘다."""
import difflib, json, re, subprocess, sys
import numpy as np
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/voice")
from pronounce import numbers
from faster_whisper import WhisperModel
ROOT = "/home/user/kimhyeoncheol/video_projects/10월_주간시세_모션그래프"
D = json.load(open(f"{ROOT}/01_대본/대본데이터.json", encoding="utf-8"))
m = WhisperModel("small", device="cpu", compute_type="int8")
norm = lambda t: re.sub(r"[^가-힣]", "", re.sub(r"(\d),(\d{3})", r"\1\2", t))
rows = []
for si, s in enumerate(D["sections"]):
    for ti, x in enumerate(s["sentences"]):
        au = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{ROOT}/02_음성/{si:02d}_{ti:02d}.wav", "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True).stdout, dtype=np.float32)
        seg, _ = m.transcribe(au, language="ko", beam_size=3)
        got = "".join(g.text for g in seg); r = difflib.SequenceMatcher(None, norm(numbers(got)), norm(x[0])).ratio()
        rows.append((r, f"{si:02d}_{ti:02d}", x[0], got)); print(f"{si:02d}_{ti:02d} {r:.2f}", flush=True)
rows.sort()
open(f"{ROOT}/02_음성/발음검수.tsv", "w", encoding="utf-8").write("\n".join(f"{r:.2f}\t{i}\t{a}\t{b}" for r, i, a, b in rows))
print("낮은 문장:"); [print(f"{r:.2f} {i} | {a} | {b}") for r, i, a, b in rows if r < 0.85]
