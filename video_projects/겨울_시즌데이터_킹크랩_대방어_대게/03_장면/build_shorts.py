# -*- coding: utf-8 -*-
"""티저 쇼츠 2편(1080×1920, 30초 이내) — 롱폼과 같은 먹색+금색 스타일. 사용: python3 build_shorts.py short1|short2"""
import json, os, re, shutil, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
NAME = sys.argv[1]
D = json.load(open(f"{ROOT}/01_대본/{NAME}.json", encoding="utf-8")); DATA = json.load(open(f"{ROOT}/00_data/data.json", encoding="utf-8"))
TTS = f"{ROOT}/02_음성_쇼츠/{NAME}"; HF = f"{HERE}/hf_{NAME}"; IMG = f"{ROOT}/09_소재/img_final"; PHOTO = json.load(open(f"{IMG}/pick.json", encoding="utf-8"))
FONTDIR = os.path.expanduser("~/.cache/ranking-video/fonts")
INK, GOLD, GOLD2, IVORY, MUTE, DOWN, UP, GREY = "#0D0E11", "#D6B26E", "#F1D9A0", "#F2EDE3", "#8C919B", "#5FB7A6", "#E4775F", "#6B7079"
FONTS = ('@font-face{font-family:"MJ";src:url("assets/fonts/NanumMyeongjo-ExtraBold.ttf");font-weight:800}@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-Bold.otf");font-weight:700}'
         '@font-face{font-family:"PXB";src:url("assets/fonts/Pretendard-ExtraBold.otf");font-weight:800}')
GAP, LEAD = 0.25, 0.3
sents = D["sections"][0]["sentences"]; S = []; cur = LEAD
for i, x in enumerate(sents):
    p = f"{TTS}/00_{i:02d}.wav"
    with wave.open(p) as w: du = w.getnframes() / w.getframerate()
    S.append(dict(text=x[0], sig=x[1], sub=x[2], start=cur, dur=du, wav=p)); cur += du + GAP
TOTAL = cur + 0.5
st = lambda k: round(max(0.1, next(x["start"] for x in S if x["sig"].get("k") == k) - 0.1), 3)

if NAME == "short1":
    title, photo = "크리스마스 주<br>킹크랩", "킹크랩"
    d = DATA["킹크랩"]; WK = ["11월1주", "11월2주", "11월3주", "11월4주", "12월1주", "12월2주", "12월3주", "12월4주", "01월1주"]
    def pts(s):
        r = {x["w"]: x["p"] for x in d[s]}; return " ".join(f"{80 + i * 110},{620 - (r[w] - 50000) / 45000 * 520:.0f}" for i, w in enumerate(WK))
    chart = (f'<svg width="1000" height="720" viewBox="0 0 1000 720"><rect x="{80 + 3 * 110 - 30}" y="80" width="170" height="560" fill="{DOWN}" opacity=".2"/>'
             f'<rect x="{80 + 6 * 110 - 30}" y="80" width="170" height="560" fill="{UP}" opacity=".18"/>'
             f'<polyline points="{pts("24-25")}" fill="none" stroke="{GREY}" stroke-width="8"/><polyline points="{pts("25-26")}" fill="none" stroke="{GOLD}" stroke-width="10"/>'
             + "".join(f'<text x="{80 + i * 110}" y="690" font-size="34" fill="{IVORY}" text-anchor="middle">{w[:2].lstrip("0")}/{w[3]}</text>' for i, w in enumerate(WK))
             + f'<text x="{80 + 3.5 * 110}" y="60" font-size="40" font-weight="800" fill="{DOWN}" text-anchor="middle">싼 구간</text><text x="{80 + 6.5 * 110}" y="60" font-size="40" font-weight="800" fill="{UP}" text-anchor="middle">크리스마스</text></svg>')
    cards = [(2, f'<div class="kick">시즌 최고가 · 12월 4주</div><div class="num" style="font-size:120px;color:{UP}">92,800</div><div style="font-size:44px;color:{MUTE}">재작년 · 원/kg</div><div class="num" style="font-size:100px;color:{UP};margin-top:20px">85,700</div><div style="font-size:44px;color:{MUTE}">작년 · 원/kg</div>'),
             (3, f'<div class="kick">재작년 · 11월 4주보다</div><div class="num" style="font-size:150px;color:{UP}">+34,100</div><div style="font-size:48px;color:{MUTE}">원 / kg</div>'),
             (4, chart),
             (5, f'<div class="mj" style="font-size:96px;color:{GOLD2}">전체 분석 ▶</div><div style="font-size:52px;margin-top:20px">관련 영상에서</div><div style="font-size:40px;color:{MUTE};margin-top:40px">도매 경락가 · 가게 판매가와 다름</div>')]
