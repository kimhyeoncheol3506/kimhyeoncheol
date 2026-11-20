#!/usr/bin/env python3
"""한국어 내레이션용 timing.json 만들기 (영어 음성인식 정렬 대신).
  python3 tools/ko_timing.py <P> --estimate [--rate 6.0] [--gap 0.45]
      script.txt 문장을 음절 수/초로 길이를 추정한다(스틸 시트·plan 확인용).
  python3 tools/ko_timing.py <P> --wavs <dir>
      문장 순서대로 저장된 TTS 파일(<dir>/0000.wav, 0001.wav …)의 실제 길이로 만든다. voice.wav 도 이어 붙여 만든다.
낱말 시각은 문장 안에서 음절 수 비례로 나눈다(우리 TTS는 문장 단위로 녹음되므로 문장 경계는 정확하다)."""
import sys, os, json, re, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.timing import sentences, norm

def syl(w):
    n = len(re.findall(r"[가-힣]", w)); d = re.findall(r"\d", w)
    return max(1, n + int(len(d) * 1.2) + len(re.findall(r"[A-Za-z]", w)) // 2)

def build(ss, durs, gap):
    out, t = [], 0.0
    for i, (s, d) in enumerate(zip(ss, durs)):
        ws = s.split(); tot = sum(syl(w) for w in ws); acc = 0; words = []
        for w in ws:
            words.append(dict(w=w, n=norm(w), t=round(t + d * acc / tot, 3))); acc += syl(w)
        out.append(dict(i=i, text=s, start=round(max(0, t - .06), 3), end=round(t + d, 3), words=words))
        t += d + gap
    return dict(duration=round(t, 3), method="ko-tts", matched=1.0, sentences=out)

def main():
    P = os.path.abspath(sys.argv[1]); a = sys.argv[2:]
    get = lambda k, dv: float(a[a.index(k) + 1]) if k in a else dv
    ss = sentences(open(os.path.join(P, "script.txt"), encoding="utf-8").read()); gap = get("--gap", .45)
    if "--wavs" in a:
        d = a[a.index("--wavs") + 1]; fs = sorted(glob.glob(os.path.join(d, "*.wav")))
        assert len(fs) == len(ss), f"wav {len(fs)}개 ≠ 문장 {len(ss)}개"
        durs = [float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f])) for f in fs]
        lst = os.path.join(P, "work", "ko_concat.txt"); os.makedirs(os.path.dirname(lst), exist_ok=True)
        g = os.path.join(P, "work", "gap.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(gap), g], check=True)
        open(lst, "w").write("".join(f"file '{f}'\nfile '{g}'\n" for f in fs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "24000", "-ac", "1", os.path.join(P, "voice.wav")], check=True)
    else:
        r = get("--rate", 6.0); durs = [sum(syl(w) for w in s.split()) / r + .2 for s in ss]
    T = build(ss, durs, gap); json.dump(T, open(os.path.join(P, "timing.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(ss)}문장 · {T['duration']:.1f}초 · {T['method']}")

if __name__ == "__main__": main()
