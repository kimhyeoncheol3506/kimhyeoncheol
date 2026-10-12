"""영상 조립: 장면 그림 + 자막 + 느린 줌 + 음성 → mp4.

레이아웃 (벤치마킹 실측 기반)
- 롱폼 1920x1080: 화면 전체 일러스트, 하단 검은 자막 박스 1줄, 오른쪽 위 채널 워터마크  (경제학똑똑 방식)
- 쇼츠 1080x1920: 검은 배경, 상단 고정 제목 2줄(노랑/흰색), 가운데 1:1 그림, 그림 위 2줄 굵은 자막,
  하단 날짜·채널 핸들  (머니치트키 방식)
"""
from __future__ import annotations

import datetime as dt
import os
import re
import subprocess

from PIL import Image, ImageDraw

from . import tts
from .draw import WHITE, YELLOW, draw_text, font, rounded, text_w, wrap
from .scenes import render_visual

FPS = 30
LAYOUT = {
    "long": {"W": 1920, "H": 1080, "content": (0, 0, 1920, 1080), "chunk": 30},
    "shorts": {"W": 1080, "H": 1920, "content": (0, 430, 1080, 1080), "chunk": 18},
}


def split_subtitles(text: str, max_chars: int) -> list[str]:
    """문장부호 기준으로 나눈 뒤, 길면 어절 단위로 max_chars 이하 조각으로 자른다."""
    sents = [s.strip() for s in re.split(r"(?<=[.?!…])\s+", text.strip()) if s.strip()]
    # 쉼표 단위로 한 번 더 나눔 (의미 단위 자막)
    pieces: list[str] = []
    for s in sents:
        if len(s) <= max_chars:
            pieces.append(s)
            continue
        parts = [x.strip() for x in re.split(r"(?<=,)\s+", s) if x.strip()]
        buf = ""
        for x in parts:
            if buf and len(buf) + len(x) + 1 > max_chars:
                pieces.append(buf)
                buf = x
            else:
                buf = f"{buf} {x}".strip()
        if buf:
            pieces.append(buf)
    out: list[str] = []
    for s in pieces:
        if len(s) <= max_chars:
            out.append(s)
            continue
        cur = ""
        for word in s.split(" "):
            if len(cur) + len(word) + 1 > max_chars and cur:
                out.append(cur)
                cur = word
            else:
                cur = f"{cur} {word}".strip()
        if cur:
            out.append(cur)
    # 문장 끝의 짧은 꼬리('필요했습니다.' 등)는 앞 조각에 붙임 — 말 중간에 한 단어만 번쩍 바뀌는 자막은 AI 티가 난다
    extra = 12 if max_chars >= 25 else 8
    merged: list[str] = []
    for c in out:
        tail = len(c.replace(" ", ""))
        prev_open = bool(merged) and not re.search(r"[.?!…]$", merged[-1])
        if merged and (tail <= 4 or (prev_open and tail <= 8)) and len(merged[-1]) + len(c) + 1 <= max_chars + extra:
            merged[-1] = f"{merged[-1]} {c}"
        else:
            merged.append(c)
    return merged


