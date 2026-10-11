"""내레이션 품질검사: Whisper로 받아쓰기 → 대본과 글자 일치율 비교.
TTS가 단어를 빼먹거나 헛소리(환각)를 하면 일치율이 떨어진다. 기준 미달 장면은 시드를 바꿔 재생성한다.

사용: python voice/qa.py projects/<프로젝트> [--min 0.85]
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path


DIG = "영일이삼사오육칠팔구"


def num2kor(n: int) -> str:
    """정수 → 한자어 수 읽기 (25 → 이십오, 250000 → 이십오만)."""
    if n == 0:
        return "영"
    out = ""
    man, rest = divmod(n, 10000)
    if man:
        out += (num2kor(man) if man > 1 else "") + "만"
    for unit, v in (("천", 1000), ("백", 100), ("십", 10)):
        q, rest = divmod(rest, v)
        if q:
            out += (DIG[q] if q > 1 else "") + unit
    if rest:
        out += DIG[rest]
    return out


def norm(s):
    s = re.sub(r"\d+", lambda m: num2kor(int(m.group())), s)
    return re.sub(r"[^가-힣a-zA-Z]", "", s)


def load16k(path):
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(str(path), dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    n = int(len(x) * 16000 / sr)
    return np.interp(np.arange(n) * sr / 16000, np.arange(len(x)), x).astype("float32")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--min", type=float, default=0.85)
    ap.add_argument("--model", default="medium")
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    m = WhisperModel(a.model, device="cpu", compute_type="int8")
    proj = Path(a.project)
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    bad, rows = [], []
    for s in script["scenes"]:
        f = proj / "narration" / f"{s['id']}.wav"
        if not f.exists():
            continue
        segs, _ = m.transcribe(load16k(f), language="ko", beam_size=5)
        heard = "".join(x.text for x in segs)
        r = difflib.SequenceMatcher(None, norm(s["say"]), norm(heard)).ratio()
        rows.append({"id": s["id"], "score": round(r, 3), "heard": heard.strip()})
        flag = "OK " if r >= a.min else "BAD"
        print(f"{flag} {s['id']} {r:.2f} | {heard.strip()}", flush=True)
        if r < a.min:
            bad.append(s["id"])
    (proj / "narration" / "qa.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BAD:", ",".join(bad) if bad else "-")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
