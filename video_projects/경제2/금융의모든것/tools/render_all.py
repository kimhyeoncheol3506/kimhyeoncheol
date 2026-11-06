#!/usr/bin/env python3
"""파트별 렌더 → 이어 붙이기 → 720p 전달본 → 챕터 타임스탬프(설명란).

  python tools/render_all.py <작업폴더> [--preview] [--parts 1,2] [--skip-render]

neogul-edit 스킬(.claude/skills/neogul-edit/scripts/neogul_edit.py)로 파트마다 project.json을 렌더한다.
"""
import json, os, subprocess, sys, glob, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
NEOGUL = os.path.join(REPO, ".claude", "skills", "neogul-edit", "scripts", "neogul_edit.py")
sys.path.insert(0, HERE)
import build  # noqa: E402


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())


def ts(t):
    t = int(t); h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return "%d:%02d:%02d" % (h, m, s) if h else "%d:%02d" % (m, s)


def main():
    work = os.path.abspath(sys.argv[1])
    preview = "--preview" in sys.argv
    parts = sorted(int(d[4:]) for d in os.listdir(work) if d.startswith("part") and os.path.isdir(os.path.join(work, d)))
    if "--parts" in sys.argv:
        parts = [int(x) for x in sys.argv[sys.argv.index("--parts") + 1].split(",")]
    outs = []
    for p in parts:
        pj = os.path.join(work, "part%d" % p, "project.json")
        out = os.path.join(work, "part%d" % p, ("preview.mp4" if preview else "part%d.mp4" % p))
        if "--skip-render" not in sys.argv and not (os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(pj)):
            t0 = time.time()
            cmd = [sys.executable, NEOGUL, "render", pj, "--out", out] + (["--preview"] if preview else [])
            print("[render] part%d ..." % p, flush=True)
            r = subprocess.run(cmd, capture_output=True, text=True)
            open(os.path.join(work, "part%d" % p, "render.log"), "w").write(r.stdout + r.stderr)
            if r.returncode:
                print(r.stdout[-1500:], r.stderr[-1500:]); raise SystemExit("part%d 렌더 실패" % p)
            print("[render] part%d 완료 %.1f분 (%.0f초 걸림)" % (p, dur(out) / 60, time.time() - t0), flush=True)
        outs.append(out)
    if len(outs) < 2 and "--parts" in sys.argv:
        return
    # 이어 붙이기
    lst = os.path.join(work, "concat_parts.txt")
    with open(lst, "w") as f:
        for o in outs:
            f.write("file '%s'\n" % o)
    final = os.path.join(work, "금융의모든것_%s.mp4" % ("preview" if preview else "1080p"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", final], check=True)
    print("[concat] %s (%.1f분)" % (final, dur(final) / 60))
    if not preview:
        small = os.path.join(work, "금융의모든것_720p.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", final, "-vf", "scale=1280:720", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", small], check=True)
        print("[720p] %s" % small)
    # 챕터 타임스탬프: 각 파트에서 section이 바뀌는 장면 시작 시각 + 앞 파트 길이
    chapters, offset, last = [], 0.0, None
    for p, o in zip(parts, outs):
        P = json.load(open(os.path.join(work, "part%d" % p, "project.json"), encoding="utf-8"))
        for sc in P["scenes"]:
            sec = sc.get("section") or last
            if sec and sec != last and sc["type"] in ("slide", "broll", "hook"):
                name = sec.split(". ", 1)[-1] if sec[0].isdigit() else sec
                if not chapters or chapters[-1][1] != name:
                    chapters.append((offset + float(sc.get("start", 0)), name))
                last = sec
        offset += dur(o)
    chapters[0] = (0.0, chapters[0][1])
    txt = "\n".join("%s %s" % (ts(t), n) for t, n in chapters)
    open(os.path.join(work, "chapters.txt"), "w", encoding="utf-8").write(txt + "\n")
    print("[chapters]\n" + txt)


if __name__ == "__main__":
    main()
