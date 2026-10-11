"""여의도 목소리(Voicebox) 클라이언트.

- 기본 목소리: 여의도남자 (engine qwen, 복제 프로필) / 대화 상대: 여의도여자 (engine qwen_custom_voice, instruct 지원)
- Voicebox는 사용자 PC(http://127.0.0.1:17493)에서 실행된다. 다른 TTS로 대체하지 않는다.
- --preview-silent 옵션일 때만 '무음 미리보기'(예상 길이의 무음)로 화면 구성을 확인할 수 있다. 결과 파일명에 표시된다.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request

BASE = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")
VOICES = {
    "여의도남자": {"engine": "qwen", "instruct": None},
    "여의도여자": {"engine": "qwen_custom_voice", "instruct": "차분하고 또렷한 아나운서 톤, 신뢰감 있게, 보통 속도"},
}
# 무음 미리보기용 낭독 속도(초당 음절, 공백 제외) — 벤치마킹 실측: 롱폼 존댓말 약 5.2, 쇼츠 반말 약 6.3
RATE = {"long": 5.2, "shorts": 6.3}


class VoiceboxUnavailable(RuntimeError):
    pass


def _req(method: str, path: str, body: dict | None = None, timeout: float = 30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        ctype = r.headers.get("Content-Type", "")
    return json.loads(raw) if "json" in ctype else raw


def available() -> bool:
    try:
        _req("GET", "/health", timeout=3)
        return True
    except Exception:
        return False


def profiles() -> dict[str, str]:
    res = _req("GET", "/profiles")
    items = res.get("profiles", res) if isinstance(res, dict) else res
    return {p["name"]: p["id"] for p in items}


def generate(text: str, voice: str, out_wav: str, instruct: str | None = None, seed: int = 7) -> None:
    if voice not in VOICES:
        raise ValueError(f"목소리는 {list(VOICES)} 중 하나여야 합니다: {voice}")
    ids = profiles()
    if voice not in ids:
        raise VoiceboxUnavailable(f"Voicebox에 '{voice}' 프로필이 없습니다. yeouido-voice 설정(setup_voices.py)을 먼저 실행하세요.")
    body = {"profile_id": ids[voice], "text": text, "language": "ko", "model_size": "1.7B", "engine": VOICES[voice]["engine"], "seed": seed}
    if voice == "여의도여자":
        body["instruct"] = instruct or VOICES[voice]["instruct"]
    gid = _req("POST", "/generate", body, timeout=60)["id"]
    for _ in range(900):  # 최대 30분 (첫 실행 시 모델 다운로드)
        h = _req("GET", f"/history/{gid}")
        st = h.get("status")
        if st == "completed":
            break
        if st == "failed":
            raise RuntimeError(f"음성 생성 실패: {h.get('error')}")
        time.sleep(2)
    else:
        raise TimeoutError("음성 생성 시간 초과")
    audio = _req("GET", f"/audio/{gid}", timeout=120)
    with open(out_wav, "wb") as f:
        f.write(audio)


def silent(out_wav: str, seconds: float) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{seconds:.3f}", out_wav], check=True)


def duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def estimate_seconds(text: str, fmt: str) -> float:
    n = len("".join(text.split()))
    return max(1.2, n / RATE[fmt] + 0.25)


def speed_up(src: str, dst: str, speed: float) -> None:
    if abs(speed - 1.0) < 1e-3:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ar", "48000", "-ac", "2", dst], check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter:a", f"atempo={speed}", "-ar", "48000", "-ac", "2", dst], check=True)


def scene_audio(scene: dict, fmt: str, audio_dir: str, speed: float, preview_silent: bool) -> tuple[str, bool]:
    """장면 음성 파일 경로와 '실제 목소리 여부'를 반환. 같은 대사·목소리는 캐시를 재사용."""
    os.makedirs(audio_dir, exist_ok=True)
    voice = scene.get("voice", "여의도남자")
    key = hashlib.sha1(f"{voice}|{scene.get('instruct')}|{scene['text']}".encode()).hexdigest()[:12]
    raw = os.path.join(audio_dir, f"{scene['id']}_{key}.wav")
    final = os.path.join(audio_dir, f"{scene['id']}_{key}_x{speed:g}.wav")
    if os.path.exists(final):
        return final, True
    if not preview_silent:
        if not available():
            raise VoiceboxUnavailable(
                "Voicebox(여의도 목소리)에 연결할 수 없습니다. PC에서 Voicebox 앱을 실행한 뒤 다시 시도하세요. "
                "화면 구성만 먼저 확인하려면 --preview-silent 옵션을 쓰세요."
            )
        if not os.path.exists(raw):
            generate(scene["text"], voice, raw, scene.get("instruct"))
        speed_up(raw, final, speed)
        return final, True
    tmp = os.path.join(audio_dir, f"{scene['id']}_{key}_silent.wav")
    silent(tmp, estimate_seconds(scene["text"], fmt))
    return tmp, False
