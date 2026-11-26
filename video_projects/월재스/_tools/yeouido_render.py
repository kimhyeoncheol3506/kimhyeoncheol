#!/usr/bin/env python3
"""여의도여자(PC Voicebox) 음성으로 한 편을 다시 렌더한다 — 클라우드에서 실행.

  python3 yeouido_render.py <편>            # 예: 04_환율IMF수준
  python3 yeouido_render.py --scan          # DONE 이 있고 아직 VOICE_YEOUIDO 가 없는 편을 모두 처리

PC → 저장소 약속(같은 브랜치):
  video_projects/월재스/<편>/voice_lines.json      클라우드가 만든 문장 목록 [{"id":"L0001","text":읽을 문장,"speed":1.0,"sid":0,"disp":화면 문장}]
  video_projects/월재스/<편>/voice_yeouido/L0001.wav …   PC가 만든 문장별 음성(48kHz mono 권장, 다른 형식도 변환함)
  video_projects/월재스/<편>/voice_yeouido/DONE     한 편 다 올렸다는 표시
처리:
  1) L####.wav → 작업폴더 tts/fix/s####.wav (48kHz mono). F3 음성은 tts/fix_supertonic/ 으로 옮겨 둔다.
  2) Whisper(medium) 받아쓰기 대조. 일치율 0.85 미만 문장은 voice_yeouido/RERECORD.json 으로 남기고 렌더하지 않는다.
     → PC가 그 문장 wav를 덮어쓰고 RERECORD.json 을 지워서 푸시하면 다시 검수한다(통과한 문장은 다시 받아쓰지 않음).
  3) 통과하면 정렬(자막·화면 타이밍을 새 음성 길이에 맞춤) → 렌더 → release/<편>/<편>_1080p.mp4 교체,
     설명란.txt 의 목차 타임스탬프만 새 길이로 바꾸고, release/<편>/VOICE_YEOUIDO 빈 파일을 만든다.
업로드·게시는 하지 않는다.
"""
import glob, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
REPO = os.path.normpath(os.path.join(PROJ, "..", ".."))
SCR = os.environ.get("WOLJE_SCRATCH", "/tmp/claude-0/-home-user-kimhyeoncheol/44362ec3-a63a-5c3d-aec2-d8ee4bace401/scratchpad/wolje")
PY = sys.executable
PRESET = {"04_환율IMF수준": "money", "05_초대형IPO": "basic", "06_테마주폭락": "tension", "07_반도체와구글": "basic",
          "08_호르무즈와기름값": "tension", "09_약세장": "tension", "10_버핏투자법": "basic", "11_사모신용": "tension",
          "12_레버리지ETF": "money", "13_연준의장교체": "money"}


