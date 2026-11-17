"""PC 자동 업로드용 묶음 만들기 (2026-11-18 현철님 지정 형식).
사용: python3 tools/make_upload.py projects/<slug>.yaml <최종 mp4> <썸네일 png> <저장소>/release_upload/hot3/ep1 hot3-ep1
만드는 것: video.mp4.part000… (90MB 조각) · video.mp4.sha256 · thumb.png(또는 thumb.jpg, 1280x720, 2MB 이하) · upload.json
READY 는 만들지 않는다 — 최종 검수(tools/final_qc.py) 통과 뒤 따로 만든다."""
import hashlib
import json
import os
import re
import subprocess
import sys

import yaml
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
proj_path, mp4, thumb, dst, date = sys.argv[1:6]
proj = yaml.safe_load(open(proj_path, encoding="utf-8"))
slug = proj.get("slug") or os.path.splitext(os.path.basename(proj_path))[0]
os.makedirs(dst, exist_ok=True)
for f in os.listdir(dst):                                   # 이전 묶음 지우기(이 폴더 안 파일만)
    if f.startswith("video.mp4") or f in ("thumb.png", "thumb.jpg", "upload.json", "READY"):
        os.remove(os.path.join(dst, f))

# 1) 조각 + sha256
subprocess.run(["split", "-b", "90m", "-d", "-a", "3", mp4, os.path.join(dst, "video.mp4.part")], check=True)
h = hashlib.sha256()
with open(mp4, "rb") as fp:
    for b in iter(lambda: fp.read(1 << 20), b""):
        h.update(b)
open(os.path.join(dst, "video.mp4.sha256"), "w").write(h.hexdigest() + "\n")

# 2) 썸네일 1280x720, 2MB 이하
im = Image.open(thumb).convert("RGB").resize((1280, 720), Image.LANCZOS)
tname = "thumb.png"
im.save(os.path.join(dst, tname), optimize=True)
if os.path.getsize(os.path.join(dst, tname)) > 2 * 1024 * 1024:
    os.remove(os.path.join(dst, tname))
    tname = "thumb.jpg"
    q = 92
    while True:
        im.save(os.path.join(dst, tname), quality=q, optimize=True)
        if os.path.getsize(os.path.join(dst, tname)) <= 2 * 1024 * 1024 or q < 60:
            break
        q -= 5

# 3) 설명란: 요약 · 챕터 · 출처(매체·날짜·링크) · 고지 · 해시태그 — 4900자 이하
desc_md = open(os.path.join(ROOT, "output", slug, "description.md"), encoding="utf-8").read().splitlines()
chap = []
if "챕터" in desc_md:
    i = desc_md.index("챕터") + 1
    while i < len(desc_md) and re.match(r"\d\d:\d\d ", desc_md[i]):
        chap.append(desc_md[i])
        i += 1
summary = proj.get("summary", "").strip()
tags = [t.lstrip("#") for t in proj.get("tags", [])]
head = [summary, "", "⏱ 챕터"] + chap + [""]
tail = ["", proj.get("disclaimer", "").strip(), "", " ".join("#" + t for t in tags[:15])]
srcs = proj.get("sources", [])


def src_line(s, url=True):
    d = str(s.get("date", ""))
    return f"· {s['outlet']} {d} 「{s['title']}」" + (f" {s['url']}" if url and s.get("url") else "")


def build(url):
    return "\n".join(head + ["📚 출처"] + [src_line(s, url) for s in srcs] + tail).strip()


desc = build(True)
if len(desc) > 4900:
    desc = build(False)
if len(desc) > 4900:                                         # 그래도 길면 출처 줄 뒤쪽을 줄이고 '외 N건'
    lines = [src_line(s, False) for s in srcs]
    while lines and len("\n".join(head + ["📚 출처"] + lines + [f"· 외 {len(srcs) - len(lines)}건"] + tail)) > 4900:
        lines.pop()
    desc = "\n".join(head + ["📚 출처"] + lines + [f"· 외 {len(srcs) - len(lines)}건"] + tail).strip()
title = proj["title"].replace("<", "‹").replace(">", "›")      # 유튜브는 < > 를 받지 않는다
desc = desc.replace("<", "‹").replace(">", "›")
assert len(title) <= 100, f"제목 100자 초과({len(title)})"
tg, n = [], 0                                               # 유튜브 태그 합계 500자 이하
for t in tags:
    if n + len(t) + 1 > 480:
        break
    tg.append(t)
    n += len(t) + 1
up = {"date": date, "long": {"file": "video.mp4", "title": title, "description": desc, "tags": tg, "thumb": tname}}
json.dump(up, open(os.path.join(dst, "upload.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
parts = sorted(f for f in os.listdir(dst) if f.startswith("video.mp4.part"))
print(f"{dst}: 조각 {len(parts)}개, sha256 {h.hexdigest()[:12]}…, {tname} {os.path.getsize(os.path.join(dst, tname)) // 1024}KB, 설명란 {len(desc)}자, 태그 {len(tg)}개")
