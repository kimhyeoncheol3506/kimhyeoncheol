# -*- coding: utf-8 -*-
"""문장별 TTS 생성 (ranking-video v2.0.0) — Microsoft Edge TTS (기본 현수 ko-KR-HyunsuMultilingualNeural)

사용법: SSL_CERT_FILE=<CA번들> python3 -I make_tts.py <대본데이터.json> <출력폴더> [목소리ID]
목소리: 기본 ko-KR-HyunsuMultilingualNeural(현수). 다른 후보: ko-KR-InJoonNeural(인준), ko-KR-SunHiNeural(선희). JSON "voice"로도 지정 가능.
속도: 기본 -12%, 느리게▲ -18%, 빠르게▼ -5%. 캡컷 애덤 목소리는 캡컷 안에서만 만들 수 있어 대체 목소리로 쓴다.
필요: pip install edge-tts
"""
import asyncio, json, os, sys, subprocess
import edge_tts
D = json.load(open(sys.argv[1], encoding="utf-8")); OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
VOICE = sys.argv[3] if len(sys.argv) > 3 else D.get("voice", "ko-KR-HyunsuMultilingualNeural")  # v1.3.1 기본: 현수(밝은 남성)
PROXY = os.environ.get("HTTPS_PROXY")
jobs = []
for si, s in enumerate(D["sections"]):
    for ti, x in enumerate(s["sentences"]):
        memo = x[1] if len(x) > 1 else ""
        rate = "+12%" if "느리게" in memo else ("+30%" if "빠르게" in memo else "+22%")
        jobs.append((f"{si:02d}_{ti:02d}", x[0], rate))
sem = asyncio.Semaphore(4)
async def one(k, text, rate):
    fn = f"{OUT}/{k}.mp3"
    if os.path.exists(fn) and os.path.getsize(fn) > 2000: return
    async with sem:
        for a in range(4):
            try:
                await edge_tts.Communicate(text, VOICE, rate=rate, proxy=PROXY).save(fn); return
            except Exception as e:
                await asyncio.sleep(3 * (a + 1)); err = e
        print("FAIL", k, err)
async def main(): await asyncio.gather(*[one(*j) for j in jobs])
asyncio.run(main())
dur = {}
for k, t, r in jobs:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{OUT}/{k}.mp3"], capture_output=True, text=True).stdout.strip()
    dur[k] = float(out)
json.dump(dur, open(f"{OUT}/durations.json", "w"), indent=0)
print(len(jobs), "sentences, total voice", round(sum(dur.values()) / 60, 2), "min")