def run(cmd, env=None):
    print("$", " ".join(os.path.basename(c) if i < 2 else c for i, c in enumerate(cmd[:4])), flush=True)
    r = subprocess.run(cmd, env=dict(os.environ, **(env or {})), capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("실패: %s\n%s\n%s" % (" ".join(cmd), r.stdout[-1500:], r.stderr[-1500:]))
    return r.stdout


def ensure_work(ep, W, env):
    """작업폴더가 사라졌으면(컨테이너 교체) 그래픽·클립을 다시 만들고 문장 목록을 만든다."""
    if not os.path.isdir(os.path.join(W, "assets", "clips")) or not os.listdir(os.path.join(W, "assets", "clips")):
        run([PY, os.path.join(HERE, "make_episode.py"), ep, "--preset", PRESET.get(ep, "basic"), "--work", W, "--to", "assets"])
        # 썸네일은 release 것을 그대로 둔다(assets 단계가 덮어쓰므로 git 판으로 되돌림)
        subprocess.run(["git", "-C", REPO, "checkout", "--", "release/%s/썸네일_A.png" % ep, "release/%s/썸네일_B.png" % ep])
    run([PY, os.path.join(HERE, "build.py"), "chunks", W], env)


def import_wavs(ep, W, lines, V):
    fix, old = os.path.join(W, "tts", "fix"), os.path.join(W, "tts", "fix_supertonic")
    mark = os.path.join(fix, "_voice.txt")
    if os.path.isdir(fix) and not os.path.exists(mark):
        if os.path.exists(old):
            shutil.rmtree(old)
        os.rename(fix, old)
        for f in ("check.json",):
            p = os.path.join(W, "tts", f)
            if os.path.exists(p):
                os.remove(p)
    os.makedirs(fix, exist_ok=True)
    open(mark, "w").write("여의도여자")
    missing = []
    for x in lines:
        src = os.path.join(V, x["id"] + ".wav")
        if not os.path.exists(src):
            missing.append(x["id"]); continue
        dst = os.path.join(fix, "s%04d.wav" % x["sid"])
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ar", "48000", "-ac", "1", dst], check=True)
    return missing


def whisper_check(W, lines):
    from faster_whisper import WhisperModel
    import difflib
    import numpy as np
    rep_p = os.path.join(W, "tts", "check_yeouido.json")
    rep = json.load(open(rep_p, encoding="utf-8")) if os.path.exists(rep_p) else {}
    fix = os.path.join(W, "tts", "fix")
    m = None
    for x in lines:
        p = os.path.join(fix, "s%04d.wav" % x["sid"]); mt = os.path.getmtime(p)
        old = rep.get(x["id"])
        if old and old["ok"] and old.get("mtime") == mt:
            continue
        if m is None:
            m = WhisperModel("medium", device="cpu", compute_type="int8")
        a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ar", "16000", "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
        segs, _ = m.transcribe(a, language="ko", beam_size=1, vad_filter=False)
        hyp = "".join(s.text for s in segs).strip()
        r1 = difflib.SequenceMatcher(None, re.sub(r"[^가-힣]", "", x["text"]), re.sub(r"[^가-힣]", "", hyp)).ratio()
        r2 = difflib.SequenceMatcher(None, re.sub(r"[^가-힣0-9]", "", x["disp"]), re.sub(r"[^가-힣0-9]", "", hyp)).ratio()
        r = max(r1, r2)
        rep[x["id"]] = {"r": round(r, 3), "heard": hyp, "ok": r >= 0.85, "mtime": mt}
        json.dump(rep, open(rep_p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return [{"id": x["id"], "text": x["text"], "disp": x["disp"], "heard": rep[x["id"]]["heard"], "score": rep[x["id"]]["r"]}
            for x in lines if not rep[x["id"]]["ok"]]


def fix_chapters(ep, W):
    R = os.path.join(REPO, "release", ep)
    p = os.path.join(R, "설명란.txt"); d = open(p, encoding="utf-8").read().split("\n")
    ch = open(os.path.join(W, "chapters.txt"), encoding="utf-8").read().strip().split("\n")
    i = next(k for k, l in enumerate(d) if l.startswith("⏱"))
    j = i + 1
    while j < len(d) and re.match(r"^\d{1,2}:\d{2}", d[j]):
        j += 1
    d[i + 1:j] = ch
    open(p, "w", encoding="utf-8").write("\n".join(d))


def one(ep):
    E = os.path.join(PROJ, ep); V = os.path.join(E, "voice_yeouido"); R = os.path.join(REPO, "release", ep)
    if not os.path.exists(os.path.join(V, "DONE")):
        print("[%s] DONE 없음 — 대기" % ep); return "wait"
    if os.path.exists(os.path.join(V, "RERECORD.json")):
        print("[%s] RERECORD.json 이 남아 있음 — PC 재녹음 대기" % ep); return "wait"
    lines = json.load(open(os.path.join(E, "voice_lines.json"), encoding="utf-8"))
    W = os.path.join(SCR, ep)
    env = {"EP_DIR": E, "EP_TITLE": ep, "SFX_PRESET": PRESET.get(ep, "basic"), "OUT_NAME": ep}
    ensure_work(ep, W, env)
    sents = json.load(open(os.path.join(W, "tts", "sentences.json"), encoding="utf-8"))
    if [s["say"] for s in sents] != [x["text"] for x in lines] and len(sents) != len(lines):
        raise SystemExit("[%s] 대본과 voice_lines.json 문장 수가 다름 (%d vs %d)" % (ep, len(sents), len(lines)))
    miss = import_wavs(ep, W, lines, V)
    if miss:
        json.dump([{"id": i, "text": next(x["text"] for x in lines if x["id"] == i), "reason": "파일 없음"} for i in miss],
                  open(os.path.join(V, "RERECORD.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("[%s] 음성 파일 없음 %d개 → RERECORD.json" % (ep, len(miss))); return "rerecord"
    bad = whisper_check(W, lines)
    if bad:
        json.dump(bad, open(os.path.join(V, "RERECORD.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("[%s] 받아쓰기 불일치 %d문장 → RERECORD.json" % (ep, len(bad)))
        for b in bad:
            print("  %s %.2f | %s | 들림: %s" % (b["id"], b["score"], b["text"][:40], b["heard"][:40]))
        return "rerecord"
    print(run([PY, os.path.join(HERE, "build.py"), "align", W], env).strip().splitlines()[-1])
    run([PY, os.path.join(HERE, "build.py"), "project", W], env)
    run([PY, os.path.join(HERE, "render_all.py"), W], env)
    src = os.path.join(W, "%s_1080p.mp4" % ep)
    shutil.copy2(src, os.path.join(R, os.path.basename(src)))
    fix_chapters(ep, W)
    open(os.path.join(R, "VOICE_YEOUIDO"), "w").close()
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    print("[완료] %s 여의도여자 %.1f분" % (ep, d / 60)); return "done"


if __name__ == "__main__":
    if sys.argv[1] == "--scan":
        for e in sorted(PRESET):
            if not os.path.exists(os.path.join(REPO, "release", e, "VOICE_YEOUIDO")):
                one(e)
    else:
        one(sys.argv[1])
