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
HEADLINE_H = 190  # v1.11.0 상단 헤드라인 띠 높이 (롱폼, 레퍼런스: 화면 위 약 18%)
LAYOUT = {
    "long": {"W": 1920, "H": 1080, "content": (0, 0, 1920, 1080), "chunk": 30},
    "shorts": {"W": 1080, "H": 1920, "content": (0, 430, 1080, 1080), "chunk": 14},
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


def headline_png(text: str, path: str, project: dict) -> None:
    """상단 헤드라인 띠: 장면의 핵심 숫자·결론 5~12자를 초대형으로. 숫자가 든 어절(또는 [대괄호] 안)은 빨강 강조."""
    W = LAYOUT["long"]["W"]
    img = Image.new("RGBA", (W, HEADLINE_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = tuple(project.get("headline_bg", (250, 247, 238)))
    d.rectangle([0, 0, W, HEADLINE_H], fill=bg + (255,))
    d.rectangle([0, HEADLINE_H - 10, W, HEADLINE_H], fill=tuple(project.get("headline_line", (24, 24, 28))) + (255,))
    words = re.findall(r"\[[^\]]+\]|\S+", text)
    toks = [(w.strip("[]"), w.startswith("[") or bool(re.search(r"\d", w))) for w in words]
    plain = " ".join(t for t, _ in toks)
    maxw = W - 330  # 오른쪽 위 채널 워터마크 자리 비움
    size = 150
    while size > 60 and text_w(font("black", size), plain) > maxw:
        size -= 4
    f = font("black", size)
    x, y = 46, (HEADLINE_H - 10) / 2
    space = text_w(f, " ")
    for t, hl in toks:
        d.text((x, y), t, font=f, fill=(222, 40, 40) if hl else (20, 20, 24), anchor="lm")
        x += text_w(f, t) + space
    img.save(path)


def corner_mascot_png(project: dict, path: str) -> None:
    """왼쪽 아래 고정 캐릭터 아이콘 (레퍼런스: 진행자 캐릭터가 모든 장면에 작게 상주)."""
    from .draw import mascot
    L = LAYOUT["long"]
    img = Image.new("RGBA", (L["W"], L["H"]), (0, 0, 0, 0))
    key = Image.new("RGB", (360, 420), (255, 0, 255))
    mascot(key, 180, 140, 0.42, "smug", "m", "normal")
    import numpy as np
    a = np.array(key)
    m = ~((a[:, :, 0] == 255) & (a[:, :, 1] == 0) & (a[:, :, 2] == 255))
    k = key.convert("RGBA")
    k.putalpha(Image.fromarray((m * 255).astype("uint8")))
    k = k.crop((40, 0, 320, 330)).resize((168, 198))
    img.alpha_composite(k, (10, L["H"] - 198))
    img.save(path)


def subtitle_png(fmt: str, text: str, path: str, maxw: int = 1600) -> None:
    L = LAYOUT[fmt]
    img = Image.new("RGBA", (L["W"], L["H"]), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    text = text.rstrip(".")
    if fmt == "long":
        f = font("bold", 54)
        lines = wrap(text, f, maxw)
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
        # 날짜·핸들은 위쪽 한 줄로 (v1.13.1): 쇼츠 아래 18%(y 1574~)는 유튜브 버튼·제목이 덮는 자리라 비운다
        tag = f"{date}  ·  ▶ {ch['handle']}" if ch.get("handle") else date
        draw_text(db, (L["W"] / 2, 135), tag, font("bold", 40), fill=(235, 235, 235))
    else:
        if project.get("corner_mascot"):
            cm = os.path.join(out_dir, "corner_mascot.png")
            corner_mascot_png(project, cm)
            top.alpha_composite(Image.open(cm))
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
    hl = scene.get("headline") if fmt == "long" else None
    if hl:  # 헤드라인이 있으면 그림은 그 아래 영역에
        cy0, chh = HEADLINE_H, L["H"] - HEADLINE_H
    v = dict(scene.get("visual", {"type": "mascot"}))
    if v.get("type") == "dialogue" and "speaker" not in v:
        v["speaker"] = "f" if scene.get("voice") == "여의도여자" else "m"
    content = os.path.join(work, f"s{i:03d}_content.png")
    stages: list[str] = []
    if fmt == "long" and v.get("type") == "checklist" and v.get("reveal", True) and "checked" not in v and len(v.get("items", [])) >= 2:
        for k in range(len(v["items"]) + 1):  # v1.13.0 체크리스트: 말하는 동안 한 칸씩 켜진다 (아직 안 켜진 칸은 회색)
            sp = os.path.join(work, f"s{i:03d}_content{k}.png")
            render_visual(dict(v, checked=k), cw, chh, scene.get("bg"), i).save(sp)
            stages.append(sp)
    else:
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
        subtitle_png(fmt, c, p, 1460 if project.get("corner_mascot") else 1600)
        sub_inputs.append(p)
        timings.append((a, b, c))

    zmax = 0.06
    z = f"1+{zmax}*on/{N}" if i % 2 == 0 else f"1+{zmax}-{zmax}*on/{N}"
    srcs = stages or [content]
    nc = len(srcs)
    fc = [f"[{k}:v]scale={cw * 2}:-1,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={N}:s={cw}x{chh}:fps={FPS},setsar=1[z{k}]" for k in range(nc)]
    if stages:
        n_it = nc - 1
        t0 = min(0.5, T * 0.1)
        gap = max(0.35, min(0.9, (T * 0.75 - t0) / n_it))
        ats = [float(x) for x in v.get("at", [])] or [t0 + k * gap for k in range(n_it)]
        prev = "z0"
        for k in range(1, nc):
            fc.append(f"[{prev}][z{k}]overlay=0:0:enable='gte(t,{ats[k - 1]:.3f})'[y{k}]")
            prev = f"y{k}"
        fc.append(f"[{prev}]null[c]")
    else:
        fc.append("[z0]null[c]")
    fc.append(f"[{nc}:v][c]overlay={cx0}:{cy0}:shortest=1[b0]")
    inputs = [x for sp in srcs for x in ("-i", sp)] + ["-loop", "1", "-t", f"{T:.3f}", "-i", chrome[0]]
    last = "b0"
    for k, p in enumerate(sub_inputs):
        inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", p]
        a, b, _ = timings[k]
        fc.append(f"[{last}][{k + nc + 1}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[b{k + 1}]")
        last = f"b{k + 1}"
    if hl:
        hp = os.path.join(work, f"s{i:03d}_headline.png")
        headline_png(hl, hp, project)
        inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", hp]
        fc.append(f"[{last}][{len(sub_inputs) + nc + 1}:v]overlay=0:0[bh]")
        last = "bh"
    inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", chrome[1]]
    top_idx = len(sub_inputs) + nc + 1 + (1 if hl else 0)
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
