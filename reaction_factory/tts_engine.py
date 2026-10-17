"""4단계(음성): 나레이션 → mp3. 공급자 교체형 인터페이스.

지원: edge(무료·키 불필요) / elevenlabs / typecast / clova / silent(테스트용 무음)
- 무음 제거: 앞뒤 무음 삭제 + 문장 사이 긴 쉼 압축 → 말 템포가 빨라지고 이탈이 줄어든다
- 캐릭터 목소리: 해설자와 등장인물(더빙)에 서로 다른 목소리를 자동 배정
세그먼트별로 따로 합성해서 정확한 길이를 재고, 그 길이로 편집 타임라인을 만든다.
단어 타이밍을 주는 공급자(edge, elevenlabs)는 자막 싱크가 더 정확해진다.
"""
from __future__ import annotations

import asyncio
import base64
import os
import re
import subprocess
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import requests

from config import AUDIO_DIR, ffmpeg_bin, settings
from script_generator import VideoScript
from speech_text import to_speech
from utils import console, media_duration, run_ffmpeg, save_json

SEGMENT_PAD = 0.25  # 나레이션 세그먼트 사이 숨 고르기(초)


@dataclass
class Word:
    start: float
    end: float
    text: str


@dataclass
class Voice:
    """목소리 지정. id 는 공급자별 보이스 ID(edge 는 보이스 이름), rate/pitch 는 edge 전용 미세조정."""
    id: str = ""
    rate: str = ""
    pitch: str = "+0Hz"
    label: str = ""
    emotion: str = "neutral"


@dataclass
class TTSResult:
    path: Path
    duration: float
    words: list[Word] = field(default_factory=list)


class TTSProvider(ABC):
    name = "base"

    @abstractmethod
    def synthesize(self, text: str, out: Path, voice: Voice | None = None) -> TTSResult: ...


# ─────────────────────────── Edge TTS (무료) ───────────────────────────
class EdgeTTS(TTSProvider):
    name = "edge"

    def __init__(self, voice: str, rate: str):
        self.voice, self.rate = voice, rate

    def synthesize(self, text: str, out: Path, voice: Voice | None = None) -> TTSResult:
        return asyncio.run(self._run(text, out, voice or Voice()))

    async def _run(self, text: str, out: Path, voice: Voice) -> TTSResult:
        import edge_tts

        comm = edge_tts.Communicate(text, voice.id or self.voice, rate=voice.rate or self.rate,
                                    pitch=voice.pitch or "+0Hz", boundary="WordBoundary")
        words: list[Word] = []
        with open(out, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                    start = chunk["offset"] / 1e7  # 100ns 단위
                    words.append(Word(start, start + chunk["duration"] / 1e7, chunk["text"]))
        return TTSResult(out, media_duration(out), words)


# ─────────────────────────── ElevenLabs ───────────────────────────
class ElevenLabsTTS(TTSProvider):
    name = "elevenlabs"
    URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps"

    def synthesize(self, text: str, out: Path, voice: Voice | None = None) -> TTSResult:
        if not (settings.elevenlabs_api_key and settings.elevenlabs_voice_id):
            raise RuntimeError("ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID 를 .env 에 넣어 주세요.")
        r = requests.post(
            self.URL.format(voice=(voice and voice.id) or settings.elevenlabs_voice_id),
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": settings.elevenlabs_api_key},
            json={"text": text, "model_id": settings.elevenlabs_model,
                  "voice_settings": ELEVEN_EMOTION.get((voice and voice.emotion) or "neutral", ELEVEN_EMOTION["neutral"])},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        out.write_bytes(base64.b64decode(data["audio_base64"]))
        return TTSResult(out, media_duration(out), _chars_to_words(data.get("alignment") or {}))


# 감정별 안정성/스타일: 흥분할수록 stability 를 낮춰 억양 폭을 키운다
ELEVEN_EMOTION = {
    "neutral": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3},
    "excited": {"stability": 0.3, "similarity_boost": 0.8, "style": 0.65},
    "surprised": {"stability": 0.28, "similarity_boost": 0.8, "style": 0.7},
    "funny": {"stability": 0.32, "similarity_boost": 0.8, "style": 0.6},
    "curious": {"stability": 0.4, "similarity_boost": 0.8, "style": 0.45},
    "calm": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.15},
    "sad": {"stability": 0.55, "similarity_boost": 0.8, "style": 0.35},
}
TYPECAST_EMOTION = {"excited": "happy", "surprised": "happy", "funny": "happy", "sad": "sad"}


