"""33편: 8부 영상을 하나로 합치고(챕터·자막 시각 보정), 규칙집 마감(구독 범퍼·아웃트로)을 한 번만 입힌 뒤 묶음을 만든다.
사용: python3 tools/econ2h/merge.py [버전]
"""
import json
import os
import re
import subprocess
import sys

ROOT = "/home/user/kimhyeoncheol/video-studio"
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from make_video import write_meta  # noqa: E402
from tools.rulebook_edit import finish  # noqa: E402

PARTS = [f"projects/20261106-econ2h-p{n:02d}" for n in range(1, 9)]
OUT_DIR = "projects/20261106-econ2h"
out = os.path.join(OUT_DIR, "output")
os.makedirs(out, exist_ok=True)


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip())


def ts_parse(t):
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def ts_fmt(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


offset = 0.0
chapters = [(0.0, "오프닝 — 월급은 그대로인데 왜 나만 가난해질까")]
srt_out, n_sub = [], 0
lst = os.path.join(out, "concat.txt")
with open(lst, "w") as fl:
    for pd in PARTS:
        v = os.path.join(pd, "output", "video.mp4")
        assert os.path.exists(v), v
        fl.write(f"file '{os.path.abspath(v)}'\n")
        for t, name in json.load(open(os.path.join(pd, "output", "chapters.json"), encoding="utf-8")):
            chapters.append((offset + t, name))
        for block in open(os.path.join(pd, "output", "subtitles.srt"), encoding="utf-8").read().strip().split("\n\n"):
            lines = block.split("\n")
            if len(lines) < 3:
                continue
            a, b = lines[1].split(" --> ")
            n_sub += 1
            srt_out.append(f"{n_sub}\n{ts_fmt(ts_parse(a) + offset)} --> {ts_fmt(ts_parse(b) + offset)}\n" + "\n".join(lines[2:]))
        offset += dur(v)

video = os.path.join(out, "video.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", video], check=True)
open(os.path.join(out, "subtitles.srt"), "w", encoding="utf-8").write("\n\n".join(srt_out) + "\n")
total = dur(video)
# 구독 범퍼는 1강(첫 장)이 끝나기 직전, 아웃트로는 마지막 6초
finish(video, chapters[1:], total)
p = json.load(open(os.path.join(OUT_DIR, "meta.json"), encoding="utf-8"))
write_meta(p, out, False, chapters)
json.dump(chapters, open(os.path.join(out, "chapters.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(f"합본 {total / 60:.1f}분 · 챕터 {len(chapters)}개 · 자막 {n_sub}줄")
if len(sys.argv) > 1:
    from studio.package import package
    package(OUT_DIR, p, version=int(sys.argv[1]))
    print("묶음 완료")
