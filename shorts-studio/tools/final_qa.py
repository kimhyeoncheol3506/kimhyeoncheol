"""최종 검수: 완성 mp4를 다시 받아써서 '현철님이 검수 없이 바로 올려도 되는지' 확인한다.

  <tts-python> tools/final_qa.py projects/<프로젝트>
검사 항목 (하나라도 FAIL이면 고치고 다시 렌더)
  1) 장면 싱크  : 장면 시간 창 안에서 들린 말 ↔ 대본 일치율 (BGM·효과음 섞인 상태 기준 0.75↑)
  2) 시작 어긋남: 장면 첫 단어가 화면 전환(자막 등장)보다 0.6초 넘게 늦거나 0.3초 넘게 이르면 FAIL
  3) 말더듬/반복: 같은 음절 3연속
  4) 긴 무음    : 말 사이 2.5초 넘는 공백 (표지·의도된 pause 제외)
  5) 자막 노출  : 자막 한 덩어리가 0.5초 미만으로 스쳐 지나가면 FAIL
  6) 음량       : 통합 음량 -15.5 ~ -12.5 LUFS
  7) 길이       : 쇼츠 20~60초 (장편 쇼츠 long_short 90~180초), 롱폼 180~420초
결과: output/<프로젝트>/final_qa.json, 종료코드 0=통과 1=불합격
"""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "voice"))

from pronounce import fix as pron  # noqa: E402
from qa import load16k, norm  # noqa: E402


def loudness(mp4: Path) -> float:
    out = subprocess.run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", out)
    return float(m[-1]) if m else 0.0


_wm = None


def energy_onset(audio, t0: float, t1: float, sr=16000) -> float | None:
    """[t0, t1] 구간에서 목소리 대역(300~3400Hz) 에너지가 처음 확 올라가는 시각.
    Whisper는 무음 뒤 첫 단어 시작을 앞 단어 끝에 붙여 찍는 버릇이 있어 이걸로 다시 잰다."""
    import numpy as np
    a, b = max(0, int(t0 * sr)), min(len(audio), int(t1 * sr))
    x = audio[a:b]
    if len(x) < sr // 5:
        return None
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    X[(f < 300) | (f > 3400)] = 0
    y = np.fft.irfft(X, len(x))
    hop = sr // 100
    rms = np.array([np.sqrt(np.mean(y[i:i + hop] ** 2)) for i in range(0, len(y) - hop, hop)])
    if not len(rms):
        return None
    floor = np.percentile(rms, 10)
    peak = np.percentile(rms, 95)
    thr = floor + (peak - floor) * 0.25
    # 직전 장면 말소리 꼬리를 피하려고 '조용한 구간을 지난 뒤' 처음 넘는 지점
    quiet = np.where(rms < floor + (peak - floor) * 0.1)[0]
    start = quiet[0] if len(quiet) else 0
    hit = np.where(rms[start:] > thr)[0]
    return t0 + (start + hit[0]) * hop / sr if len(hit) else None


