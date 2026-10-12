"""단어 단위 타임스탬프 추출 (Whisper) → 자막을 실제 말하는 순간에 맞추기 위한 정렬 정보.

각 장면의 원본 음성(audio/<id>_<hash>.wav)마다 audio/<id>_<hash>.align.json 을 만든다:
  {"words": [{"start": 0.12, "end": 0.48, "w": "기준금리"}, ...], "speech_start": 0.1, "speech_end": 3.9}
자막 문장과 받아쓰기 글자가 조금 달라도(숫자 읽기 등) 글자 수 비율로 대응시키므로 동작한다.

사용: <TTS_PYTHON> voice/align.py projects/<이름>/project.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from studio.keys import raw_name  # noqa: E402


def load16k(path: Path) -> np.ndarray:
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != 16000:
        n = int(len(x) * 16000 / sr)
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
    return x


def main():
    pj = Path(sys.argv[1])
    p = json.loads(pj.read_text(encoding="utf-8"))
    audio = pj.parent / "audio"
    todo = []
    for s in p["scenes"]:
        wav = audio / raw_name(s)
        out = wav.with_suffix(".align.json")
        if wav.exists() and not out.exists():
            todo.append((s, wav, out))
    if not todo:
        print("정렬: 새로 할 장면 없음")
        return
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    for s, wav, out in todo:
        segs, _ = model.transcribe(load16k(wav), language="ko", word_timestamps=True, initial_prompt=s["text"][:200],
                                   vad_filter=False, condition_on_previous_text=False)
        words = [{"start": round(w.start, 3), "end": round(w.end, 3), "w": w.word.strip()} for seg in segs for w in (seg.words or [])]
        x = load16k(wav)
        loud = np.where(np.abs(x) > 0.02)[0]
        data = {"words": words,
                "speech_start": round(float(loud[0]) / 16000, 3) if len(loud) else 0.0,
                "speech_end": round(float(loud[-1]) / 16000, 3) if len(loud) else len(x) / 16000}
        out.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"정렬 {s['id']}: 단어 {len(words)}개")


if __name__ == "__main__":
    main()
