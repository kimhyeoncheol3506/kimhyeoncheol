# -*- coding: utf-8 -*-
"""데이터 롱폼 #2 (산지·크기·활어 vs 선어) — 겨울 시즌데이터 롱폼과 같은 에디토리얼 골드 스타일 HyperFrames 프로젝트 생성
사용: python3 build_hf.py [--est]  → hf/ , timeline.json
장면: hook · title · origin · size · live · faq · checklist · outro
이번 영상만 템포 5% 빠르게: 음성 1.176배속, 문장 사이 쉼·장면 꼬리·전환 0.95배
"""
import json, os, re, shutil, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EST = "--est" in sys.argv
D = json.load(open(f"{ROOT}/01_대본/대본데이터.json", encoding="utf-8"))
DATA = json.load(open(f"{ROOT}/00_data/data.json", encoding="utf-8"))
TTS = f"{ROOT}/02_음성"; HF = f"{HERE}/hf"; IMG = f"{ROOT}/09_소재/img_final"
PHOTO = json.load(open(f"{IMG}/pick.json", encoding="utf-8"))
FONTDIR = os.path.expanduser("~/.cache/ranking-video/fonts")
TEMPO = 0.95  # 이번 영상만: 쉼·전환 5% 짧게
GAP, LEAD = 0.5 * TEMPO, 0.7 * TEMPO
INK, GOLD, GOLD2, IVORY, MUTE, DOWN, UP, GREY = "#0D0E11", "#D6B26E", "#F1D9A0", "#F2EDE3", "#8C919B", "#5FB7A6", "#E4775F", "#6B7079"
FONTS = ('@font-face{font-family:"MJ";src:url("assets/fonts/NanumMyeongjo-ExtraBold.ttf");font-weight:800}'
         '@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-Bold.otf");font-weight:700}'
         '@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-SemiBold.otf");font-weight:500}'
         '@font-face{font-family:"PXB";src:url("assets/fonts/Pretendard-ExtraBold.otf");font-weight:800}')
