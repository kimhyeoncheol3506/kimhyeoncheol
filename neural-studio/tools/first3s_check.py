#!/usr/bin/env python3
"""첫 3초·첫 10초 검사 + 효과음/음량 검사 (CEO 시리즈, 2026-11-25).
근거: kaomei/stickman-video-director (MIT) b4-opening-direction '첫 3초 시각 상승 검사', b5-sound-qa '소리 우선순위·음량'.
우리 영상에 맞게 줄여서 옮김 — 숫자 기준은 아래 상수.

사용: python3 tools/first3s_check.py <영상.mp4> [--out 폴더]
검사:
 1) 첫 소리 시작: 0.5초 안에 소리가 나는가 (빈 도입부 금지 · 첫 프레임 오디오 게이트)
 2) 첫 말 시작: 1.0초 안에 목소리(대사)가 시작되는가 — 첫 10초 받아쓰기(faster-whisper 있으면)
 3) 첫 3초 화면 변화: 0·1·2·3초 프레임 차이가 있는가 (멈춘 그림 위 제목만은 불합격)
 3-1) 0초 프레임이 빈 바탕인가 (첫 화면부터 숫자·질문이 보여야 함)
 4) 3초 넘게 같은 그림: 첫 10초 안에 화면이 3초 넘게 그대로인 구간이 있는가
 5) 음량: 통합 음량(LUFS)·트루피크(dBTP). 참고 기준 −16~−13 LUFS, 트루피크 −1 dBTP 이하
결과: <out>/first3s.png(첫 3초 4장 + 10초 띠) · <out>/first3s.json · 표준 출력 요약. 기계 검사일 뿐, 재미·긴장감은 사람이 봐야 한다.
"""
import sys, os, json, re, subprocess, tempfile
from PIL import Image, ImageChops, ImageStat, ImageDraw

LUFS_RANGE = (-16.0, -13.0)
TP_MAX = -1.0
SOUND_START_MAX = 0.5
SPEECH_START_MAX = 1.0
STATIC_MAX = 3.0
DIFF_MIN = 6.0          # 프레임 평균 픽셀 차이(0~255) 이 값 미만이면 '같은 그림'


def sh(*a):
    return subprocess.run(a, capture_output=True, text=True)


def frame(mp4, t, w=480):
    f = tempfile.mktemp(suffix=".png")
    sh("ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", mp4, "-frames:v", "1", "-vf", f"scale={w}:-2", "-y", f)
    im = Image.open(f).convert("RGB"); os.remove(f); return im


