"""한국어 발음 테스트 채점 — 여의도남자/여의도여자 녹음을 받아쓰기·억양·쉼으로 자동 평가.

사용: <TTS_PYTHON> tests/korean-pron/evaluate.py tests/korean-pron/male.json [female.json ...]
출력: tests/korean-pron/결과_<목소리>.md, 듣기용 mp3 (테스트별)
- 받아쓰기 오류율: 대본과 받아쓰기를 모두 발음 교정·연음 처리 후 글자 단위 비교 (Whisper 한계로 0%가 아니어도 정상일 수 있음)
- 억양: 문장 끝 0.5초 음높이 기울기 (의문문은 올라가야, 평서문은 내려가야 정상)
- 쉼: 쉼표·문장 사이 0.12초 이상 무음 개수
"""
import json
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "voice"))
from studio.keys import raw_name  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("qc", ROOT / "voice" / "qwen_cloud.py")
qc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qc)

NAMES = {"T1": "연음·받침", "T2": "된소리·거센소리", "T3": "띄어읽기·호흡", "T4": "띄어쓰기 의미", "T5": "숫자·영문",
         "T6": "억양·감정", "T7": "빠른 발음", "W": "단어표"}


def pitch_slope(w, sr):
    tail = w[-int(0.7 * sr):]
    f0, vf, _ = librosa.pyin(tail, fmin=70, fmax=400, sr=sr, frame_length=1024)
    f = f0[vf] if vf is not None else np.array([])
    f = f[~np.isnan(f)]
    if len(f) < 6:
        return None
    half = len(f) // 2
    return float(np.median(f[half:]) / np.median(f[:half]) - 1)  # +면 올라감


def pauses(w, sr, min_s=0.12):
    rms = librosa.feature.rms(y=w, frame_length=512, hop_length=256)[0]
    quiet = rms < max(0.01, rms.max() * 0.04)
    n, run = 0, 0
    for q in quiet[5:-5]:
        run = run + 1 if q else 0
        if run == int(min_s * sr / 256):
            n += 1
    return n


def main():
    asr = WhisperModel("small", device="cpu", compute_type="int8")
    for pj in map(Path, sys.argv[1:]):
        p = json.loads(pj.read_text(encoding="utf-8"))
        voice = p["scenes"][0].get("voice", "여의도남자")
        rows, groups = [], {}
        for s in p["scenes"]:
            f = pj.parent / "audio" / raw_name(s)
            if not f.exists():
                continue
            w, sr = sf.read(f, dtype="float32")
            x = librosa.resample(w, orig_sr=sr, target_sr=16000)
            hyp = " ".join(seg.text.strip() for seg in asr.transcribe(x, language="ko", beam_size=5)[0])
            e = qc.cer(s["text"], hyp)
            sl = pitch_slope(w, sr)
            g = s["id"].split("_")[0]
            groups.setdefault(g, []).append((w, sr))
            rows.append((g, s["text"], hyp, e, sl, pauses(w, sr), s["text"].count(",") + sum(s["text"].count(c) for c in ".?!") - 1))
        out = [f"# 한국어 발음 테스트 결과 — {voice}\n", "| 테스트 | 문장 수 | 평균 오류율 | 오류율 10% 넘는 문장 |", "|---|---|---|---|"]
        for g in NAMES:
            r = [x for x in rows if x[0] == g]
            if r:
                out.append(f"| {NAMES[g]} | {len(r)} | {np.mean([x[3] for x in r]) * 100:.1f}% | {sum(x[3] > 0.10 for x in r)} |")
        out.append(f"\n**전체 평균 오류율 {np.mean([x[3] for x in rows]) * 100:.1f}%** (Whisper 받아쓰기 기준 — 표준 발음 차이 일부 포함)\n")
        out.append("## 억양 (문장 끝 음높이 변화, +면 올라감)\n\n| 문장 | 끝 음높이 | 판정 |\n|---|---|---|")
        for g, t, hyp, e, sl, pz, want in rows:
            if g == "T6" or t.rstrip().endswith("?"):
                q = t.rstrip().endswith("?")
                ok = None if sl is None else (sl > 0.02 if q else sl < 0.03)
                out.append(f"| {t} | {'-' if sl is None else f'{sl * 100:+.0f}%'} | {'?' if ok is None else ('정상' if ok else '확인 필요')} |")
        out.append("\n## 문장별 받아쓰기\n\n| 테스트 | 대본 | 받아쓰기 | 오류율 | 쉼(실제/부호) |\n|---|---|---|---|---|")
        for g, t, hyp, e, sl, pz, want in rows:
            out.append(f"| {NAMES[g]} | {t} | {hyp} | {e * 100:.0f}% | {pz}/{max(0, want)} |")
        tag = pj.stem
        (pj.parent / f"결과_{tag}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
        for g, items in groups.items():  # 듣기용: 테스트별로 이어 붙이기
            sr = items[0][1]
            gap = np.zeros(int(0.6 * sr), dtype=np.float32)
            wav = np.concatenate([np.concatenate([w, gap]) for w, _ in items])
            tmp = pj.parent / f"_{tag}_{g}.wav"
            sf.write(tmp, wav, sr)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp), "-b:a", "128k",
                            str(pj.parent / f"듣기_{voice}_{g}_{NAMES[g].replace('·', '')}.mp3")], check=True)
            tmp.unlink()
        print(f"{voice}: 결과_{tag}.md")


if __name__ == "__main__":
    main()
