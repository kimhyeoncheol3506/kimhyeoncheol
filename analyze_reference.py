#!/usr/bin/env python3
"""참고 영상 편집스타일 실측 분석기.

사용:
  python analyze_reference.py ref1.mp4 ref2.mp4 ...           # 로컬 파일
  python analyze_reference.py https://youtu.be/XXXX ...        # 네트워크가 허용되면 yt-dlp 로 내려받음
  python analyze_reference.py ... --apply                       # 실측값을 style.yaml 의 measured: 에 기록

측정 항목
  - 컷 간격(장면 전환 감지): 평균/중앙값/10·90 백분위, 분당 컷 수, 인트로 30초 컷 밀도
  - 자막: OCR 로 글자 박스 위치(세로 위치), 글자 높이(→ 폰트 크기 px), 글자색/강조색, 한 줄 글자 수
  - 오디오: 통합 음량(LUFS), 말 사이 무음 길이 분포, 배경음 레벨(말 없는 구간 음량), 말 빠르기(음절/초)
  - 색상 팔레트(배경 대표색)
  - 장면 목록(컷마다 썸네일 contact sheet) → 인트로/아웃트로 구성 수동 확인용
결과: analysis/<영상>/report.md, cuts.png, analysis/summary.json
"""
import argparse
import json
import os
import re
import statistics as stt
import subprocess
import sys

import numpy as np
import yaml
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))


def sh(args):
    return subprocess.run(args, capture_output=True, text=True)


def fetch(src, outdir):
    if os.path.exists(src):
        return src
    os.makedirs(outdir, exist_ok=True)
    r = sh([sys.executable, "-m", "yt_dlp", "-f", "bv*[height<=1080]+ba/b", "--merge-output-format", "mp4",
            "--write-auto-subs", "--sub-langs", "ko", "-o", os.path.join(outdir, "%(id)s.%(ext)s"), src])
    if r.returncode != 0:
        raise SystemExit(f"다운로드 실패({src}). 네트워크 정책에서 youtube.com/googlevideo.com 허용이 필요하거나, "
                         f"영상 파일을 직접 넣어주세요.\n{r.stderr[-400:]}")
    vid = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", src).group(1)
    return os.path.join(outdir, vid + ".mp4")


def duration(mp4):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4]).stdout)


def cuts(mp4, thr=0.08, merge=0.25):
    """장면 전환 + 펀치인(확대 컷)까지 잡도록 민감하게 감지 후, 0.25초 안 중복은 합친다."""
    err = sh(["ffmpeg", "-hide_banner", "-i", mp4, "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"]).stderr
    out = []
    for t in (float(x) for x in re.findall(r"pts_time:([\d.]+)", err)):
        if not out or t - out[-1] > merge:
            out.append(t)
    return out


def cut_stats(ts, dur):
    pts = [0.0] + ts + [dur]
    iv = [b - a for a, b in zip(pts, pts[1:]) if b - a > 0.15]
    q = np.percentile(iv, [10, 50, 90]) if iv else [0, 0, 0]
    intro = [t for t in ts if t < 30]
    return {"cuts": len(ts), "per_min": round(len(ts) / dur * 60, 1), "mean": round(stt.mean(iv), 2),
            "p10": round(q[0], 2), "median": round(q[1], 2), "p90": round(q[2], 2), "intro30_cuts": len(intro)}


def audio(mp4):
    err = sh(["ffmpeg", "-hide_banner", "-i", mp4, "-af", "ebur128", "-vn", "-f", "null", "-"]).stderr
    lufs = re.findall(r"I:\s+([-\d.]+) LUFS", err)
    err2 = sh(["ffmpeg", "-hide_banner", "-i", mp4, "-af", "silencedetect=n=-35dB:d=0.12", "-vn", "-f", "null", "-"]).stderr
    sil = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", err2)]
    # 말 없는 구간 바닥 음량 ≈ 배경음 레벨
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-ac", "1", "-ar", "8000", "-f", "f32le", "-"],
                                     capture_output=True).stdout, dtype=np.float32)
    hop = 800
    rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9 for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(rms)
    return {"lufs": float(lufs[-1]) if lufs else None,
            "pause_median": round(stt.median(sil), 2) if sil else None,
            "pauses_per_min": round(len(sil) / (len(x) / 8000) * 60, 1),
            "speech_db_p90": round(float(np.percentile(db, 90)), 1),
            "floor_db_p10": round(float(np.percentile(db, 10)), 1),
            "bgm_vs_voice_db": round(float(np.percentile(db, 10) - np.percentile(db, 90)), 1)}


