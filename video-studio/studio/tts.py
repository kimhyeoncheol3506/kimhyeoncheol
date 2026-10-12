"""여의도 목소리 엔진 연결.

두 경로 모두 yeouido-voice 규격(같은 엔진 Qwen3-TTS, 같은 기준음성/프리셋)이며 다른 TTS로 대체하지 않는다.
  - voicebox : 현철님 PC의 Voicebox (http://127.0.0.1:17493)
  - cloud    : 클라우드 세션에서 Qwen3-TTS 직접 구동 (voice/qwen_cloud.py, 준비: setup_cloud.sh)
  - auto     : Voicebox가 켜져 있으면 voicebox, 아니면 cloud(준비돼 있을 때)
--preview-silent 일 때만 무음 미리보기를 만든다 (파일명에 표시).

말 속도 (현철님 피드백, 연애 튜토리얼 스튜디오 v1.1~1.2): 빠른 배속은 기계음처럼 들림 → 쇼츠 1.05배,
롱폼은 여의도남자만 1.08배. project.json의 speed / voice_speed_by로 바꿀 수 있다.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request

from .keys import raw_name

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "voice"))
from pronounce import fix as pron  # noqa: E402

BASE = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")
VOICES = {
    "여의도남자": {"engine": "qwen", "instruct": None},
    "여의도여자": {"engine": "qwen_custom_voice", "instruct": "차분하고 또렷한 아나운서 톤, 신뢰감 있게, 보통 속도"},
}
RATE = {"long": 5.2, "shorts": 6.3}  # 무음 미리보기용 초당 음절
TTS_HOME = os.environ.get("TTS_HOME", os.path.expanduser("~/.cache/yeouido-tts"))
TTS_PYTHON = os.environ.get("TTS_PYTHON", os.path.join(TTS_HOME, "venv", "bin", "python"))
MODELS = os.environ.get("QWEN_TTS_MODELS", os.path.join(TTS_HOME, "models"))


class VoiceboxUnavailable(RuntimeError):
    pass


# ───────────── Voicebox (PC) ─────────────

def _req(method, path, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        ctype = r.headers.get("Content-Type", "")
    return json.loads(raw) if "json" in ctype else raw


def voicebox_available() -> bool:
    try:
        _req("GET", "/health", timeout=3)
        return True
    except Exception:
        return False


def cloud_available() -> bool:
    return os.path.exists(TTS_PYTHON) and all(os.path.exists(os.path.join(MODELS, m, "config.json")) for m in ("base", "custom"))


def voicebox_generate(text, voice, out_wav, instruct=None, seed=7):
    res = _req("GET", "/profiles")
    items = res.get("profiles", res) if isinstance(res, dict) else res
    ids = {p["name"]: p["id"] for p in items}
    if voice not in ids:
        raise VoiceboxUnavailable(f"Voicebox에 '{voice}' 프로필이 없습니다. yeouido-voice 설정을 먼저 실행하세요.")
    body = {"profile_id": ids[voice], "text": text, "language": "ko", "model_size": "1.7B", "engine": VOICES[voice]["engine"], "seed": seed}
    if voice == "여의도여자":
        body["instruct"] = instruct or VOICES[voice]["instruct"]
    gid = _req("POST", "/generate", body, timeout=60)["id"]
    for _ in range(900):
        h = _req("GET", f"/history/{gid}")
        if h.get("status") == "completed":
            break
        if h.get("status") == "failed":
            raise RuntimeError(f"음성 생성 실패: {h.get('error')}")
        time.sleep(2)
    else:
        raise TimeoutError("음성 생성 시간 초과")
    with open(out_wav, "wb") as f:
        f.write(_req("GET", f"/audio/{gid}", timeout=120))


# ───────────── 공통 ─────────────

def resolve_engine(choice: str) -> str:
    if choice == "voicebox" or (choice == "auto" and voicebox_available()):
        if not voicebox_available():
            raise VoiceboxUnavailable("Voicebox(PC)에 연결할 수 없습니다. Voicebox 앱을 켜거나 --voice cloud 를 쓰세요.")
        return "voicebox"
    if choice in ("cloud", "auto"):
        if not cloud_available():
            raise VoiceboxUnavailable("여의도 목소리 엔진이 준비되지 않았습니다. 클라우드면 `bash setup_cloud.sh`(10~15분), PC면 Voicebox를 켜세요. "
                                      "화면만 먼저 보려면 --preview-silent.")
        return "cloud"
    raise ValueError(choice)


def generate_all(project_path: str, project: dict, engine: str, audio_dir: str) -> None:
    """모든 장면의 원본 음성을 캐시에 만든다 (이미 있으면 건너뜀)."""
    os.makedirs(audio_dir, exist_ok=True)
    if engine == "cloud":
        subprocess.run([TTS_PYTHON, os.path.join(ROOT, "voice", "qwen_cloud.py"), project_path, "--models", MODELS], check=True)
        return
    for s in project["scenes"]:
        raw = os.path.join(audio_dir, raw_name(s))
        if not os.path.exists(raw):
            voicebox_generate(pron(s["text"]), s.get("voice", "여의도남자"), raw, s.get("instruct"))
            print(f"[{s.get('voice', '여의도남자')}] {s['id']} (Voicebox)")


def silent(out_wav, seconds):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{seconds:.3f}", out_wav], check=True)


def duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def estimate_seconds(text, fmt):
    return max(1.2, len("".join(text.split())) / RATE[fmt] + 0.25)


def scene_speed(scene: dict, project: dict) -> float:
    fmt = project["format"]
    voice = scene.get("voice", "여의도남자")
    by = project.get("voice_speed_by", {"여의도남자": 1.08} if fmt == "long" else {})
    base = float(project.get("speed", 1.05 if fmt == "shorts" else 1.0))
    return base * float(by.get(voice, 1.0))


def scene_audio(scene: dict, project: dict, audio_dir: str, preview_silent: bool) -> tuple[str, bool]:
    """속도 적용된 장면 음성 경로와 실제 목소리 여부."""
    os.makedirs(audio_dir, exist_ok=True)
    raw = os.path.join(audio_dir, raw_name(scene))
    if os.path.exists(raw):
        sp = scene_speed(scene, project)
        final = raw.replace(".wav", f"_x{sp:.3g}.wav")
        if not os.path.exists(final):
            af = f"atempo={sp}," if abs(sp - 1) > 1e-3 else ""
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af + "aresample=48000", "-ac", "2", final], check=True)
        return final, True
    if not preview_silent:
        raise VoiceboxUnavailable(f"{scene['id']} 음성이 없습니다.")
    tmp = raw.replace(".wav", "_silent.wav")
    silent(tmp, estimate_seconds(scene["text"], project["format"]))
    return tmp, False