def _chars_to_words(al: dict) -> list[Word]:
    chars = al.get("characters") or []
    starts = al.get("character_start_times_seconds") or []
    ends = al.get("character_end_times_seconds") or []
    words, buf, ws, prev_end = [], "", None, 0.0
    for ch, s, e in zip(chars, starts, ends):
        if ch.isspace():
            if buf:
                words.append(Word(ws, prev_end, buf))
            buf, ws = "", None
            continue
        if ws is None:
            ws = s
        buf += ch
        prev_end = e
    if buf:
        words.append(Word(ws, prev_end, buf))
    return words


# ─────────────────────────── Typecast ───────────────────────────
class TypecastTTS(TTSProvider):
    """Typecast API v1 (https://typecast.ai/developers). 보이스 ID 는 콘솔의 'API' 메뉴에서 확인."""

    name = "typecast"
    URL = "https://api.typecast.ai/v1/text-to-speech"

    def synthesize(self, text: str, out: Path, voice: Voice | None = None) -> TTSResult:
        if not (settings.typecast_api_key and settings.typecast_voice_id):
            raise RuntimeError("TYPECAST_API_KEY / TYPECAST_VOICE_ID 를 .env 에 넣어 주세요.")
        r = requests.post(
            self.URL,
            headers={"X-API-KEY": settings.typecast_api_key, "Content-Type": "application/json"},
            json={"voice_id": (voice and voice.id) or settings.typecast_voice_id, "text": text, "model": settings.typecast_model,
                  "language": "kor", "prompt": {"emotion_preset": TYPECAST_EMOTION.get((voice and voice.emotion) or "", "normal"),
                             "emotion_intensity": 1.2 if (voice and voice.emotion in TYPECAST_EMOTION) else 1.0},
                  "output": {"audio_format": "mp3", "audio_tempo": 1.05}},
            timeout=120,
        )
        r.raise_for_status()
        out.write_bytes(r.content)
        return TTSResult(out, media_duration(out))


# ─────────────────────────── 네이버 CLOVA Voice ───────────────────────────
class ClovaTTS(TTSProvider):
    """NCP CLOVA Voice Premium. 화자 목록: nara, nminsang, njinho, nsinu, vdain 등."""

    name = "clova"
    URL = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"

    def synthesize(self, text: str, out: Path, voice: Voice | None = None) -> TTSResult:
        if not (settings.clova_client_id and settings.clova_client_secret):
            raise RuntimeError("CLOVA_CLIENT_ID / CLOVA_CLIENT_SECRET 를 .env 에 넣어 주세요.")
        r = requests.post(
            self.URL,
            headers={"X-NCP-APIGW-API-KEY-ID": settings.clova_client_id,
                     "X-NCP-APIGW-API-KEY": settings.clova_client_secret},
            data={"speaker": (voice and voice.id) or settings.clova_speaker, "text": text[:2000], "format": "mp3",
                  "speed": "-1", "volume": "0", "pitch": "0"},
            timeout=120,
        )
        r.raise_for_status()
        out.write_bytes(r.content)
        return TTSResult(out, media_duration(out))


# ─────────────────────────── 테스트용 무음 ───────────────────────────
class SilentTTS(TTSProvider):
    """키·네트워크 없이 파이프라인을 시험할 때. 글자 수로 길이를 추정한 무음 mp3."""

    name = "silent"

    def synthesize(self, text: str, out: Path, voice: Voice | None = None) -> TTSResult:
        dur = max(1.5, len(text.replace(" ", "")) * 0.14)
        run_ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{dur:.2f}",
                    "-c:a", "libmp3lame", "-b:a", "128k", out])
        return TTSResult(out, media_duration(out))


