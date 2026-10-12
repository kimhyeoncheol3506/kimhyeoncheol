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
            w, sr = gen_checked(lambda **kw: m.generate_voice_clone(text=text, language="Korean", voice_clone_prompt=prompt, **kw), text, SEED)
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
            w, sr = gen_checked(lambda **kw: m.generate_custom_voice(text=text, speaker="Sohee", language="Korean", instruct=ins, **kw), text, SEED)
            sf.write(out / raw_name(s), w, sr)
            print(f"[여의도여자] {s['id']} {time.time() - t0:.0f}s  {text[:30]}", flush=True)
        del m
        gc.collect()
    print(f"완료: 새로 생성 {len(todo)}개 (캐시 재사용 {len(p['scenes']) - len(todo)}개)")


if __name__ == "__main__":
    main()