def subtitles(mp4, workdir, every=1.0, limit=240):
    os.makedirs(workdir, exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-t", str(limit), "-vf", f"fps=1/{every},scale=1920:1080",
        os.path.join(workdir, "s_%04d.png")])
    ys, hs, cols, chars = [], [], [], []
    for fn in sorted(f for f in os.listdir(workdir) if f.startswith("s_")):
        p = os.path.join(workdir, fn)
        tsv = sh(["tesseract", p, "-", "-l", "kor", "--psm", "11", "tsv"]).stdout
        im = np.asarray(Image.open(p).convert("RGB"))
        lines = {}
        for r in tsv.splitlines()[1:]:
            c = r.split("\t")
            if len(c) < 12 or not c[11].strip() or float(c[10]) < 60 or not re.search(r"[가-힣]", c[11]):
                continue
            l, t, w, h = map(int, c[6:10])
            key = (c[2], c[3], c[4])
            lines.setdefault(key, []).append((l, t, w, h, c[11]))
            box = im[t:t + h, l:l + w].reshape(-1, 3)
            if len(box):
                bright = box[box.sum(1) > 600]
                if len(bright) > 20:
                    cols.append(tuple(int(v) for v in np.median(bright, 0)))
                sat = box[(box.max(1).astype(int) - box.min(1)) > 90]
                if len(sat) > 30:
                    cols.append(("강조후보",) + tuple(int(v) for v in np.median(sat, 0)))
        for words in lines.values():
            t = min(w[1] for w in words)
            h = max(w[3] for w in words)
            ys.append((t + h / 2) / 1080)
            hs.append(h)
            chars.append(len("".join(w[4] for w in words)))
    bottom = [(y, h) for y, h in zip(ys, hs) if y > 0.7]
    emph = [c[1:] for c in cols if c and c[0] == "강조후보"]
    return {"text_lines": len(ys),
            "bottom_sub_y": round(stt.median([y for y, _ in bottom]), 3) if bottom else None,
            "bottom_sub_px_height": int(stt.median([h for _, h in bottom])) if bottom else None,
            "est_font_size": int(stt.median([h for _, h in bottom]) * 1.25) if bottom else None,
            "chars_per_line_median": int(stt.median(chars)) if chars else None,
            "top_text_ratio": round(sum(1 for y in ys if y < 0.35) / max(1, len(ys)), 2),
            "emphasis_colors": [("#%02X%02X%02X" % c) for c in _top_colors(emph)]}


def _top_colors(cs, k=3):
    if not cs:
        return []
    q = [tuple(int(v) // 32 * 32 + 16 for v in c) for c in cs]
    from collections import Counter
    return [c for c, _ in Counter(q).most_common(k)]


def palette(mp4, k=6):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", "fps=1/5,scale=64:36", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
    return ["#%02X%02X%02X" % c for c in _top_colors([tuple(p) for p in x[::7]], k)]


def cut_sheet(mp4, ts, out, maxn=48):
    ts = [0.0] + ts
    ts = ts[:maxn]
    cols = 6
    rows = (len(ts) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 320, rows * 200), "white")
    d = ImageDraw.Draw(sheet)
    for i, t in enumerate(ts):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t + 0.1:.2f}", "-i", mp4, "-frames:v", "1", "-vf",
                            "scale=320:180", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if r.stdout:
            import io
            sheet.paste(Image.open(io.BytesIO(r.stdout)), ((i % cols) * 320, (i // cols) * 200))
        d.text(((i % cols) * 320 + 4, (i // cols) * 200 + 182), f"#{i} {t:.1f}s", fill="black")
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    base = os.path.join(ROOT, "analysis")
    os.makedirs(base, exist_ok=True)
    allres = {}
    for src in a.inputs:
        mp4 = fetch(src, os.path.join(base, "_downloads"))
        name = os.path.splitext(os.path.basename(mp4))[0]
        wd = os.path.join(base, name)
        os.makedirs(wd, exist_ok=True)
        print(f"[{name}] 분석 중…", flush=True)
        dur = duration(mp4)
        ts = cuts(mp4)
        res = {"duration": round(dur, 1), "cuts": cut_stats(ts, dur), "audio": audio(mp4),
               "subtitle": subtitles(mp4, os.path.join(wd, "frames")), "palette": palette(mp4)}
        cut_sheet(mp4, ts, os.path.join(wd, "cuts.png"))
        res["cut_times"] = [round(t, 2) for t in ts]
        allres[name] = res
        with open(os.path.join(wd, "report.md"), "w", encoding="utf-8") as f:
            f.write(f"# {name} 실측 리포트\n\n```json\n{json.dumps(res, ensure_ascii=False, indent=1)}\n```\n\n![cuts](cuts.png)\n")
        print(json.dumps({k: v for k, v in res.items() if k != "cut_times"}, ensure_ascii=False, indent=1))
    json.dump(allres, open(os.path.join(base, "summary.json"), "w"), ensure_ascii=False, indent=1)
    if a.apply and allres:
        med = lambda path: stt.median([_dig(r, path) for r in allres.values() if _dig(r, path) is not None])
        measured = {"pacing": {"cut_target_sec": round(med(("cuts", "median")), 2),
                               "cut_min_sec": round(max(0.6, med(("cuts", "p10"))), 2),
                               "cut_max_sec": round(med(("cuts", "p90")), 2)}}
        try:
            measured["subtitle"] = {"y": round(med(("subtitle", "bottom_sub_y")), 3),
                                    "size": int(med(("subtitle", "est_font_size")))}
        except stt.StatisticsError:
            pass
        try:
            measured["audio"] = {"bgm_db": round(max(-32, min(-12, med(("audio", "bgm_vs_voice_db")))), 1),
                                 "loudness_lufs": round(med(("audio", "lufs")), 1)}
        except stt.StatisticsError:
            pass
        sp = os.path.join(ROOT, "style.yaml")
        txt = open(sp, encoding="utf-8").read()
        txt = re.sub(r"measured:.*", "measured: " + json.dumps(measured, ensure_ascii=False), txt, flags=re.S)
        open(sp, "w", encoding="utf-8").write(txt)
        print("style.yaml measured: 갱신 →", measured)


def _dig(d, path):
    for p in path:
        d = d.get(p) if isinstance(d, dict) else None
    return d


if __name__ == "__main__":
    main()
