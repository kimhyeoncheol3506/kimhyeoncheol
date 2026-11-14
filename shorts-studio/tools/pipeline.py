"""쇼츠 제작 파이프라인 한 번에 돌리기 (예전 scratchpad/queue.py + regen.py 를 저장소로 옮김).

  python3 tools/pipeline.py projects/short_074_x [projects/... 여러 개 순서대로]
  python3 tools/pipeline.py --after <pid> projects/...   # 실행 중인 다른 파이프라인(pid)이 끝난 뒤 시작

순서: 구독 멘트(add_outro) → 빠진 음성 TTS(죽으면 최대 3번 다시) → 음성 QA → 불량 장면은 시드 5개로 재생성
      (그래도 불량이면 "STILL BAD" — 전달 금지, 문장 고치기/사전 등록) → 삽화(ComfyUI, 있으면) → 서버 종료(메모리 반납)
      → make.py 렌더 → tools/final_qa.py 최종 검수 → "DONE <프로젝트>"

환경 변수 (setup_cloud.sh / tools/setup_comfy.sh 출력 그대로):
  TTS_PYTHON, QWEN_TTS_MODELS  — 음성
  COMFY_DIR, COMFY_PY          — 삽화 (없으면 삽화 단계 건너뜀)
TTS는 한 번에 하나만 (메모리). 여러 프로젝트는 한 번의 실행에 나열하거나 --after 로 줄 세운다.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = os.environ.get("TTS_PYTHON", sys.executable)
MODELS = os.environ.get("QWEN_TTS_MODELS", "models")
SEEDS = [777, 4242, 9001, 1234, 31337]


def log(*a):
    print(time.strftime("%H:%M"), *a, flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, **kw)


def missing(p):
    import json
    s = json.loads((ROOT / p / "script.json").read_text(encoding="utf-8"))
    return [x["id"] for x in s["scenes"] if not (ROOT / p / "narration" / f"{x['id']}.wav").exists()]


def tts(p, ids, seed=None):
    cmd = [PY, "voice/qwen_local.py", p, "--models", MODELS, "--only", ",".join(ids)]
    if seed is not None:
        cmd += ["--seed", str(seed)]
    return run(cmd)


def qa(p, only=""):
    out = run([PY, "voice/qa.py", p] + (["--only", only] if only else [])).stdout
    m = re.search(r"^BAD: (.*)$", out, re.M)
    bad = [] if not m or m.group(1).strip() == "-" else m.group(1).split(",")
    return bad, out


def voices(p):
    run(["python3", "tools/add_outro.py", p])  # 구독·댓글 멘트(매 영상)
    for _ in range(3):  # TTS가 OOM 등으로 죽으면 빠진 파일만 다시 (QA 전에 전부 채운다)
        m = missing(p)
        if not m:
            break
        tts(p, m)
    bad, _ = qa(p)
    log(p, "QA BAD:", bad)
    still = []
    for b in bad:
        ok = False
        for i, seed in enumerate(SEEDS):
            (ROOT / p / "narration" / f"{b}.wav").unlink(missing_ok=True)
            for f in (ROOT / p / "narration" / "_tempo").glob(f"{b}*"):
                f.unlink()
            tts(p, [b], seed)
            bb, out = qa(p, b)
            line = next((l for l in out.splitlines() if f" {b} " in l and l[:3] in ("OK ", "BAD")), "")
            print(f"{time.strftime('%H:%M') + ' ' if i == 0 else ''}seed {seed}: {line}", flush=True)
            if not bb:
                ok = True
                break
        if not ok:
            still.append(b)
    if still:
        print("STILL BAD:", ",".join(still), flush=True)
    if missing(p):  # 마지막 시도 파일이 없으면 기본 시드로 채워 둔다 (STILL BAD면 어차피 전달 금지)
        tts(p, missing(p))


def illust(p):
    if not os.environ.get("COMFY_DIR"):
        return
    il = run(["python3", "tools/illust.py", p])
    log(p, (il.stdout.strip() or il.stderr.strip()[-300:]).replace("\n", " | "))
    run(["pkill", "-f", "main.py --cpu --listen"])  # ComfyUI 메모리(~4GB) 반납 → 다음 TTS와 OOM 방지


def merge_regions(p):
    """make_card.py 가 쓴 card_regions.json 을 script.json 에 합친다 (빠지면 형광펜 포커스가 안 나옴)."""
    import json
    rj, sj = ROOT / p / "card_regions.json", ROOT / p / "script.json"
    if not rj.exists():
        return
    s = json.loads(sj.read_text(encoding="utf-8"))
    regions = json.loads(rj.read_text(encoding="utf-8"))
    if s.get("card_regions") != regions:
        s["card_regions"] = regions
        sj.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
        log(p, "card_regions 합침")


def render(p):
    merge_regions(p)
    r = run(["python3", "make.py", p])
    print("\n".join(l for l in r.stdout.splitlines() if l.startswith(("렌더", "파일", "[수위]"))),
          r.stderr[-300:] if r.returncode else "", flush=True)
    q = run([PY, "tools/final_qa.py", p]).stdout
    log(q.strip())


def main(argv):
    if argv and argv[0] == "--after":
        pid = argv[1]
        argv = argv[2:]
        while Path(f"/proc/{pid}").exists():
            time.sleep(20)
    for p in argv:
        p = os.path.relpath(Path(p).resolve(), ROOT)
        voices(p)
        illust(p)
        render(p)
        log("DONE", p)


if __name__ == "__main__":
    main(sys.argv[1:])
