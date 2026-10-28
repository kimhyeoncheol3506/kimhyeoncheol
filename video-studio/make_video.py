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
from studio.package import package  # noqa: E402

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


def recent_thumb_layouts(pdir: str, n: int = 4) -> list[str]:
    """최근 n개 다른 프로젝트의 썸네일 컨셉(layout)."""
    root = os.path.dirname(pdir)
    out = []
    for d in sorted(os.listdir(root), key=lambda x: os.path.getmtime(os.path.join(root, x)), reverse=True):
        pj = os.path.join(root, d, "project.json")
        if d == os.path.basename(pdir) or not os.path.exists(pj) or "sample" in d:
            continue
        try:
            out.append(json.load(open(pj, encoding="utf-8")).get("thumbnail", {}).get("layout", "split"))
        except (OSError, ValueError):
            continue
        if len(out) >= n:
            break
    return out


def pick_thumb_font(pdir: str) -> str:
    """다른 프로젝트들이 최근에 쓴 썸네일 폰트를 피해서 순환 목록의 다음 폰트를 고른다."""
    from studio.thumbnail import THUMB_FONTS
    root = os.path.dirname(pdir)
    used = []
    for d in sorted(os.listdir(root), key=lambda n: os.path.getmtime(os.path.join(root, n)), reverse=True):
        pj = os.path.join(root, d, "project.json")
        if d == os.path.basename(pdir) or not os.path.exists(pj):
            continue
        try:
            f = json.load(open(pj, encoding="utf-8")).get("thumbnail", {}).get("font")
        except (OSError, ValueError):
            continue
        if f and f not in used:
            used.append(f)
    for f in THUMB_FONTS:
        if f not in used:
            return f
    return used[-1]  # 모두 쓰였으면 가장 오래전에 쓴 폰트



def _engine_sig() -> str:
    """엔진 코드가 바뀌면 캐시를 무효화하기 위한 서명 (studio/*.py 내용 해시)."""
    import hashlib
    h = hashlib.sha1()
    for fn in sorted(os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "studio"))):
        if fn.endswith(".py"):
            h.update(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "studio", fn), "rb").read())
    return h.hexdigest()[:10]


_SIG = None


