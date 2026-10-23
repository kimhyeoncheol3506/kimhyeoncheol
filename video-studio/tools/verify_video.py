"""완성 영상 점검 (v1.13.0) — 보내기 전에 매번 실행. 파일은 읽기만 한다.

보는 것: 해상도·fps·길이 / 검은 화면 / 영상 안 긴 무음 / 통합 음량(-14 LUFS ±2) / 트루 피크(-1 dBTP 이하) /
        한 화면이 같은 모습으로 오래 멈춘 곳(freezedetect, 12초 넘게)

사용: python tools/verify_video.py projects/<...>/output/video.mp4
결과는 PASS / WARN / FAIL. FAIL이 있으면 종료 코드 1. (스마트대디 편집 스킬의 verify_render 아이디어를 우리 형식에 맞춰 새로 작성)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def ff(args):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *map(str, args)], capture_output=True)
    return p.stderr.decode("utf-8", "replace")


def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--max-silence", type=float, default=1.6, help="이보다 긴 무음이면 WARN(초). 우리 영상은 장면 사이 쉼이 0.5초 이하")
    ap.add_argument("--freeze", type=float, default=12.0, help="이보다 오래 화면이 멈추면 WARN(초)")
    a = ap.parse_args()
    v = Path(a.video).resolve()
    if not v.exists():
        sys.exit(f"파일이 없습니다: {v}")
    rows = []

    def row(item, status, value, note=""):
        rows.append((item, status, value, note))

    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(v)],
                                   capture_output=True).stdout)
    vs = next((s for s in pr["streams"] if s["codec_type"] == "video"), None)
    au = [s for s in pr["streams"] if s["codec_type"] == "audio"]
    dur = float(pr["format"].get("duration") or 0)
    if vs:
        w, h = vs["width"], vs["height"]
        n, d = vs["avg_frame_rate"].split("/")
        fps = float(n) / float(d)
        row("해상도", "PASS" if min(w, h) >= 1080 else "WARN", f"{w}x{h}")
        row("프레임 수", "PASS" if abs(fps - 30) < 0.1 else "WARN", f"{fps:.2f} fps")
    else:
        row("영상 트랙", "FAIL", "없음")
    row("길이", "PASS" if dur > 0 else "FAIL", mmss(dur))
    row("소리 트랙", "PASS" if au else "FAIL", f"{len(au)}개")

    if vs and vs["height"] > vs["width"]:  # 쇼츠: 유튜브 버튼·제목이 덮는 아래 18%는 비워야 한다 (v1.13.1)
        zl = ff(["-i", v, "-map", "0:v:0", "-vf", "crop=iw:ih*0.18:0:ih*0.82,fps=1,signalstats,metadata=print:key=lavfi.signalstats.YMAX", "-an", "-f", "null", "-"])
        ym = [float(x) for x in re.findall(r"YMAX=([\d.]+)", zl)]
        bad = [i for i, y in enumerate(ym) if y > 60]
        row("아래 18% 비움(쇼츠)", "PASS" if not bad else "WARN", f"{len(bad)}/{len(ym)}초 사용", "유튜브 버튼이 가리는 자리에 글자·그림이 있음" if bad else "")
    log = ff(["-i", v, "-map", "0:v:0", "-vf", "scale=320:-2,blackdetect=d=0.4:pix_th=0.10,freezedetect=n=-60dB:d=%g" % a.freeze, "-an", "-f", "null", "-"])
    blacks = [(float(x), float(y)) for x, y in re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)", log)]
    row("검은 화면", "PASS" if not blacks else "WARN", f"{len(blacks)}곳", ", ".join(f"{mmss(x)}~{mmss(y)}" for x, y in blacks[:5]))
    fs = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
    fe = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)]
    fz = [(s, fe[i] if i < len(fe) else dur) for i, s in enumerate(fs)]
    row(f"멈춘 화면(>{a.freeze:g}초)", "PASS" if not fz else "WARN", f"{len(fz)}곳", ", ".join(f"{mmss(x)}~{mmss(y)}" for x, y in fz[:5]))

    if au:
        log = ff(["-i", v, "-map", "0:a:0", "-af", f"silencedetect=n=-50dB:d={a.max_silence},ebur128=peak=true", "-vn", "-f", "null", "-"])
        st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
        en = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", log)]
        sil = [(max(0, s), en[i] if i < len(en) else dur) for i, s in enumerate(st)]
        inside = [(s, e) for s, e in sil if s > 0.5 and e < dur - 0.5]
        row(f"긴 무음(>{a.max_silence:g}초)", "PASS" if not inside else "WARN", f"{len(inside)}곳", ", ".join(f"{mmss(x)}~{mmss(y)}" for x, y in inside[:5]))
        summ = log[log.rfind("Summary:"):]
        mi = re.search(r"I:\s+(-?[\d.]+) LUFS", summ)
        mp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
        if mi:
            l = float(mi.group(1))
            row("통합 음량", "PASS" if abs(l + 14) <= 2 else "WARN", f"{l:.1f} LUFS", "목표 -14±2")
        if mp:
            p = float(mp.group(1))
            row("피크", "PASS" if p <= -1.0 else "WARN", f"{p:.1f} dBFS", "-1 이하 권장")

    print(f"점검: {v.name}")
    for item, status, value, note in rows:
        print(f"{status:<5} {item:<16} {value:<14} {note}")
    nf = sum(r[1] == "FAIL" for r in rows)
    nw = sum(r[1] == "WARN" for r in rows)
    print(f"결과: FAIL {nf} · WARN {nw} · PASS {len(rows) - nf - nw}")
    sys.exit(1 if nf else 0)


if __name__ == "__main__":
    main()