else:
    title, photo = "올해<br>대방어", "대방어"
    y = DATA["대방어"]["요일"]
    cards = [(2, f'<div class="kick">11월 1주 · 원/kg</div><div class="num" style="font-size:150px;color:{UP}">23,600</div><div style="font-size:48px;color:{MUTE}">작년 같은 주 17,600</div><div class="num" style="font-size:120px;color:{UP};margin-top:16px">▲34%</div>'),
             (3, f'<div class="kick">지난 두 해 · 1월 초가 쌌다</div><div class="num" style="font-size:110px;color:{DOWN};margin-top:10px">16,700</div><div style="font-size:44px;color:{MUTE}">작년 1월 1주</div><div class="num" style="font-size:110px;color:{DOWN};margin-top:16px">14,200</div><div style="font-size:44px;color:{MUTE}">재작년 1월 2주</div>'),
             (4, f'<div class="kick">요일 · 원/kg</div><div style="display:flex;justify-content:center;gap:60px;margin-top:30px;align-items:flex-end;height:520px">'
                 f'<div><div class="num" style="font-size:56px;color:{DOWN}">17,908</div><div style="width:200px;height:{17908 / 20641 * 420:.0f}px;background:{DOWN};margin:10px auto"></div><div style="font-size:56px">월</div></div>'
                 f'<div><div class="num" style="font-size:56px;color:{UP}">20,641</div><div style="width:200px;height:420px;background:{UP};margin:10px auto"></div><div style="font-size:56px">토</div></div></div><div class="num" style="font-size:90px;color:{UP}">+15%</div>'),
             (5, f'<div class="mj" style="font-size:90px;color:{GOLD2}">장보기 달력 ▶</div><div style="font-size:52px;margin-top:20px">관련 영상에서</div><div style="font-size:40px;color:{MUTE};margin-top:40px">도매 경락가 · 가게 판매가와 다름</div>')]

body = (f'<div style="position:absolute;left:0;right:0;top:0;height:760px;overflow:hidden"><img id="ph" src="assets/img/{PHOTO[photo]}.jpg" style="width:100%;height:100%;object-fit:cover;opacity:.55">'
        f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,{INK}66,{INK})"></div></div>'
        f'<div style="position:absolute;left:0;right:0;top:120px;text-align:center"><div class="kick">노량진수산시장 · 도매 경락가</div><div id="tt" class="mj" style="font-size:150px;line-height:1.2;margin-top:24px">{title}</div></div>'
        + "".join(f'<div id="c{k}" class="card" style="left:40px;right:40px;top:640px;text-align:center">{h}</div>' for k, h in cards))
css = (FONTS + f"#root{{position:absolute;inset:0;overflow:hidden;color:{IVORY};font-family:PX,sans-serif;background:{INK}}}.mj{{font-family:MJ,serif;font-weight:800}}.num{{font-family:PXB,PX;font-weight:800}}"
       f".kick{{font-size:40px;letter-spacing:.2em;color:{GOLD};font-weight:700}}.card{{position:absolute;opacity:0}}")
ks = [k for k, _ in cards]
js = (f'const tl = gsap.timeline({{ paused: true }}); tl.fromTo("#ph", {{ scale: 1.15 }}, {{ scale: 1, duration: {TOTAL:.2f}, ease: "none" }}, 0);'
      f'tl.fromTo("#tt", {{ y: 30 }}, {{ y: 0, duration: 0.6, ease: "power3.out" }}, 0);'
      + "".join(f'tl.fromTo("#c{k}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {st(k)});' + (f'tl.to("#c{k}", {{ opacity: 0, duration: 0.3 }}, {st(ks[i + 1])} - 0.25);' if i + 1 < len(ks) else "") for i, k in enumerate(ks))
      + 'window.__timelines["sc"] = tl;')
scene = f'<template><style>{css}</style><div id="root" data-composition-id="sc" data-width="1080" data-height="1920">{body}</div><script>{js}</script></template>'


