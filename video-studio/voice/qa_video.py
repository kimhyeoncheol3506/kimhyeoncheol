"""완성 영상 받아쓰기 점검 (Whisper). 대본과 나란히 출력해 뭉개진 단어를 찾는다.

사용: <TTS_PYTHON> voice/qa_video.py projects/<이름>/project.json
주의: 받아쓰기는 실제 발음대로 적힌다 (예: '금리인하'는 표준 발음 [금리이나]로 적힘 — 정상).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import soundfile as sf
from faster_whisper import WhisperModel

pj = Path(sys.argv[1])
p = json.loads(pj.read_text(encoding="utf-8"))
out = pj.parent / "output"
video = next((f for f in (out / "video.mp4", out / "video_무음미리보기.mp4") if f.exists()))
with tempfile.TemporaryDirectory() as td:
    wav = Path(td) / "a.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    audio, _ = sf.read(wav, dtype="float32")
hint = ", ".join({w for s in p["scenes"] for w in s["text"].split() if len(w) >= 4})[:400]
segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(audio, language="ko", initial_prompt=hint)
print("── 대본 ──")
for s in p["scenes"]:
    print(f"{s['id']} [{s.get('voice', '여의도남자')}] {s['text']}")
print("── 받아쓰기 ──")
for s in segs:
    print(f"{s.start:6.1f}s {s.text.strip()}")
