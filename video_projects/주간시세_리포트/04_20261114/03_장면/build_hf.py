# -*- coding: utf-8 -*-
"""주간 시세 리포트 (#4부터 고정 틀) — 에디토리얼 골드 스타일 HyperFrames 프로젝트 생성
회차마다 바뀌는 것(훅 품목·팁·3주 흐름·대안·장바구니·요약)은 모두 대본데이터.json의 "weekly"에서 읽는다. 이 파일은 고치지 않는다.
사용: python3 build_hf.py [--est]   → hf/ (index.html + compositions/*) , timeline.json
디자인: 먹색 바탕 + 금색 헤어라인, 명조(제목)·프리텐다드(숫자), 상단 시세 티커, 장면마다 금색 선 와이프.
"""
import json, os, re, shutil, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EST = "--est" in sys.argv
D = json.load(open(f"{ROOT}/01_대본/대본데이터.json", encoding="utf-8"))
TTS = f"{ROOT}/02_음성"; HF = f"{HERE}/hf"; IMG = f"{ROOT}/09_소재/img_final"
FONTDIR = os.path.expanduser("~/.cache/ranking-video/fonts")
GAP, LEAD = 0.3, 0.55
INK, GOLD, GOLD2, IVORY, MUTE, DOWN, UP = "#0D0E11", "#D6B26E", "#F1D9A0", "#F2EDE3", "#8C919B", "#5FB7A6", "#E4775F"
FONTS = ('@font-face{font-family:"MJ";src:url("assets/fonts/NanumMyeongjo-ExtraBold.ttf");font-weight:800}'
         '@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-Bold.otf");font-weight:700}'
         '@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-SemiBold.otf");font-weight:500}'
         '@font-face{font-family:"PXB";src:url("assets/fonts/Pretendard-ExtraBold.otf");font-weight:800}')
DM = sorted(D["display_map"], key=lambda x: -len(x[0]))
DRX = re.compile("|".join(re.escape(a) for a, _ in DM)); DMP = dict(DM)
disp = lambda t: DRX.sub(lambda m: DMP[m.group(0)], t)
jd = lambda o: json.dumps(o, ensure_ascii=False)
won = lambda v: f"{int(round(v)):,}"


