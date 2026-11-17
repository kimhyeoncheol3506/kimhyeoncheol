"""장면 다시 녹음 (최종 검수에서 두 음성인식이 같은 곳을 틀리게 들은 장면만).
사용: QWEN_TTS_HOME=~/.cache/yeouido-tts python3 tools/rerecord.py projects/<slug>.yaml "<대사 일부>" ["<대사 일부>" ...] [--tries 4]
- 대사 일부(say 안의 글자)로 장면을 찾아, 빌드와 같은 캐시 키 자리(_work/tts/<key>.wav/.json)에 새 녹음을 덮어쓴다.
- 여러 번 녹음해서, 빌드 음성인식 CER + Whisper(숫자 표기 정규화) CER 합이 가장 낮은 것을 고른다.
- 그 뒤 make_editorial 을 다시 돌리면 이 녹음으로 영상이 다시 만들어진다."""
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "editorial"))
sys.path.insert(0, str(ROOT / "shorts"))
from facetube import audio as A, textnorm  # noqa: E402
from facetube.build import load_style  # noqa: E402
from facetube.textnorm import to_speech, cer  # noqa: E402
from facetube.voice import Voice, PROSODY  # noqa: E402
import make_editorial as ME  # noqa: E402

K = lambda s: re.sub(r"[^가-힣a-zA-Z0-9]", "", s)


def norm_heard(h):
    h = re.sub(r"(\d)\s*([.,])\s*(\d)", r"\1\2\3", h)
    h = re.sub(r"(\d)\s*%", r"\1%", h)
    return to_speech(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("needles", nargs="+")
    ap.add_argument("--tries", type=int, default=4)
    a = ap.parse_args()
    st = load_style()
    proj = yaml.safe_load(open(a.project, encoding="utf-8"))
    ME.apply_style(st, proj)
    textnorm.SAY_AS.update(proj.get("say_as") or {})
    proj["slug"] = proj.get("slug") or Path(a.project).stem
    proj["_dir"] = str(Path(a.project).resolve().parent)
    proj["beats"] = proj["scenes"]
    ME.autocorrect(proj, lambda m: None)
    work = ROOT / "output" / proj["slug"] / "_work"
    vc = {**st["editorial"]["voice"], **proj.get("voice", {})}
    voice = Voice(backend=vc["backend"], voice=vc.get("name"), speed=vc.get("speed", 1.0),
                  cer_retry=st["qc"]["asr_cer_retry"], instruct=vc.get("instruct"))
    base_ins = voice.instruct
    from faster_whisper import WhisperModel
    import scipy.signal as S
    wm = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)

    def wcer(x, spoken):
        y = S.resample_poly(x, 16000, A.SR).astype("float32")
        segs, _ = wm.transcribe(y, language="ko", beam_size=5, vad_filter=False, condition_on_previous_text=False)
        h = " ".join(s.text.strip() for s in segs)
        return cer(K(spoken), K(norm_heard(h))), h

    for nd in a.needles:
        hits = [sc for sc in proj["scenes"] if nd in sc["say"]]
        if len(hits) != 1:
            print(f"!! '{nd}' 장면 {len(hits)}개 — 건너뜀")
            continue
        sc = hits[0]
        voice.instruct = sc.get("instruct") or base_ins
        ik = f"|{voice.instruct}" if sc.get("instruct") else ""
        units = [sc["say"].strip()] if voice.backend == "voicebox" else ME.sentences(sc["say"])
        for unit in units:
            pv = json.dumps(PROSODY, sort_keys=True) if voice.backend == "voicebox" else ""
            key = hashlib.md5(f"{voice.backend}|{voice.voice}|{voice.speed}|{pv}|{unit}|{to_speech(unit)}{ik}".encode()).hexdigest()[:16]
            wav, meta = work / "tts" / (key + ".wav"), work / "tts" / (key + ".json")
            cands = []
            if wav.exists() and meta.exists():
                x0, _ = sf.read(wav, dtype="float32")
                i0 = json.load(open(meta, encoding="utf-8"))
                w0, h0 = wcer(x0, i0["spoken"])
                cands.append((float(i0.get("cer") or 0) + w0, x0, i0, h0, "기존"))
                print(f"  기존 {key}: 빌드 {i0.get('cer')} / Whisper {w0:.3f} 「{h0}」", flush=True)
            for t in range(a.tries):
                voice.seed_base = 101 + 37 * t                 # 같은 시드면 똑같은 녹음이 나온다
                x, info = voice.say(unit)
                w, h = wcer(x, info["spoken"])
                sc_ = float(info.get("cer") or 0) + w
                print(f"  새 녹음 {t + 1}: 빌드 {info.get('cer')} 「{info.get('asr')}」 / Whisper {w:.3f} 「{h}」", flush=True)
                cands.append((sc_, x, info, h, f"새{t + 1}"))
                if info.get("cer", 1) <= 0.03 and w <= 0.03:
                    break
            best = min(cands, key=lambda c: c[0])
            # 기존이 이기면 그대로 둔다
            if best[4] != "기존":
                sf.write(wav, best[1], A.SR)
                json.dump({**best[2], "rerecorded": True, "whisper": best[3]}, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"→ '{nd}' 채택: {best[4]} (점수 {best[0]:.3f})", flush=True)


if __name__ == "__main__":
    main()
