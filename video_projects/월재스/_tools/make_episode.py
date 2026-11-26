#!/usr/bin/env python3
"""월재스 에피소드 한 편을 끝까지: 그래픽 → 숫자 클립 → 음성(Supertonic F3) → whisper 검수 → 정렬 → 렌더(1080p) → release 패키지.

  python3 make_episode.py <에피소드폴더이름> [--preset basic|money|tension] [--work <작업폴더>] [--from 단계]
단계: assets, voice, render, release (--from 으로 중간부터)
입력: <에피>/script/*.txt, research/clips.json, research/thumbs.json, release/<에피>/설명란_템플릿.txt
출력: release/<에피>/<에피>_1080p.mp4, 썸네일_A/B.png, 설명란.txt(목차·효과음 출처 채움)
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)                       # video_projects/월재스
REPO = os.path.normpath(os.path.join(PROJ, "..", ".."))
SCR = os.environ.get("WOLJE_SCRATCH", "/tmp/claude-0/-home-user-kimhyeoncheol/44362ec3-a63a-5c3d-aec2-d8ee4bace401/scratchpad/wolje")
MASCOT = os.path.join(SCR, "common", "assets", "mascot")
PY = sys.executable


def arg(n, d=None):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


def run(cmd, env=None, log=None):
    e = dict(os.environ, **(env or {}))
    print("$", " ".join(cmd[:4]), "...", flush=True)
    r = subprocess.run(cmd, env=e, capture_output=True, text=True)
    if log:
        open(log, "a", encoding="utf-8").write(r.stdout + r.stderr)
    if r.returncode:
        raise SystemExit("실패: %s\n%s\n%s" % (" ".join(cmd), r.stdout[-2000:], r.stderr[-2000:]))
    return r.stdout


def main():
    ep = sys.argv[1]
    E = os.path.join(PROJ, ep)
    R = os.path.join(REPO, "release", ep)
    W = arg("--work", os.path.join(SCR, ep))
    preset = arg("--preset", "basic")
    start = arg("--from", "assets")
    order = ["assets", "voice", "render", "release"]
    todo = order[order.index(start):]
    A = os.path.join(W, "assets")
    for d in ("clips", "pd16"):
        os.makedirs(os.path.join(A, d), exist_ok=True)
    os.makedirs(R, exist_ok=True)
    log = os.path.join(W, "make.log")
    env = {"EP_DIR": E, "EP_TITLE": ep, "SFX_PRESET": preset, "OUT_NAME": ep}
    thumbs = json.load(open(os.path.join(E, "research", "thumbs.json"), encoding="utf-8"))

    # 대본 점검: @s JSON, 알 수 없는 지시, 장면 수
    import glob
    bad, known = [], {"part", "section", "hook", "broll", "pip", "mascot", "sub", "outro", "toc", "big", "s"}
    for f in sorted(glob.glob(os.path.join(E, "script", "*.txt"))):
        for n, ln in enumerate(open(f, encoding="utf-8"), 1):
            ln = ln.strip()
            if ln.startswith("@"):
                cmd, _, rest = ln[1:].partition(" ")
                if cmd not in known:
                    bad.append("%d: 알 수 없는 지시 @%s" % (n, cmd))
                if cmd == "s":
                    try:
                        json.loads(rest)
                    except Exception as ex:
                        bad.append("%d: JSON 오류 %s" % (n, ex))
    if bad:
        raise SystemExit("대본 점검 실패:\n" + "\n".join(bad))

    if "assets" in todo:
        if not os.path.exists(os.path.join(A, "mascot")):
            shutil.copytree(MASCOT, os.path.join(A, "mascot"))
        flag = thumbs[0].get("flag", "kr")
        f2 = thumbs[1].get("flag") if len(thumbs) > 1 else None
        other = f2 if f2 and f2 != flag else ("chart_red" if flag in ("kr", "us", "jp", "is") else "kr")
        kick = thumbs[0].get("kicker") or "월급쟁이 재테크"
        run([PY, os.path.join(HERE, "visuals.py"), "hookbg", flag, os.path.join(A, "hook.png")])
        run([PY, os.path.join(HERE, "visuals.py"), "broll", flag, os.path.join(A, "broll1.png"), kick, "월급쟁이 재테크 스킬"])
        run([PY, os.path.join(HERE, "visuals.py"), "broll", other, os.path.join(A, "broll2.png"), kick, ""])
        clips = json.load(open(os.path.join(E, "research", "clips.json"), encoding="utf-8"))
        for c in clips:
            out = os.path.join(A, "clips", c.get("file", "c1.mp4"))
            cfg = os.path.join(W, "clip_%s.json" % os.path.basename(out)[:-4])
            json.dump(c, open(cfg, "w", encoding="utf-8"), ensure_ascii=False)
            run([PY, os.path.join(HERE, "engine_clips.py"), "counter", cfg, out])
        for i, t in enumerate(thumbs[:2]):
            cfg = os.path.join(W, "thumb_%d.json" % i)
            json.dump(t, open(cfg, "w", encoding="utf-8"), ensure_ascii=False)
            run([PY, os.path.join(HERE, "visuals.py"), "thumb", cfg, os.path.join(R, "썸네일_%s.png" % "AB"[i])])

    if "voice" in todo:
        print(run([PY, os.path.join(HERE, "build.py"), "chunks", W], env).splitlines()[0])
        run([PY, os.path.join(HERE, "tts_local.py"), "gen", W], env, log)
        out = run([PY, os.path.join(HERE, "tts_local.py"), "check", W], env, log)
        print([l for l in out.splitlines() if "최종" in l])
        print(run([PY, os.path.join(HERE, "build.py"), "align", W], env, log).strip().splitlines()[-1])

    if "render" in todo:
        run([PY, os.path.join(HERE, "build.py"), "project", W], env, log)
        run([PY, os.path.join(HERE, "render_all.py"), W], env, log)

    if "release" in todo:
        src = os.path.join(W, "%s_1080p.mp4" % ep)
        shutil.copy2(src, os.path.join(R, os.path.basename(src)))
        tpl = os.path.join(R, "설명란_템플릿.txt")
        desc = open(tpl if os.path.exists(tpl) else os.path.join(R, "설명란.txt"), encoding="utf-8").read()
        ch = open(os.path.join(W, "chapters.txt"), encoding="utf-8").read().strip()
        desc = desc.replace("{CHAPTERS}", ch)
        cr = os.path.join(W, "sound_credits.txt")
        if os.path.exists(cr) and "효과음 일부" not in desc:
            line = "🔊 " + open(cr, encoding="utf-8").read().strip()
            desc = desc.replace("🎙", line + "\n🎙", 1) if "🎙" in desc else desc + "\n" + line
        open(os.path.join(R, "설명란.txt"), "w", encoding="utf-8").write(desc)
        if os.path.exists(tpl):
            os.remove(tpl)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
        print("[완료] %s %.1f분 → %s" % (ep, d / 60, R))


if __name__ == "__main__":
    main()