def wlen(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()


secs = D["sections"]; t = 0.0; TL = []
for si, s in enumerate(secs):
    cur = LEAD; S = []
    for ti, x in enumerate(s["sentences"]):
        p = f"{TTS}/{si:02d}_{ti:02d}.wav"
        if os.path.exists(p): du = wlen(p); wav = p
        elif EST: du = len(x[0].replace(" ", "")) / 7.0 + 0.2; wav = None
        else: raise SystemExit("음성 없음 " + p)
        S.append(dict(text=x[0], sig=x[1] if len(x) > 1 else {}, start=cur, dur=du, wav=wav)); cur += du + GAP
    dur = cur + (3.0 if s["kind"] == "outro" else 0.45)
    TL.append(dict(s=s, id=f"sc{si:02d}", start=t, dur=dur, S=S)); t += dur
TOTAL = t
PHOTO = json.load(open(f"{IMG}/pick.json", encoding="utf-8")) if os.path.exists(f"{IMG}/pick.json") else {}


def css_base(extra=""):
    return (FONTS + f"#root{{position:absolute;inset:0;overflow:hidden;color:{IVORY};font-family:PX,sans-serif}}#root *{{box-sizing:border-box}}"
            f".bg{{position:absolute;inset:0;background:radial-gradient(1500px 900px at 30% 20%,#1A1C22 0%,{INK} 60%,#08090B 100%)}}"
            f".frame{{position:absolute;left:36px;top:84px;right:36px;bottom:24px;border:1px solid {GOLD}55}}"
            f".wipe{{position:absolute;left:0;top:538px;width:1920px;height:3px;background:linear-gradient(90deg,transparent,{GOLD2},{GOLD},transparent)}}"
            f".mj{{font-family:MJ,serif;font-weight:800}}.num{{font-family:PXB,PX,sans-serif;font-weight:800;font-variant-numeric:tabular-nums}}"
            f".kick{{font-size:30px;letter-spacing:.32em;color:{GOLD};font-weight:700}}" + extra)


def common_js(P):
    return f'''
const tl = gsap.timeline({{ paused: true }}); const $ = (i) => "#{P}" + i;
tl.fromTo($("wipe"), {{ scaleX: 0, opacity: 1, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.55, ease: "power3.inOut" }}, 0);
tl.to($("wipe"), {{ opacity: 0, duration: 0.35 }}, 0.55);
tl.fromTo($("content"), {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, 0.3);
function count(sel, from, to, at, dur, fmt) {{ const o = {{ v: from }}; tl.to(o, {{ v: to, duration: dur || 1.1, ease: "power2.out", onUpdate: () => {{ document.querySelector(sel).textContent = fmt(o.v); }} }}, at); }}
const W = (v) => Math.round(v).toLocaleString("en-US");
'''


def scene(T, body, js, extra_css=""):
    P = T["id"] + "-"; sid = T["id"]
    html = (f'<template><style>{css_base(extra_css)}</style><div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">'
            f'<div class="bg"></div><div class="frame"></div><div id="{P}content" style="position:absolute;inset:0">{body}</div><div class="wipe" id="{P}wipe"></div></div>'
            f'<script>{common_js(P)}{js}\nwindow.__timelines["{sid}"] = tl;</script></template>')
    return html


def st(T, key, val=True, default=None):
    for x in T["S"]:
        v = x["sig"].get(key)
        if v is not None and (val is True or v == val): return round(x["start"] - 0.05, 3)
    return default


# ------------------------------------------------------------------ 장면들
def hook(T):
    P = T["id"] + "-"; mv = {m["name"]: m["ch"] for m in D["movers"]}
    H = D["weekly"]["hook"]; a, b = st(T, "hook", H[0]["sig"], 0.3), st(T, "hook", H[1]["sig"], 3)
    def blk(i, name, ch, col, sign):
        return (f'<div id="{P}h{i}" style="position:absolute;left:0;right:0;top:150px;text-align:center;opacity:0">'
                f'<div class="kick">THIS WEEK · 이번 주</div><div class="mj" style="font-size:210px;line-height:1.15;margin-top:18px">{name}</div>'
                f'<div class="num" style="font-size:250px;line-height:1;color:{col}"><span>{sign}</span><span id="{P}n{i}">0</span>%</div>'
                f'<div style="margin-top:22px;font-size:34px;color:{MUTE}">{H[i].get("note", D["weekly"]["cmp_short"] + " 대비 · kg당 경락가")}</div></div>')
    blk2 = lambda i: blk(i, H[i]["name"], mv[H[i]["name"]], UP if mv[H[i]["name"]] > 0 else DOWN, "▲" if mv[H[i]["name"]] > 0 else "▼")
    body = blk2(0) + blk2(1)
    js = f'''
tl.set($("h0"), {{ opacity: 1 }}, 0); tl.fromTo($("h0"), {{ y: 20 }}, {{ y: 0, duration: 0.6, ease: "power3.out" }}, 0);
count($("n0"), 0, {round(abs(mv[H[0]["name"]]))}, {a}+0.2, 1.2, (v) => Math.round(v));
tl.to($("h0"), {{ opacity: 0, y: -20, duration: 0.35 }}, {b} - 0.25);
tl.fromTo($("h1"), {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {b} - 0.05);
count($("n1"), 0, {round(abs(mv[H[1]["name"]]))}, {b}+0.2, 1.2, (v) => Math.round(v));'''
    return scene(T, body, js)


def title(T):
    P = T["id"] + "-"; a0, a1 = D["period"]; b0, b1 = D["compare"]
    f = lambda d: f"{int(d[5:7])}. {int(d[8:])}"
    body = (f'<div style="position:absolute;left:0;right:0;top:170px;text-align:center">'
            f'<div class="kick" id="{P}k">NORYANGJIN FISH MARKET · WEEKLY REPORT</div>'
            f'<div style="display:flex;justify-content:center;align-items:center;gap:40px;margin-top:40px"><div id="{P}l1" style="width:260px;height:2px;background:{GOLD}"></div>'
            f'<div class="mj" style="font-size:150px;line-height:1.1" id="{P}t">주간 시세 리포트</div><div id="{P}l2" style="width:260px;height:2px;background:{GOLD}"></div></div>'
            f'<div class="mj" style="font-size:84px;color:{GOLD};margin-top:6px" id="{P}no">No. {D["episode"]}</div>'
            f'<div id="{P}per" style="margin-top:38px;font-size:52px;font-weight:700;opacity:0">{a0[:4]}. {f(a0)} — {f(a1)} <span style="color:{MUTE};font-size:40px">{D["weekly"]["days_label"]}</span></div>'
            f'<div id="{P}cmp" style="margin-top:12px;font-size:38px;color:{MUTE};opacity:0">비교 · {D["weekly"]["cmp_short"]} {f(b0)} — {f(b1)}</div>'
            f'<div id="{P}src" style="display:inline-block;margin-top:40px;padding:14px 34px;border:1px solid {GOLD}88;font-size:34px;color:{GOLD2};opacity:0">자료 · 노량진수산 오늘의 경락시세 (도매 경매가)</div>'
            f'<div id="{P}ag" style="display:flex;justify-content:center;gap:28px;margin-top:34px;opacity:0">'
            + "".join(f'<div style="padding:12px 30px;background:#ffffff0d;border-top:2px solid {c};font-size:36px;font-weight:700">{x}</div>' for x, c in (("싸진 TOP 5", DOWN), ("다시 오른 3", UP), ("이번 주 장바구니", GOLD)))
            + '</div></div>')
    js = f'''
tl.fromTo([$("l1"), $("l2")], {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.9, ease: "power3.out" }}, 0.4);
tl.fromTo($("t"), {{ opacity: 0, scale: 1.08, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 1.0, ease: "power3.out" }}, 0.35);
tl.fromTo($("no"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6 }}, 0.9);
tl.fromTo($("per"), {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, "period", 1, 2)});
tl.fromTo($("cmp"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {st(T, "period", 2, 4)});
tl.fromTo($("src"), {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, "source", 1, 6)});
tl.fromTo($("ag"), {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, "agenda", 1, 9)});'''
    return scene(T, body, js)


def overview(T):
    P = T["id"] + "-"; M = D["movers"]; tv, lv = D["totals"]["this"], D["totals"]["last"]; vol = (tv / lv - 1) * 100
    stat = lambda i, big, lab, col=IVORY: (f'<div id="{P}s{i}" style="opacity:0;margin-bottom:40px"><div class="num" style="font-size:118px;line-height:1;color:{col}">{big}</div>'
                                          f'<div style="font-size:34px;color:{MUTE};margin-top:8px">{lab}</div></div>')
    left = (f'<div style="position:absolute;left:110px;top:150px;width:560px"><div class="kick" style="margin-bottom:38px">MARKET OVERVIEW</div>'
            + stat(0, f'<span id="{P}c0">0</span>', "비교 품목 (두 기간 모두 거래 충분)")
            + stat(1, f'<span style="color:{DOWN}">▼<span id="{P}c1">0</span></span><span style="color:{MUTE};font-size:70px"> / </span><span style="color:{UP}">▲<span id="{P}c2">0</span></span>', "내린 품목 / 오른 품목")
            + stat(2, f'+<span id="{P}c3">0</span>%', "kg 경매 전체 물량 (지난주 대비)", GOLD2) + '</div>')
    AX, SC, Y0, RH = 1340, 7.0, 210, (60 if len(M) <= 10 else 540 // len(M))
    rows = []
    for i, m in enumerate(M):
        v = m["ch"]; w = abs(v) * SC; col = DOWN if v < 0 else UP; y = Y0 + i * RH
        x = AX - w if v < 0 else AX; steady = m["name"] in D["weekly"]["steady"]
        rows.append(f'<g id="{P}r{i}" opacity="0"><text x="{AX - 340}" y="{y + 34}" font-size="34" font-weight="700" fill="{IVORY}" text-anchor="end">{m["name"]}</text>'
                    f'<rect id="{P}b{i}" x="{x:.1f}" y="{y + 8}" width="{max(w, 5):.1f}" height="36" fill="{col}"/>'
                    f'<text x="{(AX + w + 16) if v >= 0 else (AX + 16):.1f}" y="{y + 34}" font-size="32" font-weight="800" fill="{col}">{"±" if round(v) == 0 else ("▲" if v >= 0 else "▼")}{abs(round(v))}%</text>'
                    + (f'<rect id="{P}sd{i}" x="{AX - 560}" y="{y + 2}" width="760" height="50" fill="none" stroke="{GOLD}" stroke-width="2" opacity="0"/>' if steady else "") + '</g>')
    # 내린 품목 이름 왼쪽, 값은 막대 끝 바깥 → 이름과 값 겹치지 않게 내린 쪽은 값만 막대 안쪽 왼편에 둔다
    svg = (f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0">'
           f'<text x="{AX}" y="170" font-size="30" fill="{GOLD}" text-anchor="middle" letter-spacing="6">주요 품목 변동</text>'
           f'<line x1="{AX}" y1="190" x2="{AX}" y2="{Y0 + len(M) * RH}" stroke="{GOLD}" stroke-opacity=".6" stroke-width="2"/>{"".join(rows)}</svg>')
    exc = (f'<div id="{P}ex" style="position:absolute;left:820px;top:815px;padding:12px 26px;border-left:3px solid {GOLD};background:#ffffff0a;font-size:32px;color:{IVORY};opacity:0">'
           f'순위 제외 · {" · ".join(D["weekly"]["excluded"])} <span style="color:{MUTE}">({D["weekly"]["excluded_why"]})</span></div>')
    js = f'''
tl.fromTo($("s0"), {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {st(T, "stat", "n", 2)}); count($("c0"), 0, {D["n"]}, {st(T, "stat", "n", 2)}, 1.0, (v) => Math.round(v));
tl.fromTo($("s1"), {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {st(T, "stat", "updown", 5)}); count($("c1"), 0, {D["n_down"]}, {st(T, "stat", "updown", 5)}, 1.0, (v) => Math.round(v)); count($("c2"), 0, {D["n_up"]}, {st(T, "stat", "updown", 5)}+0.3, 1.0, (v) => Math.round(v));
tl.fromTo($("s2"), {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {st(T, "stat", "vol", 8)}); count($("c3"), 0, {round(vol)}, {st(T, "stat", "vol", 8)}, 1.0, (v) => Math.round(v));
for (let i = 0; i < {len(M)}; i++) {{ const t0 = {st(T, "stat", "n", 2)} + 0.4 + i * 0.12; tl.fromTo($("r" + i), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, t0); tl.fromTo($("b" + i), {{ scaleX: 0, transformOrigin: i < {sum(m["ch"] < 0 for m in M)} ? "right center" : "left center" }}, {{ scaleX: 1, duration: 0.7, ease: "power3.out" }}, t0); }}
document.querySelectorAll('[id^="{P}sd"]').forEach((e) => tl.fromTo(e, {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4, yoyo: true, repeat: 3 }}, {st(T, "steady", 1, 12)}));
tl.fromTo($("ex"), {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {st(T, "excluded", 1, 20)});'''
    return scene(T, left + svg + exc, js)


NOTES = D["weekly"].get("notes", {})
TIPS = D["weekly"]["tips"]


def rank(T):
    P = T["id"] + "-"; s = T["s"]; r = s["data"]; n = s["rank"]; name = s["short"]
    last, this, ch = r["지난"], r["이번"], r["변동"]; mx = max(last, this)
    ph = PHOTO.get(name)
    photo = (f'<div id="{P}ph" style="position:absolute;left:110px;top:560px;width:600px;height:290px;overflow:hidden;border:2px solid {GOLD}"><img id="{P}img" src="assets/img/{ph}.jpg" style="width:100%;height:100%;object-fit:cover"></div>' if ph else
             f'<div id="{P}ph" style="position:absolute;left:110px;top:560px;width:600px;height:290px;border:2px solid {GOLD};display:flex;flex-direction:column;justify-content:center;align-items:center;background:#ffffff08">'
             f'<div class="kick">ALSO KNOWN AS</div><div class="mj" style="font-size:96px;color:{GOLD2};margin-top:10px">{NOTES.get(name, "")}</div><div style="font-size:30px;color:{MUTE};margin-top:8px">{D["weekly"].get("note_sub", {}).get(name, "")}</div></div>')
    left = (f'<div class="mj" id="{P}rk" data-layout-ignore style="position:absolute;left:40px;top:40px;font-size:520px;line-height:1;color:transparent;-webkit-text-stroke:3px {GOLD}">0{n}</div>'
            f'<div style="position:absolute;left:110px;top:150px"><div class="kick">CHEAPER · 싸진 품목 {n}위</div>'
            f'<div class="mj" id="{P}nm" style="font-size:{150 if len(name) <= 3 else 118}px;line-height:1.2;margin-top:16px;text-shadow:0 6px 30px #000">{name}</div>'
            f'<div style="margin-top:10px;font-size:34px;color:{MUTE}"><span style="border:1px solid {GOLD}88;color:{GOLD2};padding:4px 16px;margin-right:16px">{"활어" if s["state"] == "활" else "선어"}</span>{r["산지"].replace("/", " · ")}</div></div>' + photo)
    bw = 640
    row = lambda i, lab, val, col: (f'<div style="margin-bottom:34px"><div style="display:flex;justify-content:space-between;align-items:baseline"><span style="font-size:36px;color:{MUTE}">{lab}</span>'
                                    f'<span class="num" style="font-size:72px;color:{col if i else IVORY}"><span id="{P}v{i}">{won(val)}</span><span style="font-size:36px;color:{MUTE}"> 원</span></span></div>'
                                    f'<div style="height:22px;background:#ffffff10;margin-top:10px"><div id="{P}bar{i}" style="height:100%;width:{val / mx * 100:.1f}%;background:{col if i else "#6B7079"}"></div></div></div>')
    right = (f'<div style="position:absolute;left:980px;top:150px;width:{bw + 200}px"><div class="kick" style="margin-bottom:36px">PRICE · kg당 경락가 중앙값</div>'
             + row(0, D["weekly"]["cmp_short"], last, IVORY) + row(1, "이번 주", this, DOWN)
             + f'<div id="{P}chg" style="display:flex;align-items:baseline;gap:24px;margin-top:20px;opacity:0"><span class="num" style="font-size:150px;line-height:1;color:{DOWN}">▼<span id="{P}cn">0</span>%</span><span style="font-size:34px;color:{MUTE}">지난주 대비</span></div>'
             + f'<div id="{P}info" style="display:flex;gap:46px;margin-top:30px;opacity:0;border-top:1px solid {GOLD}55;padding-top:22px">'
             + "".join(f'<div><div style="font-size:28px;color:{MUTE}">{a}</div><div style="font-size:38px;font-weight:700;margin-top:6px">{b}</div></div>'
                       for a, b in (("이번 주 물량", f"{r['이번물량']:,}kg"), ("거래일", f"{r['거래일']}일"), ("낙찰가 범위", r["범위"] + "원")))
             + '</div>'
             + f'<div id="{P}tip" style="margin-top:30px;padding:18px 28px;background:#ffffff0c;border-left:4px solid {GOLD};opacity:0"><span style="color:{GOLD};font-weight:800;font-size:32px;letter-spacing:.2em;margin-right:22px">TIP</span><span style="font-size:40px;font-weight:700">{TIPS.get(name, "")}</span></div>'
             + '</div>')
    js = f'''
tl.fromTo($("rk"), {{ opacity: 0, x: -40 }}, {{ opacity: 0.26, x: 0, duration: 0.9, ease: "power3.out" }}, 0.25);
tl.fromTo($("nm"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }}, 0.45);
tl.fromTo($('ph'), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.7 }}, 0.7);
{"tl.fromTo($('img'), { scale: 1.12 }, { scale: 1.0, duration: " + str(round(T["dur"], 2)) + ", ease: 'none' }, 0);" if ph else ""}
const tp = {st(T, "price", 1, 4)};
tl.fromTo($("bar0"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.8, ease: "power3.out" }}, tp);
count($("v0"), 0, {last}, tp, 0.8, W);
tl.fromTo($("bar1"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.9, ease: "power3.out" }}, tp + 0.9);
count($("v1"), {last}, {this}, tp + 0.9, 0.9, W);
const tc = {st(T, "change", 1, 7)};
tl.fromTo($("chg"), {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "back.out(1.6)" }}, tc); count($("cn"), 0, {round(abs(ch))}, tc, 1.0, (v) => Math.round(v));
tl.fromTo($("info"), {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, "vol", 1, 10)});
tl.fromTo($("tip"), {{ opacity: 0, x: 30 }}, {{ opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }}, {st(T, "tip", 1, 20)});'''
    return scene(T, left + right, js)


def trend(T):
    P = T["id"] + "-"
    TR = D["weekly"]["trend"]; rows = TR["rows"]
    cell = lambda v: f'<td class="num" style="color:{DOWN if v.startswith("▼") else (UP if v.startswith("▲") else MUTE)}">{v + ("%" if v != "—" else "")}</td>'
    tr = "".join(f'<tr id="{P}tr{i}" style="opacity:0"><td class="mj" style="text-align:left;color:{IVORY}">{n}</td>{"".join(cell(v) for v in vs)}</tr>' for i, (n, vs) in enumerate(rows))
    body = (f'<div style="position:absolute;left:0;right:0;top:140px;text-align:center"><div class="kick">{TR["kick"]}</div></div>'
            f'<table style="position:absolute;left:{300 - 90 * (len(TR["head"]) - 3)}px;top:230px;width:{1320 + 180 * (len(TR["head"]) - 3)}px;border-collapse:collapse;font-size:56px;text-align:center">'
            f'<tr style="font-size:32px;color:{GOLD}"><td style="text-align:left;padding-bottom:20px">품목</td>{"".join(f"<td>{h}</td>" for h in TR["head"])}</tr>{tr}</table>')
    extra = f"#root td{{padding:18px 10px;border-top:1px solid {GOLD}33}}"
    js = "".join(f'tl.fromTo($("tr{i}"), {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {st(T, "row", i, 2 + i * 3)});'
                 f'tl.fromTo($("tr{i}"), {{ backgroundColor: "rgba(214,178,110,0.18)" }}, {{ backgroundColor: "rgba(214,178,110,0)", duration: 2.2 }}, {st(T, "row", i, 2 + i * 3)});\n' for i in range(len(rows)))
    return scene(T, body, js, extra)


def up(T):
    P = T["id"] + "-"; cards = []
    for i, r in enumerate(T["s"]["data"]):
        ph = PHOTO.get(r["name"])
        cards.append(f'<div id="{P}c{i}" style="width:520px;background:#14161B;border:1px solid {GOLD}66;opacity:0">'
                     + (f'<div style="height:240px;overflow:hidden"><img src="assets/img/{ph}.jpg" style="width:100%;height:100%;object-fit:cover;opacity:.85"></div>' if ph else "")
                     + f'<div style="padding:26px 34px"><div class="mj" style="font-size:72px">{r["name"]}</div><div style="font-size:30px;color:{MUTE};margin-top:4px">{"활어" if r["상태"] == "활" else "선어"} · 이번 주 {r["이번물량"]:,}kg</div>'
                     f'<div style="font-size:38px;margin-top:18px"><span style="color:{MUTE}">{won(r["지난"])}</span> → <b>{won(r["이번"])}</b> 원</div>'
                     f'<div class="num" style="font-size:110px;line-height:1.05;color:{UP};margin-top:8px">▲{round(r["변동"])}%</div></div></div>')
    body = (f'<div style="position:absolute;left:0;right:0;top:130px;text-align:center"><div class="kick" style="color:{UP}">CAUTION · 다시 오른 품목</div></div>'
            f'<div style="position:absolute;left:0;right:0;top:200px;display:flex;justify-content:center;gap:44px">{"".join(cards)}</div>'
            f'<div id="{P}alt" style="position:absolute;left:0;right:0;top:820px;text-align:center;font-size:40px;opacity:0"><span style="color:{GOLD}">대안 ·</span> {D["weekly"]["up_alt"]}</div>')
    js = "".join(f'tl.fromTo($("c{i}"), {{ opacity: 0, y: 40 }}, {{ opacity: 0.22, y: 0, duration: 0.6, ease: "power3.out" }}, {0.5 + i * 0.15});'
                 f'tl.to($("c{i}"), {{ opacity: 1, duration: 0.5 }}, {st(T, "card", i, 2 + i * 6)});'
                 f'tl.fromTo($("c{i}"), {{ scale: 1 }}, {{ scale: 1.04, transformOrigin: "50% 50%", duration: 0.3, yoyo: true, repeat: 1 }}, {st(T, "card", i, 2 + i * 6)});\n' for i in range(3))
    js += f'tl.fromTo($("alt"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {st(T, "alt", 1, 25)});'
    return scene(T, body, js)


def basket(T):
    P = T["id"] + "-"; mv = {m["name"]: m["ch"] for m in D["movers"]}
    menus = D["weekly"]["basket"]
    cards = "".join(f'<div id="{P}m{i}" style="width:680px;padding:40px 50px;border:2px solid {GOLD};outline:1px solid {GOLD}66;outline-offset:10px;background:#121418;opacity:0">'
                    f'<div class="kick" style="text-align:center">MENU {i + 1}</div><div class="mj" style="font-size:76px;text-align:center;margin:14px 0 26px">{t}</div>'
                    + "".join(f'<div style="display:flex;justify-content:space-between;font-size:46px;padding:14px 0;border-top:1px dashed {GOLD}55"><span>{n} <span style="color:{MUTE};font-size:32px">{rk}</span></span><span class="num" style="color:{DOWN}">▼{abs(round(mv[n]))}%</span></div>' for n, rk in items)
                    + '</div>' for i, (t, items) in enumerate(menus))
    body = (f'<div style="position:absolute;left:0;right:0;top:130px;text-align:center"><div class="kick">THIS WEEK\'S BASKET · 이번 주 장바구니</div></div>'
            f'<div style="position:absolute;left:0;right:0;top:220px;display:flex;justify-content:center;gap:70px">{cards}</div>'
            f'<div id="{P}note" style="position:absolute;left:0;right:0;top:820px;text-align:center;font-size:34px;color:{MUTE};opacity:0">경락가는 도매 가격 · 가게 판매가는 이보다 높고 가게마다 다릅니다</div>')
    js = "".join(f'tl.fromTo($("m{i}"), {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }}, {st(T, "card", i, 2 + i * 8)});\n' for i in range(2))
    js += f'tl.fromTo($("note"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {st(T, "note", 1, 20)});'
    return scene(T, body, js)


def outro(T):
    P = T["id"] + "-"; mv = {m["name"]: m["ch"] for m in D["movers"]}
    top = D["weekly"]["recap"]
    lst = "".join(f'<div id="{P}l{i}" style="display:flex;align-items:baseline;gap:30px;padding:16px 0;border-bottom:1px solid {GOLD}44;opacity:0"><span class="mj" style="color:{GOLD};font-size:58px;width:90px">0{i + 1}</span>'
                  f'<span class="mj" style="font-size:62px;flex:1">{n}</span><span class="num" style="font-size:58px;color:{DOWN}">▼{abs(round(mv[n]))}%</span></div>' for i, n in enumerate(top))
    body = (f'<div id="{P}rec" style="position:absolute;left:560px;top:120px;width:800px"><div class="kick" style="text-align:center;margin-bottom:20px">THIS WEEK · 싸진 품목 정리</div>{lst}'
            f'<div id="{P}up" style="margin-top:26px;font-size:40px;text-align:center;opacity:0"><span style="color:{UP}">▲ 오른 품목</span> · {" · ".join(D["weekly"]["up_names"])}</div></div>'
            f'<div id="{P}dis" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:{INK}f2;opacity:0">'
            f'<div class="mj" style="font-size:84px;color:{GOLD2}">도매 경락가 ≠ 가게 판매가</div><div style="font-size:44px;color:{MUTE};margin-top:24px">자료 · 노량진수산 오늘의 경락시세 · 수량 가중 중앙값</div></div>'
            f'<div id="{P}end" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:{INK};opacity:0">'
            f'<div class="kick">EVERY SATURDAY · 매주 토요일</div><div class="mj" style="font-size:104px;margin-top:20px;line-height:1.3;text-align:center">이번 주 노량진 시세<br><span style="color:{GOLD2}">장보기 전에 받아보기</span></div>'
            f'<div style="display:flex;gap:30px;margin-top:40px"><div style="padding:16px 44px;background:#C8102E;color:#fff;font-size:48px;font-weight:800">구독</div><div style="padding:16px 44px;border:2px solid {GOLD};color:{GOLD2};font-size:48px;font-weight:800">🔔 알림 설정</div></div>'
            f'<div style="font-size:36px;color:{MUTE};margin-top:30px">재생목록 · 노량진 주간 시세 리포트</div></div>')
    r1 = st(T, "recap", 2, 2)
    js = "".join(f'tl.fromTo($("l{i}"), {{ opacity: 0, x: -30 }}, {{ opacity: 0.25, x: 0, duration: 0.45 }}, {0.5 + i * 0.12}); tl.to($("l{i}"), {{ opacity: 1, duration: 0.4 }}, {r1} + {i * 0.55});\n' for i in range(5))
    js += (f'tl.fromTo($("up"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {st(T, "recap", 4, 8)});'
           f'tl.fromTo($("dis"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {st(T, "disclaimer", 1, 14)}); tl.set($("rec"), {{ opacity: 0 }}, {st(T, "disclaimer", 1, 14)} + 0.5);'
           f'tl.fromTo($("end"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6 }}, {st(T, "end", 1, 20) - 0.3}); tl.set($("dis"), {{ opacity: 0 }}, {st(T, "end", 1, 20) + 0.4});')
    return scene(T, body, js)


def ticker():
    items = D["ticker"]
    seq = "".join(f'<span style="margin-right:56px"><span style="color:{IVORY}">{x["name"]}</span> <span style="color:{DOWN if x["ch"] < 0 else UP}">{"▼" if x["ch"] < 0 else "▲"}{abs(round(x["ch"]))}%</span></span>' for x in items)
    css = FONTS + (f'#root{{position:absolute;inset:0;font-family:PX,sans-serif}}.bar{{position:absolute;left:0;top:0;width:1920px;height:64px;background:#08090B;border-bottom:1px solid {GOLD}88;overflow:hidden}}'
                   f'.lab{{position:absolute;left:0;top:0;height:64px;padding:0 28px;background:{GOLD};color:#111;font-weight:800;font-size:28px;line-height:64px;letter-spacing:.12em;z-index:2}}'
                   f'.run{{position:absolute;left:0;top:0;white-space:nowrap;font-size:30px;font-weight:700;line-height:64px}}')
    js = f'const tl = gsap.timeline({{ paused: true }}); const w = document.getElementById("tk-run").scrollWidth / 3; tl.fromTo("#tk-run", {{ x: 360 }}, {{ x: 360 - w * 2, duration: {TOTAL:.2f}, ease: "none" }}, 0); window.__timelines["ticker"] = tl;'
    return (f'<template><style>{css}</style><div id="root" data-composition-id="ticker" data-width="1920" data-height="1080"><div class="bar"><div id="tk-run" class="run" data-layout-ignore data-layout-allow-overlap>{seq * 3}</div>'
            f'<div class="lab">노량진 주간 시세 No.{D["episode"]}</div></div></div><script>{js}</script></template>')


# ------------------------------------------------------------------ 자막 (87px 고정, 숫자 노랑, 쉼표·마침표 제거)
def one_line(x, n=18):
    out, cur = [], ""
    for w in x.split():
        if cur and len(cur) + 1 + len(w) > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out


def voice_split(wavp, lens, dur):
    n = len(lens); tot = float(sum(lens)); prop = [dur * l / tot for l in lens]
    if n == 1 or not wavp: return prop
    with wave.open(wavp) as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    hop = int(sr * 0.02); m = len(a) // hop
    if m < 10: return prop
    e = np.sqrt((a[:m * hop].reshape(m, hop) ** 2).mean(1)); act = e > max(0.02, e.max() * 0.08); cum = np.cumsum(act); tt = cum[-1]
    if tt < 5: return prop
    cuts = []; acc = 0
    for l in lens[:-1]:
        acc += l; i = int(np.searchsorted(cum, tt * acc / tot)); j = i
        while j < m - 1 and not act[j + 1]: j += 1
        cuts.append((i + j) / 2 * hop / sr)
    pts = [0.0] + cuts + [len(a) / sr]
    return [max(0.25, pts[i + 1] - pts[i]) for i in range(n)]


def captions():
    out = []; k = 0
    for T in TL:
        for x in T["S"]:
            sub = re.sub(r"\s{2,}", " ", re.sub(r"(?<!\d)[,.]|[,.](?!\d)", "", disp(x["text"]))).strip()
            lines = one_line(sub); durs = voice_split(x["wav"], [len(l) for l in lines], x["dur"]); t0 = T["start"] + x["start"]
            for l, du in zip(lines, durs):
                h = re.sub(r"(\d[\d,~·.%]*(?:원|kg|위|가지|일|월|%)?)", r"<b>\1</b>", l)
                out.append(f'<div class="clip cap" id="cap{k}" data-start="{t0:.3f}" data-duration="{du:.3f}" data-track-index="1"><span>{h}</span></div>'); k += 1; t0 += du
    css = (FONTS + '#root{position:absolute;inset:0;font-family:PX,sans-serif}.cap{position:absolute;left:0;right:0;bottom:56px;text-align:center;overflow:visible}'
           '.cap span{display:inline-block;background:rgba(0,0,0,.56);color:#fff;font-size:87px;font-weight:700;line-height:1.2;padding:6px 26px;white-space:nowrap}.cap b{color:#FFD640;font-weight:700}')
    return (f'<template><style>{css}</style><div id="root" data-composition-id="captions" data-width="1920" data-height="1080">{"".join(out)}</div>'
            '<script>const tl = gsap.timeline({ paused: true }); window.__timelines["captions"] = tl;</script></template>'), k


def main():
    if os.path.exists(HF): shutil.rmtree(HF)
    os.makedirs(f"{HF}/compositions"); os.makedirs(f"{HF}/assets/fonts"); os.makedirs(f"{HF}/assets/img")
    tpl = "/home/user/kimhyeoncheol/.claude/skills/ranking-video/templates/hyperframes_movers"
    for f in ("hyperframes.json", "package.json"): shutil.copy(f"{tpl}/{f}", f"{HF}/{f}")
    json.dump(dict(id="weekly03", name="weekly03", createdAt="2026-11-05T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
    for f in ("NanumMyeongjo-ExtraBold.ttf", "Pretendard-Bold.otf", "Pretendard-SemiBold.otf", "Pretendard-ExtraBold.otf"): shutil.copy(f"{FONTDIR}/{f}", f"{HF}/assets/fonts/{f}")
    for n, i in PHOTO.items(): shutil.copy(f"{IMG}/{i}.jpg", f"{HF}/assets/img/{i}.jpg")
    F = dict(hook=hook, title=title, overview=overview, rank=rank, trend=trend, up=up, basket=basket, outro=outro)
    hosts = []
    for T in TL:
        open(f"{HF}/compositions/{T['id']}.html", "w", encoding="utf-8").write(F[T["s"]["kind"]](T))
        hosts.append(f'<div id="{T["id"]}" data-composition-id="{T["id"]}" data-composition-src="compositions/{T["id"]}.html" data-start="{T["start"]:.3f}" data-duration="{T["dur"]:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
    open(f"{HF}/compositions/ticker.html", "w", encoding="utf-8").write(ticker())
    cap, k = captions(); open(f"{HF}/compositions/captions.html", "w", encoding="utf-8").write(cap)
    hosts.append(f'<div id="ticker" data-composition-id="ticker" data-composition-src="compositions/ticker.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="2" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index:40"></div>')
    hosts.append(f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="3" data-track-kind="captions" data-width="1920" data-height="1080" style="z-index:50"></div>')
    audio = f'<audio id="narr" src="assets/audio.wav" data-start="0" data-duration="{TOTAL:.3f}" data-volume="1" data-track-index="5"></audio>'
    open(f"{HF}/index.html", "w", encoding="utf-8").write(
        f'<!doctype html><html lang="ko"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
        f'<style>html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:{INK}}}</style></head><body>'
        f'<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080">{"".join(hosts)}{audio}</div>'
        f'<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script></body></html>')
    json.dump(dict(total=round(TOTAL, 2), sections=[dict(id=T["id"], name=T["s"]["name"], kind=T["s"]["kind"], start=round(T["start"], 2)) for T in TL]),
              open(f"{HERE}/timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"장면 {len(TL)} · 자막 {k} · 총 {int(TOTAL // 60)}:{int(TOTAL % 60):02d}{' (추정)' if EST else ''}")


if __name__ == "__main__":
    main()
