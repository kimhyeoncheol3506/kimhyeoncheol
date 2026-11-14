# -*- coding: utf-8 -*-
"""주간 시세 리포트 티저 쇼츠(1080×1920, 30초 이내) — 본편과 같은 먹색+금색. 음성 1.12배속. 사용: python3 build_shorts.py short1|short2"""
import json, os, re, shutil, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
NAME = sys.argv[1]
D = json.load(open(f"{ROOT}/01_대본/{NAME}.json", encoding="utf-8")); DATA = json.load(open(f"{ROOT}/00_data/비교.json", encoding="utf-8"))
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

R = {(r["품목"], r["상태"]): r for r in DATA["rows"]}
title, photo = "이번 주 노량진<br>싸진 것 1위", "부시리"
TITLES = {3: "이번 주 노량진<br>싸진 것 TOP5", 4: "이번 주 노량진<br>오른 것 TOP3", 5: "매주 토요일<br>노량진 시세"}  # 카드마다 위쪽 제목을 맞게 바꿈
rows = [("부시리", ("부시리", "활")), ("광어(선)", ("넙치", "선")), ("대구(선)", ("대구", "선")), ("홍어(선)", ("홍어", "선")), ("아귀(선)", ("아귀", "선"))]
lst = "".join(f'<div style="display:flex;justify-content:space-between;font-size:58px;padding:14px 20px;border-bottom:1px solid {GOLD}44"><span class="mj"><span style="color:{GOLD}">{i + 1}</span>  {n}</span><span class="num" style="color:{DOWN}">▼{abs(round(R[k]["변동"]))}%</span></div>' for i, (n, k) in enumerate(rows))
ups = [("킹크랩(선)", ("왕게", "선")), ("줄전갱이", ("흑점줄전갱이", "활")), ("수꽃게", ("수꽃게", "활"))]
cards = [(1, f'<div class="mj" style="font-size:150px">부시리</div><div class="num" style="font-size:200px;color:{DOWN};line-height:1.1">▼32%</div>'),
         (2, f'<div class="kick">kg당 경락가 중앙값</div><div class="num" style="font-size:110px;margin-top:20px"><span style="color:{MUTE}">7,500</span> → <span style="color:{DOWN}">5,100</span></div><div style="font-size:52px;font-weight:700;margin-top:30px">리포트 4번 연속 하락</div>'),
         (3, f'<div class="kick">싸진 것 TOP5</div><div style="text-align:left;margin-top:16px">{lst}</div>'),
         (4, f'<div class="kick" style="color:{UP}">오른 것 TOP3</div>' + "".join(f'<div style="display:flex;justify-content:space-between;font-size:62px;padding:16px 20px;border-bottom:1px solid {GOLD}44"><span class="mj">{n}</span><span class="num" style="color:{UP}">▲{round(R[k]["변동"])}%</span></div>' for n, k in ups)),
         (5, f'<div class="mj" style="font-size:86px;color:{GOLD2}">매주 토요일 시세 ▶</div><div style="font-size:52px;margin-top:20px">관련 영상에서 전체 보기</div><div style="font-size:40px;color:{MUTE};margin-top:40px">도매 경락가 · 가게 판매가와 다름 · 11/9~11/14</div>')]

body = (f'<div style="position:absolute;left:0;right:0;top:0;height:760px;overflow:hidden"><img id="ph" src="assets/img/{PHOTO[photo]}.jpg" style="width:100%;height:100%;object-fit:cover;opacity:.55">'
        f'<div style="position:absolute;inset:0;background:linear-gradient(180deg,{INK}66,{INK})"></div></div>'
        f'<div style="position:absolute;left:0;right:0;top:120px;text-align:center"><div class="kick">노량진수산시장 · 도매 경락가</div><div style="position:relative;height:370px;margin-top:24px"><div id="tt" class="mj" style="position:absolute;left:0;right:0;font-size:150px;line-height:1.2">{title}</div>'
        + "".join(f'<div id="tt{k}" class="mj" style="position:absolute;left:0;right:0;font-size:150px;line-height:1.2;opacity:0">{v}</div>' for k, v in TITLES.items()) + '</div></div>'
        + "".join(f'<div id="c{k}" class="card" style="left:40px;right:40px;top:640px;text-align:center">{h}</div>' for k, h in cards))