def get_provider(name: str | None = None) -> TTSProvider:
    name = (name or settings.tts_provider).lower()
    if name == "edge":
        return EdgeTTS(settings.edge_voice, settings.edge_rate)
    providers = {"elevenlabs": ElevenLabsTTS, "typecast": TypecastTTS, "clova": ClovaTTS, "silent": SilentTTS}
    if name not in providers:
        raise ValueError(f"알 수 없는 TTS_PROVIDER: {name} (edge|elevenlabs|typecast|clova|silent)")
    return providers[name]()


# ════════════════════════════════════════════════════════════════
#  캐릭터별 목소리 배정
# ════════════════════════════════════════════════════════════════
# edge 한국어 보이스는 3종뿐이라 피치/속도로 인물을 구분한다
EDGE_POOLS = {
    "male": [("ko-KR-HyunsuMultilingualNeural", "+0Hz", "+5%"), ("ko-KR-InJoonNeural", "-8Hz", "+0%"),
             ("ko-KR-HyunsuMultilingualNeural", "-10Hz", "-3%")],
    "female": [("ko-KR-SunHiNeural", "+0Hz", "+5%"), ("ko-KR-SunHiNeural", "+14Hz", "+8%"),
               ("ko-KR-SunHiNeural", "-8Hz", "+0%")],
}
AGE_TWEAK = {"child": ("+28Hz", "+10%"), "senior": ("-14Hz", "-8%")}


def cast_voices(characters: list[dict], provider_name: str | None = None) -> dict[str, Voice]:
    """등장인물마다 서로 다른 목소리를 배정. 해설자(narrator)와 겹치지 않게 한다."""
    name = (provider_name or settings.tts_provider).lower()
    cast: dict[str, Voice] = {"narrator": Voice(label="해설자")}
    used = {"male": 0, "female": 0}
    for ch in characters:
        g = ch.get("gender", "male")
        if name == "edge":
            pool = [v for v in EDGE_POOLS[g] if not (v[0] == settings.edge_voice and v[1] == "+0Hz")]
            vid, pitch, rate = pool[used[g] % len(pool)]
            if ch.get("age") in AGE_TWEAK:
                pitch, rate = AGE_TWEAK[ch["age"]]
            cast[ch["name"]] = Voice(vid, rate, pitch, label=f"{ch['name']} ({vid.split('-')[2]} {pitch})")
        else:
            ids = [x.strip() for x in os.getenv(f"CHARACTER_VOICES_{g.upper()}", "").split(",") if x.strip()]
            vid = ids[used[g] % len(ids)] if ids else ""
            cast[ch["name"]] = Voice(vid, label=f"{ch['name']} ({vid or '기본 보이스'})")
        used[g] += 1
    return cast