def one_line(x, n=11):
    out, c = [], ""
    for w in x.split():
        if c and len(c) + 1 + len(w) > n: out.append(c); c = w
        else: c = (c + " " + w).strip()
    if c: out.append(c)
    return out


caps = []; k = 0
for x in S:
    sub = re.sub(r"\s{2,}", " ", re.sub(r"(?<!\d)[,.]|[,.](?!\d)", "", x["sub"])).strip(); lines = one_line(sub); tot = sum(len(l) for l in lines); t0 = x["start"]
    for l in lines:
        du = x["dur"] * len(l) / tot; h = re.sub(r"(\d[\d,~·.%]*(?:원|kg|주|월|%)?)", r"<b>\1</b>", l)
        caps.append(f'<div class="clip cap" id="cap{k}" data-start="{t0:.3f}" data-duration="{du:.3f}" data-track-index="1"><span>{h}</span></div>'); k += 1; t0 += du
ccss = (FONTS + '#root{position:absolute;inset:0;font-family:PX}.cap{position:absolute;left:0;right:0;bottom:430px;text-align:center}'
        '.cap span{display:inline-block;background:rgba(0,0,0,.6);color:#fff;font-size:80px;font-weight:700;line-height:1.2;padding:8px 26px;white-space:nowrap}.cap b{color:#FFD640}')
capf = (f'<template><style>{ccss}</style><div id="root" data-composition-id="captions" data-width="1080" data-height="1920">{"".join(caps)}</div>'
        '<script>const tl = gsap.timeline({ paused: true }); window.__timelines["captions"] = tl;</script></template>')
if os.path.exists(HF): shutil.rmtree(HF)
os.makedirs(f"{HF}/compositions"); os.makedirs(f"{HF}/assets/fonts"); os.makedirs(f"{HF}/assets/img")
tpl = "/home/user/kimhyeoncheol/.claude/skills/ranking-video/templates/hyperframes_movers"
for f in ("hyperframes.json", "package.json"): shutil.copy(f"{tpl}/{f}", f"{HF}/{f}")
json.dump(dict(id=NAME, name=NAME, createdAt="2026-11-07T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
for f in ("NanumMyeongjo-ExtraBold.ttf", "Pretendard-Bold.otf", "Pretendard-ExtraBold.otf"): shutil.copy(f"{FONTDIR}/{f}", f"{HF}/assets/fonts/{f}")
shutil.copy(f"{IMG}/{PHOTO[photo]}.jpg", f"{HF}/assets/img/{PHOTO[photo]}.jpg")
open(f"{HF}/compositions/sc.html", "w", encoding="utf-8").write(scene); open(f"{HF}/compositions/captions.html", "w", encoding="utf-8").write(capf)
# 오디오: 음성 + 차분한 BGM
SR = 48000; L = int(TOTAL * SR) + SR; v = np.zeros(L, np.float32)
ld = lambda p: np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout, dtype=np.float32)
for x in S: a = ld(x["wav"]); i = int(x["start"] * SR); v[i:i + len(a)] += a
bg = ld("/home/user/kimhyeoncheol/video_projects/10월_주간시세_모션그래프/03_장면/audio_assets/sfx/bgm_loop.wav"); bg = np.tile(bg, L // len(bg) + 1)[:L]
mix = np.clip((v / (np.abs(v).max() + 1e-9) * 0.95 + bg * 10 ** (-24 / 20)) * 0.85, -1, 1)
tmp = f"{HF}/raw.wav"
with wave.open(tmp, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ac", "2", "-ar", str(SR), f"{HF}/assets/audio.wav"], check=True); os.remove(tmp)
open(f"{HF}/index.html", "w", encoding="utf-8").write(
    f'<!doctype html><html lang="ko"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
    f'<style>html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:{INK}}}</style></head><body>'
    f'<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1080" data-height="1920">'
    f'<div id="sc" data-composition-id="sc" data-composition-src="compositions/sc.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
    f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:50"></div>'
    f'<audio id="narr" src="assets/audio.wav" data-start="0" data-duration="{TOTAL:.3f}" data-volume="1" data-track-index="5"></audio></div>'
    f'<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script></body></html>')
print(f"{NAME}: {TOTAL:.1f}초, 자막 {k}")
