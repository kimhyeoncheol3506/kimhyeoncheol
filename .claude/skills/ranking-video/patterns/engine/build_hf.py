# -*- coding: utf-8 -*-
"""데이터 롱폼 공용 엔진 — 패턴(00_data/pattern.json, 없으면 0번 먹색+금색) 화면 톤으로 HyperFrames 프로젝트 생성 (음성 1.12배속, 기본 템포)
사용: python3 build_hf.py [--est]  → hf/ , timeline.json
장면: trick(대안 생선 챕터) · flow(주별 선 그래프) · title · checklist · outro (+ 공용 calc/table/pick/flow) (화면 데이터는 대본데이터.json의 vis)
"""
import json, os, re, shutil, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EST = "--est" in sys.argv
D = json.load(open(f"{ROOT}/01_대본/대본데이터.json", encoding="utf-8"))
DATA = json.load(open(f"{ROOT}/00_data/prices.json", encoding="utf-8")) if os.path.exists(f"{ROOT}/00_data/prices.json") else {}
TTS = f"{ROOT}/02_음성"; HF = f"{HERE}/hf"; IMG = f"{ROOT}/09_소재/img_final"
PHOTO = json.load(open(f"{IMG}/pick.json", encoding="utf-8"))
FONTDIR = os.path.expanduser("~/.cache/ranking-video/fonts")
TEMPO = 1.0
END_SCREEN = 17.5  # 유튜브 최종 화면(15~20초) 자리
GAP, LEAD = 0.5 * TEMPO, 0.7 * TEMPO
PATTERNS = "/home/user/kimhyeoncheol/.claude/skills/ranking-video/patterns"; sys.path.insert(0, PATTERNS)
import theme as TH
TM = TH.load(ROOT); _c = TM["c"]
INK, GOLD, GOLD2, IVORY, MUTE, DOWN, UP, GREY = _c["ink"], _c["acc"], _c["acc2"], _c["text"], _c["mute"], _c["down"], _c["up"], _c["grey"]
CARD, CARD2, BG3, LINE = _c["card"], _c["card2"], _c["bg3"], _c["line"]
FONTS = TH.fonts()
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
    dur = cur + (2.4 if s["kind"] in ("outro", "checklist") else 0.9) * TEMPO
    if s["kind"] == "outro":  # 엔딩화면 자리: 마지막 멘트(end=1)부터 영상 끝까지 최소 END_SCREEN초, 화면엔 중요 정보 없음
        e0 = next((x["start"] for x in S if x["sig"].get("end") == 1), None)
        if e0 is not None: dur = max(dur, e0 + END_SCREEN)
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
            f".hdr{{position:absolute;left:70px;top:54px;font-size:28px;letter-spacing:.18em;color:{GOLD}cc;font-weight:700}}"
            + TH.head_css(TM) + ".num{font-family:PXB,PX,sans-serif;font-weight:800;font-variant-numeric:tabular-nums}"
            f".kick{{font-size:32px;letter-spacing:.3em;color:{GOLD};font-weight:700}}" + TH.card_css(TM) + extra)


def scene(T, body, js, extra_css="", hdr=True, fade=True):
    P = T["id"] + "-"; sid = T["id"]
    js0 = f'''
const tl = gsap.timeline({{ paused: true }}); const $ = (i) => "#{P}" + i;
{TH.wipe_js(TM, fade, T["dur"])}
function count(sel, from, to, at, dur, fmt) {{ const o = {{ v: from }}; tl.to(o, {{ v: to, duration: dur || 1.2, ease: "power2.out", onUpdate: () => {{ document.querySelector(sel).textContent = fmt(o.v); }} }}, at); }}
const Wf = (v) => Math.round(v).toLocaleString("en-US");
function show(id, a, b) {{ tl.fromTo($(id), {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, a); if (b !== undefined && b !== null) tl.to($(id), {{ opacity: 0, duration: 0.35 }}, b); }}
'''
    h = f'<div class="hdr">{D["hdr"]}</div>' if hdr else ""
    return (f'<template><style>{css_base(extra_css)}</style><div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">'
            + TH.layer(TM, P, h + body) + TH.wipe_html(TM, P) + '</div>'
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


def chapter(T, n, title, sub, ph, kick=None):
    P = T["id"] + "-"
    html = (f'<div id="{P}chap" style="position:absolute;inset:0"><img id="{P}cimg" src="assets/img/{PHOTO[ph]}.jpg" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">'
            f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,{INK}f2 0%,{INK}b0 45%,{INK}40 100%)"></div>'
            f'<div style="position:absolute;left:140px;top:330px"><div class="kick">{kick or f"TRICK {n:02d}"}</div><div class="mj" style="font-size:200px;line-height:1.15;margin-top:10px">{title}</div>'
            f'<div style="font-size:44px;color:{GOLD2}">{sub}</div></div></div>')
    return html


