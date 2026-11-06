#!/usr/bin/env python3
"""현철님 PC 전용: 여의도여자(Voicebox, 127.0.0.1:17493)로 841문장을 다시 녹음하고 전체를 다시 렌더한다.

  python tools/pc_voice.py <작업폴더> [--voice 여의도여자] [--no-render]

- 클라우드 판(Supertonic F3) 음성은 tts/fix_supertonic/ 으로 옮겨 두고, 새 음성을 tts/fix/ 에 쓴다.
- 이미 만든 문장은 건너뛰므로, 중간에 끊겨도 같은 명령을 다시 실행하면 이어서 한다.
- 한 문장 20~50초 → 841문장이면 약 6~10시간. 밤새 돌려 두는 것을 권장.
"""
import json, os, sys, time, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, ".claude", "skills", "neogul-edit", "scripts"))
import neogul_edit as ne  # noqa: E402


def main():
    work = os.path.abspath(sys.argv[1])
    voice = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else "여의도여자"
    tts = os.path.join(work, "tts")
    sents = json.load(open(os.path.join(tts, "sentences.json"), encoding="utf-8"))
    fix, old = os.path.join(tts, "fix"), os.path.join(tts, "fix_supertonic")
    mark = os.path.join(fix, "_voice.txt")
    if os.path.isdir(fix) and not os.path.exists(mark):
        if os.path.exists(old):
            shutil.rmtree(old)
        os.rename(fix, old)
    os.makedirs(fix, exist_ok=True)
    open(mark, "w", encoding="utf-8").write(voice)
    t0 = time.time()
    for s in sents:
        out = os.path.join(fix, "s%04d.wav" % s["id"])
        if os.path.exists(out):
            continue
        t1 = time.time()
        ne.voicebox_tts(s["say"], out, voice)
        print("  [%s] %d/%d  %.0f초  (누적 %.0f분)" % (voice, s["id"] + 1, len(sents), time.time() - t1, (time.time() - t0) / 60), flush=True)
    if "--no-render" in sys.argv:
        return
    py = sys.executable
    subprocess.run([py, os.path.join(HERE, "build.py"), "align", work], check=True)
    subprocess.run([py, os.path.join(HERE, "build.py"), "project", work], check=True)
    subprocess.run([py, os.path.join(HERE, "render_all.py"), work], check=True)


if __name__ == "__main__":
    main()