def _cached_scene(i, sc, p, fmt, work, chrome, audio, pdir):
    """장면 클립 캐시 (v1.13.8): 장면 내용·음성·엔진이 같으면 다시 그리지 않는다. 수정한 장면만 새로 렌더."""
    import hashlib
    global _SIG
    if _SIG is None:
        _SIG = _engine_sig()
    h = hashlib.sha1()
    h.update(json.dumps(sc, sort_keys=True, ensure_ascii=False).encode())
    h.update(json.dumps({k: p.get(k) for k in ("format", "corner_mascot", "channel", "headline_bg", "headline_line", "speed")}, sort_keys=True, ensure_ascii=False).encode())
    h.update(_SIG.encode())
    h.update(str(i).encode())
    try:
        h.update(open(audio, "rb").read()) if audio and os.path.exists(audio) else h.update(b"-")
    except OSError:
        h.update(b"-")
    for key in ("image", "path"):
        img = (sc.get("visual") or {}).get(key)
        if img and os.path.exists(img):
            h.update(open(img, "rb").read())
    k = h.hexdigest()[:12]
    cdir = os.path.join(pdir, "clipcache")
    os.makedirs(cdir, exist_ok=True)
    base = os.path.join(cdir, f"{sc['id']}_{k}")
    if all(os.path.exists(base + e) for e in (".mp4", ".wav", ".json")):
        meta = json.load(open(base + ".json", encoding="utf-8"))
        return base + ".mp4", [tuple(x) for x in meta["tm"]], base + ".wav", meta["T"]
    for fn in os.listdir(cdir):  # 같은 장면의 예전 캐시 정리
        if fn.startswith(sc["id"] + "_"):
            os.remove(os.path.join(cdir, fn))
    clip, tm, swav, T = render_scene(i, sc, p, fmt, work, chrome, audio)
    shutil.copy(clip, base + ".mp4")
    shutil.copy(swav, base + ".wav")
    json.dump({"tm": tm, "T": T}, open(base + ".json", "w", encoding="utf-8"))
    return base + ".mp4", tm, base + ".wav", T


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?")
    ap.add_argument("--version", action="store_true", help="스킬·엔진 버전 확인")
    ap.add_argument("--voice", choices=["auto", "voicebox", "cloud"], default="auto",
                    help="여의도 목소리 엔진: auto(Voicebox 우선, 없으면 클라우드) / voicebox(PC) / cloud(Qwen3-TTS 직접)")
    ap.add_argument("--preview-silent", action="store_true", help="목소리 없이 무음으로 화면만 미리보기")
    ap.add_argument("--thumb-only", action="store_true")
    ap.add_argument("--no-package", action="store_true", help="다운로드 묶음(제목_v버전) 만들지 않기")
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
    if th and not th.get("font"):  # 썸네일 폰트: 최근 영상들과 겹치지 않는 대표 폰트를 골라 고정
        th["font"] = pick_thumb_font(pdir)
        p["thumbnail"] = th
        with open(a.project, "w", encoding="utf-8") as f:
            json.dump(p, f, ensure_ascii=False, indent=1)
        print(f"썸네일 폰트: {th['font']}")
    recent = recent_thumb_layouts(pdir)
    if th and th.get("layout", "split") in recent:  # 회차마다 분위기 50% 이상 다르게 (현철님 규칙)
        print(f"⚠ 썸네일 컨셉 '{th.get('layout', 'split')}'이 최근 회차와 같습니다 (최근: {recent}) — 다른 컨셉을 고르세요")
    os.environ["THUMB_PROJECT_DIR"] = pdir  # 표지 그림을 쓰는 썸네일용
    make_thumbnail(th, os.path.join(out, "thumbnail.png"), (1280, 720))
    # 썸네일 4종 (현철님 규칙: 매 회차 서로 다른 컨셉 4개) — variants의 각 항목은 기본 thumbnail 위에 덮어쓰는 값
    for i, var in enumerate(th.get("variants", [])[:4]):
        spec = {k: v for k, v in th.items() if k != "variants"}
        spec.update(var)
        make_thumbnail(spec, os.path.join(out, f"thumbnail_{'ABCD'[i]}.png"), (1280, 720))
    if fmt == "shorts":
        make_thumbnail(th, os.path.join(out, "thumbnail_shorts.png"), (1080, 1920))
    if a.thumb_only:
        write_meta(p, out, False)
        print("썸네일·메타데이터 생성 완료:", out)
        if not a.no_package:
            package(pdir, p)
        return

    audio_dir = os.path.join(pdir, "audio")
    if not a.preview_silent:
        engine = tts.resolve_engine(a.voice)
        print(f"목소리 엔진: {engine} (여의도남자{'·여의도여자' if any(s.get('voice') == '여의도여자' for s in p['scenes']) else ''})")
        tts.generate_all(os.path.abspath(a.project), p, engine, audio_dir)
        tts.align_all(os.path.abspath(a.project))  # 자막 싱크용 단어 타임스탬프 (Whisper)
    chrome = chrome_pngs(p, fmt, work)
    parts, wavs, timings, offset, all_real, chapters, sfx_events = [], [], [], 0.0, True, [], []
    for i, sc in enumerate(p["scenes"]):
        audio, real = tts.scene_audio(sc, p, audio_dir, a.preview_silent)
        all_real &= real
        if sc.get("chapter"):
            chapters.append((offset, sc["chapter"]))
        if p.get("sfx", True) and fmt == "long":  # 챕터 첫 장면 = snap, scene "sfx": "ding"|"click"|"snap" 직접 지정, "none"이면 끔
            kind = sc.get("sfx", "snap" if sc.get("chapter") and i > 0 else None)
            if kind and kind != "none":
                sfx_events.append((offset + 0.02, kind))
        if fmt == "long" and "pause" not in sc and i + 1 < len(p["scenes"]) and p["scenes"][i + 1].get("chapter"):
            sc = dict(sc, pause=0.45)  # 장이 바뀌기 전 쉼 0.45초 (v1.13.0, 일반 장면 사이는 0.30초)
        clip, tm, swav, T = _cached_scene(i, sc, p, fmt, work, chrome, audio, pdir)
        if T > 10.5:
            print(f"   ⚠ {sc['id']}: 한 장면이 {T:.1f}초 — 같은 화면이 10초를 넘기지 않게 장면을 나누거나 화면 변화를 넣기")
        parts.append(clip)
        wavs.append(swav)
        timings += [(offset + s, offset + e, c) for s, e, c in tm]
        offset += T
        print(f"[{i + 1}/{len(p['scenes'])}] {sc['id']} {'' if real else '(무음)'} {sc['text'][:30]}")
    name = "video.mp4" if all_real else "video_무음미리보기.mp4"
    # BGM: 기본은 코드로 합성한 로파이(롱폼)/펄스(쇼츠) + 목소리 더킹. "bgm": "none"이면 끔, 파일 경로면 그 음원 사용
    bgm = p.get("bgm", "lofi" if fmt == "long" else "pulse")
    final = os.path.join(out, name)
    if bgm in ("lofi", "pulse"):
        joined = final + ".nobgm.mp4"
        concat(parts, joined, wavs)
        from studio.audio import mix_bgm
        if sfx_events and offset > 0 and len(sfx_events) / (offset / 60) > 3:
            print(f"   ⚠ 효과음 {len(sfx_events)}개 = 분당 {len(sfx_events) / (offset / 60):.1f}개 — 1분에 1~3개 이내로")
        mix_bgm(joined, final, bgm, gain=float(p.get("bgm_volume", 0.16)), events=sfx_events)
        os.remove(joined)
    else:
        concat(parts, final, wavs, os.path.join(pdir, bgm) if bgm and bgm != "none" else None, float(p.get("bgm_volume", 0.10)))
    write_srt(timings, os.path.join(out, "subtitles.srt"))
    write_meta(p, out, not all_real, chapters)
    shutil.rmtree(work, ignore_errors=True)
    print(f"완료: {os.path.join(out, name)} ({offset:.1f}초)")
    if all_real and not a.no_package:
        package(pdir, p)  # 다운로드용: 제목_v버전_종류.확장자


if __name__ == "__main__":
    try:
        main()
    except tts.VoiceboxUnavailable as e:
        print("❌", e)
        sys.exit(2)
