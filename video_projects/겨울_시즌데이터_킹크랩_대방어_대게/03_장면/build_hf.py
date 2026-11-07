# -*- coding: utf-8 -*-
"""겨울 시즌 데이터 롱폼 — 에디토리얼 골드(주간 시세 #3과 같은 스타일) HyperFrames 프로젝트 생성
사용: python3 build_hf.py [--est]  → hf/ , timeline.json
장면: hook · title · item(킹크랩/대방어/대게: 챕터 카드 → 시즌 그래프 + 오른쪽 정보 카드 → 정리) · dow · faq · calendar · outro
"""
import json, os, re, shutil, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EST = "--est" in sys.argv
D = json.load(open(f"{ROOT}/01_대본/대본데이터.json", encoding="utf-8"))
DATA = json.load(open(f"{ROOT}/00_data/data.json", encoding="utf-8")); MON = json.load(open(f"{ROOT}/00_data/monthly.json", encoding="utf-8"))
TTS = f"{ROOT}/02_음성"; HF = f"{HERE}/hf"; IMG = f"{ROOT}/09_소재/img_final"
PHOTO = json.load(open(f"{IMG}/pick.json", encoding="utf-8"))
FONTDIR = os.path.expanduser("~/.cache/ranking-video/fonts")
GAP, LEAD = 0.5, 0.7
INK, GOLD, GOLD2, IVORY, MUTE, DOWN, UP, GREY = "#0D0E11", "#D6B26E", "#F1D9A0", "#F2EDE3", "#8C919B", "#5FB7A6", "#E4775F", "#6B7079"
FONTS = ('@font-face{font-family:"MJ";src:url("assets/fonts/NanumMyeongjo-ExtraBold.ttf");font-weight:800}'
         '@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-Bold.otf");font-weight:700}'
         '@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-SemiBold.otf");font-weight:500}'
         '@font-face{font-family:"PXB";src:url("assets/fonts/Pretendard-ExtraBold.otf");font-weight:800}')
W = lambda v: f"{int(v):,}"
WEEKS = [f"{m:02d}월{k}주" for m in (10, 11, 12, 1, 2, 3) for k in (1, 2, 3, 4)]