def subtitle_png(fmt: str, text: str, path: str) -> None:
    L = LAYOUT[fmt]
    img = Image.new("RGBA", (L["W"], L["H"]), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    text = text.rstrip(".")
    if fmt == "long":
        f = font("bold", 54)
        lines = wrap(text, f, 1600)
        tw = max(text_w(f, l) for l in lines)
        lh = int(f.size * 1.3)
        bh = lh * len(lines) + 34
        x0, y1 = (L["W"] - tw) / 2 - 36, L["H"] - 48
        rounded(d, [x0, y1 - bh, x0 + tw + 72, y1], 14, fill=(10, 10, 12, 225))
        draw_text(d, (L["W"] / 2, y1 - bh / 2), "\n".join(lines), f, fill=WHITE, spacing=1.3)
    else:
        f = font("black", 76)
        lines = wrap(text, f, 900)[:3]
        cy = LAYOUT["shorts"]["content"][1] + 860
        draw_text(d, (L["W"] / 2, cy), "\n".join(lines), f, fill=WHITE, stroke=9, stroke_fill=(0, 0, 0), spacing=1.2)
    img.save(path)


def chrome_pngs(project: dict, fmt: str, out_dir: str) -> tuple[str, str]:
    """(배경, 최상단 오버레이) PNG. 쇼츠는 고정 제목·날짜·핸들, 롱폼은 워터마크."""
    L = LAYOUT[fmt]
    ch = project.get("channel", {})
    bg = Image.new("RGB", (L["W"], L["H"]), (0, 0, 0))
    top = Image.new("RGBA", (L["W"], L["H"]), (0, 0, 0, 0))
    dt_ = ImageDraw.Draw(top)
    if fmt == "shorts":
        db = ImageDraw.Draw(bg)
        hdr = project.get("header") or [project["title"][:14], ""]
        f1 = font("black", 88)
        draw_text(db, (L["W"] / 2, 250), hdr[0], f1, fill=YELLOW)
        if len(hdr) > 1 and hdr[1]:
            draw_text(db, (L["W"] / 2, 360), hdr[1], f1, fill=WHITE)
        date = project.get("date") or dt.date.today().strftime("%Y.%m.%d")
        draw_text(db, (L["W"] / 2, 1590), date, font("medium", 44), fill=(235, 235, 235))
        if ch.get("handle"):
            draw_text(db, (L["W"] / 2, 1665), f"▶ {ch['handle']}", font("bold", 44), fill=(235, 235, 235))
    else:
        name = ch.get("name", "")
        if name:
            f = font("black", 30)
            lines = "\n".join(wrap(name, f, 160))
            draw_text(dt_, (L["W"] - 110, 70), lines, f, fill=(255, 255, 255, 230), stroke=4, stroke_fill=(40, 40, 40, 230))
    p_bg, p_top = os.path.join(out_dir, "chrome_bg.png"), os.path.join(out_dir, "chrome_top.png")
    bg.save(p_bg)
    top.save(p_top)
    return p_bg, p_top


def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg 실패:\n" + r.stderr[-2000:])


def render_scene(i: int, scene: dict, project: dict, fmt: str, work: str, chrome: tuple[str, str], audio: str) -> tuple[str, list[tuple[float, float, str]]]:
    L = LAYOUT[fmt]
    cx0, cy0, cw, chh = L["content"]
    v = dict(scene.get("visual", {"type": "mascot"}))
    if v.get("type") == "dialogue" and "speaker" not in v:
        v["speaker"] = "f" if scene.get("voice") == "여의도여자" else "m"
    content = os.path.join(work, f"s{i:03d}_content.png")
    render_visual(v, cw, chh, scene.get("bg"), i).save(content)

    adur = tts.duration(audio)
    N = max(1, round((adur + float(scene.get("pause", 0.30 if fmt == "long" else 0.14))) * FPS))
    T = N / FPS  # 영상·음성 모두 정확히 N프레임 길이 (누적 어긋남 방지)
    chunks = split_subtitles(scene.get("caption", scene["text"]), L["chunk"])
    starts = tts.chunk_starts(scene, project, chunks, adur, audio)
    timings = []
    sub_inputs: list[str] = []
    for k, c in enumerate(chunks):
        a = starts[k]
        b = T if k == len(chunks) - 1 else starts[k + 1]
        p = os.path.join(work, f"s{i:03d}_sub{k}.png")
        subtitle_png(fmt, c, p)
        sub_inputs.append(p)
        timings.append((a, b, c))

    zmax = 0.06
    z = f"1+{zmax}*on/{N}" if i % 2 == 0 else f"1+{zmax}-{zmax}*on/{N}"
    fc = [f"[0:v]scale={cw * 2}:-1,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={N}:s={cw}x{chh}:fps={FPS},setsar=1[c]",
          f"[1:v][c]overlay={cx0}:{cy0}:shortest=1[b0]"]
    inputs = ["-i", content, "-loop", "1", "-t", f"{T:.3f}", "-i", chrome[0]]
    last = "b0"
    for k, p in enumerate(sub_inputs):
        inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", p]
        a, b, _ = timings[k]
        fc.append(f"[{last}][{k + 2}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[b{k + 1}]")
        last = f"b{k + 1}"
    inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", chrome[1]]
    top_idx = len(sub_inputs) + 2
    fc.append(f"[{last}][{top_idx}:v]overlay=0:0,format=yuv420p[v]")
    out = os.path.join(work, f"s{i:03d}.mp4")
    _run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]",
          "-frames:v", str(N), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-an", out])
    # 장면 음성을 정확히 N/FPS초로 맞춘 PCM (앞 정렬, 뒤 무음)
    wav = os.path.join(work, f"s{i:03d}.wav")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", audio, "-af", f"aresample=48000,apad=whole_len={N * 48000 // FPS},atrim=end_sample={N * 48000 // FPS}",
          "-ac", "2", "-c:a", "pcm_s16le", wav])
    return out, timings, wav, T


def concat(parts: list[str], out: str, wavs: list[str], bgm: str | None = None, bgm_volume: float = 0.10) -> None:
    """영상 클립(무음)을 이어 붙이고, 장면 음성 PCM을 하나로 이은 트랙을 한 번만 AAC로 인코딩해 합친다.
    (장면마다 AAC로 인코딩하면 장면당 수십 ms씩 음성이 밀려 자막과 어긋난다)"""
    lst, alst = out + ".txt", out + ".a.txt"
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    with open(alst, "w") as f:
        for p in wavs:
            f.write(f"file '{os.path.abspath(p)}'\n")
    vid, aud = out + ".v.mp4", out + ".a.wav"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid])
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", alst, "-c", "copy", aud])
    norm = "loudnorm=I=-14:TP=-1.5:LRA=11"
    if bgm:
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", aud, "-stream_loop", "-1", "-i", bgm, "-filter_complex",
              f"[2:a]volume={bgm_volume}[m];[1:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,{norm}[a]",
              "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    else:
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", aud, "-map", "0:v", "-map", "1:a", "-af", norm, "-c:v", "copy",
              "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    for f in (lst, alst, vid, aud):
        os.remove(f)


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(all_timings: list[tuple[float, float, str]], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for n, (a, b, c) in enumerate(all_timings, 1):
            f.write(f"{n}\n{srt_time(a)} --> {srt_time(b)}\n{c}\n\n")