def diff(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def main():
    mp4 = sys.argv[1]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.dirname(os.path.abspath(mp4))
    os.makedirs(out, exist_ok=True)
    rep = {"file": mp4, "checks": {}}
    C = rep["checks"]

    # 1) 첫 소리
    e = sh("ffmpeg", "-hide_banner", "-t", "10", "-i", mp4, "-af", "silencedetect=noise=-40dB:d=0.1", "-f", "null", "-").stderr
    st = re.findall(r"silence_start: ([\d.]+)", e); en = re.findall(r"silence_end: ([\d.]+)", e)
    first_sound = float(en[0]) if st and float(st[0]) < 0.05 and en else 0.0
    C["first_sound_s"] = {"value": round(first_sound, 2), "ok": first_sound <= SOUND_START_MAX, "rule": f"<= {SOUND_START_MAX}s"}

    # 2) 첫 말 (가능할 때만)
    try:
        from faster_whisper import WhisperModel
        a = tempfile.mktemp(suffix=".wav")
        sh("ffmpeg", "-v", "error", "-t", "10", "-i", mp4, "-ac", "1", "-ar", "16000", "-y", a)
        m = WhisperModel(os.environ.get("WHISPER_MODEL", "small"), device="cpu", compute_type="int8")
        segs, _ = m.transcribe(a, language="ko", word_timestamps=True, vad_filter=True)
        words = [(w.start, w.word) for s in segs for w in (s.words or [])]
        os.remove(a)
        t0 = words[0][0] if words else None
        C["first_speech_s"] = {"value": round(t0, 2) if t0 is not None else None, "ok": t0 is not None and t0 <= SPEECH_START_MAX,
                               "rule": f"<= {SPEECH_START_MAX}s", "first_10s_text": "".join(w for _, w in words).strip()}
    except Exception as ex:
        C["first_speech_s"] = {"value": None, "ok": None, "note": f"받아쓰기 못 함: {type(ex).__name__}: {str(ex)[:120]}"}

    # 3) 첫 3초 화면 변화, 4) 첫 10초 정지 구간
    ts = [i * 0.5 for i in range(21)]
    fr = [frame(mp4, t) for t in ts]
    sd0 = sum(ImageStat.Stat(fr[0].convert("L")).stddev)
    C["first_frame_not_blank"] = {"value": round(sd0, 1), "ok": sd0 >= 18, "rule": "0초 프레임 밝기 편차 >= 18 (빈 바탕으로 시작 금지 · 첫 프레임에 질문·숫자·그림)"}
    d3 = max(diff(fr[0], fr[i]) for i in (2, 4, 6))
    C["first3s_visual_change"] = {"value": round(d3, 1), "ok": d3 >= DIFF_MIN, "rule": f"0~3초 최대 프레임 차이 >= {DIFF_MIN}"}
    run, longest, start = 0.0, 0.0, 0.0
    for i in range(1, len(fr)):
        if diff(fr[i - 1], fr[i]) < DIFF_MIN / 3:
            run += 0.5
            if run > longest: longest, start = run, ts[i] - run
        else:
            run = 0.0
    C["longest_static_first10s_s"] = {"value": longest, "at": start, "ok": longest <= STATIC_MAX, "rule": f"<= {STATIC_MAX}s"}

    # 5) 음량
    e = sh("ffmpeg", "-hide_banner", "-i", mp4, "-af", "ebur128=peak=true", "-f", "null", "-").stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", e); P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)
    lufs = float(I[-1]) if I else None; tp = float(P[-1]) if P else None
    C["loudness_lufs"] = {"value": lufs, "ok": lufs is not None and LUFS_RANGE[0] <= lufs <= LUFS_RANGE[1], "rule": f"{LUFS_RANGE[0]}~{LUFS_RANGE[1]}"}
    C["true_peak_dbtp"] = {"value": tp, "ok": tp is not None and tp <= TP_MAX, "rule": f"<= {TP_MAX}"}

    # 띠 그림
    W = fr[0].width; H = fr[0].height
    sheet = Image.new("RGB", (W * 4, H + H // 2 + 40), "white"); dr = ImageDraw.Draw(sheet)
    for k, i in enumerate((0, 2, 4, 6)):
        sheet.paste(fr[i], (k * W, 0)); dr.text((k * W + 6, 4), f"{ts[i]:.0f}s", fill="yellow")
    small = [f.resize((W * 4 // 20, H * 4 // 20 * 2)) for f in fr[:20]]
    for k, f in enumerate(small): sheet.paste(f, (k * (W * 4 // 20), H + 20))
    sheet.save(os.path.join(out, "first3s.png"))
    rep["pass"] = all(v.get("ok") is not False for v in C.values())
    json.dump(rep, open(os.path.join(out, "first3s.json"), "w"), ensure_ascii=False, indent=1)
    for k, v in C.items():
        mark = "통과" if v.get("ok") else ("확인 못 함" if v.get("ok") is None else "불합격")
        print(f"{mark:6} {k} = {v.get('value')} ({v.get('rule', v.get('note', ''))})")
    if C["first_speech_s"].get("first_10s_text"): print("첫 10초 말:", C["first_speech_s"]["first_10s_text"])
    print("종합:", "통과" if rep["pass"] else "고칠 것 있음", "→", os.path.join(out, "first3s.png"))


if __name__ == "__main__":
    main()