def wlen(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()


secs = D["sections"]; t = 0.0; TL = []
for si, s in enumerate(secs):
    cur = LEAD; S = []
    for ti, x in enumerate(s["sentences"]):
        p = f"{TTS}/{si:02d}_{ti:02d}.wav"
        if os.path.exists(p): du = wlen(p); wav = p
        elif EST: du = len(x[0].replace(" ", "")) / 6.8 + 0.2; wav = None
        else: raise SystemExit("음성 없음 " + p)
        S.append(dict(text=x[0], sig=x[1], sub=x[2], start=cur, dur=du, wav=wav)); cur += du + GAP
    dur = cur + (2.2 if s["kind"] in ("outro", "calendar") else 0.9)
    TL.append(dict(s=s, id=f"sc{si:02d}", start=t, dur=dur, S=S)); t += dur
TOTAL = t


def st(T, key, val=True, default=None):
    for x in T["S"]:
        v = x["sig"].get(key)
        if v is not None and (val is True or v == val): return round(max(0.2, x["start"] - 0.1), 3)
    if default is None: raise KeyError(f"{T['id']} {key}={val}")
    return default


def css_base(extra=""):
    return (FONTS + f"#root{{position:absolute;inset:0;overflow:hidden;color:{IVORY};font-family:PX,sans-serif}}#root *{{box-sizing:border-box}}"
            f".bg{{position:absolute;inset:0;background:radial-gradient(1500px 900px at 30% 20%,#1A1C22 0%,{INK} 60%,#08090B 100%)}}"
            f".frame{{position:absolute;left:36px;top:36px;right:36px;bottom:24px;border:1px solid {GOLD}55}}"
            f".hdr{{position:absolute;left:70px;top:54px;font-size:28px;letter-spacing:.18em;color:{GOLD}aa;font-weight:700}}"
            f".wipe{{position:absolute;left:0;top:538px;width:1920px;height:3px;background:linear-gradient(90deg,transparent,{GOLD2},{GOLD},transparent)}}"
            f".mj{{font-family:MJ,serif;font-weight:800}}.num{{font-family:PXB,PX,sans-serif;font-weight:800;font-variant-numeric:tabular-nums}}"
            f".kick{{font-size:32px;letter-spacing:.3em;color:{GOLD};font-weight:700}}"
            f".card{{position:absolute;opacity:0;background:#13151A;border:1px solid {GOLD}66;padding:34px 40px}}" + extra)


def scene(T, body, js, extra_css="", hdr=True, fade=True):
    P = T["id"] + "-"; sid = T["id"]
    js0 = f'''
const tl = gsap.timeline({{ paused: true }}); const $ = (i) => "#{P}" + i;
tl.fromTo($("wipe"), {{ scaleX: 0, opacity: 1, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.6, ease: "power3.inOut" }}, 0);
tl.to($("wipe"), {{ opacity: 0, duration: 0.4 }}, 0.6);
{"tl.fromTo($('content'), { opacity: 0 }, { opacity: 1, duration: 0.6 }, 0.3);" if fade else ""}
function count(sel, from, to, at, dur, fmt) {{ const o = {{ v: from }}; tl.to(o, {{ v: to, duration: dur || 1.2, ease: "power2.out", onUpdate: () => {{ document.querySelector(sel).textContent = fmt(o.v); }} }}, at); }}
const Wf = (v) => Math.round(v).toLocaleString("en-US");
function show(id, a, b) {{ tl.fromTo($(id), {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, a); if (b !== undefined && b !== null) tl.to($(id), {{ opacity: 0, duration: 0.35 }}, b); }}
'''
    h = f'<div class="hdr">노량진수산시장 · 겨울 장보기 데이터 리포트</div>' if hdr else ""
    return (f'<template><style>{css_base(extra_css)}</style><div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">'
            f'<div class="bg"></div><div class="frame"></div>{h}<div id="{P}content" style="position:absolute;inset:0">{body}</div><div class="wipe" id="{P}wipe"></div></div>'
            f'<script>{js0}{js}\nwindow.__timelines["{sid}"] = tl;</script></template>')


def seq(T, items):
    """[(id, key, val)] 순서대로 나타나고 다음 것이 나오면 사라짐"""
    out = []; times = [st(T, k, v) for _, k, v in items]
    for i, (cid, _, _) in enumerate(items):
        nxt = times[i + 1] - 0.25 if i + 1 < len(items) else None
        out.append(f'show("{cid}", {times[i]}, {nxt if nxt is not None else "null"});')
    return "\n".join(out)


# ------------------------------------------------------------------ 오프닝
def hook(T):
    P = T["id"] + "-"
    big = lambda i, lab, val, col: (f'<div style="text-align:center"><div style="font-size:40px;color:{MUTE}">{lab}</div>'
                                    f'<div class="num" style="font-size:150px;color:{col};line-height:1.1">+<span id="{P}h{i}">0</span><span style="font-size:60px">원</span></div><div style="font-size:34px;color:{MUTE}">kg당 · 11월 말 대비 크리스마스 주</div></div>')
    body = (f'<div id="{P}q" class="card" style="left:0;right:0;top:300px;background:none;border:none;text-align:center"><div class="kick">QUESTION</div>'
            f'<div class="mj" style="font-size:118px;line-height:1.25;margin-top:20px">크리스마스 주에<br>킹크랩을 사면?</div></div>'
            f'<div id="{P}c1" class="card" style="left:160px;right:160px;top:230px;display:flex;justify-content:space-around;background:none;border:none">'
            + big(1, "재작년 겨울 (24–25)", 34100, UP) + big(2, "작년 겨울 (25–26)", 16700, UP) + '</div>'
            f'<div id="{P}c2" class="card" style="left:260px;right:260px;top:260px;text-align:center"><div class="kick">2kg 한 마리라면</div>'
            f'<div class="num" style="font-size:130px;color:{GOLD2};margin-top:16px">33,400 ~ 68,200<span style="font-size:60px">원</span></div><div style="font-size:38px;color:{MUTE}">도매 경락가 기준 차이</div></div>'
            f'<div id="{P}c3" class="card" style="left:120px;right:120px;top:220px;display:flex;gap:40px;background:none;border:none">'
            + "".join(f'<div style="flex:1;border:1px solid {GOLD}66"><div style="height:330px;overflow:hidden"><img src="assets/img/{PHOTO[n]}.jpg" style="width:100%;height:100%;object-fit:cover"></div><div class="mj" style="font-size:72px;text-align:center;padding:18px 0">{n}</div></div>' for n in ("킹크랩", "대방어", "대게"))
            + '</div>'
            f'<div id="{P}c4" class="card" style="left:300px;right:300px;top:270px;text-align:center;background:none;border:none"><div class="kick">2 SEASONS · WEEKLY</div>'
            f'<div class="mj" style="font-size:100px;margin-top:20px">경락가 2년 치를<br>주 단위로 계산</div></div>'
            f'<div id="{P}c5" class="card" style="left:360px;right:360px;top:230px;text-align:center"><div class="kick">끝까지 보면</div><div class="mj" style="font-size:96px;margin-top:20px;color:{GOLD2}">올겨울 장보기 달력</div>'
            f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-top:30px">' + "".join(f'<div style="height:56px;background:{c}"></div>' for c in [DOWN, "#3a3d44", UP, UP, "#3a3d44", "#3a3d44"] * 3) + '</div></div>')
    js = (f'tl.set($("q"), {{ opacity: 1 }}, 0); tl.fromTo($("q"), {{ scale: 1.06, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 1.2, ease: "power3.out" }}, 0);'
          f'tl.to($("q"), {{ opacity: 0, duration: 0.35 }}, {st(T, "hook", 1)} - 0.25);'
          + seq(T, [("c1", "hook", 1), ("c2", "hook", 2), ("c3", "hook", 3), ("c4", "hook", 4), ("c5", "hook", 5)])
          + f'count($("h1"), 0, 34100, {st(T, "hook", 1)} + 0.3, 1.4, Wf); count($("h2"), 0, 16700, {st(T, "hook", 1)} + 0.9, 1.4, Wf);')
    return scene(T, body, js, hdr=False, fade=False)


def title(T):
    P = T["id"] + "-"
    rows = [("킹크랩", "(활)왕게 kg단가 전체"), ("대방어", "(활)방어 규격 ‘1미’ kg단가"), ("대게", "(활)대게 kg단가")]
    body = (f'<div style="position:absolute;inset:0;opacity:.18"><img src="assets/img/{PHOTO["시장"]}.jpg" style="width:100%;height:100%;object-fit:cover"></div>'
            f'<div id="{P}t" class="card" style="left:0;right:0;top:200px;background:none;border:none;text-align:center"><div class="kick">NORYANGJIN FISH MARKET · WINTER DATA REPORT</div>'
            f'<div class="mj" style="font-size:140px;margin-top:26px">겨울 장보기 데이터</div><div style="font-size:44px;color:{MUTE};margin-top:10px">킹크랩 · 대방어 · 대게</div></div>'
            f'<div id="{P}src" class="card" style="left:260px;right:260px;top:250px;text-align:center"><div class="kick">SOURCE</div><div style="font-size:56px;font-weight:700;margin-top:18px">노량진수산(주) 어종별 경락시세</div>'
            f'<div style="font-size:40px;color:{MUTE};margin-top:12px">새벽 경매 낙찰가 · 도매 가격 · susansijang.co.kr</div></div>'
            f'<div id="{P}per" class="card" style="left:200px;right:200px;top:250px;text-align:center"><div class="kick">PERIOD</div><div style="display:flex;justify-content:center;gap:30px;margin-top:26px">'
            + "".join(f'<div style="padding:22px 36px;border:1px solid {c};font-size:46px;font-weight:700;color:{c}">{a}</div>' for a, c in (("2024.10 – 2025.03", MUTE), ("2025.10 – 2026.03", GOLD2), ("2026.10 – 11월 1주", DOWN)))
            + '</div></div>'
            f'<div id="{P}defs" class="card" style="left:300px;right:300px;top:220px"><div class="kick">DEFINITIONS</div>'
            + "".join(f'<div style="display:flex;justify-content:space-between;font-size:50px;padding:22px 0;border-bottom:1px solid {GOLD}33"><span class="mj">{a}</span><span style="color:{MUTE};font-size:42px">{b}</span></div>' for a, b in rows)
            + f'<div id="{P}m" style="font-size:38px;color:{GOLD2};margin-top:26px;opacity:0">물량 가중평균 · 1~7일=1주 … 22일~말일=4주</div></div>'
            f'<div id="{P}warn" class="card" style="left:240px;right:240px;top:230px"><div class="kick" style="color:{UP}">꼭 알아 두세요</div>'
            f'<div id="{P}w1" style="font-size:54px;font-weight:700;margin-top:26px;opacity:0">① 경락가 = 도매 낙찰가 <span style="color:{MUTE}">≠ 가게 판매가</span></div>'
            f'<div id="{P}w2" style="font-size:54px;font-weight:700;margin-top:26px;opacity:0">② 지난 2년의 흐름 <span style="color:{MUTE}">≠ 올해 보장</span></div></div>')
    js = (f'tl.set($("t"), {{ opacity: 1 }}, 0.3); tl.to($("t"), {{ opacity: 0, duration: 0.3 }}, {st(T, "src", 1)} - 0.25);'
          + seq(T, [("src", "src", 1), ("per", "period", 1), ("defs", "defs", 1), ("warn", "warn", 0)])
          + f'tl.to($("m"), {{ opacity: 1, duration: 0.5 }}, {st(T, "method", 1)}); tl.to($("w1"), {{ opacity: 1, duration: 0.5 }}, {st(T, "warn", 1)}); tl.to($("w2"), {{ opacity: 1, duration: 0.5 }}, {st(T, "warn", 2)});'
          + f'tl.set($("warn"), {{ opacity: 1 }}, {st(T, "warn", 2)} + 0.1);')
    return scene(T, body, js)


# ------------------------------------------------------------------ 품목 장면
ITEMS = {
 "킹크랩": dict(photo="킹크랩", ymin=35000, ymax=97000, step=20000, cheap=("11월4주", "12월1주"), hot=("12월3주", "12월4주"),
   marks=[("25-26", "12월4주", "작년 85,700"), ("24-25", "12월4주", "재작년 92,800")], low=[("24-25", "11월4주", "58,700"), ("25-26", "12월1주", "69,000")],
   cards=[("lines", True, "범례", ["<b style='color:#8C919B'>━</b> 재작년 겨울 24–25", f"<b style='color:{GOLD}'>━</b> 작년 겨울 25–26", f"<b style='color:{DOWN}'>━</b> 올해 26–27"]),
          ("peak", 1, "시즌 꼭대기 · 12월 4주", ["재작년 <b class='num'>92,800</b>원", "작년 <b class='num'>85,700</b>원"]),
          ("vol", 1, "그 주 물량 · 시즌 최다", ["재작년 <b class='num'>15,501</b>kg", "작년 <b class='num'>16,865</b>kg"]),
          ("cheap", 1, "연말 직전 숨 고르기", ["재작년 11월 4주 <b class='num'>58,700</b>원", "작년 12월 1주 <b class='num'>69,000</b>원"]),
          ("compare", 1, "크리스마스 주보다", [f"재작년 <b class='num' style='color:{DOWN}'>37%</b> 쌌다", f"작년 <b class='num' style='color:{DOWN}'>20%</b> 쌌다"]),
          ("jan", 2, "1월 네 주", ["<b class='num'>74,100 ~ 84,900</b>원", "두 시즌 모두"]),
          ("seol", 2, "작년 설(2/17) 주", ["설 주 <b class='num'>81,500</b>원", "전 주 <b class='num'>61,900</b>원", f"<b class='num' style='color:{UP}'>+32%</b>"]),
          ("month", 2, "월별 평균 vs 시즌 평균", None),
          ("this", 2, "올해 11월 1주", ["<b class='num'>62,200</b>원", f"작년 같은 주 69,800원보다 <b style='color:{DOWN}'>11% 낮음</b>"]),
          ("this", 5, "올해 10월 4주 물량", ["<b class='num'>11,101</b>kg", "재작년 10,901 · 작년 7,480kg"]),
          ("tip", 1, "살값으로 비교", ["kg당 가격 ÷ 수율", "<b class='num'>95,000</b>원 ÷ 80% ≈ <b class='num'>118,000</b>원"], "킹크랩3"),
          ("tip", 3, "레드 · 블루 · 브라운", ["레드 = 가을~겨울", "블루 = 봄~여름"], "킹크랩2"),
          ("tip", 4, "등딱지 가운데 돌기", ["6개 = 레드", "4개 = 블루"], None),
          ("tip", 2, "다리 확인", ["눌러서 탄력", "다리가 다 붙어 있는지"], "킹크랩4")],
   avoid=["12월 3·4주 (크리스마스·연말)", "설 직전 주"], aim=["11월 4주 ~ 12월 1주"]),
 "대방어": dict(photo="대방어", ymin=8000, ymax=32000, step=5000, cheap=("01월1주", "01월2주"), hot=("11월2주", "11월3주"), start2425="12월2주",
   marks=[("25-26", "11월2주", "작년 29,700"), ("25-26", "11월3주", "28,500")], low=[("25-26", "01월1주", "16,700"), ("24-25", "01월2주", "14,200")],
   cards=[("note", 2, "재작년 초반 물량", ["10월 ~ 12월 1주", "한 주 <b class='num'>2 ~ 204</b>kg", "→ 12월 2주부터 표시"]),
          ("peak", 2, "작년 꼭대기 · 11월", ["11월 2주 <b class='num'>29,700</b>원", "11월 3주 <b class='num'>28,500</b>원"]),
          ("vol", 1, "물량 최다 · 12월 4주", ["재작년 <b class='num'>88,203</b>kg", "작년 <b class='num'>97,784</b>kg"]),
          ("cheap", 3, "1월 초가 쌌다", ["작년 1월 1주 <b class='num'>16,700</b>원", "재작년 1월 2주 <b class='num'>14,200</b>원"]),
          ("compare", 1, "작년 11월 2주보다", [f"1월 1주 <b class='num' style='color:{DOWN}'>44%</b> 쌌다"]),
          ("feb", 2, "2월은 시즌마다 달랐다", ["재작년 <b class='num'>17,500 ~ 23,600</b>원", "작년 <b class='num'>14,900 ~ 22,400</b>원"]),
          ("mar", 2, "3월 · 시즌 끝자락", ["재작년 <b class='num'>9,400 ~ 12,000</b>원", "작년 <b class='num'>12,100 ~ 19,400</b>원", "물량은 크게 줄어듦"]),
          ("month", 1, "월별 평균 vs 시즌 평균", None),
          ("season", 1, "제철 · 11월~2월", ["기름 절정 12월~1월", "값은 1월에 내려감"]),
          ("this", 2, "올해 11월 1주", ["<b class='num'>23,600</b>원", f"작년 같은 주 17,600원보다 <b style='color:{UP}'>34% 높음</b>"]),
          ("this", 6, "올해 10월 4주", ["물량 <b class='num'>39,013</b>kg (작년 24,911)", "값 <b class='num'>16,300</b>원 → 한 주 만에 상승"]),
          ("tip", 1, "크기 기준 없음", ["가게마다 기준이 다름", "몇 kg짜리인지 꼭 묻기"], "대방어2"),
          ("tip", 3, "수율 (셰프 계산)", ["4kg 방어 → 순살 약 <b class='num'>1.6</b>kg", "약 41%"], "대방어3"),
          ("tip", 2, "방어 vs 부시리", ["위턱 끝 각지면 방어", "눈 맑고 아가미 선홍빛"], None)],
   avoid=["11월 중순", "12월"], aim=["1월 1·2주", "(3월은 물량 적음)"]),
 "대게": dict(photo="대게", ymin=15000, ymax=72000, step=15000, cheap=("02월3주", "03월3주"), hot=("01월1주", "01월2주"),
   marks=[("24-25", "02월1주", "재작년 67,600"), ("25-26", "10월3주", "작년 58,500")], low=[("24-25", "10월3주", "20,200"), ("25-26", "03월3주", "34,700")],
   cards=[("peak", 1, "꼭대기는 해마다 달랐다", ["재작년 2월 1주 <b class='num'>67,600</b>원", "작년 10월 3주 <b class='num'>58,500</b>원"]),
          ("peak", 3, "두 해 모두 비싼 1월 초", ["재작년 1월 2주 <b class='num'>50,700</b>원", "작년 1월 1주 <b class='num'>57,500</b>원"]),
          ("cheap", 2, "두 시즌 최저", ["재작년 10월 3주 <b class='num'>20,200</b>원"]),
          ("cheap", 3, "2월 말 ~ 3월", ["재작년 2월 3주 <b class='num'>29,300</b>원", "작년 3월 3주 <b class='num'>34,700</b>원"]),
          ("vol", 2, "물량이 늘자 값이 내렸다", ["작년 1월 4주 <b class='num'>16,423</b>kg → <b class='num'>39,500</b>원", "1월 1주 <b class='num'>2,998</b>kg → <b class='num'>57,500</b>원"]),
          ("month", 1, "월별 평균 vs 시즌 평균", None),
          ("this", 1, "올해 10월 4주 → 11월 1주", ["<b class='num'>30,400</b> → <b class='num'>40,400</b>원"]),
          ("this", 2, "작년 같은 주보다", [f"43,300원보다 <b style='color:{DOWN}'>7% 낮음</b>"]),
          ("tip", 1, "고르는 법", ["다리가 온전한지", "움직임이 힘찬지"], "대게2")],
   avoid=["1월 초"], aim=["2월 말 ~ 3월"]),
}


def item(T):
    P = T["id"] + "-"; name = T["s"]["item"]; C = ITEMS[name]; d = DATA[name]
    X0, X1, Y0, Y1 = 150, 1250, 120, 620
    xi = lambda w: X0 + WEEKS.index(w) * (X1 - X0) / 23
    yv = lambda v: Y1 - (v - C["ymin"]) / (C["ymax"] - C["ymin"]) * (Y1 - Y0)
    svg = [f'<rect x="0" y="0" width="1300" height="720" fill="#ffffff07"/>']
    for v in range(C["ymin"] - C["ymin"] % C["step"] + C["step"], C["ymax"], C["step"]):
        svg.append(f'<line x1="{X0}" y1="{yv(v):.1f}" x2="{X1}" y2="{yv(v):.1f}" stroke="#fff" stroke-opacity=".1" stroke-width="2" stroke-dasharray="6 10"/><text x="{X0 - 16}" y="{yv(v) + 10:.1f}" font-size="30" fill="{MUTE}" text-anchor="end">{v // 10000}{"." + str(v % 10000 // 1000) if v % 10000 else ""}만</text>')
    for i, m in enumerate((10, 11, 12, 1, 2, 3)):
        x = xi(f"{m:02d}월1주"); svg.append(f'<line x1="{x:.1f}" y1="{Y0 - 20}" x2="{x:.1f}" y2="{Y1 + 10}" stroke="#fff" stroke-opacity=".08" stroke-width="2"/><text x="{x + 6:.1f}" y="{Y1 + 56}" font-size="36" font-weight="700" fill="{IVORY}">{m}월</text>')
    a, b = C["cheap"]; h1, h2 = C["hot"]
    svg.append(f'<rect id="{P}band" x="{xi(a) - 22:.1f}" y="{Y0 - 20}" width="{xi(b) - xi(a) + 44:.1f}" height="{Y1 - Y0 + 30}" fill="{DOWN}" opacity="0"/>')
    svg.append(f'<rect id="{P}hot" x="{xi(h1) - 22:.1f}" y="{Y0 - 20}" width="{xi(h2) - xi(h1) + 44:.1f}" height="{Y1 - Y0 + 30}" fill="{UP}" opacity="0"/>')
    for s, col, wd in (("24-25", GREY, 6), ("25-26", GOLD, 8), ("26-27", DOWN, 9)):
        rows = d[s]
        if s == "24-25" and C.get("start2425"): rows = rows[[r["w"] for r in rows].index(C["start2425"]):]
        pts = " ".join(f"{xi(r['w']):.1f},{yv(r['p']):.1f}" for r in rows)
        svg.append(f'<polyline id="{P}l{s[:2]}" points="{pts}" fill="none" stroke="{col}" stroke-width="{wd}" stroke-linejoin="round" stroke-linecap="butt" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" opacity="0"/>')
        if s == "26-27": svg += [f'<circle class="{P}d26" cx="{xi(r["w"]):.1f}" cy="{yv(r["p"]):.1f}" r="9" fill="{DOWN}" opacity="0"/>' for r in rows]
    for i, (s, w, lab) in enumerate(C["marks"]):
        r = next(r for r in d[s] if r["w"] == w); x, y = xi(w), yv(r["p"])
        svg.append(f'<g id="{P}mk{i}" opacity="0"><circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{UP}" stroke-width="5"/><text x="{x + (70 if i else 0):.1f}" y="{y - 30 - (0 if i else 0):.1f}" font-size="34" font-weight="800" fill="{UP}" text-anchor="{"start" if i else "end"}" style="paint-order:stroke;stroke:{INK};stroke-width:10px">{lab}</text></g>')
    for i, (s, w, lab) in enumerate(C["low"]):
        r = next(r for r in d[s] if r["w"] == w); x, y = xi(w), yv(r["p"])
        svg.append(f'<g id="{P}lo{i}" opacity="0"><circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{DOWN}" stroke-width="5"/><text x="{x:.1f}" y="{y + 54 + i * 38:.1f}" font-size="34" font-weight="800" fill="{DOWN}" text-anchor="middle" style="paint-order:stroke;stroke:{INK};stroke-width:10px">{lab}</text></g>')
    chart = (f'<div id="{P}chart" style="position:absolute;left:60px;top:150px;opacity:0"><div style="font-size:34px;color:{MUTE};margin:0 0 10px 20px">{name} · kg당 주간 평균 경락가 (원)</div>'
             f'<svg width="1300" height="720" viewBox="0 0 1300 720">{"".join(svg)}</svg></div>')
    cards = []; times = []
    for ci, cd in enumerate(sorted(C["cards"], key=lambda c: st(T, c[0], c[1]))):
        key, val, ttl, lines = cd[0], cd[1], cd[2], cd[3]; ph = cd[4] if len(cd) > 4 else None
        if lines is None:  # 월별 막대
            rel = MON[name]["rel"]
            inner = "".join(f'<div style="display:flex;align-items:center;gap:14px;font-size:34px;margin:10px 0"><span style="width:70px">{m}월</span><div style="flex:1;height:30px;position:relative">'
                            f'<div style="position:absolute;left:50%;top:0;height:30px;width:{min(abs(v), 45) / 45 * 50:.1f}%;{"right:50%;left:auto" if v < 0 else ""};background:{DOWN if v < 0 else UP}"></div>'
                            f'<div style="position:absolute;left:50%;top:-4px;width:2px;height:38px;background:{GOLD}"></div></div><span class="num" style="width:96px;text-align:right;color:{DOWN if v < 0 else UP}">{v:+.0f}%</span></div>'
                            for m, v in rel.items())
        else:
            inner = "".join(f'<div style="font-size:{44 if len(lines) <= 2 else 40}px;font-weight:700;margin:14px 0;line-height:1.3">{ln}</div>' for ln in lines)
        img = f'<div style="height:230px;margin:-34px -40px 24px;overflow:hidden"><img src="assets/img/{PHOTO[ph]}.jpg" style="width:100%;height:100%;object-fit:cover"></div>' if ph else ""
        cards.append(f'<div id="{P}k{ci}" class="card" style="left:1390px;width:470px;top:170px">{img}<div class="kick" style="font-size:30px;letter-spacing:.12em">{ttl}</div>{inner}</div>')
        times.append(st(T, key, val))
    tsum = st(T, "summary", 1)
    cjs = "\n".join(f'show("k{i}", {times[i]}, {times[i + 1] - 0.3 if i + 1 < len(times) and times[i + 1] > times[i] else tsum - 0.2});' for i in range(len(times)))
    chap = (f'<div id="{P}chap" style="position:absolute;inset:0"><img id="{P}cimg" src="assets/img/{PHOTO[C["photo"]]}.jpg" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">'
            f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,{INK}f2 0%,{INK}b0 45%,{INK}40 100%)"></div>'
            f'<div style="position:absolute;left:140px;top:330px"><div class="kick">CHAPTER {["킹크랩", "대방어", "대게"].index(name) + 1:02d}</div><div class="mj" style="font-size:220px;line-height:1.15;margin-top:10px">{name}</div>'
            f'<div style="font-size:40px;color:{GOLD2}">언제 사야 쌀까</div></div></div>')
    summ = (f'<div id="{P}sum" style="position:absolute;inset:0;background:{INK}f4;opacity:0;display:flex;justify-content:center;align-items:center;gap:80px">'
            f'<div style="width:700px;border-top:6px solid {UP};padding:36px 40px;background:#16181D"><div class="kick" style="color:{UP}">피할 때</div>' + "".join(f'<div class="mj" style="font-size:58px;margin-top:22px">{x}</div>' for x in C["avoid"]) + '</div>'
            f'<div style="width:700px;border-top:6px solid {DOWN};padding:36px 40px;background:#16181D"><div class="kick" style="color:{DOWN}">노릴 때</div>' + "".join(f'<div class="mj" style="font-size:58px;margin-top:22px">{x}</div>' for x in C["aim"]) + '</div>'
            f'<div style="position:absolute;top:150px;left:0;right:0;text-align:center" class="mj"><span style="font-size:80px">{name} 정리</span></div></div>')
    tc, tch = st(T, "chapter", 1), st(T, "chart", 1)
    js = (f'tl.fromTo($("cimg"), {{ scale: 1.12 }}, {{ scale: 1, duration: {tch + 0.5:.2f}, ease: "none" }}, 0); tl.to($("chap"), {{ opacity: 0, duration: 0.5 }}, {tch} - 0.2);'
          f'show("chart", {tch});'
          f'tl.set($("l24"), {{ opacity: 1 }}, {tch} + 0.3); tl.to($("l24"), {{ strokeDashoffset: 0, duration: 2.2, ease: "power2.inOut" }}, {tch} + 0.3);'
          f'tl.set($("l25"), {{ opacity: 1 }}, {tch} + 1.2); tl.to($("l25"), {{ strokeDashoffset: 0, duration: 2.2, ease: "power2.inOut" }}, {tch} + 1.2);'
          f'tl.to($("hot"), {{ opacity: 0.16, duration: 0.6 }}, {st(T, "peak", 1)});'
          + "".join(f'tl.fromTo($("mk{i}"), {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2)" }}, {st(T, "peak", 1)} + {0.4 + i * 0.6});' for i in range(len(C["marks"])))
          + f'tl.to($("band"), {{ opacity: 0.18, duration: 0.6 }}, {st(T, "cheap", 1)});'
          + "".join(f'tl.fromTo($("lo{i}"), {{ opacity: 0, scale: 0.6, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2)" }}, {st(T, "cheap", 1)} + {0.6 + i * 0.6});' for i in range(len(C["low"])))
          + f'const t26 = {st(T, "this", 1, st(T, "this", 2, 0))}; tl.set($("l26"), {{ opacity: 1 }}, t26); tl.to($("l26"), {{ strokeDashoffset: 0, duration: 1.4, ease: "power2.out" }}, t26);'
          + f'tl.to(".{P}d26", {{ opacity: 1, duration: 0.3, stagger: 0.15 }}, t26 + 0.4);'
          + cjs + f'\ntl.to($("sum"), {{ opacity: 1, duration: 0.6 }}, {st(T, "summary", 1)});')
    return scene(T, chap + chart + "".join(cards) + summ, js)


def dow(T):
    P = T["id"] + "-"; DAYS = ["월", "화", "수", "목", "금", "토"]; panels = []
    for i, n in enumerate(("킹크랩", "대방어", "대게")):
        y = DATA[n]["요일"]; lo, hi = min(y.values()), max(y.values()); base = lo * 0.86
        bars = "".join(f'<div style="flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:420px">'
                       f'<div class="num" style="font-size:28px;letter-spacing:-0.03em;color:{DOWN if v == lo else (UP if v == hi else MUTE)}">{round(v, -2) / 10000:.2f}만</div>'
                       f'<div class="{P}b{i}" style="width:62px;height:{(v - base) / (hi - base) * 330:.0f}px;background:{DOWN if v == lo else (UP if v == hi else "#4a4e57")};margin-top:8px"></div>'
                       f'<div style="font-size:36px;font-weight:700;margin-top:10px;color:{IVORY if d not in ("토",) else UP}">{d}</div></div>' for d, v in y.items())
        diff = (hi / lo - 1) * 100
        panels.append(f'<div id="{P}p{i}" style="width:590px;opacity:0"><div class="mj" style="font-size:64px;text-align:center">{n}</div>'
                      f'<div style="font-size:32px;text-align:center;color:{MUTE};margin:6px 0 14px">가장 싼 요일 대비 <b style="color:{UP}">+{diff:.0f}%</b></div><div style="display:flex;gap:6px">{bars}</div></div>')
    body = (f'<div id="{P}h" style="position:absolute;left:0;right:0;top:110px;text-align:center"><div class="kick">BY WEEKDAY · 요일별 평균 경락가 (원/kg)</div></div>'
            f'<div style="position:absolute;left:0;right:0;top:200px;display:flex;justify-content:center;gap:24px">{"".join(panels)}</div>'
            f'<div id="{P}r" style="position:absolute;left:0;right:0;top:790px;text-align:center;font-size:44px;font-weight:700;opacity:0"><span style="color:{UP}">토요일은 비싸고</span> · <span style="color:{DOWN}">평일이 쌌다</span></div>')
    js = "".join(f'show("p{i}", {st(T, "item", i)}); tl.fromTo(".{P}b{i}", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.7, stagger: 0.08, ease: "power3.out" }}, {st(T, "item", i)} + 0.2);' for i in range(3))
    js += f'tl.to($("r"), {{ opacity: 1, duration: 0.5 }}, {st(T, "recap", 1)});'
    return scene(T, body, js)


def faq(T):
    P = T["id"] + "-"
    qa = [("Q1. 그냥 10월에 사면 제일 싸지 않나요?", ["킹크랩 재작년 10월 2주 <b class='num'>39,500</b>원 = 시즌 최저", "작년 10월은 <b class='num'>64,000 ~ 72,100</b>원", f"<span style='color:{GOLD2}'>→ 10월이 늘 싸다고 단정하긴 어렵다</span>"]),
          ("Q2. 물량이 많으면 싸지 않나요?", ["세 품목 모두 물량 최다 = 12월 4주", "그 주 킹크랩 = 시즌 최고가", f"<span style='color:{GOLD2}'>→ 수요가 몰리면 물량이 많아도 오를 수 있다</span>"])]
    body = "".join(f'<div id="{P}q{i}" class="card" style="left:220px;right:220px;top:220px"><div class="mj" style="font-size:66px;color:{GOLD2}">{q}</div>'
                   + "".join(f'<div id="{P}a{i}{j}" style="font-size:48px;font-weight:700;margin-top:30px;opacity:0">{a}</div>' for j, a in enumerate(ans)) + '</div>' for i, (q, ans) in enumerate(qa))
    js = seq(T, [("q0", "q", 1), ("q1", "q", 2)])
    js += "".join(f'tl.to($("a0{j}"), {{ opacity: 1, duration: 0.5 }}, {st(T, "a", j + 1)});' for j in range(3))
    js += "".join(f'tl.to($("a1{j}"), {{ opacity: 1, duration: 0.5 }}, {st(T, "a", 4 + min(j, 1))} + {0.8 if j == 1 else 0});' for j in range(3))
    js += f'tl.set($("q1"), {{ opacity: 1 }}, {st(T, "a", 5)} + 0.2);'
    return scene(T, body, js)


def calendar(T):
    P = T["id"] + "-"; MONS = ["10", "11", "12", "1", "2", "3"]
    col = lambda v: DOWN if v <= -7 else (UP if v >= 7 else "#3a3d44")
    rows = "".join(f'<tr id="{P}r{i}" style="opacity:0"><td class="mj" style="font-size:60px;text-align:left;padding-right:30px">{n}</td>'
                   + "".join(f'<td><div style="height:96px;background:{col(MON[n]["rel"][m])};display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:800;color:{INK if abs(MON[n]["rel"][m]) >= 7 else IVORY}">{MON[n]["rel"][m]:+.0f}%</div></td>' for m in MONS)
                   + '</tr>' for i, n in enumerate(("킹크랩", "대방어", "대게")))
    body = (f'<div style="position:absolute;left:0;right:0;top:80px;text-align:center"><div class="kick">WINTER SHOPPING CALENDAR</div><div class="mj" style="font-size:84px;margin-top:8px">올겨울 장보기 달력</div></div>'
            f'<table id="{P}tb" style="position:absolute;left:150px;top:270px;width:1620px;border-collapse:separate;border-spacing:10px">'
            f'<tr style="font-size:40px;font-weight:700;color:{GOLD}"><td></td>' + "".join(f'<td style="text-align:center">{m}월</td>' for m in MONS) + f'</tr>{rows}</table>'
            f'<div id="{P}lg" style="position:absolute;left:170px;top:752px;font-size:34px;opacity:0"><span style="background:{DOWN};color:{INK};padding:4px 14px">초록 = 쌌던 달</span>  <span style="background:{UP};color:{INK};padding:4px 14px">빨강 = 비쌌던 달</span>  <span style="color:{MUTE}">두 시즌 평균 대비 · ±7%</span></div>'
            f'<div id="{P}wk" style="position:absolute;left:170px;top:812px;font-size:40px;font-weight:700;opacity:0"><span style="color:{DOWN}">노릴 주</span> · 킹크랩 11월 4주~12월 1주 · 대방어 1월 초 · 대게 2월 말 이후</div>'
            f'<div id="{P}dw" style="position:absolute;right:170px;top:752px;font-size:40px;font-weight:700;opacity:0;color:{GOLD2}">요일 · 토요일 피하고 평일</div>'
            f'<div id="{P}cap" style="position:absolute;right:120px;top:120px;padding:14px 26px;border:2px solid {GOLD};font-size:36px;font-weight:800;color:{GOLD2};opacity:0;transform:rotate(4deg)">📸 캡처해 두세요</div>'
            f'<div id="{P}how" class="card" style="left:300px;right:300px;top:330px;text-align:center"><div class="kick">매일 경락가 보는 곳</div><div style="font-size:56px;font-weight:700;margin-top:20px">노량진수산 홈페이지 → 수산물가격정보</div>'
            f'<div style="font-size:40px;color:{MUTE};margin-top:14px">susansijang.co.kr · 가기 전날 확인</div></div>')
    js = (f'tl.to($("lg"), {{ opacity: 1, duration: 0.5 }}, {st(T, "legend", 1)});'
          + "".join(f'tl.fromTo($("r{i}"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.6 }}, {st(T, "row", i)});' for i in range(3))
          + f'tl.to($("wk"), {{ opacity: 1, duration: 0.5 }}, {st(T, "weeks", 1)}); tl.to($("dw"), {{ opacity: 1, duration: 0.5 }}, {st(T, "dowline", 1)});'
          + f'tl.to($("cap"), {{ opacity: 1, duration: 0.4 }}, {st(T, "hold", 1)}); tl.to([$("tb"), $("lg"), $("wk"), $("dw"), $("cap")], {{ opacity: 0, duration: 0.4 }}, {st(T, "howto", 1)} - 0.3); show("how", {st(T, "howto", 1)});')
    return scene(T, body, js)


def outro(T):
    P = T["id"] + "-"
    body = (f'<div id="{P}d" class="card" style="left:220px;right:220px;top:230px;text-align:center"><div class="kick" style="color:{UP}">꼭 기억하세요</div>'
            f'<div class="mj" style="font-size:76px;margin-top:24px;color:{GOLD2}">경락가 = 도매 낙찰가 ≠ 가게 판매가</div>'
            f'<div class="mj" style="font-size:66px;margin-top:30px">지난 2년의 흐름 ≠ 올해 보장</div><div style="font-size:36px;color:{MUTE};margin-top:26px">자료 · 노량진수산(주) 어종별 경락시세 (susansijang.co.kr)</div></div>'
            f'<div id="{P}o" class="card" style="left:300px;right:300px;top:300px"><div class="kick">MY TAKE</div><div class="mj" style="font-size:64px;line-height:1.5;margin-top:20px">올해는 <span style="color:{DOWN}">킹크랩 낮게</span>,<br><span style="color:{UP}">대방어 높게</span> 출발</div></div>'
            f'<div id="{P}e" style="position:absolute;inset:0;opacity:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:{INK}">'
            f'<div class="kick">SEE YOU NEXT WEEK</div><div class="mj" style="font-size:110px;margin-top:20px">주간 시세 리포트에서</div><div style="font-size:46px;color:{GOLD2};margin-top:26px">구독 · 알림 설정</div></div>')
    js = seq(T, [("d", "disc", 1), ("o", "opinion", 1), ("e", "cta", 1)])
    return scene(T, body, js)


# ------------------------------------------------------------------ 자막
def one_line(x, n=16):  # 45~54세 시청층: 한 화면 글자를 조금 줄임(16자)
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
            sub = re.sub(r"\s{2,}", " ", re.sub(r"(?<!\d)[,.]|[,.](?!\d)", "", x["sub"])).strip()
            lines = one_line(sub); durs = voice_split(x["wav"], [len(l) for l in lines], x["dur"]); t0 = T["start"] + x["start"]
            for l, du in zip(lines, durs):
                h = re.sub(r"(\d[\d,~·.%]*(?:원|kg|위|가지|일|월|주|년|%|개)?)", r"<b>\1</b>", l)
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
    json.dump(dict(id="winter_data", name="winter_data", createdAt="2026-11-07T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
    for f in ("NanumMyeongjo-ExtraBold.ttf", "Pretendard-Bold.otf", "Pretendard-SemiBold.otf", "Pretendard-ExtraBold.otf"): shutil.copy(f"{FONTDIR}/{f}", f"{HF}/assets/fonts/{f}")
    for i in PHOTO.values(): shutil.copy(f"{IMG}/{i}.jpg", f"{HF}/assets/img/{i}.jpg")
    F = dict(hook=hook, title=title, item=item, dow=dow, faq=faq, calendar=calendar, outro=outro)
    hosts = []
    for T in TL:
        open(f"{HF}/compositions/{T['id']}.html", "w", encoding="utf-8").write(F[T["s"]["kind"]](T))
        hosts.append(f'<div id="{T["id"]}" data-composition-id="{T["id"]}" data-composition-src="compositions/{T["id"]}.html" data-start="{T["start"]:.3f}" data-duration="{T["dur"]:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
    cap, k = captions(); open(f"{HF}/compositions/captions.html", "w", encoding="utf-8").write(cap)
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
