#!/usr/bin/env python3
"""여의도여자(Qwen3-TTS CustomVoice · Sohee) 음성 생성기 — Voicebox 가 없는 곳(클라우드)용.

Voicebox(현철님 PC)의 '여의도여자' 프로필은 Qwen3-TTS-12Hz-1.7B-CustomVoice 의 Sohee 프리셋이다.
같은 모델·같은 프리셋을 이 컴퓨터에서 직접 돌려서 같은 목소리를 만든다(다른 TTS 로 바꾸는 것이 아님).
참고: 연애 튜토리얼 세션의 shorts-studio/voice/qwen_local.py (2026-11-03).

설치(1회, 약 10~15분):  bash tools/setup_qwen_tts.sh
facetube/voice.py 가 이 파일을 venv 파이썬으로 띄워 한 줄씩 주고받는다(모델은 한 번만 읽는다).
  입력  {"text": "...", "instruct": "...", "seed": 7, "out": "/tmp/x.wav", "est": 4.2}
  출력  {"ok": true, "out": "/tmp/x.wav", "sec": 4.1}  또는 {"ok": false, "error": "..."}
"""
import json
import os
import sys

import numpy as np
import soundfile as sf
import torch

MODEL = os.environ.get("QWEN_TTS_MODEL", os.path.expanduser("~/.cache/qwen-tts/models/custom"))
SPEAKER = os.environ.get("QWEN_TTS_SPEAKER", "Sohee")


def trim(w, sr, thr=0.01, pad=0.06):
    idx = np.where(np.abs(w) > thr)[0]
    if len(idx) == 0:
        return w
    return w[max(0, idx[0] - int(pad * sr)):min(len(w), idx[-1] + int(pad * sr * 2))]


def main():
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count() or 4)
    m = Qwen3TTSModel.from_pretrained(MODEL, dtype=torch.float32, device_map="cpu")
    print(json.dumps({"ok": True, "ready": True}), flush=True)
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            q = json.loads(line)
            est = float(q.get("est") or 4.0)
            best = None
            for k in range(3):                               # 끝없이 생성·잘림 방지: 예상 길이와 크게 다르면 시드를 바꿔 다시
                torch.manual_seed(int(q.get("seed", 7)) + k * 101)
                wavs, sr = m.generate_custom_voice(text=q["text"], speaker=SPEAKER, language="Korean",
                                                   instruct=q.get("instruct") or None, max_new_tokens=int(12 * (est * 2 + 3)))
                w = trim(np.asarray(wavs[0], dtype=np.float32), sr)
                ratio = (len(w) / sr) / est
                if best is None or abs(np.log(ratio)) < abs(np.log(best[2])):
                    best = (w, sr, ratio)
                if 0.6 <= ratio <= 1.6:
                    break
            sf.write(q["out"], best[0], best[1])
            print(json.dumps({"ok": True, "out": q["out"], "sec": round(len(best[0]) / best[1], 2)}), flush=True)
        except Exception as e:                                # 한 문장이 실패해도 일꾼은 계속 산다
            print(json.dumps({"ok": False, "error": repr(e)[:300]}), flush=True)


if __name__ == "__main__":
    main()
