# -*- coding: utf-8 -*-
"""가락시장 시리즈 쇼츠(공통, short1.json의 cards로 화면 구성)(1080×1920, 30~40초) 1편 — 첫 1.5초 큰 숫자 훅(상단 고정) → 문장마다 장면 전환 → 질문으로 끝(댓글 유도). 무음으로 봐도 이해되게 큰 자막+큰 숫자.
사용: python3 build_shorts.py short1|short2|short3"""
import json, os, re, shutil, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import yieldfx
NAME = sys.argv[1]
D = json.load(open(f"{ROOT}/01_대본/{NAME}.json", encoding="utf-8")); DATA = json.load(open(f"{ROOT}/00_data/prices.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/00_data/prices.json") else {}
TTS = f"{ROOT}/02_음성_쇼츠/{NAME}"; HF = f"{HERE}/hf_{NAME}"
FONTDIR = os.path.expanduser("~/.cache/ranking-video/fonts")
INK, GOLD, GOLD2, IVORY, MUTE, DOWN, UP = "#0D0E11", "#D6B26E", "#F1D9A0", "#F2EDE3", "#8C919B", "#5FB7A6", "#E4775F"
FONTS = ('@font-face{font-family:"MJ";src:url("assets/fonts/NanumMyeongjo-ExtraBold.ttf");font-weight:800}@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-Bold.otf");font-weight:700}'
         '@font-face{font-family:"PXB";src:url("assets/fonts/Pretendard-ExtraBold.otf");font-weight:800}')
GAP, LEAD = 0.18, 0.15
EST = "--est" in sys.argv
sents = D["sections"][0]["sentences"]; S = []; cur = LEAD
for i, x in enumerate(sents):
    p = f"{TTS}/00_{i:02d}.wav"
    if os.path.exists(p):
        with wave.open(p) as w: du = w.getnframes() / w.getframerate()
    elif EST: du = len(x[0].replace(" ", "")) / 6.8 + 0.2; p = None
    else: raise SystemExit("음성 없음 " + p)
    S.append(dict(text=x[0], sig=x[1], sub=x[2], start=cur, dur=du, wav=p)); cur += du + GAP
TOTAL = cur + 0.8
import runpy
B = lambda big, small="", col=GOLD2, size=170: f'<div class="num" style="font-size:{size}px;color:{col};line-height:1.1">{big}</div>' + (f'<div style="font-size:54px;font-weight:700;margin-top:18px;line-height:1.3">{small}</div>' if small else "")
K = lambda t: f'<div class="kick">{t}</div>'
VS = lambda a, b: (f'<div style="display:flex;gap:30px;margin-top:20px">' + "".join(f'<div style="flex:1;border-top:8px solid {c};background:#16181D;padding:30px 10px"><div style="font-size:52px;font-weight:700">{n}</div><div class="num" style="font-size:96px;color:{c};margin-top:10px">{v}</div></div>' for n, v, c in (a, b)) + '</div>')
ASK = lambda q: f'<div class="mj" style="font-size:96px;line-height:1.3;color:{IVORY}">{q}</div><div style="font-size:60px;font-weight:700;color:{GOLD2};margin-top:40px">댓글로 알려 주세요 👇</div>'
WARN = f'{K("꼭 알아 두세요")}<div style="font-size:64px;font-weight:700;line-height:1.45;margin-top:20px">노량진 <span style="color:{GOLD2}">새벽 경매 도매가</span><br>≠ 가게 판매가</div>'
WARN = f'{K("꼭 알아 두세요")}<div style="font-size:60px;font-weight:700;line-height:1.45;margin-top:20px">노량진 <span style="color:{GOLD2}">도매 경락가</span><br>≠ 소래포구 가게 값</div>'
def card(c):
    if c.get("t") == "warn": return WARN
    if c.get("t") == "ask": return ASK(c["q"])
    if c.get("t") == "vs": return K(c["kick"]) + VS(tuple(c["a"]), tuple(c["b"]))
    return (K(c["kick"]) if c.get("kick") else "") + B(c["big"], c.get("small", ""), col=c.get("col", GOLD2), size=c.get("size", 150))
CARDS = {k: card(v) for k, v in D["cards"].items()}
FISH = "참돔" if NAME == "short3" else "광어"; ENDG = "300g" if NAME == "short3" else "400g"

# 카드 시간표: c가 있는 문장에서 시작해 다음 카드 시작 전까지
marks = [(x["sig"]["c"], x["start"]) for x in S if x["sig"].get("c")]
fx = {}
for x in S:
    for k, f in (x["sig"].get("fx") or {}).items(): fx[k] = round(x["start"] + x["dur"] * f, 3)
P = "s-"
body = (f'<div class="bg"></div><div style="position:absolute;left:0;right:0;top:90px;text-align:center" class="kick">노량진 · 도매 경락가</div>'
        f'<div id="hk" class="mj" style="position:absolute;left:0;right:0;top:160px;text-align:center;font-size:132px;line-height:1.18">{D["hook"]}</div>')
for i, (c, t0) in enumerate(marks):
    if c == "fish" and False: body += f'<div id="cfish" style="position:absolute;left:0;top:520px;width:1080px;height:860px;opacity:0">{yieldfx.html(P, 40, 40, 1000, FISH, end_g=ENDG)}</div>'
    else: body += f'<div id="c{c}" class="card" style="left:50px;right:50px;top:700px;text-align:center">{CARDS[c]}</div>'
css = (FONTS + f"#root{{position:absolute;inset:0;overflow:hidden;color:{IVORY};font-family:PX,sans-serif}}.bg{{position:absolute;inset:0;background:radial-gradient(1200px 1400px at 50% 30%,#1A1C22 0%,{INK} 60%,#08090B 100%)}}"
       f".mj{{font-family:MJ,serif;font-weight:800}}.num{{font-family:PXB,PX;font-weight:800}}.kick{{font-size:40px;letter-spacing:.14em;color:{GOLD};font-weight:700}}"
       f".card{{position:absolute;opacity:0;background:#13151A;border:2px solid {GOLD}66;padding:50px 30px}}.card .kick{{margin-bottom:26px}}")
js = 'const tl = gsap.timeline({ paused: true }); const $ = (i) => document.getElementById(i);'
js += 'tl.fromTo($("hk"), { scale: 1.25, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(1.8)" }, 0);'
for i, (c, t0) in enumerate(marks):
    t1 = marks[i + 1][1] - 0.12 if i + 1 < len(marks) else None; el = "cfish" if c == "fish" else f"c{c}"
    js += f'tl.fromTo($("{el}"), {{ opacity: 0, y: 50, scale: 0.96 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "power3.out" }}, {max(0.1, t0 - 0.05):.3f});'
    if t1: js += f'tl.to($("{el}"), {{ opacity: 0, y: -40, duration: 0.18 }}, {t1:.3f});'
if fx:
    js += yieldfx.js(P, dict(show=fx.get("show", 0.1), head=fx["head"], bone=fx["bone"], skin=fx["skin"], plate=fx["plate"])).replace(f'tl.fromTo(document.getElementById("{P}yf"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5 }}', f'tl.fromTo(document.getElementById("{P}yf"), {{ opacity: 1 }}, {{ opacity: 1, duration: 0.1 }}')
js += 'window.__timelines["sc"] = tl;'
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
    sub = re.sub(r"\s{2,}", " ", re.sub(r"(?<!\d)[,.?]|[,.](?!\d)", "", x["sub"])).strip(); sub = re.sub(r"(\d만) (\d천)", "\\1\u00a0\\2", sub); sub = re.sub(r"(\d천|\d만) 원", "\\1\u00a0원", sub); lines = one_line(sub); tot = sum(len(l) for l in lines); t0 = x["start"]
    for l in lines:
        du = x["dur"] * len(l) / tot; h = re.sub(r"(\d[\d,~·./%]*(?:만(?: \d천)? 원|천 원|원|kg|g|%|마리)?)", r"<b>\1</b>", l)
        caps.append(f'<div class="clip cap" id="cap{k}" data-start="{t0:.3f}" data-duration="{du:.3f}" data-track-index="1"><span>{h}</span></div>'); k += 1; t0 += du
ccss = (FONTS + '#root{position:absolute;inset:0;font-family:PX}.cap{position:absolute;left:0;right:0;bottom:440px;text-align:center}'
        '.cap span{display:inline-block;background:rgba(0,0,0,.72);color:#fff;font-size:84px;font-weight:700;line-height:1.2;padding:10px 28px;white-space:nowrap;border-radius:10px}.cap b{color:#FFD640}')
capf = (f'<template><style>{ccss}</style><div id="root" data-composition-id="captions" data-width="1080" data-height="1920">{"".join(caps)}</div>'
        '<script>const tl = gsap.timeline({ paused: true }); window.__timelines["captions"] = tl;</script></template>')
if os.path.exists(HF): shutil.rmtree(HF)
os.makedirs(f"{HF}/compositions"); os.makedirs(f"{HF}/assets/fonts")
tpl = "/home/user/kimhyeoncheol/.claude/skills/ranking-video/templates/hyperframes_movers"
for f in ("hyperframes.json", "package.json"): shutil.copy(f"{tpl}/{f}", f"{HF}/{f}")
json.dump(dict(id=f"garak_{NAME}", name=f"garak_{NAME}", createdAt="2026-11-25T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
for f in ("NanumMyeongjo-ExtraBold.ttf", "Pretendard-Bold.otf", "Pretendard-ExtraBold.otf"): shutil.copy(f"{FONTDIR}/{f}", f"{HF}/assets/fonts/{f}")
open(f"{HF}/compositions/sc.html", "w", encoding="utf-8").write(scene); open(f"{HF}/compositions/captions.html", "w", encoding="utf-8").write(capf)
audio_tag = ""
if not EST:  # 음성 + 잔잔한 BGM, -14 LUFS
    SR = 48000; L = int(TOTAL * SR) + SR; v = np.zeros(L, np.float32)
    ld = lambda p: np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout, dtype=np.float32)
    for x in S: a = ld(x["wav"]); i = int(x["start"] * SR); v[i:i + len(a)] += a
    bg = ld("/home/user/kimhyeoncheol/video_projects/10월_주간시세_모션그래프/03_장면/audio_assets/sfx/bgm_loop.wav"); bg = np.tile(bg, L // len(bg) + 1)[:L]
    mix = np.clip((v / (np.abs(v).max() + 1e-9) * 0.95 + bg * 10 ** (-24 / 20)) * 0.85, -1, 1)
    tmp = f"{HF}/raw.wav"
    with wave.open(tmp, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ac", "2", "-ar", str(SR), f"{HF}/assets/audio.wav"], check=True); os.remove(tmp)
    audio_tag = f'<audio id="narr" src="assets/audio.wav" data-start="0" data-duration="{TOTAL:.3f}" data-volume="1" data-track-index="5"></audio>'
open(f"{HF}/index.html", "w", encoding="utf-8").write(
    f'<!doctype html><html lang="ko"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
    f'<style>html,body{{margin:0;width:1080px;height:1920px;overflow:hidden;background:{INK}}}</style></head><body>'
    f'<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1080" data-height="1920">'
    f'<div id="sc" data-composition-id="sc" data-composition-src="compositions/sc.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1080" data-height="1920"></div>'
    f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="3" data-track-kind="captions" data-width="1080" data-height="1920" style="z-index:50"></div>'
    f'{audio_tag}</div>'
    f'<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script></body></html>')
print(f"{NAME}: {TOTAL:.1f}초, 자막 {k}, 장면 전환 {len(marks) + len(fx)}회")
