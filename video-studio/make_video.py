"""경제 영상 1세트 생성기: 영상(mp4) + 제목 + 설명란 + 태그 + 썸네일 + 자막(srt)

사용법
  python make_video.py projects/<이름>/project.json                 # 여의도 목소리(Voicebox)로 완성본
  python make_video.py projects/<이름>/project.json --preview-silent # 목소리 없이 화면 구성 미리보기
  python make_video.py projects/<이름>/project.json --thumb-only     # 썸네일·메타데이터만

결과: projects/<이름>/output/
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from studio import tts  # noqa: E402
from studio.render import LAYOUT, chrome_pngs, concat, render_scene, write_srt  # noqa: E402
from studio.thumbnail import make_thumbnail  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.join(HERE, "..", ".claude", "skills", "econ-video", "SKILL.md")


def engine_version() -> str:
    with open(os.path.join(HERE, "VERSION"), encoding="utf-8") as f:
        return f.read().strip()


def skill_version() -> str | None:
    if not os.path.exists(SKILL):
        return None
    with open(SKILL, encoding="utf-8") as f:
        for line in f:
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip()
    return None


def check_version() -> bool:
    ev, sv = engine_version(), skill_version()
    if sv is None:
        print(f"엔진 v{ev} (스킬 파일 없음 — 엔진만 단독 사용)")
        return True
    if ev != sv:
        print(f"⚠️ 버전 불일치: 스킬 v{sv} / 엔진 v{ev}. git pull 로 맞춘 뒤 다시 실행하세요.")
        return False
    print(f"econ-video v{ev} (스킬·엔진 일치)")
    return True


def chapter_block(chapters: list[tuple[float, str]]) -> str:
    """유튜브 챕터: 첫 항목 00:00, 3개 이상일 때만 표시."""
    if len(chapters) < 3:
        return ""
    def ts(t: float) -> str:
        t = int(t)
        return f"{t // 3600}:{t // 60 % 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60:02d}:{t % 60:02d}"
    return "⏱ 타임라인\n" + "\n".join(f"{ts(0 if i == 0 else t)} {name}" for i, (t, name) in enumerate(chapters))


def write_meta(p: dict, out: str, silent: bool, chapters: list[tuple[float, str]] | None = None) -> None:
    tags = p.get("tags", [])
    hashtags = " ".join(h if h.startswith("#") else f"#{h}" for h in p.get("hashtags", []))
    chap = chapter_block(chapters or [])
    desc = p["description"].strip() + ("\n\n" + chap if chap else "") + ("\n\n" + hashtags if hashtags else "")
    with open(os.path.join(out, "title.txt"), "w", encoding="utf-8") as f:
        f.write(p["title"] + "\n")
    with open(os.path.join(out, "description.txt"), "w", encoding="utf-8") as f:
        f.write(desc + "\n")
    with open(os.path.join(out, "tags.txt"), "w", encoding="utf-8") as f:
        f.write(", ".join(tags) + "\n")
    with open(os.path.join(out, "업로드정보.md"), "w", encoding="utf-8") as f:
        f.write(f"# 업로드 세트 — {p['title']}\n\n제작 도구: econ-video v{engine_version()}\n\n")
        if silent:
            f.write("> ⚠️ 무음 미리보기입니다. 업로드 전 여의도 목소리로 다시 생성하세요.\n\n")
        f.write(f"## 제목\n{p['title']}\n\n## 설명란\n{desc}\n\n## 태그\n{', '.join(tags)}\n\n")
        f.write(f"## 형식\n{'쇼츠 (9:16)' if p['format'] == 'shorts' else '롱폼 (16:9)'}\n\n")
        f.write("## 파일\n- video.mp4 — 업로드할 영상\n- thumbnail.png — 썸네일 (쇼츠는 thumbnail_shorts.png를 앱에서 커버로 지정)\n- subtitles.srt — 유튜브 자막 업로드용\n")
        if p.get("sources"):
            f.write("\n## 확인한 자료 출처\n" + "\n".join(f"- {s}" for s in p["sources"]) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?")
    ap.add_argument("--version", action="store_true", help="스킬·엔진 버전 확인")
    ap.add_argument("--voice", choices=["auto", "voicebox", "cloud"], default="auto",
                    help="여의도 목소리 엔진: auto(Voicebox 우선, 없으면 클라우드) / voicebox(PC) / cloud(Qwen3-TTS 직접)")
    ap.add_argument("--preview-silent", action="store_true", help="목소리 없이 무음으로 화면만 미리보기")
    ap.add_argument("--thumb-only", action="store_true")
    a = ap.parse_args()
    ok = check_version()
    if a.version:
        sys.exit(0 if ok else 1)
    if not ok:
        sys.exit(1)
    if not a.project:
        ap.error("project.json 경로가 필요합니다")

    pdir = os.path.dirname(os.path.abspath(a.project))
    with open(a.project, encoding="utf-8") as f:
        p = json.load(f)
    fmt = p["format"]
    assert fmt in LAYOUT, "format은 long 또는 shorts"
    out = os.path.join(pdir, "output")
    work = os.path.join(pdir, "work")
    os.makedirs(out, exist_ok=True)
    os.makedirs(work, exist_ok=True)

    th = p.get("thumbnail", {})
    make_thumbnail(th, os.path.join(out, "thumbnail.png"), (1280, 720))
    if fmt == "shorts":
        make_thumbnail(th, os.path.join(out, "thumbnail_shorts.png"), (1080, 1920))
    if a.thumb_only:
        write_meta(p, out, False)
        print("썸네일·메타데이터 생성 완료:", out)
        return

    audio_dir = os.path.join(pdir, "audio")
    if not a.preview_silent:
        engine = tts.resolve_engine(a.voice)
        print(f"목소리 엔진: {engine} (여의도남자{'·여의도여자' if any(s.get('voice') == '여의도여자' for s in p['scenes']) else ''})")
        tts.generate_all(os.path.abspath(a.project), p, engine, audio_dir)
    chrome = chrome_pngs(p, fmt, work)
    parts, timings, offset, all_real, chapters = [], [], 0.0, True, []
    for i, sc in enumerate(p["scenes"]):
        audio, real = tts.scene_audio(sc, p, audio_dir, a.preview_silent)
        all_real &= real
        if sc.get("chapter"):
            chapters.append((offset, sc["chapter"]))
        clip, tm = render_scene(i, sc, p, fmt, work, chrome, audio)
        parts.append(clip)
        timings += [(offset + s, offset + e, c) for s, e, c in tm]
        offset += tts.duration(clip)
        print(f"[{i + 1}/{len(p['scenes'])}] {sc['id']} {'' if real else '(무음)'} {sc['text'][:30]}")
    name = "video.mp4" if all_real else "video_무음미리보기.mp4"
    bgm = p.get("bgm")
    concat(parts, os.path.join(out, name), os.path.join(pdir, bgm) if bgm else None, float(p.get("bgm_volume", 0.10)))
    write_srt(timings, os.path.join(out, "subtitles.srt"))
    write_meta(p, out, not all_real, chapters)
    shutil.rmtree(work, ignore_errors=True)
    print(f"완료: {os.path.join(out, name)} ({offset:.1f}초)")


if __name__ == "__main__":
    try:
        main()
    except tts.VoiceboxUnavailable as e:
        print("❌", e)
        sys.exit(2)
