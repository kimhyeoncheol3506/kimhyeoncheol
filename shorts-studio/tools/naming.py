"""다운로드용 파일 이름 = 영상 제목 그대로 (현철님 규칙, v1.7.0~).
  "결혼식 날 축의금 다 가져간 장모님… | 처가 전쟁 1화"
    → 결혼식 날 축의금 다 가져간 장모님… ｜ 처가 전쟁 1화.mp4 / .jpg / .txt
  윈도우·휴대폰에서 못 쓰는 기호(\\ / : * ? " < > |)는 모양이 같은 전각 문자로 바꿔 제목이 그대로 보이게 한다.
  같은 제목이 이미 다른 영상에 쓰였으면 ' (2)', ' (3)' … 로 구분. 순화본은 끝에 ' (순화)'.
  제목이 바뀌어 다시 렌더하면 예전 이름 파일은 지운다.
모든 파일은 output/_업로드/ 한 폴더에도 모아 둔다 (한 폴더에 내려받아도 구분되도록).
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "state" / "names.json"
EXTS = (("video.mp4", "mp4"), ("thumbnail.jpg", "jpg"), ("upload.txt", "txt"))
SAFE = str.maketrans({"\\": "＼", "/": "／", ":": "：", "*": "＊", "?": "？", '"': "'",
                      "<": "〈", ">": "〉", "|": "｜"})
MAX = 90  # 파일 이름 길이 상한 (확장자 제외)


def base_name(title: str) -> str:
    t = re.sub(r"[\x00-\x1f]", "", title).translate(SAFE)
    t = re.sub(r"\s+", " ", t).strip().rstrip(".")
    if len(t) > MAX:
        t = t[:MAX].rstrip(" .") + "…"
    return t or "영상"


def name_for(project: str, title: str, variant: str = "") -> str:
    reg = json.loads(REG.read_text(encoding="utf-8")) if REG.exists() else {}
    b = base_name(title)
    suffix = f" {variant}" if variant else ""
    taken = {v for k, v in reg.items() if k != project}
    n, k = b + suffix, 2
    while n in taken:
        n = f"{b} ({k}){suffix}"
        k += 1
    old = reg.get(project)
    if old and old != n:  # 제목이 바뀌었으면 예전 이름 파일 정리
        for _, ext in EXTS:
            for d in (ROOT / "output" / project, ROOT / "output" / "_업로드"):
                (d / f"{old}.{ext}").unlink(missing_ok=True)
    reg[project] = n
    REG.parent.mkdir(exist_ok=True)
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    return n


def export(out_dir: Path, project: str, title: str, variant: str = "") -> list[Path]:
    n = name_for(project, title, variant)
    flat = ROOT / "output" / "_업로드"
    flat.mkdir(parents=True, exist_ok=True)
    made = []
    for src, ext in EXTS:
        s = out_dir / src
        if s.exists():
            for d in (out_dir / f"{n}.{ext}", flat / f"{n}.{ext}"):
                shutil.copyfile(s, d)
            made.append(out_dir / f"{n}.{ext}")
    return made
