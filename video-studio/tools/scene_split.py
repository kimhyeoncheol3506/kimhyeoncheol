"""PySceneDetect 장면 나누기 (2026-11-11 도입).

쓰는 곳 두 가지:
1. 현철님이 첨부한 참고 영상 분석 — 컷 위치·평균 컷 길이·컷 리듬을 뽑고 컷마다 대표 프레임 한 장씩 모은 밀착 인화지(contact sheet)를 만든다.
   우리 장면 설계(장면 10초 규칙, 장면 수)를 참고 영상 리듬에 맞출 때 쓴다.
2. 완성본 검수 — 한 화면이 너무 오래 가는 구간(기본 12초 초과)을 찾아 보고한다.

사용:
  python3 tools/scene_split.py <영상.mp4> [--out <폴더>] [--threshold 27] [--max-shot 12] [--sheet]
결과: <폴더>/scenes.json (컷 목록·통계), <폴더>/scenes.csv, --sheet 이면 <폴더>/contact_sheet.jpg
"""
import argparse
import csv
import json
import os
import statistics
import subprocess
import tempfile

from scenedetect import ContentDetector, detect


def analyze(video, threshold=27.0, min_len=0.4):
    scenes = detect(video, ContentDetector(threshold=threshold, min_scene_len=max(1, int(min_len * 30))), show_progress=False)
    rows = [dict(no=i + 1, start=round(a.seconds, 2), end=round(b.seconds, 2), dur=round(b.seconds - a.seconds, 2))
            for i, (a, b) in enumerate(scenes)]
    if not rows:  # 컷이 하나도 없으면 영상 전체를 한 장면으로
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                                   capture_output=True, text=True).stdout.strip() or 0)
        rows = [dict(no=1, start=0.0, end=round(dur, 2), dur=round(dur, 2))]
    durs = [r["dur"] for r in rows]
    stats = dict(cuts=len(rows), total=round(sum(durs), 1), mean=round(statistics.mean(durs), 2),
                 median=round(statistics.median(durs), 2), longest=max(durs), shortest=min(durs),
                 cuts_per_min=round(len(rows) / max(sum(durs) / 60, 1e-6), 1))
    return rows, stats


def contact_sheet(video, rows, dst, cols=6, width=320):
    """컷마다 가운데 프레임 한 장 → 격자 한 장 (컷 번호·시각 표시)"""
    with tempfile.TemporaryDirectory() as td:
        frames = []
        for r in rows[:120]:
            t = (r["start"] + r["end"]) / 2
            f = os.path.join(td, f"{r['no']:04d}.jpg")
            label = f"{r['no']}  {int(r['start'] // 60)}:{r['start'] % 60:04.1f}  ({r['dur']}s)"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                            "-vf", f"scale={width}:-2,drawbox=y=ih-26:w=iw:h=26:color=black@0.7:t=fill,"
                                   f"drawtext=text='{label}':x=6:y=h-21:fontsize=16:fontcolor=white", f], check=False)
            if os.path.exists(f):
                frames.append(f)
        if not frames:
            return None
        n = len(frames)
        inputs = []
        for f in frames:
            inputs += ["-i", f]
        # xstack 은 좌표에 크기 표현식이 필요 → 모든 칸이 같은 크기라 w0/h0 배수로 계산
        layout = "|".join(f"{'+'.join(['w0'] * (i % cols)) or '0'}_{'+'.join(['h0'] * (i // cols)) or '0'}" for i in range(n))
        fc = f"xstack=inputs={n}:layout={layout}:fill=black" if n > 1 else "null"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-frames:v", "1", "-q:v", "3", dst], check=True)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out")
    ap.add_argument("--threshold", type=float, default=27.0, help="낮을수록 컷을 더 잘게 찾음 (모션그래픽은 20~27, 실사는 27~35)")
    ap.add_argument("--max-shot", type=float, default=12.0, help="이보다 긴 화면을 경고")
    ap.add_argument("--sheet", action="store_true", help="컷별 대표 프레임 밀착 인화지 만들기")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.video)[0] + "_scenes"
    os.makedirs(out, exist_ok=True)
    rows, stats = analyze(a.video, a.threshold)
    long = [r for r in rows if r["dur"] > a.max_shot]
    stats["long_shots"] = [dict(no=r["no"], start=r["start"], dur=r["dur"]) for r in long]
    json.dump(dict(video=os.path.abspath(a.video), stats=stats, scenes=rows), open(os.path.join(out, "scenes.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(out, "scenes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["no", "start", "end", "dur"])
        w.writeheader()
        w.writerows(rows)
    if a.sheet:
        contact_sheet(a.video, rows, os.path.join(out, "contact_sheet.jpg"))
    print(f"컷 {stats['cuts']}개 · 평균 {stats['mean']}초 · 중간값 {stats['median']}초 · 분당 {stats['cuts_per_min']}컷 · 최장 {stats['longest']}초")
    if long:
        print(f"{a.max_shot}초 넘는 화면 {len(long)}개: " + ", ".join(f"#{r['no']}({r['start']}s, {r['dur']}s)" for r in long[:15]))
    print("결과:", out)


if __name__ == "__main__":
    main()
