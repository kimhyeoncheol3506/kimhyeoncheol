"""편집 규칙집(v1.15.0) 적용기 — 완성 영상에 규칙집의 '구독 범퍼·아웃트로 CTA·클릭 효과음'을 입힌다 (파이썬 + ffmpeg).

규칙 문서: video-studio/편집규칙집.md  (레퍼런스: '바로쓰는 심리학' 혼잣말의 뇌과학 편 분해)
엔진(make_video)이 project.json "rulebook": true 일 때 자동 호출한다. 단독 실행:
  python tools/rulebook_edit.py finish <video.mp4> [--bumper 초] [--out 결과.mp4]
  python tools/rulebook_edit.py build <이미지·클립 폴더> <내레이션.wav> <자막.srt> <out.mp4> [--title 제목]
     ↳ 그림/클립 + 내레이션 + 자막만 있는 소재를 규칙집대로 한 편으로 조립 (그림 5~6초 유지·느린 확대·하단 자막 박스·상단 제목/배지·범퍼·아웃트로)
"""
from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
FPS = 30
RED, WHITE, INK, GOLD = (226, 39, 39), (255, 255, 255), (30, 30, 36), (226, 176, 70)


def _font(size, w="black"):
    from studio.draw import font
    return font(w, size)


def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return r


def duration(path):
    return float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


# ───────────── 애니메이션 PNG 시퀀스 ─────────────
def _button(d, x, y, w, h, label, pressed, f):
    if pressed:
        d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=(110, 110, 118))
        d.text((x + w / 2, y + h / 2), "✓ " + label.replace("구독", "구독중"), font=f, fill=WHITE, anchor="mm")
    else:
        d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=RED)
        d.text((x + w / 2, y + h / 2), label, font=f, fill=WHITE, anchor="mm")


def _cursor(d, x, y, s=1.0, click=False):
    pts = [(0, 0), (0, 46), (12, 35), (21, 56), (30, 52), (21, 32), (37, 32)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    d.polygon(pts, fill=WHITE, outline=INK)
    d.line(pts + [pts[0]], fill=INK, width=4)
    if click:
        d.ellipse([x - 26, y - 26, x + 26, y + 26], outline=(255, 255, 255, 220), width=5)


def bumper_frames(tmp, secs=5.0):
    """오른쪽 아래(자막 위) 구독 팝업: 배지+문구 카드가 미끄러져 들어오고 → 커서가 '구독'을 누르고 → 회색 '구독중'으로 바뀐 뒤 사라짐."""
    from studio.render import channel_badge
    W, H = 640, 220
    badge = channel_badge(150)
    n = int(secs * FPS)
    fdir = os.path.join(tmp, "bumper")
    os.makedirs(fdir, exist_ok=True)
    f1, f2 = _font(40), _font(30, "bold")
    clicks = []
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        a_in = min(1, t / 0.35)
        a_out = min(1, max(0, (secs - t) / 0.35))
        off = int((1 - a_in) ** 2 * W)
        card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, W - 1, H - 1], 28, fill=(255, 255, 255, 240), outline=GOLD, width=4)
        card.alpha_composite(badge, (24, 35))
        cd.text((200, 50), "월급쟁이 재테크 스킬", font=f2, fill=INK)
        pressed = t > 2.2
        _button(cd, 200, 110, 260, 76, "구독", pressed, f1)
        cd.rounded_rectangle([480, 110, 616, 186], 38, fill=(240, 240, 240))
        cd.text((548, 148), "알림 ✓" if t > 3.0 else "알림", font=_font(34, "bold"), fill=INK, anchor="mm")
        if 1.2 < t < 3.6:
            cx = 330 + (1 - min(1, (t - 1.2) / 0.9)) * 220
            cy = 150 + (1 - min(1, (t - 1.2) / 0.9)) * 70
            _cursor(cd, cx, cy, 1.0, 2.15 < t < 2.4)
        img.alpha_composite(card, (off, 0))
        if a_out < 1:
            img.putalpha(img.getchannel("A").point(lambda v: int(v * a_out)))
        img.save(os.path.join(fdir, f"{i:04d}.png"))
    clicks.append(2.2)
    return fdir, (W, H), clicks


