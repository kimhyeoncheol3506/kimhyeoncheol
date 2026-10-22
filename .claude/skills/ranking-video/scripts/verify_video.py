# -*- coding: utf-8 -*-
"""완성 영상 점검 (ranking-video v2.7.0) — 파일은 읽기만 한다.

사용법: python3 -I verify_video.py <영상.mp4> [--target-lufs -14] [--json 결과.json]
보는 것: 해상도·fps·길이·소리 트랙 / 검은 화면 / 영상 안 긴 무음 / 통합 음량(LUFS)·트루 피크
결과는 PASS/WARN/FAIL 표. FAIL(소리 없음 등)이면 종료 코드 1. WARN은 '확인해 보라'는 뜻.
(스마트대디 영상 편집 스킬의 verify_render 점검 항목을 이 키트에 맞게 옮김)
"""
import argparse, json, re, subprocess, sys

def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + [str(a) for a in args], capture_output=True).stderr.decode("utf-8", "replace")

def mmss(t): return f"{int(t // 60)}:{int(t % 60):02d}"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video")
    ap.add_argument("--target-lufs", type=float, default=-16.0); ap.add_argument("--lufs-tol", type=float, default=2.0)
    ap.add_argument("--max-tp", type=float, default=-1.0); ap.add_argument("--silence-db", type=float, default=-50.0)
    ap.add_argument("--max-silence", type=float, default=2.0); ap.add_argument("--black-min", type=float, default=0.5)
    ap.add_argument("--json"); a = ap.parse_args()
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", a.video], capture_output=True).stdout or "{}")
    vs = next((s for s in pr.get("streams", []) if s.get("codec_type") == "video"), None)
    au = [s for s in pr.get("streams", []) if s.get("codec_type") == "audio"]
    dur = float(pr.get("format", {}).get("duration") or 0); rows = []
    row = lambda item, st, val, note="": rows.append(dict(item=item, status=st, value=val, note=note))
    if vs:
        w, h = vs["width"], vs["height"]; n, d = vs["avg_frame_rate"].split("/"); fps = float(n) / float(d or 1)
        row("해상도", "PASS" if min(w, h) >= 720 else "WARN", f"{w}x{h}"); row("프레임", "PASS" if abs(fps - 30) < .1 or abs(fps - 25) < .1 or abs(fps - 24) < .1 else "WARN", f"{fps:.2f} fps")
        vd = float(vs.get("duration") or dur)
    else: row("영상 트랙", "FAIL", "없음"); vd = 0
    row("길이", "PASS" if dur > 0 else "FAIL", mmss(dur))
    if au:
        ad = float(au[0].get("duration") or dur); row("소리 트랙", "PASS", f"{au[0].get('codec_name')} {au[0].get('sample_rate')}Hz")
        row("영상·소리 길이", "PASS" if abs(vd - ad) < 0.3 else "WARN", f"{vd:.2f}s / {ad:.2f}s")
    else: row("소리 트랙", "FAIL", "없음")
    if vs:
        log = ff(["-i", a.video, "-map", "0:v:0", "-vf", f"scale=320:-2,blackdetect=d={a.black_min}:pix_th=0.10", "-an", "-f", "null", "-"])
        bl = [(float(x), float(y)) for x, y in re.findall(r"black_start:([\d.]+)\s+black_end:([\d.]+)", log)]
        row("검은 화면", "PASS" if not bl else "WARN", f"{len(bl)}곳", ", ".join(f"{mmss(x)}~{mmss(y)}" for x, y in bl[:6]))
    if au:
        log = ff(["-i", a.video, "-map", "0:a:0", "-af", f"silencedetect=n={a.silence_db}dB:d={a.max_silence},ebur128=peak=true", "-vn", "-f", "null", "-"])
        st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", log)]
        sil = [(max(0, s), en[i] if i < len(en) else dur) for i, s in enumerate(st)]; ins = [(s, e) for s, e in sil if s > .5 and e < dur - .5]
        row(f"긴 무음(>{a.max_silence:g}초)", "PASS" if not ins else "WARN", f"{len(ins)}곳", ", ".join(f"{mmss(x)}~{mmss(y)}" for x, y in ins[:6]))
        sm = log[log.rfind("Summary:"):]; mi = re.search(r"I:\s+(-?[\d.]+) LUFS", sm); mp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", sm)
        if mi:
            L = float(mi.group(1)); ok = abs(L - a.target_lufs) <= a.lufs_tol
            row("통합 음량", "PASS" if ok else "WARN", f"{L:.1f} LUFS", f"목표 {a.target_lufs:g}±{a.lufs_tol:g}" + ("" if ok else (" · 작음" if L < a.target_lufs else " · 큼")))
        else: row("통합 음량", "FAIL", "측정 불가")
        if mp: T = float(mp.group(1)); row("피크", "PASS" if T <= a.max_tp else "WARN", f"{T:.1f} dBFS", f"{a.max_tp:g} 이하 권장")
    print("점검:", a.video); print("-" * 70)
    for r in rows: print(f"{r['status']:<5} {r['item']:<18} {r['value']:<18} {r['note']}")
    nf = sum(r["status"] == "FAIL" for r in rows); nw = sum(r["status"] == "WARN" for r in rows)
    print("-" * 70); print(f"결과: FAIL {nf} · WARN {nw} · PASS {len(rows) - nf - nw}")
    if a.json: json.dump(rows, open(a.json, "w"), ensure_ascii=False, indent=1)
    sys.exit(1 if nf else 0)

if __name__ == "__main__": main()
