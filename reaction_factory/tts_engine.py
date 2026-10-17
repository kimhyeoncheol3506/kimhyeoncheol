"""4단계(음성): 나레이션 → mp3. 공급자 교체형 인터페이스.

지원: edge(무료·키 불필요) / elevenlabs / typecast / clova / silent(테스트용 무음)
세그먼트별로 따로 합성해서 정확한 길이를 재고, 그 길이로 편집 타임라인을 만든다.
단어 타이밍을 주는 공급자(edge, elevenlabs)는 자막 싱크가 더 정확해진다.
"""
from __future__ import annotations

import asyncio
import base64
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from pathlib import Path

import requests

from config import AUDIO_DIR, settings
from script_generator import VideoScript
from utils import console, media_duration, run_ffmpeg, save_json

SEGMENT_PAD = 0.25  # 나레이션 세그먼트 사이 숨 고르기(초)


@dataclass
class Word:
    start: float
    end: float
    text: str


@dataclass
class TTSResult:
    path: Path
    duration: float
    words: list[Word] = field(default_factory=list)


class TTSProvider(ABC):
    name = "base"

    @abstractmethod
    def synthesize(self, text: str, out: Path) -> TTSResult: ...


# ─────────────────────────── Edge TTS (무료) ───────────────────────────
class EdgeTTS(TTSProvider):
    name = "edge"

    def __init__(self, voice: str, rate: str):
        self.voice, self.rate = voice, rate

    def synthesize(self, text: str, out: Path) -> TTSResult:
        return asyncio.run(self._run(text, out))

    async def _run(self, text: str, out: Path) -> TTSResult:
        import edge_tts

        comm = edge_tts.Communicate(text, self.voice, rate=self.rate, boundary="WordBoundary")
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

    def synthesize(self, text: str, out: Path) -> TTSResult:
        if not (settings.elevenlabs_api_key and settings.elevenlabs_voice_id):
            raise RuntimeError("ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID 를 .env 에 넣어 주세요.")
        r = requests.post(
            self.URL.format(voice=settings.elevenlabs_voice_id),
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": settings.elevenlabs_api_key},
            json={"text": text, "model_id": settings.elevenlabs_model,
                  "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3}},
            timeout=120,
        )
        r.raise_for_status()
        data = r.json()
        out.write_bytes(base64.b64decode(data["audio_base64"]))
        return TTSResult(out, media_duration(out), _chars_to_words(data.get("alignment") or {}))


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

    def synthesize(self, text: str, out: Path) -> TTSResult:
        if not (settings.typecast_api_key and settings.typecast_voice_id):
            raise RuntimeError("TYPECAST_API_KEY / TYPECAST_VOICE_ID 를 .env 에 넣어 주세요.")
        r = requests.post(
            self.URL,
            headers={"X-API-KEY": settings.typecast_api_key, "Content-Type": "application/json"},
            json={"voice_id": settings.typecast_voice_id, "text": text, "model": settings.typecast_model,
                  "language": "kor", "prompt": {"emotion_preset": "normal", "emotion_intensity": 1.0},
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

    def synthesize(self, text: str, out: Path) -> TTSResult:
        if not (settings.clova_client_id and settings.clova_client_secret):
            raise RuntimeError("CLOVA_CLIENT_ID / CLOVA_CLIENT_SECRET 를 .env 에 넣어 주세요.")
        r = requests.post(
            self.URL,
            headers={"X-NCP-APIGW-API-KEY-ID": settings.clova_client_id,
                     "X-NCP-APIGW-API-KEY": settings.clova_client_secret},
            data={"speaker": settings.clova_speaker, "text": text[:2000], "format": "mp3",
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

    def synthesize(self, text: str, out: Path) -> TTSResult:
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
#  대본 전체 → 세그먼트별 음성 + 타임라인
# ════════════════════════════════════════════════════════════════
@dataclass
class TimelineItem:
    index: int
    type: str                 # narration | original
    start: float              # 최종 영상에서의 시작 시각
    duration: float
    audio: str | None         # 나레이션 mp3 (original 이면 None)
    words: list[dict]
    segment: dict             # 원본 Segment 데이터


def build_voice_track(script: VideoScript, run_id: str, provider: TTSProvider | None = None) -> tuple[list[TimelineItem], Path]:
    provider = provider or get_provider()
    folder = AUDIO_DIR / run_id / script.format
    folder.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold]TTS[/] {provider.name} · {script.format} · {len(script.segments)}개 세그먼트")

    timeline: list[TimelineItem] = []
    t = 0.0
    for i, seg in enumerate(script.segments):
        if seg.type == "narration":
            out = folder / f"seg_{i:03d}.mp3"
            res = _synthesize_with_retry(provider, seg.narration, out)
            dur = res.duration + SEGMENT_PAD
            item = TimelineItem(i, "narration", t, dur, str(out), [asdict(w) for w in res.words], seg.model_dump())
        else:
            dur = max(1.0, seg.clip_end - seg.clip_start)
            item = TimelineItem(i, "original", t, dur, None, [], seg.model_dump())
        timeline.append(item)
        t += dur

    narration_mix = folder / "narration_full.mp3"
    _mix_narration(timeline, t, narration_mix)
    path = save_json(folder / "timeline.json", {"total": t, "items": [asdict(x) for x in timeline]})
    console.print(f"[green]✔ 음성 완료[/] 총 {t:.1f}초 → {narration_mix}")
    return timeline, path


def _synthesize_with_retry(provider: TTSProvider, text: str, out: Path, tries: int = 3) -> TTSResult:
    last: Exception | None = None
    for n in range(tries):
        try:
            return provider.synthesize(text, out)
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
