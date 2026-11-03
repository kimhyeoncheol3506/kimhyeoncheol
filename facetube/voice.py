"""음성 더빙(TTS) + 음성인식(ASR) 검수.

백엔드
- edge   : Microsoft Edge 신경망 음성(기본 ko-KR-HyunsuMultilingualNeural, 현철님 선택). 인터넷 필요, 가장 자연스러움.
- sherpa : 오프라인 VITS 한국어(KSS). 인터넷 없이 동작.
- voicebox: 현철님 PC의 Voicebox(Qwen3-TTS) '여의도남자'/'여의도여자'. 서버는 VOICEBOX_URL(기본 http://127.0.0.1:17493).
            PC에서만 돈다. 닿지 않으면 다른 목소리로 바꾸지 않고 멈춘다(에디토리얼 롱폼은 여의도여자 전용).
auto 는 edge 가 접속되면 edge, 아니면 sherpa.

모든 덩어리는 생성 직후 ASR 로 다시 받아적어 대본과 비교하고(CER),
틀리면 속도/문장부호를 바꿔 재생성해서 가장 정확한 것을 고른다.
"""
import asyncio
import os
import subprocess
import numpy as np
import soundfile as sf

from .textnorm import to_speech, cer, phrase_breaks
from .g2p import pronounce, tense_hints
from .pron_dict import pron_hints
from . import pron_learn

MODEL_DIR = os.environ.get("FACETUBE_MODELS", os.path.expanduser("~/.cache/facetube/models"))
SR = 44100
DEFAULT_VOICE = "ko-KR-HyunsuMultilingualNeural"   # 현수(남성) — 채널 기본 목소리

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
    # 클라우드 환경처럼 프록시 뒤에 있으면 프록시와 그 인증서를 쓴다
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy and os.path.exists("/root/.ccr/ca-bundle.crt"):
        os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
    for k in range(3):                    # 서버가 가끔 빈 응답(NoAudioReceived)을 준다: 잠깐 쉬고 다시
        try:
            asyncio.run(edge_tts.Communicate(text, voice, rate=rate, proxy=proxy).save(tmp))
            break
        except edge_tts.exceptions.NoAudioReceived:
            if k == 2:
                raise
            import time
            time.sleep(2 * (k + 1))
    wav = tmp + ".wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ac", "1", "-ar", str(SR), wav], check=True)
    x, _ = sf.read(wav, dtype="float32")
    os.remove(tmp), os.remove(wav)
    return x


VOICEBOX_URL = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")
LAST_PROFILE = None
VOICEBOX_INSTRUCT = {"여의도여자": ("차분하고 또렷한 뉴스 아나운서 톤, 신뢰감 있게, 보통 속도. 쉼표에서 짧게 끊어 읽고 문장 끝은 자연스럽게 내려 닫는다. "
                                 "숫자와 핵심 낱말은 또박또박 조금 힘주어 읽는다. 높낮이를 살려 단조롭지 않게, 기계처럼 일정하게 읽지 않는다.")}
# 아나운서 운율 목표(voice_ref/announcer_profile.yaml 이 있으면 그 값). 기본값은 ElevenLabs 한국어 아나운서 미리듣기 3개 실측(2026-11-02)
PROSODY = {"pause_comma_s": 0.32, "pause_sentence_s": 0.6, "breaks": True, "tense": True, "pron": True, "learn": True}
try:
    import yaml as _yaml
    _pf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voice_ref", "announcer_profile.yaml")
    if os.path.exists(_pf):
        PROSODY.update({k: v for k, v in (_yaml.safe_load(open(_pf, encoding="utf-8")).get("apply") or {}).items() if v is not None})
except Exception:
    pass


