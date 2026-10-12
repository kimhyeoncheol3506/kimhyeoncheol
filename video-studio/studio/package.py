"""다운로드용 파일 묶음: 모든 파일 이름에 '제목_v버전_종류.확장자'를 붙여 output/다운로드/ 에 모은다.

수정할 때마다 버전이 하나씩 올라가고(v1, v2, …), 예전 버전 파일은 그대로 남는다.
영상이 전송 한도(29MB)를 넘으면 화질을 거의 유지한 압축본을 만든다 (원본 output/video.mp4는 그대로).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess

SEND_LIMIT = 29 * 1024 * 1024


def file_title(p: dict) -> str:
    t = p.get("file_title") or p.get("title", "영상")
    t = re.sub(r"[\\/:*?\"<>|'’‘“”]", "", t)
    t = re.sub(r"[.,!·]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > 30:
        cut = t[:30]
        t = cut[: cut.rfind(" ")] if " " in cut else cut
    return t.replace(" ", "_")


def next_version(ddir: str) -> int:
    vs = [int(m.group(1)) for f in os.listdir(ddir) if (m := re.search(r"_v(\d+)_", f))] if os.path.isdir(ddir) else []
    return max(vs, default=0) + 1


def _send_copy(src: str, out_dir: str) -> str:
    """전송 한도를 넘으면 압축본(캐시)을 만들어 그 경로를 돌려준다."""
    if os.path.getsize(src) <= SEND_LIMIT:
        return src
    cache = os.path.join(out_dir, "video_전송용.mp4")
    if not (os.path.exists(cache) and os.path.getmtime(cache) >= os.path.getmtime(src)):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-c:v", "libx264", "-preset", "slow", "-crf", "26",
                        "-tune", "animation", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", cache], check=True)
    return cache


def package(pdir: str, p: dict, version: int | None = None) -> list[str]:
    out = os.path.join(pdir, "output")
    ddir = os.path.join(out, "다운로드")
    os.makedirs(ddir, exist_ok=True)
    v = version or next_version(ddir)
    base = f"{file_title(p)}_v{v}"
    made = []

    def put(src, kind, ext):
        if src and os.path.exists(src):
            dst = os.path.join(ddir, f"{base}_{kind}.{ext}")
            shutil.copyfile(src, dst)
            made.append(dst)

    video = os.path.join(out, "video.mp4")
    put(_send_copy(video, out) if os.path.exists(video) else None, "영상", "mp4")
    put(os.path.join(out, "thumbnail.png"), "썸네일", "png")
    put(os.path.join(out, "thumbnail_shorts.png"), "쇼츠썸네일", "png")
    put(os.path.join(out, "subtitles.srt"), "자막", "srt")
    put(os.path.join(out, "업로드정보.md"), "업로드정보", "md")
    meta = [os.path.join(out, n) for n in ("title.txt", "description.txt", "tags.txt")]
    if all(os.path.exists(m) for m in meta):
        dst = os.path.join(ddir, f"{base}_제목·설명·태그.txt")
        t, d, g = (open(m, encoding="utf-8").read().strip() for m in meta)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(f"[제목]\n{t}\n\n[설명]\n{d}\n\n[태그]\n{g}\n")
        made.append(dst)
    print(f"다운로드 묶음 v{v}: {ddir}")
    for m in made:
        print("  ", os.path.basename(m))
    return made
