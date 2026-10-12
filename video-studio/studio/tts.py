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


def align_all(project_path: str) -> None:
    """Whisper 단어 타임스탬프 생성 (클라우드 엔진 venv 필요, 없으면 글자 수 비율 자막으로 대체)."""
    if not os.path.exists(TTS_PYTHON):
        print("⚠️ 정렬 엔진 없음 → 자막은 글자 수 비율로 배치합니다.")
        return
    subprocess.run([TTS_PYTHON, os.path.join(ROOT, "voice", "align.py"), project_path], check=False)


def silent(out_wav, seconds):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{seconds:.3f}", out_wav], check=True)


def duration(path: str) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def first_voice(path: str) -> float | None:
    import wave
    import numpy as np
    with wave.open(path) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    hop = int(sr * 0.01)
    n = len(x) // hop
    if n == 0:
        return None
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    thr = max(0.008, 0.12 * np.percentile(rms, 95))
    idx = np.where(rms > thr)[0]
    return float(idx[0]) * 0.01 if len(idx) else None


def speech_onsets(path: str, min_gap: float = 0.07) -> list[float]:
    """파형에서 '쉼 뒤에 말이 다시 시작되는 시각'(10ms 해상도)을 찾는다."""
    import wave
    import numpy as np
    with wave.open(path) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    hop = int(sr * 0.01)
    n = len(x) // hop
    if n == 0:
        return []
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
    thr = max(0.008, 0.12 * np.percentile(rms, 95))
    voiced = rms > thr
    onsets, quiet = [0.0], 0
    for i, v in enumerate(voiced):
        if not v:
            quiet += 1
        else:
            if quiet * 0.01 >= min_gap and i > 0:
                onsets.append(i * 0.01)
            quiet = 0
    return onsets


def _snap(est: list[float], ons: list[float]) -> list[float]:
    out = [est[0]]
    for k in range(1, len(est)):
        guess = est[k] + SUB_LEAD
        near = [o for o in ons if abs(o - guess) <= 0.7 and o > out[-1] + SUB_LEAD + 0.4]
        out.append(max(0.0, (min(near, key=lambda o: abs(o - guess)) if near else guess) - SUB_LEAD))
    return out


def _sentences(t: str) -> list[str]:
    import re
    return [x for x in re.split(r"(?<=[.?!…])\s+", t.strip()) if x.strip()]


def chunk_starts(scene: dict, project: dict, chunks: list[str], adur: float, audio_path: str | None = None) -> list[float]:
    """자막 조각 시작 시각: Whisper로 대략 위치를 잡고, 파형의 '쉼 뒤 말 시작'에 10ms 단위로 붙인다."""
    ons = speech_onsets(audio_path) if audio_path else []
    cap = scene.get("caption")
    if cap and cap != scene["text"]:
        cs, ts = _sentences(cap), _sentences(scene["text"])
        if len(cs) == len(ts) and len(ts) > 1:
            # 문장 대 문장으로 맞춘 뒤, 문장 안에서는 글자 수 비율
            tscene = dict(scene, caption=None)
            sstart = _snap(_chunk_estimates(tscene, project, ts, adur), ons) if ons else _chunk_estimates(tscene, project, ts, adur)
            bounds = sstart + [adur]
            import re
            norm = lambda x: re.sub(r"[^0-9A-Za-z가-힣]", "", x)
            sl = [len(norm(x)) for x in cs]
            send, acc = [], 0
            for L in sl:
                acc += L
                send.append(acc)
            out, pos = [], 0
            for ch_ in chunks:
                si = next(i for i, e in enumerate(send) if pos < e) if pos < send[-1] else len(cs) - 1
                s0 = send[si] - sl[si]
                frac = (pos - s0) / max(1, sl[si])
                out.append(bounds[si] + (bounds[si + 1] - bounds[si]) * frac)
                pos += len(norm(ch_))
            if len(out) == len(chunks):
                first = first_voice(audio_path) if audio_path else None
                if first is not None and first < 0.8:
                    out[0] = max(0.0, first - SUB_LEAD)
                return out
    est = _chunk_estimates(scene, project, chunks, adur)
    if not ons:
        return est
    out = _snap(est, ons) if len(chunks) > 1 else est
    if audio_path:
        first = first_voice(audio_path)
        if first is not None and first < 0.8:
            out[0] = max(0.0, first - SUB_LEAD)
    return out