def retime_pauses(x, comma=0.32, sentence=0.6, thr_db=-38, min_run=0.12):
    """생성된 음성 안의 쉼을 아나운서 목표 길이로 맞춘다. 짧은 쉼(<0.45s)=쉼표급, 긴 쉼=문장급.
    목표와 40% 넘게 다를 때만 쉼의 가운데를 잘라내거나 무음을 끼워 넣는다(앞뒤 숨소리는 남김)."""
    h = int(0.01 * SR)
    e = np.array([10 * np.log10(np.mean(x[i:i + h] ** 2) + 1e-12) for i in range(0, len(x) - h, h)])
    loud = np.percentile(e, 95)
    rms = np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) for i in range(0, len(x) - h, h)])
    sil = e < loud + thr_db
    if np.percentile(rms, 95) > 0.05:                  # 목소리가 충분히 클 때만: 검수(qc.narration_gaps)의 '조용함' 기준(RMS 0.008)도 쉼으로 본다(숨소리 꼬리)
        sil |= rms < 0.008
    out, last, i = [], 0, 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]:
                j += 1
            L = (j - i) * 0.01
            if L >= min_run and i > 0 and j < len(sil):
                tgt = comma if L < 0.45 else sentence
                if abs(L - tgt) > 0.4 * tgt:
                    mid = (i + j) // 2 * h
                    out.append(x[last:mid])
                    d = int((tgt - L) * SR)
                    if d > 0:
                        out.append(np.zeros(d, np.float32))
                    last = mid + (-d if d < 0 else 0)
            i = j
        else:
            i += 1
    out.append(x[last:])
    return np.concatenate(out).astype(np.float32)