def chap_js(t_off):
    return f'tl.fromTo($("cimg"), {{ scale: 1.12 }}, {{ scale: 1, duration: {t_off + 0.5:.2f}, ease: "none" }}, 0); tl.to($("chap"), {{ opacity: 0, duration: 0.5 }}, {t_off} - 0.2);'


def summary(T, name, left, right, foot):
    P = T["id"] + "-"
    col = lambda c, k, xs: (f'<div style="width:740px;border-top:6px solid {c};padding:36px 40px;background:{CARD2}"><div class="kick" style="color:{c}">{k}</div>'
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


# ------------------------------------------------------------------ 장면 (화면 숫자는 vis에서만)
V = lambda T: T["s"].get("vis", {})


def hook(T):
    P = T["id"] + "-"; v = V(T)
    body = (f'<div id="{P}q" class="card" style="left:0;right:0;top:250px;background:none;border:none;text-align:center"><div class="kick">CHRISTMAS · YEAR-END · 연말 모임</div>'
            f'<div class="mj" style="font-size:120px;line-height:1.25;margin-top:20px">{v["q"]}</div></div>'
            f'<div id="{P}c1" class="card" style="left:0;right:0;top:170px;background:none;border:none;text-align:center"><div class="kick">{v["label"]}</div>'
            f'<div class="num" style="font-size:230px;color:{GOLD2};line-height:1.1"><span id="{P}w">0</span><span style="font-size:90px">원</span></div>'
            f'<div style="font-size:46px;font-weight:700;margin-top:10px">{v["sub"]}</div><div style="font-size:34px;color:{MUTE};margin-top:14px">{v["note"]}</div></div>'
            f'<div id="{P}c2" class="card" style="left:0;right:0;top:250px;background:none;border:none;text-align:center"><div class="kick">이 두 가지만 알면</div>'
            f'<div style="display:flex;justify-content:center;gap:50px;margin-top:40px">' + "".join(f'<div style="width:520px;padding:40px;border:2px solid {GOLD}"><div class="mj" style="font-size:84px;color:{GOLD2}">{a}</div><div style="font-size:40px;margin-top:14px">{b}</div></div>' for a, b in v["two"]) + '</div></div>'
            f'<div id="{P}c3" class="card" style="left:200px;right:200px;top:280px;text-align:center"><div class="kick">오늘 정리</div><div style="display:flex;justify-content:center;gap:24px;margin-top:30px;flex-wrap:wrap">'
            + "".join(f'<div class="mj" style="font-size:54px;padding:12px 26px;border:1px solid {GOLD}88">{w}</div>' for w in v["agenda"]) + '</div></div>')
    js = (f'tl.set($("q"), {{ opacity: 1 }}, 0); tl.fromTo($("q"), {{ scale: 1.06, transformOrigin: "50% 50%" }}, {{ scale: 1, duration: 1.2 }}, 0); tl.to($("q"), {{ opacity: 0, duration: 0.3 }}, {st(T, "count", 1)} - 0.25);'
          + seq(T, [("c1", "count", 1), ("c2", "two", 1), ("c3", "agenda", 1)]) + f'count($("w"), 0, {v["won"]}, {st(T, "count", 1)} + 0.4, 1.8, Wf);'
          + f'tl.set($("c3"), {{ opacity: 1 }}, {st(T, "agenda", 1)} + 0.7);')
    return scene(T, body, js, hdr=False, fade=False)


def cards_scene(T, extra_html="", extra_js=""):
    """vis.cards: [{sig:[key,val], kick, big, lines, photo}] — 화면 가운데 큰 카드가 차례로"""
    P = T["id"] + "-"; v = V(T); C = v["cards"]; html = []
    for i, c in enumerate(C):
        img = f'<div style="height:300px;margin:-34px -40px 26px;overflow:hidden"><img src="assets/img/{PHOTO[c["photo"]]}.jpg" style="width:100%;height:100%;object-fit:cover"></div>' if c.get("photo") else ""
        big = f'<div class="num" style="font-size:{c.get("bigsize", 130)}px;color:{GOLD2};line-height:1.1;margin-top:10px">{c["big"]}</div>' if c.get("big") else ""
        if c.get("vs"):
            col = lambda k, t_, xs, cl: (f'<div style="flex:1;border-top:6px solid {cl};padding:26px 30px;background:{CARD2}"><div class="kick" style="color:{cl}">{t_}</div>'
                                         + "".join(f'<div class="mj" style="font-size:50px;margin-top:20px;line-height:1.3;word-break:keep-all">{x}</div>' for x in xs) + '</div>')
            vs = c["vs"]; big = f'<div style="display:flex;gap:40px;margin-top:26px;text-align:left">{col(0, vs[0][0], vs[0][1], DOWN)}{col(1, vs[1][0], vs[1][1], UP)}</div>'
        lines = "".join(f'<div style="font-size:{c.get("size", 46)}px;font-weight:700;margin-top:18px;line-height:1.35;word-break:keep-all">{ln}</div>' for ln in c.get("lines", []))
        html.append(f'<div id="{P}x{i}" class="card" style="left:{c.get("left", 300)}px;right:{c.get("left", 300)}px;top:{c.get("top", 200)}px;text-align:center">{img}<div class="kick">{c["kick"]}</div>{big}{lines}</div>')
    js = seq(T, [(f"x{i}", c["sig"][0], c["sig"][1]) for i, c in enumerate(C)]) + f'tl.set($("x{len(C) - 1}"), {{ opacity: 1 }}, {st(T, C[-1]["sig"][0], C[-1]["sig"][1])} + 0.7);'
    return scene(T, "".join(html) + extra_html, js + extra_js)


def title(T): return cards_scene(T)


def calc(T): return cards_scene(T)


def table(T):
    P = T["id"] + "-"; v = V(T); H = v["head"]
    rows = "".join(f'<tr id="{P}r{i}" style="opacity:0"><td class="mj" style="text-align:left;font-size:48px">{r[0]}<div style="font-size:22px;color:{MUTE};font-family:PX">{r[1]}</div></td>'
                   + "".join(f'<td><div class="num" style="font-size:42px">{a}</div><div class="num" style="font-size:32px;color:{GOLD2}">{b}</div></td>' for a, b in r[2]) + '</tr>' for i, r in enumerate(v["rows"]))
    body = (f'<div style="position:absolute;left:0;right:0;top:110px;text-align:center"><div class="kick">{v["kick"]}</div></div>'
            f'<table style="position:absolute;left:150px;top:180px;width:1620px;border-collapse:collapse;text-align:center">'
            f'<tr style="font-size:34px;color:{GOLD}"><td style="text-align:left">{v.get("head0", "생선 · 수율 · kg당 경락가")}</td>' + "".join(f'<td>{h}</td>' for h in H) + f'</tr>{rows}</table>'
            f'<div id="{P}ft" style="position:absolute;left:0;right:0;top:868px;text-align:center;font-size:30px;color:{MUTE};opacity:0">{v["foot"]}</div>')
    tr, last = [], 0.8
    for i in range(len(v["rows"])):
        last = st(T, "row", i, last + 0.35); tr.append(last)   # 대본이 짚지 않는 행은 앞 행 바로 뒤에
    js = "".join(f'tl.fromTo($("r{i}"), {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.5 }}, {t});' for i, t in enumerate(tr))
    js += f'tl.to($("ft"), {{ opacity: 1, duration: 0.5 }}, {st(T, "foot", 1, last + 0.6)});'
    return scene(T, body, js, f"#root td{{padding:6px 10px;border-top:1px solid {GOLD}33}}")


def pick(T):
    P = T["id"] + "-"; v = V(T); B = v["bars"]; mx = max(b[1] for b in B)
    bars = "".join(f'<div id="{P}b{i}" style="display:flex;align-items:center;gap:22px;margin:18px 0;opacity:0"><div class="mj" style="width:200px;text-align:right;font-size:52px">{n}</div>'
                   f'<div id="{P}bb{i}" style="height:64px;width:{val / mx * 760:.0f}px;background:linear-gradient(90deg,{GOLD}44,{c})"></div><div class="num" style="font-size:50px;white-space:nowrap">{val:,}<span style="font-size:30px;color:{MUTE}">원</span></div></div>'
                   for i, (n, val, c) in enumerate((b[0], b[1], {"down": DOWN, "up": UP}.get(b[2], GOLD2)) for b in B))
    panel = (f'<div id="{P}pb" style="position:absolute;left:100px;top:150px;width:1700px;opacity:0"><div class="kick">{v["kick"]}</div><div style="font-size:34px;color:{MUTE};margin:10px 0 20px">{v["sub"]}</div>{bars}</div>')
    js = f'tl.to($("pb"), {{ opacity: 1, duration: 0.5 }}, {st(T, "bars", 1)}); tl.to($("pb"), {{ opacity: 0, duration: 0.3 }}, {st(T, v["cards"][0]["sig"][0], v["cards"][0]["sig"][1])} - 0.3);'
    js += "".join(f'tl.to($("b{i}"), {{ opacity: 1, duration: 0.3 }}, {st(T, "bars", 1)} + {0.6 + i * 0.35:.2f}); tl.fromTo($("bb{i}"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.7 }}, {st(T, "bars", 1)} + {0.6 + i * 0.35:.2f});' for i in range(len(B)))
    return cards_scene(T, panel, js)


def flow(T):
    P = T["id"] + "-"; v = V(T); L = v["lines"]; X0, X1, Y0, Y1 = 140, 1180, 110, 560; lo, hi = v["ymin"], v["ymax"]; n = len(v["x"])
    xi = lambda i: X0 + i * (X1 - X0) / (n - 1); yv = lambda p: Y1 - (p - lo) / (hi - lo) * (Y1 - Y0)
    svg = [f'<rect width="1260" height="640" fill="{LINE}07"/>']
    for p in range(lo, hi + 1, v["step"]):
        svg.append(f'<line x1="{X0}" y1="{yv(p):.0f}" x2="{X1}" y2="{yv(p):.0f}" stroke="{LINE}" stroke-opacity=".15" stroke-dasharray="6 10"/><text x="{X0 - 14}" y="{yv(p) + 10:.0f}" font-size="28" fill="{MUTE}" text-anchor="end">{p / 10000:g}만</text>')
    for i, x in enumerate(v["x"]): svg.append(f'<text x="{xi(i):.0f}" y="{Y1 + 50}" font-size="30" font-weight="700" fill="{IVORY}" text-anchor="middle">{x}</text>')
    leg = []
    for k, l in enumerate(L):
        pts = [(xi(i), yv(p)) for i, p in enumerate(l["p"]) if p]
        svg.append(f'<polyline id="{P}l{k}" points="{" ".join(f"{a:.0f},{b:.0f}" for a, b in pts)}" fill="none" stroke="{l["c"]}" stroke-width="7" stroke-linecap="butt" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" opacity="0"/>')
        svg += [f'<g class="{P}d{k}" opacity="0"><circle cx="{a:.0f}" cy="{b:.0f}" r="9" fill="{l["c"]}"/></g>' for (a, b), p in zip(pts, [p for p in l["p"] if p])]
        leg.append(f'<span style="margin-right:30px"><b style="color:{l["c"]}">━</b> {l["name"]}</span>')
    chart = (f'<div id="{P}ch" style="position:absolute;left:60px;top:150px;opacity:0"><div style="font-size:34px;color:{MUTE};margin:0 0 6px 20px">{v["title"]}</div>'
             f'<div style="font-size:30px;margin:0 0 10px 20px">{"".join(leg)}</div><svg width="1260" height="640" viewBox="0 0 1260 640">{"".join(svg)}</svg></div>')
    js = f'tl.to($("ch"), {{ opacity: 1, duration: 0.5 }}, {st(T, "chart", 1)});'
    for k, l in enumerate(L):
        t0 = st(T, "line", k); js += f'tl.set($("l{k}"), {{ opacity: 1 }}, {t0}); tl.to($("l{k}"), {{ strokeDashoffset: 0, duration: 1.6 }}, {t0}); tl.to(".{P}d{k}", {{ opacity: 1, duration: 0.3, stagger: 0.12 }}, {t0} + 0.4);'
    ch, cj = rcards(T, [tuple(c) for c in v["rc"]], st(T, "end", 1, T["dur"]))
    return scene(T, chart + ch, js + cj)


def checklist(T):
    P = T["id"] + "-"; v = V(T)
    rows = "".join(f'<div id="{P}r{i}" style="display:flex;align-items:center;gap:36px;padding:14px 30px;border-bottom:1px solid {GOLD}44;opacity:0">'
                   f'<div class="num" style="font-size:64px;color:{GOLD};width:70px">{i + 1}</div><div class="mj" style="font-size:66px;width:330px">{a}</div><div style="font-size:42px;font-weight:700;color:{MUTE}">{b}</div></div>' for i, (a, b) in enumerate(v["rows"]))
    body = (f'<div id="{P}tb" style="position:absolute;left:180px;right:180px;top:100px"><div style="text-align:center"><div class="kick">SHOPPING CHECKLIST</div><div class="mj" style="font-size:76px;margin-top:6px">{v["title"]}</div></div>{rows}</div>'
            f'<div id="{P}cap" style="position:absolute;right:110px;top:110px;padding:14px 26px;border:2px solid {GOLD};font-size:36px;font-weight:800;color:{GOLD2};opacity:0;transform:rotate(4deg)">📸 캡처해 두세요</div>')
    js = "".join(f'tl.fromTo($("r{i}"), {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.6 }}, {st(T, "row", i)});' for i in range(len(v["rows"])))
    js += f'tl.to($("cap"), {{ opacity: 1, duration: 0.4 }}, {st(T, "hold", 1)});'
    return scene(T, body, js)


def outro(T):
    P = T["id"] + "-"; v = V(T)
    body = (f'<div id="{P}d" class="card" style="left:180px;right:180px;top:220px;text-align:center"><div class="kick" style="color:{UP}">꼭 기억하세요</div>'
            + "".join(f'<div class="mj" style="font-size:{60 if i else 72}px;margin-top:24px;color:{GOLD2 if not i else IVORY}">{x}</div>' for i, x in enumerate(v["disc"]))
            + f'<div style="font-size:30px;color:{MUTE};margin-top:26px">{D["src_label"]}</div></div>'
            f'<div id="{P}o" class="card" style="left:280px;right:280px;top:300px"><div class="kick">MY TAKE</div><div class="mj" style="font-size:62px;line-height:1.5;margin-top:20px">{v["take"]}</div></div>'
            f'<div id="{P}e" style="position:absolute;inset:0;opacity:0;display:flex;flex-direction:column;justify-content:center;align-items:center;background:{INK}">'
            f'<div class="kick">EVERY SATURDAY · 매주 토요일</div><div class="mj" style="font-size:96px;margin-top:20px;text-align:center;line-height:1.3">이번 주 노량진 시세<br><span style="color:{GOLD2}">장보기 전에 받아보기</span></div>'
            f'<div style="font-size:36px;color:{MUTE};margin-top:30px">재생목록 · 노량진 주간 시세 리포트</div></div>'
            f'<div id="{P}end" style="position:absolute;inset:0;background:{INK};opacity:0"><div class="kick" style="position:absolute;left:0;right:0;top:110px;text-align:center;font-size:28px;color:{GOLD}99">{D["end_label"]}</div></div>')
    js = seq(T, [("d", "disc", 1), ("o", "opinion", 1), ("e", "cta", 1)]) + f'tl.set($("e"), {{ opacity: 1 }}, {st(T, "cta", 1)} + 0.7); tl.to($("end"), {{ opacity: 1, duration: 0.6 }}, {st(T, "end", 1)} - 0.3);'
    return scene(T, body, js)


# ------------------------------------------------------------------ 킹크랩 편 전용
def scale_html(P, sid, x, y, label, color):
    return (f'<div id="{P}{sid}" style="position:absolute;left:{x}px;top:{y}px;width:640px;text-align:center;opacity:0">'
            f'<div class="kick" style="color:{color}">{label}</div>'
            f'<div style="margin:20px auto 0;width:560px;padding:18px 0;background:{BG3};border:3px solid {color};box-shadow:0 0 40px {color}33">'
            f'<span class="num" id="{P}{sid}v" style="font-size:170px;color:{color};line-height:1">0.00</span><span class="num" style="font-size:64px;color:{color}"> kg</span></div>'
            f'<div style="margin:26px auto 0;width:640px;height:26px;background:linear-gradient(180deg,{GOLD2},{GOLD});border-radius:4px"></div>'
            f'<div style="margin:0 auto;width:520px;height:150px;background:linear-gradient(180deg,{CARD2},{BG3});border:1px solid {GOLD}55;clip-path:polygon(4% 0,96% 0,100% 100%,0 100%)"></div></div>')


def hookscale(T):
    P = T["id"] + "-"; v = V(T); ta = st(T, "a", 1)
    body = (scale_html(P, "s1", 230, 220, "가게 저울", GOLD2) + scale_html(P, "s2", 1050, 220, "집 저울", UP)
            + f'<div id="{P}qm" class="mj" style="position:absolute;left:0;right:0;top:120px;text-align:center;font-size:64px;color:{IVORY};opacity:0">킹크랩, 3kg 샀는데 2kg?</div>'
            f'<div id="{P}c1" class="card" style="left:0;right:0;top:200px;background:none;border:none;text-align:center"><div class="kick">1kg 차이 · 도매 경락가로만</div>'
            f'<div class="num" style="font-size:220px;color:{GOLD2};line-height:1.1"><span id="{P}w">0</span><span style="font-size:90px">원</span></div>'
            f'<div style="font-size:44px;font-weight:700;margin-top:10px">{v["sub"]}</div><div style="font-size:36px;color:{UP};margin-top:16px">{v["note"]}</div></div>'
            f'<div id="{P}c2" class="card" style="left:260px;right:260px;top:210px;text-align:center"><div class="kick">하지만 · 찌면 원래 줄어든다</div>'
            f'<div class="num" style="font-size:150px;color:{GOLD2};margin-top:10px">−30~35%</div><div style="font-size:44px;font-weight:700;margin-top:6px">일반 킹크랩 찜 감량 · 전문가 설명(보도)</div>'
            f'<div id="{P}c2b" class="mj" style="font-size:66px;margin-top:30px;opacity:0">3kg → 약 2kg = <span style="color:{DOWN}">자연 감량일 수도</span></div></div>'
            f'<div id="{P}c3" class="card" style="left:160px;right:160px;top:280px;text-align:center"><div class="kick">오늘 정리</div><div style="display:flex;justify-content:center;gap:24px;margin-top:30px;flex-wrap:wrap">'
            + "".join(f'<div class="mj" style="font-size:52px;padding:12px 26px;border:1px solid {GOLD}88">{w}</div>' for w in v["agenda"]) + '</div></div>')
    js = (f'tl.set($("s1"), {{ opacity: 1 }}, 0); tl.set($("s2"), {{ opacity: 1 }}, 0); tl.set($("qm"), {{ opacity: 1 }}, 0);'
          f'tl.fromTo([$("s1"), $("s2")], {{ y: 40 }}, {{ y: 0, duration: 0.8, ease: "power3.out" }}, 0);'
          f'count($("s1v"), 0, {v["a"]}, {ta} + 0.2, 1.4, (x) => x.toFixed(2)); count($("s2v"), 0, {v["b"]}, {ta} + 2.0, 1.4, (x) => x.toFixed(2));'
          f'tl.to([$("s1"), $("s2"), $("qm")], {{ opacity: 0, duration: 0.35 }}, {st(T, "loss", 1)} - 0.3);'
          + seq(T, [("c1", "loss", 1), ("c2", "steam", 1), ("c3", "agenda", 1)]) + f'count($("w"), 0, {v["loss"]}, {st(T, "loss", 1)} + 0.4, 1.6, Wf);'
          f'tl.to($("c2b"), {{ opacity: 1, duration: 0.5 }}, {st(T, "steam", 3)}); tl.set($("c3"), {{ opacity: 1 }}, {st(T, "agenda", 1)} + 0.7);')
    return scene(T, body, js, hdr=False, fade=False)


def trick(T):
    v = V(T); t1 = st(T, v["cards"][0]["sig"][0], v["cards"][0]["sig"][1])
    kick = f"ALT {v['n']:02d} · 제2의 방어 {v['n']}"
    return cards_scene(T, chapter(T, v["n"], v["title"], v["sub"], v["photo"], kick), chap_js(t1))


def loss(T):
    P = T["id"] + "-"; v = V(T); R = v["rows"]; mx = max(r[2] for r in R)
    bars = "".join(f'<div id="{P}b{i}" style="display:flex;align-items:center;gap:24px;margin:22px 0;opacity:0"><div style="width:330px;text-align:right"><div class="mj" style="font-size:46px">{a}</div><div class="num" style="font-size:34px;color:{MUTE}">{g:,}g</div></div>'
                   f'<div id="{P}bb{i}" style="height:70px;width:{amt / mx * 900:.0f}px;background:linear-gradient(90deg,{GOLD}44,{UP if i == len(R) - 1 else GOLD2})"></div>'
                   f'<div class="num" style="font-size:54px;white-space:nowrap">약 {won_disp(amt)}</div></div>' for i, (a, g, amt) in enumerate(R))
    body = (f'<div style="position:absolute;left:110px;top:120px;width:1700px"><div class="kick" style="font-size:28px;letter-spacing:.1em">{v["kick"]}</div>{bars}</div>'
            f'<div id="{P}ft" style="position:absolute;left:0;right:0;top:900px;text-align:center;font-size:30px;color:{MUTE};opacity:0">{v["foot"]}</div>')
    plan = {0: st(T, "row", 1), 1: st(T, "row", 1) + 1.6, 2: st(T, "row", 3), 3: st(T, "row", 3) + 2.0, 4: st(T, "row", 4)}
    js = "".join(f'tl.to($("b{i}"), {{ opacity: 1, duration: 0.3 }}, {plan[i]:.2f}); tl.fromTo($("bb{i}"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.7 }}, {plan[i]:.2f});' for i in range(len(R)))
    js += f'tl.to($("ft"), {{ opacity: 1, duration: 0.5 }}, {st(T, "foot", 1)});'
    return scene(T, body, js)


# ------------------------------------------------------------------ 광어 수율 편 전용
import yieldfx


def sx(T, key, val=1):
    x = next(x for x in T["S"] if x["sig"].get(key) == val); return x["start"], x["dur"]


def yieldhook(T):
    P = T["id"] + "-"; v = V(T); a0, _ = sx(T, "q"); c0, cd = sx(T, "cut"); r0, _ = sx(T, "res")
    body = (f'<div id="{P}qq" class="mj" style="position:absolute;left:0;right:0;top:70px;text-align:center;font-size:84px;opacity:0">{v["fish"]} {v["start"]} 사면, 회는 몇 g?</div>'
            + yieldfx.html(P, 385, 175, 1150, v["fish"], start_kg=v["start"], end_g=v["end"])
            + f'<div id="{P}c1" class="card" style="left:0;right:0;top:200px;background:none;border:none;text-align:center"><div class="kick">회 100g당 도매 원가 · {v["fish"]} · 수율 40%</div>'
            f'<div class="num" style="font-size:230px;color:{GOLD2};line-height:1.1"><span id="{P}w">0</span><span style="font-size:90px">원</span></div>'
            f'<div style="font-size:44px;font-weight:700;margin-top:10px">kg당 경락가 {DATA["two"]["items"]["넙치(활)"]["med"]:,}원 ÷ 40% ÷ 10</div><div style="font-size:34px;color:{MUTE};margin-top:14px">노량진 도매 경락가 · 가게 판매가 아님</div></div>'
            f'<div id="{P}c3" class="card" style="left:200px;right:200px;top:300px;text-align:center"><div class="kick">오늘 정리</div><div style="display:flex;justify-content:center;gap:24px;margin-top:30px;flex-wrap:wrap">'
            + "".join(f'<div class="mj" style="font-size:52px;padding:12px 26px;border:1px solid {GOLD}88">{w}</div>' for w in v["agenda"]) + '</div></div>')
    t = dict(show=0.15, head=c0 + 0.05, bone=c0 + cd * 0.38, skin=c0 + cd * 0.68, plate=r0)
    js = (f'tl.fromTo($("qq"), {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, 0.05);' + yieldfx.js(P, t)
          + f'tl.to([$("yf"), $("qq")], {{ opacity: 0, duration: 0.35 }}, {st(T, "cost", 1)} - 0.3);'
          + seq(T, [("c1", "cost", 1), ("c3", "agenda", 1)]) + f'count($("w"), 0, {v["c100"]}, {st(T, "cost", 1)} + 0.4, 1.6, Wf); tl.set($("c3"), {{ opacity: 1 }}, {st(T, "agenda", 1)} + 0.7);')
    return scene(T, body, js, hdr=False, fade=False)


def ybars(T):
    P = T["id"] + "-"; v = V(T); R = v["rows"]; X0, WD, MX = 330, 760, 60
    xp = lambda p: X0 + p / MX * WD
    grid = "".join(f'<div style="position:absolute;left:{xp(p):.0f}px;top:0;bottom:0;border-left:1px dashed {LINE}22"><div style="position:absolute;top:-44px;left:-30px;width:60px;text-align:center;font-size:28px;color:{MUTE}">{p}%</div></div>' for p in range(0, MX + 1, 10))
    rows = "".join(f'<div id="{P}r{i}" style="position:absolute;left:0;top:{40 + i * 108}px;width:1700px;height:100px;opacity:0"><div class="mj" style="position:absolute;left:0;width:290px;text-align:right;font-size:56px;top:14px">{n}</div>'
                   f'<div id="{P}b{i}" style="position:absolute;left:{xp(lo):.0f}px;top:22px;height:56px;width:{max(14, (hi - lo) / MX * WD):.0f}px;background:linear-gradient(90deg,{GOLD},{GOLD2});border-radius:28px"></div>'
                   f'<div class="num" style="position:absolute;left:{xp(MX) + 40:.0f}px;top:16px;font-size:50px;white-space:nowrap">{lo}{"" if lo == hi else f"~{hi}"}% <span style="font-size:34px;color:{MUTE}">1kg → 회 {lab}</span></div></div>'
                   for i, (n, lo, hi, lab) in enumerate(R))
    body = (f'<div id="{P}pn" style="position:absolute;left:110px;top:120px;width:1700px;opacity:0"><div class="kick" style="font-size:28px;letter-spacing:.12em">{v["kick"]}</div>'
            f'<div style="position:absolute;left:0;top:120px;width:1700px;height:620px">{grid}{rows}</div></div>'
            f'<div id="{P}ft" style="position:absolute;left:0;right:0;top:850px;text-align:center;font-size:30px;color:{MUTE};opacity:0">{v["foot"]}</div>')
    js = f'tl.to($("pn"), {{ opacity: 1, duration: 0.5 }}, {st(T, "bars", 1)});'
    for i in range(len(R)):
        t0 = st(T, "row", i); js += f'tl.to($("r{i}"), {{ opacity: 1, duration: 0.3 }}, {t0}); tl.fromTo($("b{i}"), {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.7, ease: "power3.out" }}, {t0});'
    js += f'tl.to($("ft"), {{ opacity: 1, duration: 0.5 }}, {st(T, "foot", 1)});'
    return scene(T, body, js)



def pctbars(T):
    """vis.rows: [(이름, 변화%, 단위)] — 0을 가운데 두고 내린 것은 왼쪽(초록), 오른 것은 오른쪽(빨강)"""
    P = T["id"] + "-"; v = V(T); R = v["rows"]; MX = max(abs(r[1]) for r in R); C0, HW = 1000, 420
    rows = ""
    for i, (n, pc, lab) in enumerate(R):
        w = abs(pc) / MX * HW; x = C0 - w if pc < 0 else C0; col = DOWN if pc < 0 else UP
        rows += (f'<div id="{P}r{i}" style="position:absolute;left:0;top:{i * 82}px;width:1720px;height:80px;opacity:0">'
                 f'<div class="mj" style="position:absolute;left:0;width:380px;text-align:right;font-size:48px;top:6px;white-space:nowrap">{n}</div><div style="position:absolute;left:0;width:380px;text-align:right;top:56px;font-size:22px;white-space:nowrap;color:{MUTE}">{lab}</div>'
                 f'<div id="{P}b{i}" style="position:absolute;left:{x:.0f}px;top:12px;height:52px;width:{w:.0f}px;background:{col};border-radius:6px"></div>'
                 f'<div class="num" style="position:absolute;left:{(x - 190) if pc < 0 else (x + w + 20):.0f}px;width:170px;text-align:{"right" if pc < 0 else "left"};top:8px;font-size:48px;color:{col}">{pc:+d}%</div></div>')
    body = (f'<div style="position:absolute;left:100px;top:120px;width:1720px"><div class="kick" style="font-size:28px;letter-spacing:.12em">{v["kick"]}</div>'
            f'<div style="position:absolute;left:{C0}px;top:70px;width:3px;height:{len(R) * 82}px;background:{GOLD}88"></div><div style="position:absolute;left:0;top:76px;width:1720px">{rows}</div></div>'
            f'<div id="{P}ft" style="position:absolute;left:0;right:0;top:900px;text-align:center;font-size:30px;color:{MUTE};opacity:0">{v["foot"]}</div>')
    tr, last = [], st(T, "bars", 1)
    for i in range(len(R)):
        last = st(T, "row", i, last + 0.4); tr.append(last)
    js = "".join(f'tl.to($("r{i}"), {{ opacity: 1, duration: 0.3 }}, {t}); tl.fromTo($("b{i}"), {{ scaleX: 0, transformOrigin: "{"100% 50%" if R[i][1] < 0 else "0% 50%"}" }}, {{ scaleX: 1, duration: 0.6 }}, {t});' for i, t in enumerate(tr))
    js += f'tl.to($("ft"), {{ opacity: 1, duration: 0.5 }}, {st(T, "foot", 1)});'
    return scene(T, body, js)

def won_disp(n):
    r = int(n / 1000 + 0.5); m, k = divmod(r, 10)
    return (f"{m}만" if m else "") + (f" {k}천" if k else "") + " 원"


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
    css = FONTS + '#root{position:absolute;inset:0;font-family:PX,sans-serif}' + TH.cap_css(TM)
    return (f'<template><style>{css}</style><div id="root" data-composition-id="captions" data-width="1920" data-height="1080">{"".join(out)}</div>'
            '<script>const tl = gsap.timeline({ paused: true }); window.__timelines["captions"] = tl;</script></template>'), k


def main():
    if os.path.exists(HF): shutil.rmtree(HF)
    os.makedirs(f"{HF}/compositions"); os.makedirs(f"{HF}/assets/fonts"); os.makedirs(f"{HF}/assets/img")
    tpl = "/home/user/kimhyeoncheol/.claude/skills/ranking-video/templates/hyperframes_movers"
    for f in ("hyperframes.json", "package.json"): shutil.copy(f"{tpl}/{f}", f"{HF}/{f}")
    json.dump(dict(id=D.get("hf_id", "longform"), name=D.get("hf_id", "longform"), createdAt="2026-11-14T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
    for f in TH.FONT_FILES: shutil.copy(f"{FONTDIR}/{f}", f"{HF}/assets/fonts/{f}")
    for i in PHOTO.values(): shutil.copy(f"{IMG}/{i}.jpg", f"{HF}/assets/img/{i}.jpg")
    F = dict(pctbars=pctbars, yieldhook=yieldhook, ybars=ybars, hookscale=hookscale, trick=trick, loss=loss, hook=hook, title=title, calc=calc, faq=calc, table=table, pick=pick, flow=flow, checklist=checklist, outro=outro)
    hosts = []
    for T in TL:
        open(f"{HF}/compositions/{T['id']}.html", "w", encoding="utf-8").write(TH.remap(TM, F[T["s"]["kind"]](T)))
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
