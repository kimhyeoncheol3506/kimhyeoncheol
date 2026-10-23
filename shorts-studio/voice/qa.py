"""내레이션 품질검사: Whisper로 받아쓰기 → 대본과 글자 일치율 비교.
TTS가 단어를 빼먹거나 헛소리(환각)를 하면 일치율이 떨어진다. 기준 미달 장면은 시드를 바꿔 재생성한다.

사용: python voice/qa.py projects/<프로젝트> [--min 0.85]
"""
from __future__ import annotations

import argparse
import os
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


def onset_stutter(words, texts):
    """단어 첫음이 겹쳐 들리는 TTS 결함('당황해서'→'당당황해서', Whisper는 '딱 / 당황해서'로 받아씀) 검출.
    words: [(start, end, word)]. 아주 짧은(0.2초 미만) 1~2음절 토막이 있고, 그 토막+다음 단어가 대본에 없으면 결함.
    texts: 대본 문장(들) — 숫자 읽기 차이를 고려해 여러 형태를 받는다."""
    scripts = [norm(x) for x in texts]
    for i in range(len(words) - 1):
        s, e, w = words[i]
        a, b = norm(w), norm(words[i + 1][2])
        if not (a and len(a) <= 2 and e - s < 0.2 and b) or any((a + b) in sc for sc in scripts):
            continue
        # 토막이 대본에 없는 소리이거나(딱), 다음 단어 앞부분과 같으면(당 / 당황해서) 결함. 대본에 있는 짧은 단어는 철자 차이(에요/예요)일 뿐이라 제외
        if not any(a in sc for sc in scripts) or b.startswith(a):
            return w.strip() + " " + words[i + 1][2].strip()
    return None


def load16k(path):
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(str(path), dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    n = int(len(x) * 16000 / sr)
    return np.interp(np.arange(n) * sr / 16000, np.arange(len(x)), x).astype("float32")


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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
        segs, _ = m.transcribe(load16k(f), language="ko", beam_size=5, word_timestamps=True)
        segs = list(segs)
        heard = "".join(x.text for x in segs)
        words = [(w.start, w.end, w.word) for x in segs for w in (x.words or [])]
        from pronounce import fix as pron
        r = max(difflib.SequenceMatcher(None, norm(x), norm(heard)).ratio() for x in (s["say"], pron(s["say"])))
        rows.append({"id": s["id"], "score": round(r, 3), "heard": heard.strip()})
        # 같은 음절 3번 이상 반복(뚝뚝뚝, 그 그 그)은 TTS 말더듬 → 일치율과 상관없이 불량
        stutter = re.search(r"([가-힣])\1{2,}|([가-힣]+) \2 \2|(?<![가-힣])([가-힣]) \3 ", heard) and not re.search(r"([가-힣])\1{2,}", s["say"])
        # 첫 단어가 뭉개지면(그래서→그게서, 둘 다→뚝뚝) 귀에 바로 띔 → 첫 두 음절이 다르면 불량
        # 받아쓰기가 숫자로 시작하면(스물일곱→27) 읽기 방식 차이일 뿐이라 첫 음절 비교는 건너뜀
        h2 = "" if re.match(r"\s*\d", heard) else norm(heard)[:2]
        first_bad = h2 and all(norm(x)[:2] != h2 for x in (s["say"], pron(s["say"])))
        onset = onset_stutter(words, (s["say"], pron(s["say"])))  # 단어 첫음 겹침(당당황해서)
        if onset:
            print(f"   ! {s['id']} 첫음 겹침 의심: {onset}", flush=True)
        if stutter or first_bad or onset:
            r = min(r, a.min - 0.01)
        flag = "OK " if r >= a.min else "BAD"
        print(f"{flag} {s['id']} {r:.2f} | {heard.strip()}", flush=True)
        if r < a.min:
            bad.append(s["id"])
    (proj / "narration" / "qa.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("BAD:", ",".join(bad) if bad else "-")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
