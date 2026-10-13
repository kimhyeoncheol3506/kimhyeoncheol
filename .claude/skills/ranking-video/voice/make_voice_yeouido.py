"""여의도남자/여의도여자 음성을 클라우드에서 직접 생성 (ranking-video v2.2.0)

PC의 Voicebox 없이 같은 엔진(Qwen3-TTS)을 직접 돌린다. 방식은 연애 쇼츠 스튜디오(shorts-studio/voice/qwen_local.py)와 같다.
  - 여의도남자: assets/여의도남자_기준음성.wav 복제(Base 모델) → PC Voicebox와 같은 목소리
  - 여의도여자: CustomVoice 프리셋 Sohee + instruct

준비(새 세션에서 1회, 10~15분): bash voice/setup_cloud.sh  (남자만 쓸 땐 Base 모델만 있으면 된다)
사용:
  $TTS_PYTHON voice/make_voice_yeouido.py <대본데이터.json> <tts폴더> [--models ~/.cache/shorts-tts/models] [--voice 여의도남자] [--speed 1.0] [--only 00_00,01_02]
출력: <tts폴더>/{섹션:02d}_{문장:02d}.wav (렌더러와 check_tts.py가 그대로 읽는다)

- 대본 문장은 voice/pronounce.py로 '읽는 글'로 바꿔 넣는다(숫자·약어·자모 교정 + lexicon.json 누적 대체어).
- 폭주(끝없이 생성)·누락 방지: 예상 길이의 0.6~1.6배를 벗어나면 시드를 바꿔 최대 4번 다시 만든다.
- --speed: 말 속도 배율(ffmpeg atempo, 음높이 유지). 랭킹 영상은 초당 약 6음절이 목표다.
"""
from __future__ import annotations

import argparse, gc, json, os, re, subprocess, sys, time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pronounce import fix as pron  # noqa: E402

MALE_REF = HERE / "assets" / "여의도남자_기준음성.wav"
REF_TEXT = ("안녕하십니까. 오늘의 경제 소식을 전해 드리겠습니다. 여의도 증권가는 이른 아침부터 분주한 하루를 시작했습니다. "
            "차분하게, 그리고 정확하게 시장의 흐름을 짚어 보겠습니다.")
FEMALE_INSTRUCT = "밝고 또렷한 아나운서 톤, 신뢰감 있게, 약간 빠른 속도"


def load(path):
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    return Qwen3TTSModel.from_pretrained(str(path), dtype=torch.float32, device_map="cpu")


def trim(wav, sr, thresh=0.01, pad=0.05):
    idx = np.where(np.abs(wav) > thresh)[0]
    if len(idx) == 0: return wav
    return wav[max(0, idx[0] - int(pad * sr)): min(len(wav), idx[-1] + int(pad * sr * 2))]


def est_seconds(text):
    return len(re.sub(r"\s", "", text)) / 6.5 + 0.6


def gen_checked(fn, text, seed, tries=4):
    est = est_seconds(text); best = None
    for k in range(tries):
        torch.manual_seed(seed + k * 101)
        wavs, sr = fn(max_new_tokens=int(12 * (est * 2.0 + 3)))
        w = trim(wavs[0], sr); ratio = (len(w) / sr) / est
        if best is None or abs(np.log(ratio)) < abs(np.log(best[2])): best = (w, sr, ratio)
        if 0.6 <= ratio <= 1.6: break
        print(f"   재시도 {k + 1}: 길이 비율 {ratio:.2f}", flush=True)
    return best[0], best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data"); ap.add_argument("out")
    ap.add_argument("--models", default=os.environ.get("QWEN_TTS_MODELS", os.path.expanduser("~/.cache/shorts-tts/models")))
    ap.add_argument("--voice", default="여의도남자", choices=["여의도남자", "여의도여자"])
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    D = json.load(open(a.data, encoding="utf-8")); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    jobs = [(f"{si:02d}_{ti:02d}", x[0]) for si, s in enumerate(D["sections"]) for ti, x in enumerate(s["sentences"])]
    jobs = [j for j in jobs if (not only or j[0] in only) and (only or not (out / f"{j[0]}.wav").exists())]
    print(f"{a.voice}: {len(jobs)}문장 생성", flush=True)
    if not jobs: return
    if a.voice == "여의도남자":
        m = load(Path(a.models) / "base")
        ref_wav, ref_sr = sf.read(MALE_REF)
        prompt = m.create_voice_clone_prompt(ref_audio=(ref_wav.astype(np.float32), ref_sr), ref_text=REF_TEXT)
        gen = lambda t: (lambda **kw: m.generate_voice_clone(text=t, language="Korean", voice_clone_prompt=prompt, **kw))
    else:
        m = load(Path(a.models) / "custom")
        gen = lambda t: (lambda **kw: m.generate_custom_voice(text=t, speaker="Sohee", language="Korean", instruct=FEMALE_INSTRUCT, **kw))
    for k, (jid, text) in enumerate(jobs, 1):
        t0 = time.time(); say = pron(text)
        w, sr = gen_checked(gen(say), say, a.seed)
        f = out / f"{jid}.wav"
        if abs(a.speed - 1.0) > 1e-3:
            tmp = out / f"{jid}.raw.wav"; sf.write(tmp, w, sr)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-filter:a", f"atempo={a.speed}", str(f)], check=True); tmp.unlink()
        else:
            sf.write(f, w, sr)
        print(f"[{k}/{len(jobs)}] {jid} {time.time() - t0:.0f}s  {text[:24]}", flush=True)
    del m; gc.collect()


if __name__ == "__main__":
    main()