def outro_frames(tmp, secs=6.0):
    """마지막 화면 가운데 아래: 구독·좋아요·알림 버튼 3개가 차례로 눌림 (레퍼런스 아웃트로: 노트북 앞 캐릭터 + 구독 버튼)."""
    W, H = 1100, 170
    n = int(secs * FPS)
    fdir = os.path.join(tmp, "outro")
    os.makedirs(fdir, exist_ok=True)
    f = _font(46)
    labels = [("구독", 0), ("좋아요", 1), ("알림 설정", 2)]
    press_t = [1.4, 2.4, 3.4]
    for i in range(n):
        t = i / FPS
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        a_in = min(1, t / 0.4)
        y = 40 + int((1 - a_in) * 60)
        xs = [20, 400, 760]
        ws = [340, 320, 320]
        for (lab, k), x, w in zip(labels, xs, ws):
            pressed = t > press_t[k]
            if pressed:
                d.rounded_rectangle([x, y, x + w, y + 96], 48, fill=(110, 110, 118, int(240 * a_in)))
                d.text((x + w / 2, y + 48), "✓ " + lab.split()[0], font=f, fill=WHITE, anchor="mm")
            else:
                d.rounded_rectangle([x, y, x + w, y + 96], 48, fill=RED + (int(245 * a_in),))
                d.text((x + w / 2, y + 48), lab, font=f, fill=WHITE, anchor="mm")
        for k, pt in enumerate(press_t):
            if pt - 0.7 < t < pt + 0.3:
                fx = xs[k] + ws[k] / 2 + 30
                _cursor(d, fx + (pt - t) * 120 if t < pt else fx, y + 60 + (max(0, pt - t)) * 60, 1.0, pt - 0.05 < t < pt + 0.2)
        img.save(os.path.join(fdir, f"{i:04d}.png"))
    return fdir, (W, H), press_t


def click_wav(path, sr=48000):
    """짧은 '딸깍' (두 번의 감쇠 노이즈 버스트)."""
    n = int(0.12 * sr)
    t = np.arange(n) / sr
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n) * np.exp(-t / 0.006) * 0.6
    x[int(0.035 * sr):] += rng.standard_normal(n - int(0.035 * sr)) * np.exp(-t[: n - int(0.035 * sr)] / 0.004) * 0.35
    x += np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.01) * 0.25
    pcm = (np.clip(x, -1, 1) * 32767 * 0.7).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def finish(video, chapters=None, total=None, bumper_at=None, out=None):
    """완성 영상에 구독 범퍼(첫 장이 끝나기 직전)와 아웃트로 CTA(마지막 6초)를 덧입힌다. out 없으면 제자리 교체."""
    total = total or duration(video)
    if bumper_at is None:
        starts = [c[0] for c in (chapters or [])]
        first = min(starts) if starts else 0.0  # 오프닝 뒤에 첫 장이 시작하면(31편) 그 장이 끝나기 직전에 띄운다
        nxt = [s for s in starts if s > max(25.0, first + 1.0)]
        bumper_at = (nxt[0] - 5.5) if nxt else min(90.0, total * 0.25)
    bumper_at = max(8.0, min(bumper_at, total - 20))
    out_at = max(bumper_at + 10, total - 6.2)
    tmp = tempfile.mkdtemp(prefix="rulebook_")
    try:
        bdir, (bw, bh), bclicks = bumper_frames(tmp)
        odir, (ow, oh), oclicks = outro_frames(tmp)
        cw = os.path.join(tmp, "click.wav")
        click_wav(cw)
        clicks = [bumper_at + c for c in bclicks] + [out_at + c for c in oclicks]
        res = out or video + ".rb.mp4"
        fc = [f"[1:v]setpts=PTS-STARTPTS+{bumper_at:.3f}/TB[b]", f"[2:v]setpts=PTS-STARTPTS+{out_at:.3f}/TB[o]",
              f"[0:v][b]overlay=x=W-{bw}-40:y=H-{bh}-190:eof_action=pass[v1]",
              f"[v1][o]overlay=x=(W-{ow})/2:y=H-{oh}-200:eof_action=pass,format=yuv420p[v]"]
        mix = []
        for k, c in enumerate(clicks):
            fc.append(f"[3:a]adelay={int(c * 1000)}|{int(c * 1000)},volume=0.55[c{k}]")
            mix.append(f"[c{k}]")
        fc.append(f"[0:a]{''.join(mix)}amix=inputs={len(mix) + 1}:duration=first:dropout_transition=0:normalize=0[a]")
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", video,
              "-framerate", str(FPS), "-i", os.path.join(bdir, "%04d.png"),
              "-framerate", str(FPS), "-i", os.path.join(odir, "%04d.png"),
              "-i", cw, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
              "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", res])
        if not out:
            shutil.move(res, video)
        print(f"규칙집 적용: 구독 범퍼 {bumper_at:.1f}s · 아웃트로 CTA {out_at:.1f}s · 클릭음 {len(clicks)}개")
        return out or video
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ───────────── 소재만으로 한 편 조립 (규칙집 그대로) ─────────────
def _srt(path):
    txt = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"(\d\d):(\d\d):(\d\d)[,.](\d+)\s*-->\s*(\d\d):(\d\d):(\d\d)[,.](\d+)\s*\n(.+?)(?:\n\n|\Z)", txt, re.S):
        g = m.groups()
        a = int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000
        b = int(g[4]) * 3600 + int(g[5]) * 60 + int(g[6]) + int(g[7]) / 1000
        out.append((a, b, g[8].strip().replace("\n", " ")))
    return out


