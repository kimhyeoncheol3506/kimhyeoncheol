"""다운로드용 파일 이름: 영상 제목 앞 두 글자 (현철님 규칙).
  "예비 시댁 '이혼 서류'…" → 예비.mp4 / 예비.jpg / 예비.txt
  같은 앞 두 글자가 이미 다른 영상에 쓰였으면 예비2, 예비3 … 로 구분. 순화본은 '예비(순화)'.
모든 파일은 output/_업로드/ 한 폴더에도 모아 둔다 (한 폴더에 내려받아도 구분되도록).
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "state" / "names.json"


def base_name(title: str) -> str:
    chars = re.sub(r"[^0-9A-Za-z가-힣]", "", title)
    return chars[:2] or "영상"


def name_for(project: str, title: str, variant: str = "") -> str:
    reg = json.loads(REG.read_text(encoding="utf-8")) if REG.exists() else {}
    key = project
    if key in reg:
        return reg[key]
    b = base_name(title)
    taken = set(reg.values())
    n, k = b, 2
    while (n + variant) in taken:
        n = f"{b}{k}"
        k += 1
    reg[key] = n + variant
    REG.parent.mkdir(exist_ok=True)
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    return reg[key]


def export(out_dir: Path, project: str, title: str, variant: str = "") -> list[Path]:
    n = name_for(project, title, variant)
    flat = ROOT / "output" / "_업로드"
    flat.mkdir(parents=True, exist_ok=True)
    made = []
    for src, ext in (("video.mp4", "mp4"), ("thumbnail.jpg", "jpg"), ("upload.txt", "txt")):
        s = out_dir / src
        if s.exists():
            for d in (out_dir / f"{n}.{ext}", flat / f"{n}.{ext}"):
                shutil.copyfile(s, d)
            made.append(out_dir / f"{n}.{ext}")
    return made