def _vb(path, body=None, raw=False, timeout=600):
    import json, urllib.request
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))     # PC 안 서버: 프록시를 거치지 않는다
    req = urllib.request.Request(VOICEBOX_URL + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with op.open(req, timeout=timeout) as r:
        data = r.read()
    return data if raw else json.loads(data)


def _voicebox(text, speed, profile, seed=7, instruct=None):
    import io, time
    try:
        profs = _vb("/profiles", timeout=10)
    except Exception as e:
        raise SystemExit(f"Voicebox({VOICEBOX_URL})에 닿지 않음: {e}\n"
                         "현철님 PC에서 Voicebox 앱을 켜고, 이 저장소를 PC에서 실행해 주세요(다른 목소리로 대체하지 않음).")
    profs = profs.get("profiles", profs) if isinstance(profs, dict) else profs
    names = profile if isinstance(profile, (list, tuple)) else [profile]      # 여러 개면 Voicebox 에 있는 것 중 앞의 것(예: [여의도여자, 엠마])
    p = next((x for n in names for x in profs if x.get("name") == n), None)
    if not p:
        raise SystemExit(f"Voicebox 에 {' / '.join(names)} 프로필이 없음 (yeouido-voice 스킬의 프로필 재생성 절차)")
    profile = p["name"]
    global LAST_PROFILE
    LAST_PROFILE = profile                                   # 실제로 쓴 프로필(발음 학습 기록에 목소리별로 남김)
    eng = p.get("default_engine") or ("qwen_custom_voice" if profile == "여의도여자" else "qwen")
    body = {"profile_id": p["id"], "text": text, "language": "ko", "model_size": "1.7B", "engine": eng, "seed": seed}
    ins = instruct or VOICEBOX_INSTRUCT.get(profile) or VOICEBOX_INSTRUCT.get("여의도여자")
    if ins and eng == "qwen_custom_voice":
        body["instruct"] = ins
    gid = _vb("/generate", body)["id"]
    for _ in range(900):
        h = _vb(f"/history/{gid}", timeout=30)
        if h.get("status") == "completed":
            break
        if h.get("status") == "failed":
            raise RuntimeError(f"Voicebox 생성 실패: {h.get('error')}")
        time.sleep(2)
    x, sr = sf.read(io.BytesIO(_vb(f"/audio/{gid}", raw=True)), dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = _resample(x, sr)
    if abs(speed - 1.0) > 0.01:                       # 속도는 음높이를 지키며 ffmpeg atempo 로
        import tempfile
        a, b = tempfile.mktemp(suffix=".wav"), tempfile.mktemp(suffix=".wav")
        sf.write(a, x, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-filter:a", f"atempo={speed}", b], check=True)
        x, _ = sf.read(b, dtype="float32")
        os.remove(a), os.remove(b)
    return x


def edge_available():
    try:
        import edge_tts  # noqa
        _edge("테스트", 1.0, DEFAULT_VOICE)
        return True
    except Exception:
        return False


class Voice:
    def __init__(self, backend="auto", voice=None, speed=1.05, cer_retry=0.18, verify=True, instruct=None):
        if backend == "auto":
            backend = "edge" if edge_available() else "sherpa"
        if backend == "voicebox" and not voice:
            voice = "여의도남자"
        self.backend, self.voice, self.speed = backend, voice or DEFAULT_VOICE, speed
        self.cer_retry, self.verify, self.instruct = cer_retry, verify, instruct
        self._try = 0
        if backend == "voicebox" and PROSODY.get("learn"):     # 지난 생성에서 틀린 낱말을 사전에 반영(발음사전 학습)
            try:
                pron_learn.update()
            except Exception as e:  # 학습 실패로 생성이 멈추면 안 됨
                print(f"[발음학습] 건너뜀: {e}")

    def _gen(self, text, speed):
        if self.backend == "voicebox":                # 다시 만들 때는 시드를 바꿔 다른 읽기를 받는다
            self._try += 1
            return _voicebox(text, speed, self.voice, seed=7 + self._try - 1, instruct=self.instruct)
        if self.backend == "edge":
            return _edge(text, speed, self.voice)
        return _sherpa(text, speed)

    def say(self, display_text):
        """화면 문장 -> (오디오, 정보). 정보에는 ASR 결과와 CER, 시도 횟수가 들어간다."""
        spoken = to_speech(display_text)
        tts_text = spoken
        self._try = 0
        if self.backend == "voicebox" and PROSODY.get("breaks"):      # 아나운서식 끊어 읽기(자막은 그대로)
            tts_text = to_speech(phrase_breaks(display_text))
        if self.backend == "voicebox" and PROSODY.get("pron"):        # 발음 사전(ㄴ첨가·비음화·유음화 + 학습한 낱말)
            tts_text = pron_hints(tts_text)
        if self.backend == "voicebox" and PROSODY.get("tense"):       # 철자에 안 보이는 된소리(할 수→할 쑤, 주가→주까)
            tts_text = tense_hints(tts_text)
        if self.backend == "sherpa":   # 오프라인 모델은 '?' 를 모름
            tts_text = spoken.replace("?", ".")
        variants = [(tts_text, self.speed)]
        if self.backend == "sherpa":   # 연음·비음화를 직접 적은 '소리 나는 대로' 표기 후보
            g = pronounce(tts_text)
            variants += [(g, self.speed), (g, self.speed * 0.9)]
            if tts_text.count(" ") >= 2:   # 첫 어절 뒤 숨 쉬기
                variants.append((g.replace(" ", ", ", 1), self.speed * 0.95))
        variants += [(tts_text, self.speed * 0.9), (tts_text, self.speed * 1.08)]
        best, fixed = None, False
        i = -1
        while i + 1 < len(variants):
            i += 1
            txt, sp = variants[i]
            x = _trim(self._gen(txt, sp), pad=0.08 if self.backend == "voicebox" else 0.03)
            if self.backend == "voicebox":
                x = retime_pauses(x, PROSODY["pause_comma_s"], PROSODY["pause_sentence_s"])
            if not self.verify:
                return x, {"spoken": spoken, "asr": None, "cer": None, "tries": 1}
            hyp = transcribe(x, SR)
            e = cer(spoken, hyp)
            if best is None or e < best[2]:
                best = (x, hyp, e, i + 1)
            if e <= self.cer_retry:
                break
            if self.backend == "voicebox" and not fixed:            # 틀린 낱말만 소리 나는 대로 고쳐 한 번 더
                fixed = True
                fix = txt
                for it in pron_learn.misread_words(spoken, hyp):
                    cand = pron_learn.suggest(it["word"])
                    if cand and it["word"] in fix:
                        fix = fix.replace(it["word"], cand)
                if fix != txt:
                    variants.insert(i + 1, (fix, sp))
        x, hyp, e, tries = best
        if self.backend == "voicebox" and PROSODY.get("learn") and e > 0:
            try:
                pron_learn.log_misreads(pron_learn.misread_words(spoken, hyp), LAST_PROFILE if self.backend == "voicebox" else self.voice, spoken)
            except Exception as ex:
                print(f"[발음학습] 기록 건너뜀: {ex}")
        return x, {"spoken": spoken, "asr": hyp, "cer": round(e, 3), "tries": tries}
