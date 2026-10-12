"""자막 싱크 점검 (파형 기준).
Whisper 단어 시각은 쉼 구간 안쪽으로 0.3~0.6초 일찍 찍히는 경향이 있어 기준으로 쓰지 않는다.
대신 완성 영상 음성의 파형에서 '쉼 뒤에 말이 다시 시작되는 순간'(10ms 해상도)을 찾고,
각 자막의 시작 시각과 비교한다. 자막을 0.06초 먼저 띄우는 것은 의도된 값이다.
사용: python3 voice/sync_check.py projects/<이름>
통과 기준: 쉼 뒤에 시작하는 자막의 평균 지연 |차이| ≤ 0.12초, 0.25초 초과 0개
"""
import statistics
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

proj = Path(sys.argv[1])
out = proj / "output"
video = next(f for f in (out / "video.mp4", out / "video_무음미리보기.mp4") if f.exists())
with tempfile.TemporaryDirectory() as td:
    wav = Path(td) / "a.wav"
    # BGM이 섞여 있으므로 목소리 대역만 남겨서 판단
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-af", "highpass=f=250,lowpass=f=4000", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    with wave.open(str(wav)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
hop = 160
n = len(x) // hop
rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
thr = max(0.01, 0.18 * np.percentile(rms, 95))
voiced = rms > thr
onsets, quiet = [], 0
for i, v in enumerate(voiced):
    if not v:
        quiet += 1
    else:
        if quiet >= 7:
            onsets.append(i * 0.01)
        quiet = 0
onsets = np.array(onsets)


def t2s(t):
    h, m, r = t.split(":")
    s_, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s_) + int(ms) / 1000


diffs, bad, cont = [], [], 0
for blk in (out / "subtitles.srt").read_text(encoding="utf-8").strip().split("\n\n"):
    ln = blk.split("\n")
    st = t2s(ln[1].split(" --> ")[0])
    near = onsets[np.abs(onsets - st) <= 0.5] if len(onsets) else []
    if len(near) == 0:
        cont += 1  # 쉼 없이 이어지는 말 중간의 자막 → 파형으로 판단 불가
        continue
    o = near[np.argmin(np.abs(near - st))]
    d = o - st
    diffs.append(d)
    if abs(d - 0.06) > 0.25:
        bad.append(f"{st:7.2f}s 자막이 말보다 {d:+.2f}s '{ln[2][:22]}'")
mean_abs = statistics.mean(abs(d - 0.06) for d in diffs) if diffs else 0
ok = mean_abs <= 0.12 and not bad
print(f"쉼 뒤 자막 {len(diffs)}개 | 의도값(0.06초 먼저) 대비 평균 오차 {mean_abs:.3f}s | 0.25초 초과 {len(bad)}개 | 말 중간 자막 {cont}개 → {'통과' if ok else '재확인 필요'}")
for b in bad:
    print("  ", b)
