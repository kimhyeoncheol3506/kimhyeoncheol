# -*- coding: utf-8 -*-
"""클라우드(PC 없이)용 내레이션: edge-tts 한국어 신경망 음성 -> voice.wav + timings.json
PC 의 Voicebox(여의도여자)를 못 쓸 때 사용. 목소리는 여의도여자와 다르다(영상 설명/보고에 명시).
사용: python cloud_voice.py <프로젝트폴더> [--voice ko-KR-SunHiNeural] [--rate +8%] [--target 158]
  - script.txt 한 줄 = 한 문장. 문장별로 합성 -> 앞뒤 무음 제거 -> 0.30초 간격으로 이어붙임
  - --target 보다 길면 atempo 로 줄임(최대 1.25배 권장), 짧으면 그대로 두고 storyboard end_pad 로 맞춤
  - timings.json 은 문장 안에서 음절 비례 분배(오차 0.1~0.2초) -> t2d.py words --from timings.json
설치: pip install edge-tts imageio-ffmpeg   (네트워크 필요)
대체: edge-tts 가 막히면 gTTS(lang='ko') 로 같은 흐름 (품질 낮음), 그것도 막히면 사용자에게 보고.
"""
import argparse, asyncio, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("proj")
ap.add_argument("--voice", default="ko-KR-SunHiNeural")
ap.add_argument("--rate", default="+8%")
ap.add_argument("--target", type=float, default=158.0)
ap.add_argument("--gap", type=float, default=0.30)
a = ap.parse_args()

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FF = "ffmpeg"
import edge_tts
# 클라우드 프록시(자체 CA) 환경: SSL_CERT_FILE 이 있으면 그 CA 묶음으로 검증 (edge-tts 는 기본적으로 certifi 만 씀)
if os.environ.get("SSL_CERT_FILE") and os.path.exists(os.environ["SSL_CERT_FILE"]):
    import ssl, edge_tts.communicate as _ec
    _ec._SSL_CTX = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])

P = os.path.abspath(a.proj)
VD = os.path.join(P, "vo"); os.makedirs(VD, exist_ok=True)
lines = [l.strip() for l in open(os.path.join(P, "script.txt"), encoding="utf-8").read().splitlines() if l.strip()]


async def synth(text, out):
    c = edge_tts.Communicate(text, a.voice, rate=a.rate)
    await c.save(out)


def dur_of(f):
    r = subprocess.run([FF, "-i", f, "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr).groups()
    return int(h) * 3600 + int(m) * 60 + float(s)


def bounds(f):
    r = subprocess.run([FF, "-i", f, "-af", "silencedetect=n=-40dB:d=0.08", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    d = dur_of(f)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    s0 = en[0] if st and st[0] < 0.02 and en else 0.0
    s1 = st[-1] if st and (not en or st[-1] > en[-1]) else d
    return max(0, s0 - 0.03), min(d, s1 + 0.08)


def syl(w):
    return max(1, len(re.findall(r"[가-힣A-Za-z]", w)) + 2 * len(re.findall(r"\d", w)))


parts, words, t = [], [], 0.0
for i, line in enumerate(lines):
    mp3 = os.path.join(VD, "s%02d.mp3" % i)
    if not os.path.exists(mp3):
        for k in range(3):
            try:
                asyncio.run(synth(line, mp3)); break
            except Exception as e:
                print("retry", i, e, flush=True)
    raw = os.path.join(VD, "s%02d_raw.wav" % i)
    subprocess.run([FF, "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "1", raw], check=True)
    s0, s1 = bounds(raw)
    cut = os.path.join(VD, "s%02d.wav" % i)
    subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-ss", "%.3f" % s0, "-to", "%.3f" % s1, "-ar", "48000", "-ac", "1", cut], check=True)
    L = s1 - s0
    toks = line.split(); tot = sum(syl(w) for w in toks); c = t
    for w in toks:
        dw = L * syl(w) / tot
        words.append({"word": w, "start": c, "end": c + dw * 0.92}); c += dw
    parts.append(cut); t += L
    if i < len(lines) - 1:
        t += a.gap
    print(i + 1, "/", len(lines), "%.1fs" % L, flush=True)

gap = os.path.join(VD, "gap.wav")
subprocess.run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(a.gap), gap], check=True)
lst = os.path.join(VD, "list.txt")
with open(lst, "w", encoding="utf-8") as f:
    for i, p in enumerate(parts):
        f.write("file '%s'\n" % p.replace("\\", "/"))
        if i < len(parts) - 1:
            f.write("file '%s'\n" % gap.replace("\\", "/"))
v1 = os.path.join(P, "voice_1x.wav")
subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-ar", "48000", "-ac", "1", v1], check=True)
D = dur_of(v1)
k = max(1.0, D / a.target)
subprocess.run([FF, "-v", "error", "-y", "-i", v1, "-af", "atempo=%.5f" % k, "-ar", "48000", "-ac", "1", os.path.join(P, "voice.wav")], check=True)
for w in words:
    w["start"] = round(w["start"] / k, 3); w["end"] = round(w["end"] / k, 3)
json.dump(words, open(os.path.join(P, "timings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("DONE raw %.1fs tempo %.3f -> %.1fs, %d words" % (D, k, D / k, len(words)))
