#!/usr/bin/env python3
"""문장별 음성 생성(클라우드용: Supertonic-3, 목소리 F3) + whisper 발음 검수.

  python tools/tts_local.py gen   <작업폴더> [--voice F3]     # tts/fix/sXXXX.wav 생성(있으면 건너뜀)
  python tools/tts_local.py check <작업폴더> [--redo 2]       # 받아쓰기 대조, 일치율 낮은 문장 재생성
PC에서 여의도여자로 바꿀 때는 tools/pc_voice.py 를 쓰세요.
"""
import json, os, re, sys, random, difflib, subprocess, time
import numpy as np

def load(work):
    return json.load(open(os.path.join(work, "tts", "sentences.json"), encoding="utf-8"))

def speed_for(s, rnd):
    sp = 1.0 + rnd.uniform(-0.03, 0.035)
    if s["disp"].startswith("!"):
        sp -= 0.05          # 강조 문장은 조금 천천히
    if len(s["say"]) < 14:
        sp -= 0.03          # 짧은 문장은 서두르지 않게
    return round(sp, 3)

def gen(work, voice="F3", only=None, seed=0):
    from supertonic import TTS
    sents = load(work)
    out = os.path.join(work, "tts", "fix"); os.makedirs(out, exist_ok=True)
    tts = TTS(); st = tts.get_voice_style(voice)
    rnd = random.Random(11 + seed)
    t0 = time.time(); n = 0
    for s in sents:
        sp = speed_for(s, rnd)
        p = os.path.join(out, "s%04d.wav" % s["id"])
        if only is not None and s["id"] not in only:
            continue
        if only is None and os.path.exists(p):
            continue
        wav, d = tts.synthesize(s["say"], voice_style=st, lang="ko", total_steps=16, speed=sp)
        tts.save_audio(wav, p); n += 1
        if n % 25 == 0:
            print("  %d/%d (%.0f초)" % (s["id"] + 1, len(sents), time.time() - t0), flush=True)
    print("[gen] %d문장 생성, %.0f초" % (n, time.time() - t0))

norm = lambda s: re.sub(r"[^가-힣]", "", s)

def check(work, redo=2):
    from faster_whisper import WhisperModel
    sents = load(work)
    fx = os.path.join(work, "tts", "fix")
    m = WhisperModel("medium", device="cpu", compute_type="int8")
    rep_p = os.path.join(work, "tts", "check.json")
    rep = json.load(open(rep_p)) if os.path.exists(rep_p) else {}
    def score(s):
        a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(fx, "s%04d.wav" % s["id"]), "-ar", "16000", "-ac", "1", "-f", "f32le", "-"],
                                         capture_output=True).stdout, np.float32)
        segs, _ = m.transcribe(a, language="ko", beam_size=5, initial_prompt=s["say"][:40] if False else None)
        hyp = "".join(x.text for x in segs)
        # 숫자는 받아쓰기에서 아라비아 숫자로 나오므로 화면 문장과도 비교해 더 높은 쪽을 쓴다
        r1 = difflib.SequenceMatcher(None, norm(s["say"]), norm(hyp)).ratio()
        r2 = difflib.SequenceMatcher(None, re.sub(r"[^가-힣0-9]", "", s["disp"]), re.sub(r"[^가-힣0-9]", "", hyp)).ratio()
        return max(r1, r2), hyp
    t0 = time.time()
    for s in sents:
        k = str(s["id"])
        if k in rep and rep[k]["ok"]:
            continue
        r, hyp = score(s)
        rep[k] = {"r": round(r, 3), "hyp": hyp, "ok": r >= 0.85}
        if int(k) % 50 == 0:
            print("  check %s (%.0f초)" % (k, time.time() - t0), flush=True)
            json.dump(rep, open(rep_p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(rep, open(rep_p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    for it in range(redo):
        bad = [int(k) for k, v in rep.items() if not v["ok"]]
        print("[check] 회차 %d: 의심 문장 %d개" % (it + 1, len(bad)))
        if not bad:
            break
        keep = {}
        for sid in bad:
            p = os.path.join(fx, "s%04d.wav" % sid); os.replace(p, p + ".prev.wav"); keep[sid] = rep[str(sid)]
        gen(work, only=set(bad), seed=it + 1)
        for sid in bad:
            r, hyp = score(sents[sid])
            if r >= keep[sid]["r"]:
                rep[str(sid)] = {"r": round(r, 3), "hyp": hyp, "ok": r >= 0.85}
                os.remove(os.path.join(fx, "s%04d.wav.prev.wav" % sid))
            else:
                os.replace(os.path.join(fx, "s%04d.wav.prev.wav" % sid), os.path.join(fx, "s%04d.wav" % sid))
        json.dump(rep, open(rep_p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    bad = sorted(((v["r"], int(k), v["hyp"]) for k, v in rep.items() if not v["ok"]))
    print("[check] 최종 의심 문장 %d개" % len(bad))
    for r, sid, hyp in bad[:40]:
        print("  s%04d %.2f | %s | %s" % (sid, r, sents[sid]["say"][:50], hyp[:50]))

if __name__ == "__main__":
    c, work = sys.argv[1], sys.argv[2]
    if c == "gen":
        v = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else "F3"
        gen(work, v)
    elif c == "check":
        check(work, int(sys.argv[sys.argv.index("--redo") + 1]) if "--redo" in sys.argv else 2)