def build(media_dir, narration, srt, out, title=""):
    """그림/클립을 자막 문장 경계에 맞춰 5~6초씩 배치(느린 확대, 방향 번갈아), 하단 자막 박스, 상단 제목·배지, BGM 없이 내레이션 -14 LUFS, 마지막에 finish()."""
    from studio.render import channel_badge, subtitle_png
    files = sorted(f for f in os.listdir(media_dir) if f.lower().endswith((".png", ".jpg", ".jpeg", ".mp4", ".mov")))
    if not files:
        raise SystemExit("그림/클립이 없습니다")
    T = duration(narration)
    subs = _srt(srt)
    # 컷 지점: 5~6초 목표, 자막 경계에 스냅
    bounds = [0.0]
    edges = sorted({round(b, 3) for _, b, _ in subs})
    while bounds[-1] < T - 3:
        target = bounds[-1] + 5.5
        cand = [e for e in edges if bounds[-1] + 3.5 <= e <= bounds[-1] + 8]
        bounds.append(min(cand, key=lambda e: abs(e - target)) if cand else min(T, target))
    bounds[-1] = T
    tmp = tempfile.mkdtemp(prefix="rbbuild_")
    try:
        parts = []
        for i in range(len(bounds) - 1):
            a, b = bounds[i], bounds[i + 1]
            dur = b - a
            src = os.path.join(media_dir, files[i % len(files)])
            N = max(1, round(dur * FPS))
            o = os.path.join(tmp, f"p{i:04d}.mp4")
            if src.lower().endswith((".mp4", ".mov")):
                vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps={FPS},tpad=stop_mode=clone:stop_duration=30"
                _run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-an", "-vf", vf, "-frames:v", str(N), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", o])
            else:
                z = f"1+0.06*on/{N}" if i % 2 == 0 else f"1.06-0.06*on/{N}"
                vf = f"scale=3840:-1,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={N}:s=1920x1080:fps={FPS}"
                _run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", src, "-vf", vf, "-frames:v", str(N), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", o])
            parts.append(o)
        lst = os.path.join(tmp, "l.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
        base = os.path.join(tmp, "base.mp4")
        _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])
        # 상단 크롬 + 자막 PNG
        top = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        dt = ImageDraw.Draw(top)
        dt.text((28, 18), title[:60], font=_font(26, "bold"), fill=(255, 255, 255, 200), stroke_width=3, stroke_fill=(0, 0, 0, 160))
        top.alpha_composite(channel_badge(150), (1920 - 176, 22))
        tp = os.path.join(tmp, "top.png")
        top.save(tp)
        inputs = ["-i", base, "-i", narration, "-loop", "1", "-i", tp]
        fc = ["[0:v][2:v]overlay=0:0:shortest=1[v0]"]
        last = "v0"
        for k, (a, b, text) in enumerate(subs):
            sp = os.path.join(tmp, f"s{k:04d}.png")
            subtitle_png("long", text, sp)
            inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", sp]
            fc.append(f"[{last}][{k + 3}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[v{k + 1}]")
            last = f"v{k + 1}"
        fc.append(f"[{last}]format=yuv420p[v];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        mid = os.path.join(tmp, "mid.mp4")
        _run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
              "-t", f"{T:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", mid])
        finish(mid, None, T, out=out)
        print("완성:", out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("finish")
    a1.add_argument("video")
    a1.add_argument("--bumper", type=float)
    a1.add_argument("--out")
    a2 = sub.add_parser("build")
    a2.add_argument("media_dir"); a2.add_argument("narration"); a2.add_argument("srt"); a2.add_argument("out")
    a2.add_argument("--title", default="")
    a = ap.parse_args()
    if a.cmd == "finish":
        finish(a.video, None, None, a.bumper, a.out)
    else:
        build(a.media_dir, a.narration, a.srt, a.out, a.title)