W = lambda v: f"{int(v):,}"


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
    dur = cur + (2.2 if s["kind"] in ("outro", "checklist") else 0.9) * TEMPO
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
tl.fromTo($("wipe"), {{ scaleX: 0, opacity: 1, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.57, ease: "power3.inOut" }}, 0);
tl.to($("wipe"), {{ opacity: 0, duration: 0.38 }}, 0.57);
{"tl.fromTo($('content'), { opacity: 0 }, { opacity: 1, duration: 0.6 }, 0.3);" if fade else ""}
function count(sel, from, to, at, dur, fmt) {{ const o = {{ v: from }}; tl.to(o, {{ v: to, duration: dur || 1.2, ease: "power2.out", onUpdate: () => {{ document.querySelector(sel).textContent = fmt(o.v); }} }}, at); }}
const Wf = (v) => Math.round(v).toLocaleString("en-US");
function show(id, a, b) {{ tl.fromTo($(id), {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, a); if (b !== undefined && b !== null) tl.to($(id), {{ opacity: 0, duration: 0.35 }}, b); }}
'''
    h = f'<div class="hdr">노량진수산시장 · 데이터 리포트 #2 · 같은 1kg, 다른 값</div>' if hdr else ""
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


# ------------------------------------------------------------------ 공통 조각
def has(T, key, val=True):
    try: st(T, key, val); return True
    except KeyError: return False


def rcard(P, i, ttl, lines, ph=None, top=170):
    inner = "".join(f'<div style="font-size:{40 if len(lines) <= 2 else 36}px;font-weight:700;margin:14px 0;line-height:1.3;word-break:keep-all">{ln}</div>' for ln in lines)
    img = f'<div style="height:230px;margin:-34px -40px 24px;overflow:hidden"><img src="assets/img/{PHOTO[ph]}.jpg" style="width:100%;height:100%;object-fit:cover"></div>' if ph else ""
    return f'<div id="{P}k{i}" class="card" style="left:1380px;width:500px;top:{top}px">{img}<div class="kick" style="font-size:30px;letter-spacing:.12em">{ttl}</div>{inner}</div>'


def rcards(T, specs, end):
    """specs: (key, val, 제목, [줄], 사진) — 시간순으로 하나씩, 다음 카드나 end에서 사라짐"""
    P = T["id"] + "-"; specs = sorted(specs, key=lambda c: st(T, c[0], c[1])); times = [st(T, c[0], c[1]) for c in specs]
    html = "".join(rcard(P, i, c[2], c[3], c[4] if len(c) > 4 else None) for i, c in enumerate(specs))
    js = "\n".join(f'show("k{i}", {times[i]}, {times[i + 1] - 0.3 if i + 1 < len(times) else end - 0.2});' for i in range(len(times)))
    return html, js


def panels(T, items, end):
    """[(panel id, 시작 시각)] — 다음 패널이 오면 앞 패널은 사라짐"""
    out = []
    for i, (pid, t0) in enumerate(items):
        t1 = items[i + 1][1] - 0.25 if i + 1 < len(items) else end - 0.2
        out.append(f'tl.fromTo($("{pid}"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.5 }}, {t0}); tl.to($("{pid}"), {{ opacity: 0, duration: 0.3 }}, {t1});')
    return "\n".join(out)


def chapter(T, n, title, sub, ph):
    P = T["id"] + "-"
    html = (f'<div id="{P}chap" style="position:absolute;inset:0"><img id="{P}cimg" src="assets/img/{PHOTO[ph]}.jpg" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">'
            f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,{INK}f2 0%,{INK}b0 45%,{INK}40 100%)"></div>'
            f'<div style="position:absolute;left:140px;top:330px"><div class="kick">CRITERION {n:02d}</div><div class="mj" style="font-size:200px;line-height:1.15;margin-top:10px">{title}</div>'
            f'<div style="font-size:44px;color:{GOLD2}">{sub}</div></div></div>')
    return html


def chap_js(t_off):
    return f'tl.fromTo($("cimg"), {{ scale: 1.12 }}, {{ scale: 1, duration: {t_off + 0.5:.2f}, ease: "none" }}, 0); tl.to($("chap"), {{ opacity: 0, duration: 0.5 }}, {t_off} - 0.2);'


def summary(T, name, left, right, foot):
    P = T["id"] + "-"
    col = lambda c, k, xs: (f'<div style="width:740px;border-top:6px solid {c};padding:36px 40px;background:#16181D"><div class="kick" style="color:{c}">{k}</div>'
                            + "".join(f'<div class="mj" style="font-size:54px;margin-top:22px;line-height:1.3;word-break:keep-all">{x}</div>' for x in xs) + '</div>')
    return (f'<div id="{P}sum" style="position:absolute;inset:0;background:{INK}f4;opacity:0">'
            f'<div style="position:absolute;top:150px;left:0;right:0;text-align:center" class="mj"><span style="font-size:80px">{name}</span></div>'
            f'<div style="position:absolute;top:320px;left:0;right:0;display:flex;justify-content:center;gap:70px">{col(GOLD2, left[0], left[1])}{col(DOWN, right[0], right[1])}</div>'
            f'<div style="position:absolute;top:800px;left:0;right:0;text-align:center;font-size:46px;font-weight:700;color:{GOLD2}">{foot}</div></div>')


def hbar_group(P, gid, title, rows, unit_fmt, width=1000, hl=None):
    vmax = max(v for _, v in rows)
    out = [f'<div id="{P}{gid}" style="position:absolute;left:80px;top:170px;width:1240px;opacity:0"><div style="font-size:38px;color:{MUTE};margin-bottom:26px">{title}</div>']
    for i, (lab, v) in enumerate(rows):
        c = GOLD2 if hl is not None and i in hl else GOLD
        out.append(f'<div id="{P}{gid}r{i}" style="display:flex;align-items:center;gap:22px;margin:22px 0">'
                   f'<div class="mj" style="width:170px;font-size:50px;text-align:right">{lab}</div>'
                   f'<div class="{P}{gid}b" style="height:74px;width:{v / vmax * width:.0f}px;background:linear-gradient(90deg,{c}55,{c})"></div>'
                   f'<div class="num" style="font-size:52px;color:{IVORY};white-space:nowrap">{unit_fmt(v)}</div></div>')
    return "".join(out) + '</div>'


def bars_in(P, gid, idx, t):
    return "".join(f'tl.fromTo("#{P}{gid}r{i} .{P}{gid}b", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.7, ease: "power3.out" }}, {t} + {k * 0.15:.2f}); tl.fromTo($("{gid}r{i}"), {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {t} + {k * 0.15:.2f});' for k, i in enumerate(idx))


WON = lambda v: f'{int(v):,}<span style="font-size:32px">원</span>'


# ------------------------------------------------------------------ 오프닝
def hook(T):
    P = T["id"] + "-"
    side = lambda i, lab, v, sub, col: (f'<div style="text-align:center;width:640px"><div class="kick" style="color:{col}">{lab}</div>'
                                        f'<div class="num" style="font-size:150px;color:{col};line-height:1.1;margin-top:16px"><span id="{P}h{i}">0</span><span style="font-size:60px">원</span></div>'
                                        f'<div style="font-size:36px;color:{MUTE}">{sub}</div></div>')
    body = (f'<div id="{P}c1" class="card" style="left:0;right:0;top:200px;background:none;border:none;display:flex;justify-content:center;gap:120px">'
            + side(1, "A · 광어 1kg", 27310, "활어 · 4미 · kg당 경락가", GOLD2) + side(2, "B · 광어 1kg", 4330, "선어 · 4미 · kg당 경락가", MUTE) + '</div>'
            f'<div id="{P}same" style="position:absolute;left:0;right:0;top:640px;text-align:center;font-size:52px;font-weight:700;opacity:0">둘 다 <span style="color:{GOLD2}">광어</span> · 둘 다 <span style="color:{GOLD2}">4미</span> 규격</div>'
            f'<div id="{P}c2" class="card" style="left:0;right:0;top:190px;background:none;border:none;text-align:center"><div class="kick">SAME 1KG · DIFFERENT PRICE</div>'
            f'<div class="num" style="font-size:300px;color:{GOLD2};line-height:1.1"><span id="{P}x">1.0</span><span style="font-size:130px">배</span></div>'
            f'<div id="{P}lv" style="font-size:54px;font-weight:700;opacity:0"><span style="color:{GOLD2}">살아 있는 활어</span>  vs  <span style="color:{MUTE}">숨이 멎은 선어</span></div></div>'
            f'<div id="{P}c4" class="card" style="left:0;right:0;top:200px;background:none;border:none;text-align:center"><div class="kick">값을 가르는 기준</div>'
            f'<div style="display:flex;justify-content:center;gap:40px;margin-top:40px">'
            + "".join(f'<div id="{P}t{i}" style="width:440px;padding:46px 0;border:2px solid {GOLD};opacity:0"><div class="kick" style="font-size:30px">0{i + 1}</div><div class="mj" style="font-size:96px;margin-top:10px">{w}</div></div>' for i, w in enumerate(("산지", "크기", "활어·선어")))
            + '</div></div>'
            f'<div id="{P}c5" class="card" style="left:300px;right:300px;top:260px;text-align:center"><div class="kick">노량진수산 경락시세</div>'
            f'<div class="num" style="font-size:150px;color:{GOLD2};margin-top:10px">18,983<span style="font-size:64px">건</span></div><div style="font-size:40px;color:{MUTE}">2026.9.1 – 11.7 · 직접 계산</div></div>'
            f'<div id="{P}c6" class="card" style="left:200px;right:200px;top:280px;text-align:center"><div class="kick">끝까지 보면 · 장보기 체크리스트</div>'
            f'<div style="display:flex;justify-content:center;align-items:center;gap:22px;margin-top:34px">'
            + f'<span style="font-size:60px;color:{GOLD}">→</span>'.join(f'<div class="mj" style="font-size:66px;padding:14px 26px;border:1px solid {GOLD}88">{w}</div>' for w in ("용도", "크기", "산지", "활·선")) + '</div></div>')
    t1, tc, t3 = st(T, "hook", 1), st(T, "count", 1), st(T, "three", 1)
    js = (f'tl.set($("c1"), {{ opacity: 1 }}, 0); count($("h1"), 0, 27310, 0.2, 1.6, Wf); count($("h2"), 0, 4330, 0.5, 1.6, Wf);'
          f'tl.to($("same"), {{ opacity: 1, duration: 0.4 }}, {st(T, "hook", 2)}); tl.to([$("c1"), $("same")], {{ opacity: 0, duration: 0.3 }}, {tc} - 0.25);'
          f'show("c2", {tc}, {t3} - 0.25); count($("x"), 1, 6.3, {tc} + 0.1, 1.4, (v) => v.toFixed(1));'
          f'tl.to($("lv"), {{ opacity: 1, duration: 0.4 }}, {st(T, "hook", 3)});'
          + seq(T, [("c4", "three", 1), ("c5", "hook", 4), ("c6", "hook", 5)])
          + "".join(f'tl.fromTo($("t{i}"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {t3} + {0.3 + i * 0.45:.2f});' for i in range(3))
          + f'tl.to([$("t0"), $("t1"), $("t2")], {{ borderColor: "{GOLD2}", duration: 0.4, stagger: 0.25 }}, {st(T, "three", 2)});'
          + f'tl.set($("c6"), {{ opacity: 1 }}, {st(T, "hook", 5)} + 0.7);')
    return scene(T, body, js, hdr=False, fade=False)


def title(T):
    P = T["id"] + "-"
    body = (f'<div style="position:absolute;inset:0;opacity:.18"><img src="assets/img/{PHOTO["경매"]}.jpg" style="width:100%;height:100%;object-fit:cover"></div>'
            f'<div id="{P}t" class="card" style="left:0;right:0;top:200px;background:none;border:none;text-align:center"><div class="kick">NORYANGJIN FISH MARKET · DATA REPORT #2</div>'
            f'<div class="mj" style="font-size:130px;margin-top:26px">같은 1kg, 다른 값</div><div style="font-size:46px;color:{MUTE};margin-top:10px">산지 · 크기 · 활어 vs 선어</div></div>'
            f'<div id="{P}src" class="card" style="left:260px;right:260px;top:250px;text-align:center"><div class="kick">SOURCE</div><div style="font-size:56px;font-weight:700;margin-top:18px">노량진수산(주) 어종별 경락시세</div>'
            f'<div style="font-size:40px;color:{MUTE};margin-top:12px">새벽 경매 낙찰가 · 도매 가격 · susansijang.co.kr</div></div>'
            f'<div id="{P}per" class="card" style="left:240px;right:240px;top:250px;text-align:center"><div class="kick">PERIOD</div><div style="display:flex;justify-content:center;gap:30px;margin-top:26px">'
            + "".join(f'<div style="padding:22px 36px;border:1px solid {c};font-size:46px;font-weight:700;color:{c}">{a}</div>' for a, c in (("2026.9.1 – 11.7", GOLD2), ("경매일 56일", IVORY), ("18,983건", DOWN)))
            + '</div></div>'
            f'<div id="{P}m" class="card" style="left:280px;right:280px;top:220px"><div class="kick">METHOD</div>'
            + "".join(f'<div id="{P}m{i}" style="font-size:46px;font-weight:700;padding:20px 0;border-bottom:1px solid {GOLD}33;opacity:0">{x}</div>' for i, x in enumerate(
                ("kg당 가격 = 평균가 ÷ 중량 · 물량 가중평균", "물량 200kg 미만 칸 · 마리 단위 거래 제외", f"<span style='color:{GOLD2}'>말은 천 원 단위 반올림 · 카드는 원 단위</span>")))
            + '</div>'
            f'<div id="{P}warn" class="card" style="left:220px;right:220px;top:230px"><div class="kick" style="color:{UP}">꼭 알아 두세요</div>'
            f'<div id="{P}w1" style="font-size:54px;font-weight:700;margin-top:26px;opacity:0">① 경락가 = 도매 낙찰가 <span style="color:{MUTE}">≠ 가게 판매가</span></div>'
            f'<div id="{P}w2" style="font-size:54px;font-weight:700;margin-top:26px;opacity:0">② 2026년 9~11월 숫자 <span style="color:{MUTE}">≠ 다른 시기 보장</span></div></div>')
    js = (f'tl.set($("t"), {{ opacity: 1 }}, 0.3); tl.to($("t"), {{ opacity: 0, duration: 0.3 }}, {st(T, "src", 1)} - 0.25);'
          + seq(T, [("src", "src", 1), ("per", "period", 1), ("m", "method", 1), ("warn", "warn", 0)])
          + "".join(f'tl.to($("m{i}"), {{ opacity: 1, duration: 0.5 }}, {st(T, "method", i + 1)});' for i in range(3))
          + f'tl.to($("w1"), {{ opacity: 1, duration: 0.5 }}, {st(T, "warn", 1)}); tl.to($("w2"), {{ opacity: 1, duration: 0.5 }}, {st(T, "warn", 2)});'
          + f'tl.set($("warn"), {{ opacity: 1 }}, {st(T, "warn", 2)} + 0.1);')
    return scene(T, body, js)


# ------------------------------------------------------------------ 기준 1 산지
def origin(T):
    P = T["id"] + "-"; O = {x["item"]: x["rows"] for x in DATA["origin"]}; end = st(T, "summary", 1)
    G = [("g1", "광어 4미 · 산지별 kg당 경락가", O["광어 4미"], "chart", 1), ("g2", "광어 3미 · 산지별 kg당 경락가", O["광어 3미"], "chart3", 1),
         ("g3", "참돔 3미 · 산지별 kg당 경락가", O["참돔 3미"], "imp", 1), ("g4", "방어 1미 · 산지별 kg당 경락가", O["방어 1미"], "imp", 4),
         ("g5", "농어 2미 · 산지별 kg당 경락가", O["농어 2미"], "imp", 6), ("g6", "킹크랩 10/15미 · 산지별 kg당 경락가", O["킹크랩 10/15미"], "king", 1)]
    html = "".join(hbar_group(P, g, ttl, rows, WON, width=760) for g, ttl, rows, _, _ in G)
    html += (f'<div id="{P}g7" style="position:absolute;left:80px;top:220px;width:1240px;opacity:0;text-align:center"><div class="kick">RULE</div>'
             f'<div class="mj" style="font-size:96px;margin-top:20px;color:{GOLD2}">같은 크기끼리 비교</div>'
             f'<div style="display:flex;justify-content:center;gap:40px;margin-top:50px;font-size:54px;font-weight:700">'
             f'<div style="padding:20px 40px;border:2px solid {DOWN}">4미 vs 4미 ✓</div><div style="padding:20px 40px;border:2px solid {UP};color:{MUTE}">3미 vs 4미 ✕</div></div></div>')
    js = panels(T, [(g, st(T, k, v)) for g, _, _, k, v in G] + [("g7", st(T, "tip", 1))], end)
    js += bars_in(P, "g1", [0, 1], st(T, "bar", 1)) + bars_in(P, "g1", [2, 3], st(T, "bar", 2))
    for g, _, rows, k, v in G[1:]: js += bars_in(P, g, range(len(rows)), st(T, k, v) + 0.2)
    specs = [("rumor", 1, "블로그 속설", ["완도 광어 > 제주 광어", "kg당 1,000~2,000원 더"]), ("rumor", 2, "광어는 전량 국산", ["활광어 수입 없음", "국내 산지끼리 비교"]),
             ("gap", 1, "제주 vs 완도", ["<b class='num'>90</b>원 차이", "사실상 같은 값"]), ("gap", 2, "제주 ÷ 안흥", [f"<b class='num' style='font-size:80px;color:{GOLD2}'>1.98</b>배"]),
             ("gap3", 1, "광어 3미", ["제주 ÷ 여수 <b class='num'>1.55</b>배", "완도 ÷ 여수 <b class='num'>1.43</b>배"]),
             ("share", 1, "활광어 물량", ["제주산 <b class='num'>77%</b>", "<b class='num'>79.7</b>톤"]),
             ("why", 1, "자연산이라서?", ["경락시세에는", "자연산 여부 표기 없음"]), ("why", 2, "원인은?", ["이 데이터로는", "알 수 없음"]),
             ("imp", 2, "통영산 대비", ["대천산 <b class='num'>−28%</b>", "일본산 <b class='num'>+9%</b>"]), ("imp", 3, "활참돔 물량", ["일본산 <b class='num'>75%</b>", "<b class='num'>140</b>톤"]),
             ("imp", 5, "동해시산 대비", ["일본산 <b class='num'>+29%</b>", "활방어 물량 일본산 <b class='num'>57%</b>"]),
             ("imp", 7, "목포산 대비", ["중국산 <b class='num'>+81%</b>", "활농어 물량 중국산 <b class='num'>65%</b>"]),
             ("imp", 9, "알려진 설명", ["일본산 방어 = 전량 양식", "일본산 참돔 = 크게 키운 양식", f"<span style='color:{MUTE};font-size:30px'>출처 · 입질의 추억</span>"]),
             ("imp", 10, "원인 단정 X", ["경락시세만으로는", "가릴 수 없음"]), ("king", 2, "킹크랩 10/15미", ["러시아산 <b class='num'>+9%</b>", "일본산 대비"]),
             ("fair", 1, "좋고 나쁨이 아니라", ["이 기간", "경매 거래 기록"]),
             ("tip", 3, "원산지 표시 확인", ["국립수산물품질관리원", "위반 업소 정기 공표"]),
             ("tip", 5, "서울시 메뉴판 예시", ["참돔회(국산) <b class='num'>40,000</b>원", "참돔회(일본산) <b class='num'>30,000</b>원", f"<span style='color:{GOLD2}'>도매가 ≠ 가게 값</span>"])]
    ch, cj = rcards(T, specs, end)
    summ = summary(T, "산지 정리", ("국내 산지끼리", ["광어 4미 최대 1.98배", "제주 ≈ 완도 (90원)"]), ("수입 어종", ["국내산보다 최대 +81%", "(농어 2미)"]), "같은 크기끼리 · 원산지 표시와 함께")
    js += cj + chap_js(st(T, "chart", 1)) + f'\ntl.to($("sum"), {{ opacity: 1, duration: 0.6 }}, {end});'
    # 챕터 카드 위 첫 카드(rumor)는 사진 위에 뜸
    return scene(T, chapter(T, 1, "산지", "같은 크기, 다른 산지", "시장") + html + ch + summ, js)


# ------------------------------------------------------------------ 기준 2 크기
def size(T):
    P = T["id"] + "-"; Z = DATA["size"]; end = st(T, "summary", 1)
    fish = lambda cx, cy, rx, ry: f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx}" ry="{ry}" fill="{GOLD}" opacity=".9"/><path d="M{cx + rx - 2:.0f},{cy:.0f} l{rx * .5:.0f},-{ry * .8:.0f} v{ry * 1.6:.0f}z" fill="{GOLD}"/>'
    def scale_svg(n, rx, ry, cols):
        s = [f'<rect x="20" y="300" width="460" height="22" rx="6" fill="{MUTE}"/><rect x="230" y="322" width="40" height="70" fill="{MUTE}"/><rect x="140" y="392" width="220" height="18" fill="{MUTE}"/>']
        for i in range(n):
            r, c = divmod(i, cols); s.append(f'<g class="{P}f{n}">' + fish(60 + c * (380 / max(cols - 1, 1)), 280 - ry - r * (ry * 2 + 6), rx, ry) + '</g>')
        return f'<svg width="500" height="420" viewBox="0 0 500 420">{"".join(s)}</svg>'
    mi = (f'<div id="{P}pm" style="position:absolute;left:80px;top:150px;width:1240px;opacity:0;text-align:center">'
          f'<div class="mj" style="font-size:72px">‘미’ = <span style="color:{GOLD2}">1kg</span>에 올라가는 마리 수</div>'
          f'<div id="{P}sc" style="display:flex;justify-content:center;gap:120px;margin-top:40px;opacity:0">'
          f'<div>{scale_svg(5, 34, 22, 5)}<div class="num" style="font-size:64px;color:{GOLD2}">5미</div><div style="font-size:34px;color:{MUTE}">1kg = 5마리 · 한 마리 큼</div></div>'
          f'<div>{scale_svg(30, 13, 8, 10)}<div class="num" style="font-size:64px">30미</div><div style="font-size:34px;color:{MUTE}">1kg = 30마리 · 한 마리 작음</div></div></div>'
          f'<div id="{P}ar" style="font-size:46px;font-weight:700;margin-top:24px;opacity:0">숫자 <span style="color:{DOWN}">작을수록</span> 한 마리가 <span style="color:{GOLD2}">크다</span></div></div>')
    ab = Z["전복"]; vmax = max(v for _, v in ab); X0 = 60; cw = 104
    cols = "".join(f'<div id="{P}c{i}" style="position:absolute;left:{X0 + i * (cw + 8)}px;bottom:0;width:{cw}px;opacity:0;text-align:center">'
                   f'<div class="num" style="font-size:25px;margin-bottom:6px">{v:,}</div><div id="{P}cb{i}" style="height:{v / vmax * 470:.0f}px;background:linear-gradient(180deg,{GOLD2},{GOLD}66)"></div>'
                   f'<div style="font-size:28px;font-weight:700;margin-top:10px">{lab}</div></div>' for i, (lab, v) in enumerate(ab))
    stair = (f'<div id="{P}ps" style="position:absolute;left:80px;top:150px;width:1260px;height:740px;opacity:0"><div style="font-size:38px;color:{MUTE}">전복 · 크기(미)별 kg당 경락가 (원) · 왼쪽일수록 큰 전복</div>'
             f'<div style="position:absolute;left:0;top:80px;width:1260px;height:620px">{cols}</div></div>')
    uses = [("use", 1, "회 · 숙회", "8~10미"), ("use", 2, "찜 · 구이", "중대형"), ("use", 2, "죽 · 탕 · 라면", "작은 전복 (40미 등)"), ("use", 3, "마트에서 흔한 크기", "12~20미")]
    use = (f'<div id="{P}pu" style="position:absolute;left:80px;top:160px;width:1240px;opacity:0"><div class="kick">전복 · 용도별 추천 크기</div>'
           + "".join(f'<div id="{P}u{i}" style="display:flex;justify-content:space-between;align-items:center;padding:30px 10px;border-bottom:1px solid {GOLD}44;opacity:0">'
                     f'<span class="mj" style="font-size:66px">{a}</span><span class="num" style="font-size:62px;color:{GOLD2}">{b}</span></div>' for i, (_, _, a, b) in enumerate(uses))
           + f'<div style="font-size:30px;color:{MUTE};margin-top:20px">출처 · 완도군 안내(seasontable.kr 인용) · 전복 유통업체 블로그 · 인어교주해적단</div></div>')
    def vpanel(i, name, rows):
        m = max(v for _, v in rows)
        bars = "".join(f'<div style="flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:440px">'
                       f'<div class="num" style="font-size:19px;letter-spacing:-0.04em">{v:,}</div><div class="{P}ob{i}" style="width:34px;height:{v / m * 340:.0f}px;background:{GOLD};margin-top:6px"></div>'
                       f'<div style="font-size:23px;font-weight:700;margin-top:8px;white-space:nowrap">{lab}</div></div>' for lab, v in rows)
        return f'<div id="{P}o{i}" style="width:390px;opacity:0;border:1px solid {GOLD}33;padding:10px 6px"><div class="mj" style="font-size:56px;text-align:center;margin-bottom:10px">{name}</div><div style="display:flex;gap:4px">{bars}</div></div>'
    other = (f'<div id="{P}po" style="position:absolute;left:60px;top:170px;width:1280px;opacity:0"><div style="font-size:36px;color:{MUTE};margin-bottom:20px">크기별 kg당 경락가 (원) · 활어</div>'
             f'<div style="display:flex;gap:22px">{vpanel(0, "참돔", Z["참돔"])}{vpanel(1, "방어", Z["방어"])}{vpanel(2, "수꽃게", Z["수꽃게"])}</div></div>')
    js = panels(T, [("pm", st(T, "mi", 1)), ("ps", st(T, "stair", 1)), ("pu", st(T, "use", 0)), ("po", st(T, "other", 0))], end)
    js += (f'tl.to($("sc"), {{ opacity: 1, duration: 0.4 }}, {st(T, "mi", 3)}); tl.fromTo(".{P}f5", {{ opacity: 0, y: -40 }}, {{ opacity: 1, y: 0, duration: 0.4, stagger: 0.12 }}, {st(T, "mi", 3)} + 0.2);'
           f'tl.fromTo(".{P}f30", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.25, stagger: 0.04 }}, {st(T, "mi", 3)} + 1.2); tl.to($("ar"), {{ opacity: 1, duration: 0.4 }}, {st(T, "mi", 4)});')
    for k, idx in ((2, [0, 1, 2]), (3, [3, 4, 5]), (4, [6, 7]), (5, [8, 9, 10])):
        js += "".join(f'tl.to($("c{i}"), {{ opacity: 1, duration: 0.3 }}, {st(T, "stair", k)} + {j * 0.5:.1f}); tl.fromTo($("cb{i}"), {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.6, ease: "power3.out" }}, {st(T, "stair", k)} + {j * 0.5:.1f});' for j, i in enumerate(idx))
    hl = lambda idx, t, col: "".join(f'tl.to($("cb{i}"), {{ background: "{col}", duration: 0.3 }}, {t});' for i in idx)
    rs = lambda t: f'tl.to("[id^={P}cb]", {{ background: "linear-gradient(180deg,{GOLD2},{GOLD}66)", duration: 0.2 }}, {t} - 0.15);'
    js += hl([0, 9, 10], st(T, "ratio", 1), UP) + rs(st(T, "ratio", 2)) + hl([4, 7], st(T, "ratio", 2), DOWN) + rs(st(T, "ratio", 3)) + hl([4, 6], st(T, "ratio", 3), DOWN)
    js += rs(st(T, "odd", 1)) + hl([0, 1], st(T, "odd", 1), UP) + rs(st(T, "odd", 2)) + hl([8, 9, 10], st(T, "odd", 2), DOWN)
    js += "".join(f'tl.to($("u{i}"), {{ opacity: 1, duration: 0.5 }}, {st(T, k, v)} + {0.9 if i == 2 else 0});' for i, (k, v, _, _) in enumerate(uses))
    for i in range(3):
        js += f'tl.to($("o{i}"), {{ opacity: 1, duration: 0.4 }}, {st(T, "other", i + 1)}); tl.fromTo(".{P}ob{i}", {{ scaleY: 0, transformOrigin: "50% 100%" }}, {{ scaleY: 1, duration: 0.6, stagger: 0.08 }}, {st(T, "other", i + 1)} + 0.2);'
    specs = [("mi", 5, "전복 한 마리 무게", ["8미 ≈ <b class='num'>125</b>g", "10미 ≈ <b class='num'>100</b>g", "15미 ≈ <b class='num'>67</b>g", "20미 ≈ <b class='num'>50</b>g"]),
             ("mi", 6, "참고", ["흔히 쓰는 환산값", "실제와 조금 다를 수 있음"]),
             ("ratio", 1, "가장 비싼 5/6미는", ["30미의 <b class='num'>2.87</b>배", "40미의 <b class='num'>5.38</b>배"]),
             ("ratio", 2, "많이 찾는 크기", ["10/11미 ÷ 18/19미", f"<b class='num' style='color:{GOLD2}'>1.50</b>배"]),
             ("ratio", 3, "한 칸 차이", ["10/11미 ÷ 15/16미", f"<b class='num' style='color:{GOLD2}'>1.24</b>배"]),
             ("odd", 1, "큰 게 더 싼 칸", ["4/5미 < 5/6미", "<b class='num'>250</b>원 낮음"]), ("odd", 2, "작은 쪽", ["25미 ≈ 30미", "40미에서 뚝"]),
             ("use", 5, "라면 · 탕용이라면", ["40미 <b class='num'>6,590</b>원", "5/6미 <b class='num'>35,480</b>원", "5배 넘게 차이"]),
             ("use", 4, "고르는 팁", ["수조 벽에 잘 붙은 전복", "= 활력 좋은 편"], "전복"),
             ("season", 1, "올여름 (한국경제)", ["대형 전복 10~20% 저렴", "6~10미 대 · 11~20미 중", "20미 이상 소"]),
             ("other", 1, "참돔", ["1미 ÷ 10미", f"<b class='num' style='color:{GOLD2}'>2.24</b>배"], "참돔"),
             ("other", 2, "방어", ["1미 ÷ 4미", f"<b class='num' style='color:{GOLD2}'>2.78</b>배"], "방어"),
             ("other", 4, "수꽃게", ["대 ÷ 소 <b class='num'>1.92</b>배", "대 ÷ B급 <b class='num'>4.19</b>배"], "꽃게")]
    ch, cj = rcards(T, specs, end)
    summ = summary(T, "크기 정리", ("같은 어종, 다른 크기", ["2배에서 5배 넘게", "(전복 5/6미 ÷ 40미 5.38배)"]), ("고르는 기준", ["비싼 크기 ✕", "용도에 맞는 크기 ✓"]), "회 · 숙회 8~10미 · 죽 · 탕 · 라면은 작은 것")
    js += cj + chap_js(st(T, "mi", 1)) + f'\ntl.to($("sum"), {{ opacity: 1, duration: 0.6 }}, {end});'
    return scene(T, chapter(T, 2, "크기", "‘미’를 읽으면 값이 보인다", "전복") + mi + stair + use + other + ch + summ, js)


# ------------------------------------------------------------------ 기준 3 활어 vs 선어
def live(T):
    P = T["id"] + "-"; end = st(T, "summary", 1)
    defs = [("활어회", "살아 있는 생선을 바로", "씹는 맛", "def1"), ("싱싱회", "잡은 뒤 약 10시간 이내", "씹는 맛 + 감칠맛", "def2"), ("선어회", "냉장 3~4일 뒤", "감칠맛↑ · 초밥용", "def3")]
    pd = (f'<div id="{P}pd" style="position:absolute;left:100px;right:100px;top:170px;opacity:0"><div class="kick" style="text-align:center">용어 정리</div><div style="display:flex;gap:40px;margin-top:30px">'
          + "".join(f'<div id="{P}d{i}" style="flex:1;opacity:0;border-top:6px solid {GOLD};background:#16181D;padding:40px"><div class="mj" style="font-size:80px;color:{GOLD2}">{a}</div>'
                    f'<div style="font-size:46px;font-weight:700;margin-top:26px">{b}</div><div style="font-size:42px;color:{MUTE};margin-top:16px">{c}</div></div>' for i, (a, b, c, _) in enumerate(defs))
          + f'</div><div id="{P}dsrc" style="font-size:32px;color:{MUTE};margin-top:26px;text-align:center;opacity:0">출처 · 수산물안전정보서비스(fsis.go.kr, 국립수산물품질관리원)</div>'
          f'<div id="{P}d4" style="font-size:46px;font-weight:700;margin-top:30px;text-align:center;opacity:0;color:{GOLD2}">오늘 표의 ‘선어’ = 경매에 선어로 나온 거래</div></div>')
    L = DATA["live"]; rmax = max(a / b for *_, a, b in L)
    rows = "".join(f'<div id="{P}r{i}" style="display:flex;align-items:center;gap:20px;margin:10px 0;opacity:0"><div class="mj" style="width:220px;text-align:right;font-size:42px">{n}</div>'
                   f'<div id="{P}rb{i}" style="height:52px;width:{a / b / rmax * 980:.0f}px;background:linear-gradient(90deg,{GOLD}44,{GOLD2})"></div>'
                   f'<div class="num" style="font-size:44px;color:{GOLD2};width:150px">{a / b:.2f}배</div><div style="font-size:26px;color:{MUTE}">{x} {a:,} · {y} {b:,}</div></div>' for i, (n, x, y, a, b) in enumerate(L))
    pb = f'<div id="{P}pb" style="position:absolute;left:60px;top:150px;width:1800px;opacity:0"><div style="font-size:36px;color:{MUTE};margin-bottom:14px">같은 품목 · 같은 규격 · 활어 ÷ 선어(수꽃게는 냉동) kg당 경락가</div>{rows}</div>'
    pk = (f'<div id="{P}pk" style="position:absolute;left:100px;right:100px;top:200px;opacity:0;text-align:center"><div class="kick">꼭 짚고 갈 것</div>'
          f'<div id="{P}k1" class="mj" style="font-size:100px;margin-top:30px;opacity:0">선어 = <span style="color:{GOLD2}">등급·용도</span>가 다른 물건</div>'
          f'<div id="{P}k2" style="display:flex;justify-content:center;gap:40px;margin-top:50px;opacity:0;font-size:52px;font-weight:700">'
          f'<div style="padding:20px 40px;border:2px solid {GOLD2}">활어 → 회</div><div style="padding:20px 40px;border:2px solid {DOWN}">선어 → 구이 · 조림</div></div>'
          f'<div id="{P}k3" style="font-size:42px;margin-top:50px;opacity:0">경매 → 가게 최소 <b class="num" style="color:{GOLD2}">36</b>시간 · 횟감은 <b class="num" style="color:{GOLD2}">24</b>시간 이내 · 반찬감은 충분</div>'
          f'<div id="{P}k3s" style="font-size:30px;color:{MUTE};margin-top:14px;opacity:0">출처 · 입질의 추억(김지민)</div></div>')
    tw = DATA["twist"]
    def pair(i, n, a, av, b, bv, ph):
        a, b = {"선": "선어"}.get(a, a), {"선": "선어"}.get(b, b); m = max(av, bv); hi = a if av > bv else b
        img = f'<div style="height:200px;overflow:hidden;margin:-30px -30px 20px"><img src="assets/img/{PHOTO[ph]}.jpg" style="width:100%;height:100%;object-fit:cover"></div>' if ph else '<div style="height:170px"></div>'
        bar = lambda lab, v: (f'<div style="display:flex;align-items:center;gap:14px;margin:16px 0"><div style="width:90px;font-size:36px;font-weight:700">{lab}</div>'
                              f'<div class="{P}tb{i}" style="height:50px;width:{v / m * 300:.0f}px;background:{GOLD2 if lab == hi else GREY}"></div><div class="num" style="font-size:34px">{v:,}</div></div>')
        r = max(av, bv) / min(av, bv)
        tag = f"{hi} {r:.2f}배" if r > 1.05 else "거의 같음"
        return (f'<div id="{P}t{i}" style="width:560px;opacity:0;background:#16181D;border:1px solid {GOLD}55;padding:30px">{img}<div class="mj" style="font-size:60px">{n}</div>'
                f'{bar(a, av)}{bar(b, bv)}<div class="num" style="font-size:40px;color:{GOLD2};margin-top:10px">{tag}</div></div>')
    pt = (f'<div id="{P}pt" style="position:absolute;left:0;right:0;top:120px;opacity:0"><div class="kick" style="text-align:center">반전 · 냉동이 늘 싼 건 아니다</div>'
          f'<div style="display:flex;justify-content:center;gap:40px;margin-top:24px">{pair(0, *tw[0], "고등어")}{pair(1, *tw[1], None)}{pair(2, *tw[2], "갈치")}</div>'
          f'<div id="{P}t5" style="position:absolute;left:0;right:0;text-align:center;top:640px;font-size:36px;color:{MUTE};opacity:0">이 기간 냉동 고등어 대부분 노르웨이산</div>'
          f'<div id="{P}t4" style="position:absolute;left:0;right:0;text-align:center;top:695px;font-size:42px;font-weight:700;color:{GOLD2};opacity:0">품목마다 거래 등급·크기가 다를 수 있음</div></div>')
    pc = (f'<div id="{P}pc" style="position:absolute;left:160px;right:160px;top:180px;opacity:0;display:flex;gap:50px">'
          f'<div style="width:600px;height:600px;overflow:hidden;border:1px solid {GOLD}66"><img src="assets/img/{PHOTO["꽃게"]}.jpg" style="width:100%;height:100%;object-fit:cover"></div>'
          f'<div style="flex:1"><div class="kick">꽃게</div><div style="font-size:46px;font-weight:700;margin-top:24px;line-height:1.45">수조에서 오래 지낸 활꽃게 → 살이 빠질 수 있음<br><span style="color:{GOLD2}">잡자마자 얼린 냉동이 나을 수도</span></div>'
          f'<div style="font-size:30px;color:{MUTE};margin-top:10px">출처 · 동아일보 김창일의 갯마을 탐구(2024.11.26)</div>'
          f'<div id="{P}c2" style="opacity:0;margin-top:40px"><div style="display:flex;gap:20px">' + "".join(f'<div style="padding:16px 26px;border:2px solid {GOLD};font-size:44px;font-weight:700">{w}</div>' for w in ("활꽃게", "기절꽃게", "빙장꽃게"))
          + f'</div><div style="font-size:40px;margin-top:20px">신선도 · 값 · 보관법이 다름 · <span style="color:{GOLD2}">가을 = 수꽃게</span></div><div style="font-size:30px;color:{MUTE};margin-top:10px">출처 · 이투데이(2026.8.31)</div></div></div></div>')
    pu = (f'<div id="{P}pu" style="position:absolute;left:0;right:0;top:170px;opacity:0"><div class="kick" style="text-align:center">용도로 고르기</div><div style="display:flex;justify-content:center;gap:60px;margin-top:30px">'
          f'<div id="{P}u1" style="width:760px;opacity:0;border-top:8px solid {GOLD2};background:#16181D;padding:44px"><div class="mj" style="font-size:90px">회</div><div style="font-size:54px;font-weight:700;margin-top:24px;color:{GOLD2}">활어</div><div style="font-size:42px;margin-top:12px">또는 잡은 지 24시간 이내 선어</div></div>'
          f'<div id="{P}u2" style="width:760px;opacity:0;border-top:8px solid {DOWN};background:#16181D;padding:44px;position:relative"><div class="mj" style="font-size:90px">구이·조림·찜·탕</div><div style="font-size:54px;font-weight:700;margin-top:24px;color:{DOWN}">선어 · 냉동</div><div style="font-size:42px;margin-top:12px">가성비</div>'
          f'<div id="{P}stamp" style="position:absolute;right:30px;bottom:30px;padding:12px 24px;border:4px solid {DOWN};color:{DOWN};font-size:44px;font-weight:800;transform:rotate(-8deg);opacity:0">이건 선어로</div></div></div>'
          f'<div id="{P}u3" style="text-align:center;font-size:44px;font-weight:700;margin-top:50px;opacity:0">익혀 먹을 생선까지 활어로 사면 <span style="color:{UP}">같은 1kg에 몇 배</span></div></div>')
    js = panels(T, [("pd", st(T, "def0", 1)), ("pb", st(T, "bars", 1)), ("pk", st(T, "key", 0)), ("pt", st(T, "twist", 0)), ("pc", st(T, "crab", 1)), ("pu", st(T, "use", 0))], end)
    js += "".join(f'tl.fromTo($("d{i}"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, k, 1)});' for i, (_, _, _, k) in enumerate(defs))
    js += f'tl.to($("dsrc"), {{ opacity: 1, duration: 0.4 }}, {st(T, "def3", 2)}); tl.to($("d4"), {{ opacity: 1, duration: 0.4 }}, {st(T, "def4", 1)});'
    for k, idx in ((1, [0]), (2, [1, 3]), (3, [2, 4, 5]), (4, [6, 7, 8])):
        js += "".join(f'tl.to($("r{i}"), {{ opacity: 1, duration: 0.3 }}, {st(T, "bar", k)} + {j * 0.4:.1f}); tl.fromTo($("rb{i}"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.7, ease: "power3.out" }}, {st(T, "bar", k)} + {j * 0.4:.1f});' for j, i in enumerate(idx))
    js += f'tl.to([$("rb0"), $("rb1")], {{ background: "{UP}", duration: 0.4 }}, {st(T, "bar", 5)});'
    js += "".join(f'tl.to($("k{i}"), {{ opacity: 1, duration: 0.5 }}, {st(T, "key", i)});' for i in (1, 2, 3)) + f'tl.to($("k3s"), {{ opacity: 1, duration: 0.4 }}, {st(T, "key", 3)} + 0.3);'
    for i, k in enumerate((1, 2, 3)):
        js += f'tl.fromTo($("t{i}"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, "twist", k)}); tl.fromTo(".{P}tb{i}", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.6, stagger: 0.2 }}, {st(T, "twist", k)} + 0.2);'
    js += f'tl.to($("t5"), {{ opacity: 1, duration: 0.4 }}, {st(T, "twist", 5)}); tl.to($("t4"), {{ opacity: 1, duration: 0.4 }}, {st(T, "twist", 4)}); tl.to($("c2"), {{ opacity: 1, duration: 0.5 }}, {st(T, "crab", 2)});'
    js += (f'tl.fromTo($("u1"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, "use", 1)}); tl.fromTo($("u2"), {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {st(T, "use", 2)});'
           f'tl.fromTo($("stamp"), {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }}, {st(T, "use", 2)} + 0.8); tl.to($("u3"), {{ opacity: 1, duration: 0.4 }}, {st(T, "use", 3)});')
    summ = summary(T, "활어 vs 선어 정리", ("같은 1kg", ["활어 = 선어의 최대 6.31배", "(넙치 4미)"]), ("선어는", ["등급·용도가 다른 물건", "구이·조림·찜·탕에"]), "회는 활어 · 익혀 먹을 건 선어나 냉동")
    js += chap_js(st(T, "def0", 1)) + f'\ntl.to($("sum"), {{ opacity: 1, duration: 0.6 }}, {end});'
    return scene(T, chapter(T, 3, "활어 vs 선어", "같은 생선, 다른 물건", "수조") + pd + pb + pk + pt + pc + pu + summ, js)


def faq(T):
    P = T["id"] + "-"
    qa = [("Q1. 제주 광어가 무조건 좋나요?", [("a", 1, "이번 경락가 · 제주 ≈ 완도 (<b class='num'>90</b>원 차이)"), ("a", 2, "2014 보도 · 제주 <b class='num'>23,000</b>t · 완도 <b class='num'>12,000</b>t · 완도 kg당 1,000원가량 더"),
                                          ("a", 3, "업계 설명 · 원가 차이 kg당 <b class='num'>500~1,500</b>원 · 체감 품질 차이 거의 없음")]),
          ("Q2. 크면 무조건 비싼가요?", [("a", 4, "대체로 그렇지만 · 전복 4/5미 &lt; 5/6미"), ("a", 5, f"<span style='color:{GOLD2}'>→ 올여름엔 큰 전복이 더 쌌던 때도 · 그때그때 시세 확인</span>")]),
          ("Q3. 선어회는 맛이 떨어지나요?", [("a", 6, "맛은 취향 · 경락시세로 답할 수 없음"), ("a", 7, f"<span style='color:{GOLD2}'>→ 저온 숙성한 회 · 감칠맛·부드러움으로 소개</span>")])]
    body = "".join(f'<div id="{P}q{i}" class="card" style="left:160px;right:160px;top:200px"><div class="mj" style="font-size:66px;color:{GOLD2}">{q}</div>'
                   + "".join(f'<div id="{P}a{i}{j}" style="font-size:44px;font-weight:700;margin-top:30px;opacity:0;word-break:keep-all">{a}</div>' for j, (_, _, a) in enumerate(ans)) + '</div>' for i, (q, ans) in enumerate(qa))
    body += f'<div id="{P}fin" class="card" style="left:300px;right:300px;top:330px;text-align:center"><div class="mj" style="font-size:80px">숫자로 확인하고,<br><span style="color:{GOLD2}">용도에 맞게</span></div></div>'
    js = seq(T, [("q0", "q", 1), ("q1", "q", 2), ("q2", "q", 3), ("fin", "a", 8)])
    js += "".join(f'tl.to($("a{i}{j}"), {{ opacity: 1, duration: 0.5 }}, {st(T, k, v)});' for i, (_, ans) in enumerate(qa) for j, (k, v, _) in enumerate(ans))
    js += f'tl.set($("fin"), {{ opacity: 1 }}, {st(T, "a", 8)} + 0.7);'
    return scene(T, body, js)


def checklist(T):
    P = T["id"] + "-"
    steps = [("용도", "회? 구이·탕?"), ("크기", "용도에 맞는 ‘미’ · 전복 회 8~10미"), ("산지", "같은 크기끼리 · 원산지 표시"), ("활·선", "회는 활어 · 익혀 먹으면 선어·냉동")]
    rows = "".join(f'<div id="{P}r{i}" style="display:flex;align-items:center;gap:40px;padding:14px 30px;border-bottom:1px solid {GOLD}44;opacity:0">'
                   f'<div class="num" style="font-size:72px;color:{GOLD};width:90px">{i + 1}</div><div class="mj" style="font-size:78px;width:300px">{a}</div><div style="font-size:48px;font-weight:700;color:{MUTE}">{b}</div></div>' for i, (a, b) in enumerate(steps))
    body = (f'<div id="{P}tb" style="position:absolute;left:220px;right:220px;top:110px"><div style="text-align:center"><div class="kick">SHOPPING CHECKLIST</div><div class="mj" style="font-size:80px;margin-top:6px">장보기 전 4단계</div></div>{rows}'
            f'<div id="{P}ord" style="font-size:42px;font-weight:700;margin-top:18px;text-align:center;color:{GOLD2};opacity:0">산지보다 <u>용도와 크기</u>를 먼저</div></div>'
            f'<div id="{P}cap" style="position:absolute;right:120px;top:120px;padding:14px 26px;border:2px solid {GOLD};font-size:36px;font-weight:800;color:{GOLD2};opacity:0;transform:rotate(4deg)">📸 캡처해 두세요</div>'
            f'<div id="{P}how" class="card" style="left:300px;right:300px;top:330px;text-align:center"><div class="kick">매일 경락가 보는 곳</div><div style="font-size:56px;font-weight:700;margin-top:20px">노량진수산 홈페이지 → 수산물가격정보</div>'
            f'<div style="font-size:40px;color:{MUTE};margin-top:14px">susansijang.co.kr · 가기 전날 확인</div></div>')
    js = ("".join(f'tl.fromTo($("r{i}"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.6 }}, {st(T, "row", i)});' for i in range(4))
          + f'tl.to($("ord"), {{ opacity: 1, duration: 0.5 }}, {st(T, "order", 1)}); tl.to($("cap"), {{ opacity: 1, duration: 0.4 }}, {st(T, "hold", 1)});'
          + f'tl.to([$("tb"), $("cap")], {{ opacity: 0, duration: 0.4 }}, {st(T, "howto", 1)} - 0.3); show("how", {st(T, "howto", 1)});')
    return scene(T, body, js)


def outro(T):
    P = T["id"] + "-"
    body = (f'<div id="{P}d" class="card" style="left:200px;right:200px;top:210px;text-align:center"><div class="kick" style="color:{UP}">꼭 기억하세요</div>'
            f'<div class="mj" style="font-size:72px;margin-top:24px;color:{GOLD2}">경락가 = 도매 낙찰가 ≠ 가게 판매가</div>'
            f'<div class="mj" style="font-size:58px;margin-top:26px">2026년 9~11월 숫자 ≠ 다른 시기 보장</div>'
            f'<div id="{P}d3" class="mj" style="font-size:52px;margin-top:26px;opacity:0">산지 차이의 원인은 알 수 없음 · 산지·나라의 좋고 나쁨 ✕</div>'
            f'<div style="font-size:34px;color:{MUTE};margin-top:26px">자료 · 노량진수산(주) 어종별 경락시세 (susansijang.co.kr)</div></div>'
            f'<div id="{P}o" class="card" style="left:280px;right:280px;top:300px"><div class="kick">MY TAKE</div><div class="mj" style="font-size:64px;line-height:1.5;margin-top:20px">값을 가장 크게 가른 건<br><span style="color:{GOLD2}">활어냐 선어냐</span>, 그리고 <span style="color:{GOLD2}">크기</span></div></div>'
            f'<div id="{P}e" style="position:absolute;inset:0;opacity:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:{INK}">'
            f'<div class="kick">SEE YOU NEXT REPORT</div><div class="mj" style="font-size:100px;margin-top:20px">산지와 크기, 뭘 먼저 보세요?</div><div style="font-size:46px;color:{GOLD2};margin-top:26px">댓글 · 구독 · 알림 설정</div></div>')
    js = seq(T, [("d", "disc", 1), ("o", "opinion", 1), ("e", "cta", 1)]) + f'tl.to($("d3"), {{ opacity: 1, duration: 0.5 }}, {st(T, "disc", 3)});'
    return scene(T, body, js)


# ------------------------------------------------------------------ 자막
def one_line(x, n=16):  # 45~54세 시청층: 한 화면 글자를 조금 줄임(16자)
    out, cur = [], ""
    for w in x.split(" "):
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
            sub = re.sub(r"(\d만) (\d천)", "\\1\u00a0\\2", sub); sub = re.sub(r"(\d천|\d만) 원", "\\1\u00a0원", sub)
            lines = one_line(sub); durs = voice_split(x["wav"], [len(l) for l in lines], x["dur"]); t0 = T["start"] + x["start"]
            for l, du in zip(lines, durs):
                h = re.sub(r"(\d[\d,~·./%]*(?:만(?: \d천)? 원|천 원|원|kg|배|미|톤|g|건|일|월|년|%|시간|가지|단계|품목|개|달)?)", r"<b>\1</b>", l)
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
    json.dump(dict(id="data_longform2", name="data_longform2", createdAt="2026-11-08T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
    for f in ("NanumMyeongjo-ExtraBold.ttf", "Pretendard-Bold.otf", "Pretendard-SemiBold.otf", "Pretendard-ExtraBold.otf"): shutil.copy(f"{FONTDIR}/{f}", f"{HF}/assets/fonts/{f}")
    for i in PHOTO.values(): shutil.copy(f"{IMG}/{i}.jpg", f"{HF}/assets/img/{i}.jpg")
    F = dict(hook=hook, title=title, origin=origin, size=size, live=live, faq=faq, checklist=checklist, outro=outro)
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
