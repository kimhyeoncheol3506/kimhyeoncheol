"""음성 더빙(TTS) + 음성인식(ASR) 검수.

백엔드
- edge   : Microsoft Edge 신경망 음성(ko-KR-InJoonNeural 등). 인터넷 필요, 가장 자연스러움.
- sherpa : 오프라인 VITS 한국어(KSS). 인터넷 없이 동작.
auto 는 edge 가 접속되면 edge, 아니면 sherpa.

모든 덩어리는 생성 직후 ASR 로 다시 받아적어 대본과 비교하고(CER),
틀리면 속도/문장부호를 바꿔 재생성해서 가장 정확한 것을 고른다.
"""
import asyncio
import os
import subprocess
import numpy as np
import soundfile as sf

from .textnorm import to_speech, cer
from .g2p import pronounce

MODEL_DIR = os.environ.get("FACETUBE_MODELS", os.path.expanduser("~/.cache/facetube/models"))
SR = 44100

_tts = None
_asr = None


def _sherpa_tts():
    global _tts
    if _tts is None:
        import sherpa_onnx
        d = os.path.join(MODEL_DIR, "vits-mimic3-ko_KO-kss_low") + "/"
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=d + "ko_KO-kss_low.onnx", tokens=d + "tokens.txt", data_dir=d + "espeak-ng-data"),
            num_threads=2))
        _tts = sherpa_onnx.OfflineTts(cfg)
    return _tts


def asr():
    global _asr
    if _asr is None:
        import sherpa_onnx
        d = os.path.join(MODEL_DIR, "sherpa-onnx-zipformer-korean-2024-06-24") + "/"
        _asr = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=d + "encoder-epoch-99-avg-1.int8.onnx", decoder=d + "decoder-epoch-99-avg-1.int8.onnx",
            joiner=d + "joiner-epoch-99-avg-1.int8.onnx", tokens=d + "tokens.txt", num_threads=4)
    return _asr


def transcribe(samples, sr):
    r = asr()
    x = np.asarray(samples, dtype=np.float32)
    if sr != 16000:
        x = np.interp(np.linspace(0, len(x) - 1, int(len(x) * 16000 / sr)), np.arange(len(x)), x).astype(np.float32)
    s = r.create_stream()
    s.accept_waveform(16000, x)
    r.decode_stream(s)
    return s.result.text


def _resample(x, sr_in, sr_out=SR):
    if sr_in == sr_out:
        return x.astype(np.float32)
    n = int(round(len(x) * sr_out / sr_in))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def _trim(x, thr=0.012, pad=0.03):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]


def _sherpa(text, speed):
    a = _sherpa_tts().generate(text, sid=0, speed=speed)
    x = np.array(a.samples, dtype=np.float32)
    x = _resample(x, a.sample_rate)
    # KSS 저음질 모델 보정: 살짝 밝게, 피크 정규화
    return x / (np.max(np.abs(x)) + 1e-6) * 0.89


def _edge(text, speed, voice):
    import edge_tts, tempfile
    rate = f"{int(round((speed - 1) * 100)):+d}%"
    tmp = tempfile.mktemp(suffix=".mp3")
    asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(tmp))
    wav = tmp + ".wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ac", "1", "-ar", str(SR), wav], check=True)
    x, _ = sf.read(wav, dtype="float32")
    os.remove(tmp), os.remove(wav)
    return x


def edge_available():
    try:
        import edge_tts  # noqa
        _edge("테스트", 1.0, "ko-KR-SunHiNeural")
        return True
    except Exception:
        return False


class Voice:
    def __init__(self, backend="auto", voice="ko-KR-InJoonNeural", speed=1.05, cer_retry=0.18, verify=True):
        if backend == "auto":
            backend = "edge" if edge_available() else "sherpa"
        self.backend, self.voice, self.speed = backend, voice, speed
        self.cer_retry, self.verify = cer_retry, verify

    def _gen(self, text, speed):
        if self.backend == "edge":
            return _edge(text, speed, self.voice)
        return _sherpa(text, speed)

    def say(self, display_text):
        """화면 문장 -> (오디오, 정보). 정보에는 ASR 결과와 CER, 시도 횟수가 들어간다."""
        spoken = to_speech(display_text)
        tts_text = spoken
        if self.backend == "sherpa":   # 오프라인 모델은 '?' 를 모름
            tts_text = spoken.replace("?", ".")
        variants = [(tts_text, self.speed)]
        if self.backend == "sherpa":   # 연음·비음화를 직접 적은 '소리 나는 대로' 표기 후보
            g = pronounce(tts_text)
            variants += [(g, self.speed), (g, self.speed * 0.9)]
            if tts_text.count(" ") >= 2:   # 첫 어절 뒤 숨 쉬기
                variants.append((g.replace(" ", ", ", 1), self.speed * 0.95))
        variants += [(tts_text, self.speed * 0.9), (tts_text, self.speed * 1.08)]
        best = None
        for i, (txt, sp) in enumerate(variants):
            x = _trim(self._gen(txt, sp))
            if not self.verify:
                return x, {"spoken": spoken, "asr": None, "cer": None, "tries": 1}
            hyp = transcribe(x, SR)
            e = cer(spoken, hyp)
            if best is None or e < best[2]:
                best = (x, hyp, e, i + 1)
            if e <= self.cer_retry:
                break
        x, hyp, e, tries = best
        return x, {"spoken": spoken, "asr": hyp, "cer": round(e, 3), "tries": tries}