def _chunk_estimates(scene: dict, project: dict, chunks: list[str], adur: float) -> list[float]:
    """자막 조각별 시작 시각(장면 음성 기준, 초).
    Whisper 단어 타임스탬프가 있으면 각 조각의 첫 단어가 실제로 들리는 순간에 맞추고,
    없으면 글자 수 비율로 나눈다."""
    import re
    norm = lambda x: re.sub(r"[^0-9A-Za-z가-힣]", "", x)
    lens = [max(1, len(norm(c))) for c in chunks]
    tot = sum(lens)
    fracs, acc = [], 0
    for L in lens:
        fracs.append(acc / tot)
        acc += L
    audio_dir = project.get("_audio_dir")
    al = align_info(scene, audio_dir) if audio_dir else None
    words = (al or {}).get("words") or []
    if not words:
        return [f * adur for f in fracs]
    if scene.get("caption") and norm(scene["caption"]) != norm(scene["text"]):  # 문장 수가 다를 때만 여기로
        sp_ = scene_speed(scene, project)
        cut_, _ = trim_window(scene, audio_dir)
        t0 = max(0.0, (words[0]["start"] - cut_) / sp_)
        t1 = min(adur, (words[-1]["end"] - cut_) / sp_)
        return [max(0.0, t0 + f * (t1 - t0) - SUB_LEAD) if k else 0.0 for k, f in enumerate(fracs)]
    sp = scene_speed(scene, project)
    cut, _ = trim_window(scene, audio_dir)
    wl = [max(1, len(norm(w["w"]))) for w in words]
    wt = sum(wl)
    if wt < 0.6 * tot:  # Whisper가 문장 일부를 놓침 → 실제 말소리 구간에 글자 수 비율로 배치 (이후 파형 쉼에 스냅)
        t0 = max(0.0, (al["speech_start"] - cut) / sp)
        t1 = min(adur, (al["speech_end"] - cut) / sp)
        return [max(0.0, t0 + f * (t1 - t0) - SUB_LEAD) if k else 0.0 for k, f in enumerate(fracs)]
    wbefore, acc = [], 0
    for L in wl:
        wbefore.append(acc / wt)
        acc += L
    wn = [norm(w["w"]) for w in words]
    # 숫자는 받아쓰기에서 한글로 나올 수 있으므로 비교용 키는 앞 두 글자(숫자면 숫자만)
    def key(tok: str) -> str:
        t = norm(tok)
        return t[:2] if t else ""
    out = []
    j_prev = 0
    for k, f in enumerate(fracs):
        if k == 0:
            t, j = words[0]["start"], 0
        else:
            est = min(range(len(words)), key=lambda j: abs(wbefore[j] - f))
            first = key(chunks[k].split()[0]) if chunks[k].split() else ""
            # 1순위: 추정 위치 ±3단어 안에서 첫 단어가 실제로 일치하는 단어 (순서 유지)
            cands = [j for j in range(max(j_prev + 1, est - 3), min(len(words), est + 4)) if first and wn[j].startswith(first)]
            j = min(cands, key=lambda j: abs(j - est)) if cands else max(est, j_prev + 1 if j_prev + 1 < len(words) else est)
            t = words[j]["start"]
        j_prev = j
        out.append(max(0.0, (t - cut) / sp - SUB_LEAD))
    out[0] = 0.0 if out[0] < 0.25 else out[0]
    for k in range(1, len(out)):  # 순서 보장 + 최소 노출 0.5초
        out[k] = max(out[k], out[k - 1] + 0.5)
    return [min(x, adur) for x in out]


def estimate_seconds(text, fmt):
    return max(1.2, len("".join(text.split())) / RATE[fmt] + 0.25)


def scene_speed(scene: dict, project: dict) -> float:
    fmt = project["format"]
    voice = scene.get("voice", "여의도남자")
    by = project.get("voice_speed_by", {"여의도남자": 1.08} if fmt == "long" else {})
    base = float(project.get("speed", 1.05 if fmt == "shorts" else 1.0))
    return base * float(by.get(voice, 1.0))


# 방송 톤 후처리 (연애 스튜디오 v1.1 방식): 저역 잡음 컷 → 따뜻함 → 또렷함 → 치찰음 완화 → 부드러운 압축
VOICE_CHAIN = ("highpass=f=70,equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3500:t=q:w=1.2:g=2,"
               "deesser=i=0.3,acompressor=threshold=-21dB:ratio=2.5:attack=8:release=120:makeup=2")
SUB_LEAD = 0.06  # 자막을 말소리보다 살짝 먼저 띄우면 사람 눈에는 '딱 맞게' 보인다


def align_info(scene: dict, audio_dir: str) -> dict | None:
    f = os.path.join(audio_dir, raw_name(scene)).replace(".wav", ".align.json")
    if os.path.exists(f):
        with open(f, encoding="utf-8") as fh:
            return json.load(fh)
    return None


def trim_window(scene: dict, audio_dir: str) -> tuple[float, float | None]:
    """원본 음성에서 앞뒤 무음을 뺀 구간 (초). 정렬 정보가 없으면 자르지 않음."""
    al = align_info(scene, audio_dir)
    if not al:
        return 0.0, None
    a = max(0.0, al["speech_start"] - 0.05)
    return a, al["speech_end"] + 0.12


def scene_audio(scene: dict, project: dict, audio_dir: str, preview_silent: bool) -> tuple[str, bool]:
    """앞뒤 무음 정리 + 방송 톤 후처리 + 속도 적용된 장면 음성 경로와 실제 목소리 여부."""
    os.makedirs(audio_dir, exist_ok=True)
    raw = os.path.join(audio_dir, raw_name(scene))
    if os.path.exists(raw):
        sp = scene_speed(scene, project)
        a, b = trim_window(scene, audio_dir)
        tag = f"_v2_{a:.2f}" if b is not None else "_v2"
        final = raw.replace(".wav", f"{tag}_x{sp:.3g}.wav")
        if not os.path.exists(final):
            trim = f"atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS," if b is not None else ""
            tempo = f",atempo={sp}" if abs(sp - 1) > 1e-3 else ""
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", trim + VOICE_CHAIN + tempo + ",aresample=48000", "-ac", "2", final], check=True)
        project.setdefault("_audio_dir", audio_dir)
        return final, True
    if not preview_silent:
        raise VoiceboxUnavailable(f"{scene['id']} 음성이 없습니다.")
    tmp = raw.replace(".wav", "_silent.wav")
    silent(tmp, estimate_seconds(scene["text"], project["format"]))
    return tmp, False
