"""PC(Windows) 로컬 제작 큐: Voicebox(여의도남자/여자) 음성 → Whisper 검수(불량 장면 시드 재생성) → 렌더.

  python tools/local_queue.py projects/A projects/B ...
클라우드 tools/pipeline.py 의 PC 버전 (Qwen 로컬 대신 Voicebox http://127.0.0.1:17493).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "voice"))
from voicebox_client import FEMALE_DEFAULT_INSTRUCT, call  # noqa: E402
from pronounce import fix as pron  # noqa: E402

SEEDS = [7, 101, 202, 303, 404]
PY = sys.executable


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def gen(proj: Path, sc: dict, profiles, seed=7):
    voice = sc.get("voice", "여의도남자")
    body = {"profile_id": profiles[voice]["id"], "text": pron(sc["say"]), "language": "ko", "model_size": "1.7B",
            "engine": "qwen" if voice == "여의도남자" else "qwen_custom_voice", "seed": seed}
    if voice == "여의도여자":
        body["instruct"] = sc.get("instruct") or FEMALE_DEFAULT_INSTRUCT
    gid = call("POST", "/generate", body)["id"]
    while True:
        h = call("GET", f"/history/{gid}")
        if h.get("status") == "completed":
            break
        if h.get("status") == "failed":
            raise RuntimeError(f"{sc['id']} 생성 실패: {h.get('error')}")
        time.sleep(2)
    f = proj / "narration" / f"{sc['id']}.wav"
    f.write_bytes(call("GET", f"/audio/{gid}", raw=True))
    for old in (proj / "narration" / "_tempo").glob(f"{sc['id']}_*"):
        old.unlink()
    return f


def qa(proj: Path, only=""):
    cmd = [PY, "voice/qa.py", str(proj), "--model", "small"] + (["--only", only] if only else [])
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    m = re.search(r"^BAD: (.*)$", out, re.M)
    bad = [] if not m or m.group(1).strip() in ("-", "") else [x.strip() for x in m.group(1).split(",")]
    return bad, out


def timings(proj: Path, script):
    rows, t = [], 0.0
    for s in script["scenes"]:
        f = proj / "narration" / f"{s['id']}.wav"
        with wave.open(str(f)) as w:
            d = w.getnframes() / w.getframerate()
        rows.append({"id": s["id"], "voice": s.get("voice", "여의도남자"), "start": round(t, 3), "end": round(t + d, 3),
                     "duration": round(d, 3)})
        t += d
    (proj / "narration" / "timings.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


def run(proj: Path):
    subprocess.run([PY, "tools/add_outro.py", str(proj)], cwd=ROOT)
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    profiles = {p["name"]: p for p in call("GET", "/profiles")}
    # PC Voicebox 에 여의도남자 프로필이 없으면(2026-11-28 확인) 그 장면은 여의도여자로 (구독 멘트 포함)
    changed = False
    for sc in script["scenes"]:
        if sc.get("voice", "여의도남자") not in profiles:
            sc["voice"] = "여의도여자"
            sc.setdefault("instruct", "밝고 상냥한 30대 여성 톤, 부탁하듯 부드럽게")
            changed = True
    if changed:
        (proj / "script.json").write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    (proj / "narration").mkdir(exist_ok=True)
    for sc in script["scenes"]:
        if not (proj / "narration" / f"{sc['id']}.wav").exists():
            gen(proj, sc, profiles)
            log(proj.name, "음성", sc["id"])
    bad, out = qa(proj)
    (proj / "narration" / "qa_log.txt").write_text(out, encoding="utf-8")
    log(proj.name, "QA BAD:", bad or "-")
    still = []
    byid = {s["id"]: s for s in script["scenes"]}
    for b in bad:
        ok = False
        for seed in SEEDS[1:]:
            gen(proj, byid[b], profiles, seed)
            bb, o2 = qa(proj, b)
            log(proj.name, b, "seed", seed, "BAD" if bb else "OK")
            if not bb:
                ok = True
                break
        if not ok:
            still.append(b)
    if still:
        log(proj.name, "STILL BAD:", ",".join(still))
    timings(proj, script)
    r = subprocess.run([PY, "make.py", str(proj)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    log(proj.name, "렌더", "OK" if r.returncode == 0 else "FAIL", (r.stdout + r.stderr)[-600:].replace("\n", " | "))
    return still


def main(argv):
    try:
        call("GET", "/health")
    except Exception:
        sys.exit("Voicebox 꺼짐")
    summary = {}
    for p in argv:
        proj = (ROOT / p).resolve() if not Path(p).is_absolute() else Path(p)
        try:
            summary[proj.name] = run(proj)
        except Exception as e:  # 한 편이 실패해도 다음 편 진행
            log(proj.name, "ERROR", repr(e))
            summary[proj.name] = ["ERROR"]
        log("DONE", proj.name)
    log("ALL DONE", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