def main():
    proj = Path(sys.argv[1]).resolve()
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    if script["format"] == "short":
        from studio.short import load
        r = load(proj)
    else:
        from studio.long import LongRenderer
        r = LongRenderer(proj)
    out_dir = ROOT / "output" / proj.name
    mp4 = out_dir / "video.mp4"
    fails, warns, rows = [], [], []

    # 7) 길이
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(mp4)], capture_output=True, text=True).stdout.strip())
    lo, hi = (20, 66) if script["format"] == "short" else (180, 420)  # 쇼츠 본편 60초 + 마지막 구독·좋아요 멘트
    if script["format"] == "short" and script.get("long_short"):  # 여러 장 사연 장편 쇼츠: 2~3분 (쇼츠 상한 180초)
        lo, hi = (90, 180)
    if not lo <= dur <= hi:
        fails.append(f"길이 {dur:.1f}s (기준 {lo}~{hi}s)")
    # 6) 음량
    lufs = loudness(mp4)
    if not -15.5 <= lufs <= -12.5:
        fails.append(f"음량 {lufs:.1f} LUFS (기준 -14±1.5)")

    # 받아쓰기 (단어 시간 포함)
    cache = out_dir / "final_qa_words.json"
    if cache.exists() and cache.stat().st_mtime > mp4.stat().st_mtime:
        words = [tuple(w) for w in json.loads(cache.read_text(encoding="utf-8"))]
    else:
        words = None
    with tempfile.TemporaryDirectory() as td:
      wav = Path(td) / "a.wav"
      subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-ac", "1", "-ar", "16000", str(wav)])
      audio = load16k(wav)
      if words is None:
        from faster_whisper import WhisperModel
        m = WhisperModel("medium", device="cpu", compute_type="int8")
        segs, _ = m.transcribe(audio, language="ko", beam_size=5, word_timestamps=True,
                               vad_filter=True)
        words = [(w.start, w.end, w.word) for s in segs for w in (s.words or [])]
        cache.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")

    prev_end = 0.0
    for s in r.scenes:
        # 단어 '시작' 기준 창 (앞 장면 끝 단어가 섞이지 않게). Whisper 단어 시각은 0.1~0.3초 이르게 찍히는 경향
        win = [w for w in words if s.voice_start - 0.35 <= w[0] < s.voice_end + 0.2]
        heard = "".join(w[2] for w in win)
        ratio = max(difflib.SequenceMatcher(None, norm(x), norm(heard)).ratio() for x in (s.data["say"], pron(s.data["say"])))
        row = {"id": s.id, "ratio": round(ratio, 2), "heard": heard.strip()}
        if ratio < 0.75:  # 전체 받아쓰기의 VAD가 구간을 통째로 놓치는 경우 → 장면만 잘라 VAD 없이 재확인
            global _wm
            if _wm is None:
                from faster_whisper import WhisperModel
                _wm = WhisperModel("medium", device="cpu", compute_type="int8")
            a, b = int(max(0, s.voice_start - 0.2) * 16000), int((s.voice_end + 0.2) * 16000)
            segs, _ = _wm.transcribe(audio[a:b], language="ko", beam_size=5, vad_filter=False)
            heard2 = "".join(x.text for x in segs)
            r2 = max(difflib.SequenceMatcher(None, norm(x), norm(heard2)).ratio() for x in (s.data["say"], pron(s.data["say"])))
            if r2 > ratio:
                ratio, heard = r2, heard2
                row.update(ratio=round(r2, 2), heard=heard2.strip(), recheck=True)
        if ratio < 0.75:
            fails.append(f"{s.id} 싱크/발음 불일치 {ratio:.2f}: '{heard.strip()[:40]}'")
        if win:
            off = win[0][0] - s.voice_start
            row["offset"] = round(off, 2)
            if off > 0.6 or off < -0.3:
                eo = energy_onset(audio, max(s.voice_start - 0.6, prev_end + 0.02), s.voice_start + 1.2)
                if eo is not None and -0.3 <= eo - s.voice_start <= 0.6:
                    row["onset_energy"] = round(eo - s.voice_start, 2)
                    warns.append(f"{s.id} Whisper 시각 {off:+.2f}s, 실제 음성 시작 {eo - s.voice_start:+.2f}s → 통과")
                else:
                    fails.append(f"{s.id} 시작 어긋남 {off:+.2f}s (에너지 기준 {'-' if eo is None else f'{eo - s.voice_start:+.2f}'}s)")
        if re.search(r"([가-힣])\1{2,}", heard) and not re.search(r"([가-힣])\1{2,}", s.data["say"]):
            fails.append(f"{s.id} 말더듬 의심: '{heard.strip()[:30]}'")
        for c in s.chunks:
            if c.end - c.start < 0.5:
                fails.append(f"{s.id} 자막 '{c.text[:12]}' 노출 {c.end - c.start:.2f}s (너무 짧음)")
        rows.append(row)
        prev_end = s.voice_end

    # 4) 긴 무음
    cover = script.get("cover_sec", 0.35 if script["format"] == "short" else 0)
    pauses = {round(s.voice_end, 1) for s in r.scenes if s.data.get("pause_after", 0) >= 1.0}
    for a, b in zip(words, words[1:]):
        gap = b[0] - a[1]
        if gap > 2.5 and a[1] > cover and round(a[1], 1) not in pauses:
            warns.append(f"무음 {gap:.1f}s @ {a[1]:.1f}s")

    rep = {"pass": not fails, "duration": round(dur, 1), "lufs": lufs, "fails": fails, "warns": warns, "scenes": rows}
    (out_dir / "final_qa.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[최종검수] {'통과' if not fails else '불합격'} · {dur:.1f}s · {lufs:.1f} LUFS")
    for f in fails:
        print("  FAIL", f)
    for w in warns:
        print("  WARN", w)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