# ════════════════════════════════════════════════════════════════
#  무음 제거: 앞뒤 무음 삭제 + 문장 사이 긴 쉼을 MAX_PAUSE 로 압축 (단어 타이밍도 함께 보정)
# ════════════════════════════════════════════════════════════════
def detect_silences(path: Path, threshold_db: float, min_len: float) -> list[tuple[float, float]]:
    proc = subprocess.run(
        [ffmpeg_bin(), "-hide_banner", "-i", str(path), "-af",
         f"silencedetect=noise={threshold_db}dB:d={min_len}", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", proc.stderr)]
    total = media_duration(path)
    ends += [total] * (len(starts) - len(ends))      # 끝까지 이어진 무음
    return [(max(0.0, a), b) for a, b in zip(starts, ends)]


def compress_silence(res: TTSResult, max_pause: float, threshold_db: float = -50.0) -> tuple[TTSResult, float]:
    total = res.duration
    removed: list[tuple[float, float]] = []
    for a, b in detect_silences(res.path, threshold_db, 0.12):
        if a <= 0.01:                                 # 앞 무음: 0.05초만 남김
            if b - a > 0.08:
                removed.append((a, b - 0.05))
        elif b >= total - 0.01:                       # 뒤 무음: 말끝('~요') 잔향 0.15초는 남김
            if b - a > 0.2:
                removed.append((a + 0.15, b))
        elif b - a > max_pause:                       # 문장 사이 쉼 압축
            keep = max_pause / 2
            removed.append((a + keep, b - keep))
    cut = sum(b - a for a, b in removed)
    if cut < 0.05:
        return res, 0.0

    keeps, t = [], 0.0
    for a, b in removed:
        if a > t:
            keeps.append((t, a))
        t = b
    if t < total:
        keeps.append((t, total))
    tmp = res.path.with_suffix(".trim.mp3")
    chains = [f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[k{i}]" for i, (a, b) in enumerate(keeps)]
    graph = ";".join(chains) + ";" + "".join(f"[k{i}]" for i in range(len(keeps))) + f"concat=n={len(keeps)}:v=0:a=1[out]"
    run_ffmpeg(["-i", res.path, "-filter_complex", graph, "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", tmp])
    tmp.replace(res.path)

    def remap(x: float) -> float:
        shift = 0.0
        for a, b in removed:
            if x >= b:
                shift += b - a
            elif x > a:                               # 잘린 구간 안 → 잘린 시작점으로
                shift += x - a
        return max(0.0, x - shift)

    words = [Word(remap(w.start), max(remap(w.end), remap(w.start) + 0.05), w.text) for w in res.words]
    return TTSResult(res.path, media_duration(res.path), words), cut


# ════════════════════════════════════════════════════════════════
#  억양 살리기: 문장별 합성 + 감정/문장 유형에 따른 속도·피치 변화 (edge)
#  AI 음성 티의 주원인인 '모든 문장이 같은 속도·같은 높이'를 깬다.
# ════════════════════════════════════════════════════════════════
EMOTION_PROSODY = {  # (속도 %, 피치 Hz)
    "neutral": (0, 0), "excited": (10, 6), "surprised": (6, 10), "funny": (8, 4),
    "curious": (-2, 4), "calm": (-6, -3), "sad": (-10, -6),
}
SENTENCE_GAP = 0.14  # 문장 사이 숨 (무음 압축 후에도 이 정도는 남는다)


def _pct(v: str) -> int:
    return int(re.sub(r"[^\d\-+]", "", v or "0") or 0)


def split_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
    return parts or [text]


def synth_expressive(provider: TTSProvider, text: str, out: Path, voice: Voice) -> TTSResult:
    # 다른 공급자는 감정 파라미터(ElevenLabs style, Typecast emotion_preset)로 한 번에 처리
    if provider.name != "edge" or (len(split_sentences(text)) == 1 and voice.emotion == "neutral"):
        return provider.synthesize(text, out, voice)
    base_rate, base_pitch = _pct(voice.rate or settings.edge_rate), _pct(voice.pitch)
    e_rate, e_pitch = EMOTION_PROSODY.get(voice.emotion, (0, 0))
    parts, words, t = [], [], 0.0
    for k, sentence in enumerate(split_sentences(text)):
        rate, pitch = base_rate + e_rate, base_pitch + e_pitch
        if sentence.endswith("?"):
            pitch += 4                                   # 질문은 살짝 높게
        elif sentence.endswith("!"):
            rate, pitch = rate + 4, pitch + 3            # 감탄은 빠르고 높게
        rate += (2, -1, 1)[k % 3]                        # 문장마다 미세하게 템포를 바꿔 '기계 박자' 제거
        v = Voice(voice.id, f"{rate:+d}%", f"{pitch:+d}Hz", voice.label, voice.emotion)
        part = out.with_name(f"{out.stem}_s{k}.mp3")
        res = provider.synthesize(sentence, part, v)
        parts.append(part)
        words += [Word(w.start + t, w.end + t, w.text) for w in res.words]
        t += res.duration + SENTENCE_GAP
    if len(parts) == 1:
        parts[0].replace(out)
    else:
        args: list = []
        for p in parts:
            args += ["-i", p]
        gap = f"aevalsrc=0:d={SENTENCE_GAP}:s=24000"
        chains = "".join(f"[{i}:a]aresample=24000,aformat=channel_layouts=mono[p{i}];" for i in range(len(parts)))
        seq = "".join(f"[p{i}][g{i}]" if i < len(parts) - 1 else f"[p{i}]" for i in range(len(parts)))
        gaps = "".join(f"{gap}[g{i}];" for i in range(len(parts) - 1))
        n = len(parts) * 2 - 1
        run_ffmpeg(args + ["-filter_complex", f"{chains}{gaps}{seq}concat=n={n}:v=0:a=1[out]",
                           "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", out])
        for p in parts:
            p.unlink(missing_ok=True)
    return TTSResult(out, media_duration(out), words)


def normalize_loudness(res: TTSResult, target: float = -16.0) -> TTSResult:
    """목소리마다 음량이 들쭉날쭉하면 어색하다 → 세그먼트별로 같은 크기(LUFS)로 맞춘다."""
    tmp = res.path.with_suffix(".norm.mp3")
    run_ffmpeg(["-i", res.path, "-af", f"highpass=f=70,loudnorm=I={target}:TP=-2:LRA=7,aresample=44100",
                "-c:a", "libmp3lame", "-b:a", "192k", tmp])
    tmp.replace(res.path)
    return TTSResult(res.path, media_duration(res.path), res.words)


def fit_duration(res: TTSResult, target: float, max_speed: float = 1.18) -> tuple[TTSResult, float]:
    """더빙이 원본 인물의 발화보다 길면 입 모양과 따로 논다 → 최대 1.18배까지만 자연스럽게 당긴다."""
    if target <= 0 or res.duration <= target * 1.05:
        return res, 1.0
    factor = min(res.duration / target, max_speed)
    tmp = res.path.with_suffix(".fit.mp3")
    run_ffmpeg(["-i", res.path, "-af", f"atempo={factor:.3f}", "-c:a", "libmp3lame", "-b:a", "192k", tmp])
    tmp.replace(res.path)
    words = [Word(w.start / factor, w.end / factor, w.text) for w in res.words]
    return TTSResult(res.path, media_duration(res.path), words), factor


# ════════════════════════════════════════════════════════════════
#  대본 전체 → 세그먼트별 음성 + 타임라인
# ════════════════════════════════════════════════════════════════
@dataclass
class TimelineItem:
    index: int
    type: str                 # narration | original | dub
    start: float              # 최종 영상에서의 시작 시각
    duration: float
    audio: str | None         # TTS mp3 (original 이면 None)
    words: list[dict]
    segment: dict             # 원본 Segment 데이터


def build_voice_track(script: VideoScript, run_id: str, provider: TTSProvider | None = None,
                      characters: list[dict] | None = None) -> tuple[list[TimelineItem], Path]:
    provider = provider or get_provider()
    folder = AUDIO_DIR / run_id / script.format
    folder.mkdir(parents=True, exist_ok=True)
    cast = cast_voices(characters or [], provider.name)
    console.print(f"[bold]TTS[/] {provider.name} · {script.format} · {len(script.segments)}개 세그먼트"
                  + (f" · 캐릭터 목소리 {len(cast) - 1}명" if len(cast) > 1 else ""))

    timeline: list[TimelineItem] = []
    t, silence_cut, speech = 0.0, 0.0, 0.0
    qa: list[dict] = []
    for i, seg in enumerate(script.segments):
        if seg.type in ("narration", "dub"):
            out = folder / f"seg_{i:03d}.mp3"
            voice = cast.get(seg.speaker if seg.type == "dub" else "narrator")
            if voice is None:                         # 대본에 없는 인물 → 그 자리에서 배정
                voice = cast_voices([{"name": seg.speaker, "gender": "male", "age": "adult"}], provider.name)[seg.speaker]
                cast[seg.speaker] = voice
            spoken, unknown = to_speech(seg.narration)       # 자막 표기 → 실제 읽기
            for w in unknown:
                qa.append({"index": i, "issue": f"영어 '{w}' 를 한글 발음으로 못 바꿈 (data/pronunciation.json 에 추가 권장)"})
            voice = replace(voice, emotion=getattr(seg, "emotion", "neutral"))
            res = _synthesize_with_retry(provider, spoken, out, voice)
            if settings.silence_remove:
                res, cut = compress_silence(res, settings.max_pause)
                silence_cut += cut
            res = normalize_loudness(res)
            if seg.type == "dub":
                res, factor = fit_duration(res, seg.clip_end - seg.clip_start)
                if res.duration > (seg.clip_end - seg.clip_start) * 1.3:
                    qa.append({"index": i, "issue": f"더빙({res.duration:.1f}s)이 원본 발화({seg.clip_end - seg.clip_start:.1f}s)보다 많이 김 — 대사를 줄이세요"})
            speech += res.duration
            dur = res.duration + SEGMENT_PAD
            item = TimelineItem(i, seg.type, t, dur, str(out), [asdict(w) for w in res.words],
                                {**seg.model_dump(), "spoken": spoken})
        else:
            dur = max(1.0, seg.clip_end - seg.clip_start)
            item = TimelineItem(i, "original", t, dur, None, [], seg.model_dump())
        timeline.append(item)
        t += dur

    narration_mix = folder / "narration_full.mp3"
    _mix_narration(timeline, t, narration_mix)
    first = next((x for x in timeline if x.audio), None)
    first_line = 0.0
    if first:  # 첫 음성 세그먼트의 '첫 문장'이 차지하는 시간(글자 수 비례)
        text = first.segment["narration"].strip()
        sentence = re.split(r"(?<=[.!?…])\s+", text)[0]
        first_line = (first.duration - SEGMENT_PAD) * len(sentence) / max(len(text), 1)
    stats = {
        "total": round(t, 1), "speech": round(speech, 1), "silence_removed": round(silence_cut, 1),
        "first_line": round(first_line, 1),
        "first_line_starts_at": round(first.start, 1) if first else 0,
        "voices": {k: v.label or v.id for k, v in cast.items()},
        "voice_warnings": len(qa),
    }
    path = save_json(folder / "timeline.json", {"total": t, "stats": stats, "qa": qa, "items": [asdict(x) for x in timeline]})
    for q in qa:
        console.print(f"  [yellow]⚠ 목소리 검수 컷 {q['index'] + 1}: {q['issue']}[/]")
    console.print(f"[green]✔ 음성 완료[/] 총 {t:.1f}초 (음성 {speech:.1f}초 · 무음 제거 {silence_cut:.1f}초) → {narration_mix}")
    return timeline, path


def _synthesize_with_retry(provider: TTSProvider, text: str, out: Path, voice: Voice | None = None,
                           tries: int = 3) -> TTSResult:
    last: Exception | None = None
    for n in range(tries):
        try:
            return synth_expressive(provider, text, out, voice or Voice())
        except Exception as exc:  # 네트워크 일시 오류 대비
            last = exc
            console.print(f"[yellow]TTS 재시도 {n + 1}/{tries}: {exc}[/]")
    raise RuntimeError(f"TTS 실패: {last}")


def _mix_narration(timeline: list[TimelineItem], total: float, out: Path) -> None:
    """세그먼트 mp3 들을 타임라인 위치에 배치한 전체 나레이션 트랙(검수/재사용용)."""
    items = [x for x in timeline if x.audio]
    if not items:
        run_ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{total:.2f}", out])
        return
    args: list = []
    for x in items:
        args += ["-i", x.audio]
    chains = [f"[{k}:a]adelay={int(x.start * 1000)}:all=1[a{k}]" for k, x in enumerate(items)]
    mix = "".join(f"[a{k}]" for k in range(len(items)))
    graph = ";".join(chains) + f";{mix}amix=inputs={len(items)}:normalize=0,apad,atrim=0:{total:.3f}[out]"
    run_ffmpeg(args + ["-filter_complex", graph, "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", out])