css = (FONTS + f"#root{{position:absolute;inset:0;overflow:hidden;color:{IVORY};font-family:PX,sans-serif;background:{INK}}}.mj{{font-family:MJ,serif;font-weight:800}}.num{{font-family:PXB,PX;font-weight:800}}"
       f".kick{{font-size:40px;letter-spacing:.2em;color:{GOLD};font-weight:700}}.card{{position:absolute;opacity:0}}")
ks = [k for k, _ in cards]
js = (f'const tl = gsap.timeline({{ paused: true }}); tl.fromTo("#ph", {{ scale: 1.15 }}, {{ scale: 1, duration: {TOTAL:.2f}, ease: "none" }}, 0);'
      f'tl.fromTo("#tt", {{ y: 30 }}, {{ y: 0, duration: 0.6, ease: "power3.out" }}, 0);'
      + "".join(f'tl.fromTo("#c{k}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {st(k)});' + (f'tl.to("#c{k}", {{ opacity: 0, duration: 0.3 }}, {st(ks[i + 1])} - 0.25);' if i + 1 < len(ks) else "") for i, k in enumerate(ks))
      + "".join((lambda prev: f'tl.to("#{prev}", {{ opacity: 0, duration: 0.3 }}, {st(k)} - 0.2); tl.fromTo("#tt{k}", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {st(k)});')("tt" if i == 0 else f"tt{list(TITLES)[i - 1]}") for i, k in enumerate(TITLES))
      + 'window.__timelines["sc"] = tl;')
scene = f'<template><style>{css}</style><div id="root" data-composition-id="sc" data-width="1080" data-height="1920">{body}</div><script>{js}</script></template>'


def one_line(x, n=11):
    out, c = [], ""
    for w in x.split(" "):
        if c and len(c) + 1 + len(w) > n: out.append(c); c = w
        else: c = (c + " " + w).strip()
    if c: out.append(c)
    return out


caps = []; k = 0
for x in S:
    sub = re.sub(r"\s{2,}", " ", re.sub(r"(?<!\d)[,.]|[,.](?!\d)", "", x["sub"])).strip(); sub = re.sub(r"(\d만) (\d천)", "\\1\u00a0\\2", sub); sub = re.sub(r"(\d천|\d만) 원", "\\1\u00a0원", sub); lines = one_line(sub); tot = sum(len(l) for l in lines); t0 = x["start"]
    for l in lines:
        du = x["dur"] * len(l) / tot; h = re.sub(r"(\d[\d,~·./%]*(?:만(?: \d천)? 원|천 원|원|kg|배|미|월|%)?)", r"<b>\1</b>", l)
        caps.append(f'<div class="clip cap" id="cap{k}" data-start="{t0:.3f}" data-duration="{du:.3f}" data-track-index="1"><span>{h}</span></div>'); k += 1; t0 += du
ccss = (FONTS + '#root{position:absolute;inset:0;font-family:PX}.cap{position:absolute;left:0;right:0;bottom:430px;text-align:center}'
        '.cap span{display:inline-block;background:rgba(0,0,0,.6);color:#fff;font-size:80px;font-weight:700;line-height:1.2;padding:8px 26px;white-space:nowrap}.cap b{color:#FFD640}')
capf = (f'<template><style>{ccss}</style><div id="root" data-composition-id="captions" data-width="1080" data-height="1920">{"".join(caps)}</div>'
        '<script>const tl = gsap.timeline({ paused: true }); window.__timelines["captions"] = tl;</script></template>')
if os.path.exists(HF): shutil.rmtree(HF)
os.makedirs(f"{HF}/compositions"); os.makedirs(f"{HF}/assets/fonts"); os.makedirs(f"{HF}/assets/img")
tpl = "/home/user/kimhyeoncheol/.claude/skills/ranking-video/templates/hyperframes_movers"
for f in ("hyperframes.json", "package.json"): shutil.copy(f"{tpl}/{f}", f"{HF}/{f}")
json.dump(dict(id=NAME, name=NAME, createdAt="2026-11-08T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
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
