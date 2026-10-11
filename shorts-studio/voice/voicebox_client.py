"""PC의 Voicebox(http://127.0.0.1:17493)로 여의도남자/여의도여자 내레이션 생성. (yeouido-voice 스킬 규격)

사용 (현철님 PC에서): python voice/voicebox_client.py projects/<프로젝트>
출력: projects/<프로젝트>/narration/sXX.wav + timings.json  → 그대로 make.py 렌더에 사용
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import wave
from pathlib import Path

BASE = "http://127.0.0.1:17493"
FEMALE_DEFAULT_INSTRUCT = "차분하고 또렷한 아나운서 톤, 신뢰감 있게, 보통 속도"


def call(method, path, body=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        b = r.read()
    return b if raw else json.loads(b)


def main():
    proj = Path(sys.argv[1])
    try:
        call("GET", "/health")
    except Exception:
        sys.exit("Voicebox가 꺼져 있습니다. Voicebox 앱을 실행해 주세요 (https://voicebox.sh)")
    profiles = {p["name"]: p for p in call("GET", "/profiles")}
    for need in ("여의도남자", "여의도여자"):
        if need not in profiles:
            sys.exit(f"Voicebox 프로필 '{need}' 없음 → yeouido-voice 스킬의 '프로필 재생성' 절차를 먼저 실행")
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    out = proj / "narration"
    out.mkdir(exist_ok=True)
    rows, t = [], 0.0
    for s in script["scenes"]:
        voice = s.get("voice", "여의도남자")
        body = {"profile_id": profiles[voice]["id"], "text": s["say"], "language": "ko", "model_size": "1.7B",
                "engine": "qwen" if voice == "여의도남자" else "qwen_custom_voice", "seed": 7}
        if voice == "여의도여자":
            body["instruct"] = s.get("instruct") or FEMALE_DEFAULT_INSTRUCT
        gid = call("POST", "/generate", body)["id"]
        while True:
            h = call("GET", f"/history/{gid}")
            if h.get("status") == "completed":
                break
            if h.get("status") == "failed":
                sys.exit(f"{s['id']} 생성 실패: {h.get('error')}")
            time.sleep(2)
        f = out / f"{s['id']}.wav"
        f.write_bytes(call("GET", f"/audio/{gid}", raw=True))
        with wave.open(str(f)) as w:
            d = w.getnframes() / w.getframerate()
        rows.append({"id": s["id"], "voice": voice, "start": round(t, 3), "end": round(t + d, 3), "duration": round(d, 3)})
        t += d
        print(f"[{voice}] {s['id']} {d:.1f}s", flush=True)
    (out / "timings.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
