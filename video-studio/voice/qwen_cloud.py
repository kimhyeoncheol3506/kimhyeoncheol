"""여의도남자/여의도여자 음성 생성 — Voicebox와 같은 엔진(Qwen3-TTS)을 클라우드에서 직접 구동.

yeouido-voice 규격과 동일:
  - 여의도남자: Base 모델 + 기준음성(assets/voices/여의도남자_기준음성.wav) 복제, seed 7
  - 여의도여자: CustomVoice 프리셋 Sohee + instruct (기본: 차분하고 또렷한 아나운서 톤)
(연애 튜토리얼 스튜디오 shorts-studio/voice/qwen_local.py와 같은 방식·같은 기준음성)

사용: <TTS_PYTHON> voice/qwen_cloud.py projects/<이름>/project.json --models <모델폴더>
출력: projects/<이름>/audio/<id>_<hash>.wav  (make_video.py가 이 파일을 그대로 사용)
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
from pronounce import fix as pron  # noqa: E402
from studio.keys import raw_name  # noqa: E402

MALE_REF = ROOT / "assets" / "voices" / "여의도남자_기준음성.wav"
REF_TEXT = ("안녕하십니까. 오늘의 경제 소식을 전해 드리겠습니다. 여의도 증권가는 이른 아침부터 분주한 하루를 시작했습니다. "
            "차분하게, 그리고 정확하게 시장의 흐름을 짚어 보겠습니다.")
FEMALE_DEFAULT_INSTRUCT = "차분하고 또렷한 아나운서 톤, 신뢰감 있게, 보통 속도"
SEED = 7
# v1.10.0 더빙 품질 (TTS 자연스러움 가이드 반영: 짧은 문장 단위 생성, 문장부호로 쉼 조절, 받아쓰기로 검수 후 다시 생성)
PAUSE = {".": 0.26, "?": 0.34, "!": 0.30, "…": 0.40}  # 문장 사이 쉼(초)
CER_OK = 0.08      # 받아쓰기 글자 오류율이 이 이하면 통과
MAX_TAKES = 3      # 문장당 최대 생성 횟수 (가장 정확한 것 선택)
_asr = None


def load(path):
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    return Qwen3TTSModel.from_pretrained(str(path), dtype=torch.float32, device_map="cpu")


def trim(wav, sr, thresh=0.01, pad=0.06):
    idx = np.where(np.abs(wav) > thresh)[0]
    if len(idx) == 0:
        return wav
    return wav[max(0, idx[0] - int(pad * sr)): min(len(wav), idx[-1] + int(pad * sr * 2))]


def est_seconds(text):
    return len(re.sub(r"\s", "", text)) / 6.0 + 0.6


def gen_checked(fn, text, seed, tries=4):
    """폭주·잘림 방지: 예상 길이 대비 비정상이면 시드를 바꿔 재시도하고 가장 정상에 가까운 결과를 쓴다."""
    est = est_seconds(text)
    best = None
    for k in range(tries):
        torch.manual_seed(seed + k * 101)
        wavs, sr = fn(max_new_tokens=int(12 * (est * 2.0 + 3)))
        w = trim(wavs[0], sr)
        ratio = (len(w) / sr) / est
        if best is None or abs(np.log(ratio)) < abs(np.log(best[2])):
            best = (w, sr, ratio)
        if 0.6 <= ratio <= 1.6:
            break
        print(f"   재시도 {k + 1}: 길이 비율 {ratio:.2f}", flush=True)
    return best[0], best[1]


def split_sentences(text):
    """한 장면 대사를 문장 단위로 나눈다 (긴 덩어리를 한 번에 읽히면 억양이 흐트러지고 오독이 늘어남)."""
    parts = re.split(r"(?<=[.?!…])\s+", text.strip())
    out = []
    for p in parts:
        if out and len(re.sub(r"\s", "", p)) < 6:  # '네.' 같은 아주 짧은 문장은 앞 문장에 붙여 자연스럽게
            out[-1] += " " + p
        else:
            out.append(p)
    return out


_MOVE = {1: 0, 4: 2, 7: 3, 8: 5, 16: 6, 17: 7, 19: 9, 22: 12, 23: 14, 24: 15, 25: 16, 26: 17}  # 받침 → 초성 (연음)


def liaison(t):
    """연음 규칙(받침 + 'ㅇ'으로 시작하는 음절)을 적용 — '연준은'은 [연주는]으로 들리는 게 정상이라 오류로 세지 않게."""
    cs = list(t)
    for i in range(len(cs) - 1):
        a, b = ord(cs[i]) - 0xAC00, ord(cs[i + 1]) - 0xAC00
        if 0 <= a < 11172 and 0 <= b < 11172 and b // 588 == 11:  # 다음 음절 초성 ㅇ
            fin = a % 28
            if fin == 27:  # ㅎ 받침은 탈락
                cs[i] = chr(0xAC00 + a - fin)
            elif fin in _MOVE:
                cs[i] = chr(0xAC00 + a - fin)
                cs[i + 1] = chr(0xAC00 + _MOVE[fin] * 588 + b % 588)
    return "".join(cs)


def _hangul(t):
    return liaison(re.sub(r"[^가-힣]", "", pron(t)))


def cer(ref, hyp):
    a, b = _hangul(ref), _hangul(hyp)
    if not a:
        return 0.0
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev, d[j] = d[j], cur
    return d[-1] / len(a)


def asr(w, sr):
    """받아쓰기 (대본 힌트 없이 — 들리는 그대로)."""
    global _asr
    if _asr is None:
        from faster_whisper import WhisperModel
        _asr = WhisperModel("small", device="cpu", compute_type="int8")
    import librosa
    x = librosa.resample(w.astype(np.float32), orig_sr=sr, target_sr=16000)
    segs, _ = _asr.transcribe(x, language="ko", beam_size=5)
    return " ".join(seg.text for seg in segs)


def nums(t):
    """숫자 덩어리 (쉼표 제거). 숫자 오독은 글자 오류율이 낮아도 치명적이라 따로 본다."""
    return re.findall(r"\d+(?:\.\d+)?", t.replace(",", ""))


def gen_sentence(fn, orig, text, seed):
    """길이 이상(폭주·잘림) 검사 + 받아쓰기로 숫자·글자 오류를 확인해 시드를 바꿔 다시 생성, 가장 정확한 테이크를 고른다."""
    best = None
    want = nums(orig)
    for k in range(MAX_TAKES):
        w, sr = gen_checked(fn, text, seed + k * 1009)
        try:
            hyp = asr(w, sr)
        except Exception as ex:  # 받아쓰기 실패 시 길이 검사만으로 통과
            print(f"   받아쓰기 생략: {ex}", flush=True)
            return w, sr
        got = re.sub(r"\D", "", hyp)  # 받아쓰기 숫자 모양이 달라도(4.5조/4조5천) 숫자열 포함 여부로 비교
        miss = sum(1 for n in want if n.replace(".", "") not in got)
        e = cer(text, hyp)
        score = (miss, e)
        if best is None or score < best[2]:
            best = (w, sr, score)
        if miss == 0 and e <= CER_OK:
            break
        print(f"   다시 생성 {k + 1}: 숫자 불일치 {miss}개, 오류율 {e:.2f}  [{hyp.strip()[:40]}]", flush=True)
    return best[0], best[1]


def gen_scene(fn_for, orig, seed):
    """문장마다 따로 생성해 문장부호에 맞는 쉼으로 잇는다 (원문 문장 → 발음 교정 → 생성)."""
    chunks, sr = [], 24000
    sents = split_sentences(orig)
    for i, o in enumerate(sents):
        t = pron(o)
        w, sr = gen_sentence(fn_for(t), o, t, seed + i)
        chunks.append(w)
        if i < len(sents) - 1:
            chunks.append(np.zeros(int(PAUSE.get(t.rstrip()[-1:], 0.24) * sr), dtype=w.dtype))
    return np.concatenate(chunks), sr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--models", default=os.environ.get("QWEN_TTS_MODELS", str(Path.home() / ".cache/yeouido-tts/models")))
    a = ap.parse_args()
    pj = Path(a.project)
    p = json.loads(pj.read_text(encoding="utf-8"))
    out = pj.parent / "audio"
    out.mkdir(exist_ok=True)
    todo = [s for s in p["scenes"] if not (out / raw_name(s)).exists()]
    males = [s for s in todo if s.get("voice", "여의도남자") == "여의도남자"]
    females = [s for s in todo if s.get("voice") == "여의도여자"]
    models = Path(a.models)
    if males:
        m = load(models / "base")
        ref, rsr = sf.read(MALE_REF)
        prompt = m.create_voice_clone_prompt(ref_audio=(ref.astype(np.float32), rsr), ref_text=REF_TEXT)
        for s in males:
            t0 = time.time()
            text = pron(s["text"])
            w, sr = gen_scene(lambda t: (lambda **kw: m.generate_voice_clone(text=t, language="Korean", voice_clone_prompt=prompt, **kw)), s["text"], SEED)
            sf.write(out / raw_name(s), w, sr)
            print(f"[여의도남자] {s['id']} {time.time() - t0:.0f}s  {text[:30]}", flush=True)
        del m
        gc.collect()
    if females:
        m = load(models / "custom")
        for s in females:
            t0 = time.time()
            text = pron(s["text"])
            ins = s.get("instruct") or FEMALE_DEFAULT_INSTRUCT
            w, sr = gen_scene(lambda t: (lambda **kw: m.generate_custom_voice(text=t, speaker="Sohee", language="Korean", instruct=ins, **kw)), s["text"], SEED)
            sf.write(out / raw_name(s), w, sr)
            print(f"[여의도여자] {s['id']} {time.time() - t0:.0f}s  {text[:30]}", flush=True)
        del m
        gc.collect()
    print(f"완료: 새로 생성 {len(todo)}개 (캐시 재사용 {len(p['scenes']) - len(todo)}개)")


if __name__ == "__main__":
    main()
