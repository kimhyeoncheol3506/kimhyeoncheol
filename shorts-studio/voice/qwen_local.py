"""여의도남자/여의도여자 음성 생성 — Voicebox와 같은 엔진(Qwen3-TTS)을 직접 구동.

Voicebox(PC)에 접근할 수 없는 클라우드/서버에서 쓰는 경로다. 설정은 yeouido-voice 스킬과 동일:
  - 여의도여자: CustomVoice 프리셋 Sohee + instruct
  - 여의도남자: 기준음성(assets/voices/여의도남자_기준음성.wav) 복제(Base 모델, ICL).
    기준음성이 없으면 VoiceDesign(seed 20261011)으로 만든 뒤 저장한다.
    → PC의 ~/.yeouido-voice/여의도남자_기준음성.wav 를 assets/voices/ 에 넣으면 PC와 완전히 같은 목소리가 된다.

사용: python voice/qwen_local.py projects/<프로젝트> [--models <모델폴더>] [--only s01,s02]
출력: projects/<프로젝트>/narration/sXX.wav + timings.json
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pronounce import fix as pron  # noqa: E402  발음 교정

ROOT = Path(__file__).resolve().parent.parent
VOICE_DIR = ROOT / "assets" / "voices"
MALE_REF = VOICE_DIR / "여의도남자_기준음성.wav"
REF_TEXT = ("안녕하십니까. 오늘의 경제 소식을 전해 드리겠습니다. 여의도 증권가는 이른 아침부터 분주한 하루를 시작했습니다. "
            "차분하게, 그리고 정확하게 시장의 흐름을 짚어 보겠습니다.")
MALE_DESIGN = ("A Korean man in his late 30s. Calm, trustworthy, warm baritone with a clear mid-low register. "
               "Crisp standard Seoul pronunciation, professional news-anchor and documentary narrator delivery, "
               "measured moderate pace, no accent, studio-quality clean recording.")
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
    a = max(0, idx[0] - int(pad * sr))
    b = min(len(wav), idx[-1] + int(pad * sr * 2))
    return wav[a:b]


def est_seconds(text):
    import re
    return len(re.sub(r"\s", "", text)) / 6.5 + 0.6


def gen_checked(fn, text, seed, tries=4):
    """폭주(끝없이 생성)·잘림 방지: 예상 길이 대비 이상하면 시드를 바꿔 재시도."""
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


def ensure_male_ref(models: Path):
    if MALE_REF.exists():
        return
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    print("[여의도남자] 기준음성 없음 → VoiceDesign(seed 20261011)으로 생성", flush=True)
    m = load(models / "design")
    torch.manual_seed(20261011)
    wavs, sr = m.generate_voice_design(text=REF_TEXT, instruct=MALE_DESIGN, language="Korean")
    sf.write(MALE_REF, trim(wavs[0], sr), sr)
    del m
    gc.collect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--models", default=os.environ.get("QWEN_TTS_MODELS", "models"))
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    proj = Path(a.project)
    models = Path(a.models)
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    out = proj / "narration"
    out.mkdir(exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    scenes = [s for s in script["scenes"] if not only or s["id"] in only]

    males = [s for s in scenes if s.get("voice", "여의도남자") == "여의도남자"]
    females = [s for s in scenes if s.get("voice") == "여의도여자"]

    if males:
        ensure_male_ref(models)
        m = load(models / "base")
        ref_wav, ref_sr = sf.read(MALE_REF)
        prompt = m.create_voice_clone_prompt(ref_audio=(ref_wav.astype(np.float32), ref_sr), ref_text=REF_TEXT)
        for s in males:
            t0 = time.time()
            w, sr = gen_checked(lambda **kw: m.generate_voice_clone(
                text=pron(s["say"]), language="Korean", voice_clone_prompt=prompt, **kw), pron(s["say"]), a.seed)
            sf.write(out / f"{s['id']}.wav", w, sr)
            print(f"[여의도남자] {s['id']} {time.time() - t0:.0f}s", flush=True)
        del m
        gc.collect()
    if females:
        m = load(models / "custom")
        for s in females:
            t0 = time.time()
            instruct = s.get("instruct") or FEMALE_DEFAULT_INSTRUCT
            w, sr = gen_checked(lambda **kw: m.generate_custom_voice(
                text=pron(s["say"]), speaker="Sohee", language="Korean", instruct=instruct, **kw), pron(s["say"]), a.seed)
            sf.write(out / f"{s['id']}.wav", w, sr)
            print(f"[여의도여자] {s['id']} {time.time() - t0:.0f}s", flush=True)
        del m
        gc.collect()

    # timings.json (Voicebox 플러그인과 같은 형식)
    rows, t = [], 0.0
    for s in script["scenes"]:
        f = out / f"{s['id']}.wav"
        if not f.exists():
            continue
        d = sf.info(f).duration
        rows.append({"id": s["id"], "voice": s.get("voice", "여의도남자"), "start": round(t, 3),
                     "end": round(t + d, 3), "duration": round(d, 3)})
        t += d
    (out / "timings.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("done", len(rows), "clips")


if __name__ == "__main__":
    sys.exit(main())
