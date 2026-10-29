# -*- coding: utf-8 -*-
"""대본데이터.json + 음성 길이 → HyperFrames 프로젝트(hf/)와 합친 오디오(hf/assets/audio.wav) 생성
사용: python3 -I build_hf.py [--est]   (--est: 음성이 아직 없으면 글자 수로 길이를 추정)
"""
import json, os, re, subprocess, sys, shutil, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import animals as AN
EST = "--est" in sys.argv
D = json.load(open(f"{ROOT}/01_대본/대본데이터.json", encoding="utf-8"))
TTS = f"{ROOT}/02_음성"; HF = f"{HERE}/hf"
SKILL_TPL = "/home/user/kimhyeoncheol/.claude/skills/ranking-video/templates/hyperframes_movers"
GAP, LEAD = 0.28, 0.45
SR = 48000
ACC = {"활": "#2EE6C8", "선": "#8CC8FF"}
UP, DOWN, FLAT, YEL = "#FF5A4D", "#4DA3FF", "#9AA7B4", "#FFD640"
DOWNBG, FLATBG = "#2F7DE1", "#5F6F80"  # 흰 글씨를 얹는 배경용(대비 3:1 이상)
FONTS = '@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-Bold.otf");font-weight:700}@font-face{font-family:"PX";src:url("assets/fonts/Pretendard-SemiBold.otf");font-weight:500}'
ORD = ["첫째", "둘째", "셋째", "넷째"]; WK = ["1주", "2주", "3주", "4주"]; WD = ["10/1~7", "10/8~14", "10/15~21", "10/22~28"]


def wav_len(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()


# ---------------------------------------------------------------- 타임라인
secs = D["sections"]; t = 0.0; TL = []
for si, s in enumerate(secs):
    lead = 0.3 if s["kind"] == "chapter" else LEAD
    st = t; cur = lead; sents = []
    for ti, x in enumerate(s["sentences"]):
        p = f"{TTS}/{si:02d}_{ti:02d}.wav"
        if os.path.exists(p): du = wav_len(p); has = True
        elif EST: du = len(x[0].replace(" ", "")) / 7.2 + 0.2; has = False
        else: raise SystemExit(f"음성 없음: {p}")
        sents.append(dict(si=si, ti=ti, tts=x[0], sub=x[1], sig=x[2], start=cur, dur=du, wav=p if has else None)); cur += du + GAP
    tail = 0.9 if s["kind"] == "chapter" else (1.4 if s["kind"] == "outro" else 0.4)
    dur = cur + tail
    TL.append(dict(s=s, id=f"sc{si:02d}", start=st, dur=dur, sents=sents)); t += dur
TOTAL = t


def money(v): return f"{int(round(v, -2)):,}"
def jdump(o): return json.dumps(o, ensure_ascii=False)


# ---------------------------------------------------------------- 공통 조각
def base_css():
    return f"{FONTS}#root{{position:absolute;inset:0;overflow:hidden;font-family:PX,sans-serif;color:#fff}}#root *{{box-sizing:border-box}}"


def fit_size(name, maxw, top=150):
    return int(min(top, maxw / max(1, len(name)) * 0.96))


SWIM_JS = '''
function swim(sel, dur) {
  let t = 0, dir = 1; tl.set(sel, { x: -62, y: 0, scaleX: 1, svgOrigin: "200 120" }, 0);
  while (t < dur) {
    tl.to(sel, { x: dir > 0 ? 62 : -62, duration: 3.1, ease: "sine.inOut" }, t);
    tl.to(sel, { y: -12, duration: 1.55, ease: "sine.inOut", yoyo: true, repeat: 1 }, t);
    t += 3.1; dir = -dir;
    tl.to(sel, { scaleX: dir, duration: 0.4, ease: "power2.inOut" }, t); t += 0.4;
  }
}
function sidestep(sel, dur, amp) {
  amp = amp || 70; let t = 0, dir = 1; tl.set(sel, { x: -amp, svgOrigin: "200 120" }, 0);
  while (t < dur) { tl.to(sel, { x: dir > 0 ? amp : -amp, duration: 2.6, ease: "sine.inOut" }, t); t += 2.9; dir = -dir; }
}'''


def tank_svg(P, key, live, dur):
    """왼쪽 아래 패널: 활어=수조(움직임), 선어=얼음 위(정지)"""
    kind, inner = AN.markup(P, key)
    W, H = 600, 275
    bottom = kind in ("crab", "abalone", "flat")
    ay = 38 if bottom else 12
    animal = f'<svg x="120" y="{ay}" width="360" height="216" viewBox="0 0 400 240" overflow="visible"><g id="{P}animal">{inner}</g></svg>'
    if live:
        bub = "".join(f'<circle id="{P}b{i}" cx="{90 + i * 105}" cy="{H - 30}" r="{5 + i % 3 * 2}" fill="none" stroke="#bfefff" stroke-width="3" opacity="0"/>' for i in range(5))
        weeds = "".join(f'<path id="{P}w{i}" d="M {x} {H} q -14 -40 0 -78 q 14 -30 0 -58" stroke="#2fae7b" stroke-width="9" fill="none" stroke-linecap="round" opacity=".75"/>' for i, x in enumerate((40, 548)))
        pebbles = "".join(f'<ellipse cx="{x}" cy="{H - 8}" rx="{r}" ry="{r * .6:.0f}" fill="#c9b78f" opacity=".7"/>' for x, r in ((90, 22), (160, 16), (250, 20), (360, 14), (450, 24), (520, 15)))
        svg = (f'<svg id="{P}tank" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:70px;top:575px;border-radius:28px;overflow:hidden">'
               f'<defs><linearGradient id="{P}water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1a7aa8"/><stop offset="1" stop-color="#06304a"/></linearGradient></defs>'
               f'<rect width="{W}" height="{H}" fill="url(#{P}water)"/>'
               f'<g id="{P}rays"><path d="M 80 0 L 150 0 L 70 {H} L 0 {H} Z" fill="#fff" opacity=".07"/><path d="M 300 0 L 380 0 L 300 {H} L 220 {H} Z" fill="#fff" opacity=".06"/></g>'
               f'<path id="{P}wave" d="M -60 16 q 30 -12 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 t 60 0 V -10 H -60 Z" fill="#a9ecff" opacity=".28"/>'
               f'{pebbles}{weeds}{bub}{animal}</svg>')
        return svg, kind
    cubes = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#ffffff" opacity="{o}" transform="rotate({r} {x + w / 2} {y + h / 2})"/>' for x, y, w, h, r, o in
                    ((14, 150, 96, 80, -8, .5), (96, 190, 110, 70, 6, .42), (210, 170, 100, 90, -4, .5), (318, 196, 110, 66, 9, .4), (430, 156, 112, 84, -6, .5), (500, 200, 96, 66, 5, .36), (-10, 214, 90, 60, 3, .36), (170, 140, 80, 60, -10, .32)))
    svg = (f'<svg id="{P}tank" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:70px;top:575px;border-radius:28px;overflow:hidden">'
           f'<defs><linearGradient id="{P}ice" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d6e9f7"/><stop offset="1" stop-color="#8fb4d0"/></linearGradient></defs>'
           f'<rect width="{W}" height="{H}" fill="url(#{P}ice)"/>{cubes}{animal}</svg>')
    return svg, kind


def nice_ticks(vmin, vmax):
    for step in (500, 1000, 2000, 2500, 5000, 10000, 20000, 25000, 50000):
        n = int(vmax // step) - int(-(-vmin // step)) + 1
        if 2 <= n <= 4: break
    k0 = int(-(-vmin // step)); return [k * step for k in range(k0, int(vmax // step) + 1)]


# ---------------------------------------------------------------- 품종 장면
def species_scene(T):
    s, sid = T["s"], T["id"]; P = sid + "-"; state = s["state"]; acc = ACC[state]; live = state == "활"
    Pv, Kv = s["P"], s["K"]; hi, lo = s["hi"], s["lo"]
    lo_v, hi_v = min(Pv), max(Pv); span = max(hi_v - lo_v, 0.10 * hi_v); mid = (hi_v + lo_v) / 2
    vmax, vmin = mid + span * 0.62, mid - span * 0.62
    Y0, Y1 = 250, 480
    yv = lambda v: Y1 - (v - vmin) / (vmax - vmin) * (Y1 - Y0)
    X = [270, 520, 770, 1020]
    pts = [(X[k], yv(Pv[k])) for k in range(4)]
    total = s["total"]; tcol = UP if total >= 3 else (DOWNBG if total <= -3 else FLATBG); tsign = "▲" if total >= 3 else ("▼" if total <= -3 else "■")
    svg = [f'<rect width="1140" height="780" rx="32" fill="#ffffff" opacity=".07"/><rect x="1" y="1" width="1138" height="778" rx="31" fill="none" stroke="#fff" stroke-opacity=".14" stroke-width="2"/>',
           f'<text x="44" y="68" font-size="36" font-weight="500" fill="#9fb6cb">주별 킬로그램당 평균 경락가</text><text x="1096" y="68" font-size="30" font-weight="500" fill="#7f95aa" text-anchor="end">단위 원</text>']
    for tv in nice_ticks(vmin, vmax):
        y = yv(tv); svg.append(f'<line x1="150" y1="{y:.1f}" x2="1096" y2="{y:.1f}" stroke="#fff" stroke-opacity=".13" stroke-width="2" stroke-dasharray="6 10"/><text x="132" y="{y + 10:.1f}" font-size="28" font-weight="500" fill="#7f95aa" text-anchor="end">{tv:,}</text>')
    ref_y = pts[0][1]
    svg.append(f'<line id="{P}ref" x1="{X[0]}" y1="{ref_y:.1f}" x2="1096" y2="{ref_y:.1f}" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-dasharray="4 10" opacity="0"/>')
    # 영역 · 선 · 점 · 라벨
    for k in range(1, 4):
        x0, y0 = pts[k - 1]; x1, y1 = pts[k]
        svg.append(f'<path id="{P}area{k}" d="M {x0} {y0:.1f} L {x1} {y1:.1f} L {x1} {Y1 + 24} L {x0} {Y1 + 24} Z" fill="{acc}" opacity="0"/>')
    for k in range(1, 4):
        x0, y0 = pts[k - 1]; x1, y1 = pts[k]
        svg.append(f'<path id="{P}seg{k}" d="M {x0} {y0:.1f} L {x1} {y1:.1f}" stroke="{acc}" stroke-width="11" stroke-linecap="butt" fill="none" opacity="0" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
    for k in range(4):
        x, y = pts[k]
        svg.append(f'<line id="{P}drop{k}" x1="{x}" y1="{y + 18:.1f}" x2="{x}" y2="{Y1 + 24}" stroke="{acc}" stroke-opacity=".35" stroke-width="3" stroke-dasharray="3 9" opacity="0"/>')
    for k in range(1, 4):
        x0, y0 = pts[k - 1]; x1, y1 = pts[k]; ch = (Pv[k] / Pv[k - 1] - 1) * 100
        col = UP if ch >= 2 else (DOWNBG if ch <= -2 else FLATBG); sg = "▲" if ch >= 2 else ("▼" if ch <= -2 else "■"); mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 60
        svg.append(f'<g id="{P}chip{k}" opacity="0"><rect x="{mx - 70:.1f}" y="{my - 27:.1f}" width="140" height="54" rx="27" fill="{col}"/><text x="{mx:.1f}" y="{my + 12:.1f}" font-size="34" font-weight="700" text-anchor="middle" fill="#fff">{sg}{abs(int(round(ch)))}%</text></g>')
    for k in range(4):
        x, y = pts[k]
        svg.append(f'<circle id="{P}ring{k}" cx="{x}" cy="{y:.1f}" r="16" fill="none" stroke="{acc}" stroke-width="5" opacity="0"/>')
        svg.append(f'<circle id="{P}dot{k}" cx="{x}" cy="{y:.1f}" r="17" fill="#ffffff" stroke="{acc}" stroke-width="8" opacity="0"/>')
        svg.append(f'<text id="{P}val{k}" x="{x}" y="{y - 36:.1f}" font-size="56" font-weight="700" text-anchor="middle" fill="#fff" opacity="0" style="paint-order:stroke;stroke:#0b2237;stroke-width:12px;stroke-linejoin:round">{money(Pv[k])}</text>')
        thin = Kv[k] < 300
        vol = ("거래 적음" if thin else ("거래 " + (f"{round(Kv[k] / 1000)}톤" if Kv[k] >= 10000 else f"{int(round(Kv[k], -2 if Kv[k] >= 1000 else -1)):,}kg")))
        svg.append(f'<text id="{P}wk{k}" x="{x}" y="622" font-size="48" font-weight="700" text-anchor="middle" fill="#6f8aa3">{WK[k]}</text>')
        svg.append(f'<text x="{x}" y="664" font-size="30" font-weight="500" text-anchor="middle" fill="#7f95aa">{WD[k]}</text>')
        svg.append(f'<text id="{P}vol{k}" x="{x}" y="706" font-size="30" font-weight="700" text-anchor="middle" fill="{"#FFA94D" if thin else "#7f95aa"}" opacity="0">{vol}</text>')
    # 최고·최저 표식 / 한 달 변화 괄호
    hx, hy = pts[hi]; lx, ly = pts[lo]
    svg.append(f'<g id="{P}tagHi" opacity="0"><rect x="{hx - 52}" y="{hy - 132:.1f}" width="104" height="46" rx="23" fill="{UP}"/><text x="{hx}" y="{hy - 98:.1f}" font-size="30" font-weight="700" text-anchor="middle" fill="#fff">최고</text></g>')
    svg.append(f'<g id="{P}tagLo" opacity="0"><rect x="{lx - 52}" y="{ly + 36:.1f}" width="104" height="46" rx="23" fill="{DOWNBG}"/><text x="{lx}" y="{ly + 70:.1f}" font-size="30" font-weight="700" text-anchor="middle" fill="#fff">최저</text></g>')
    ex, ey = 1082, pts[3][1]
    svg.append(f'<g id="{P}brk" opacity="0"><line x1="{ex}" y1="{ref_y:.1f}" x2="{ex}" y2="{ey:.1f}" stroke="{tcol}" stroke-width="8" stroke-linecap="round"/>'
               f'<path d="M {ex - 14} {ey + (18 if ey < ref_y else -18):.1f} L {ex} {ey:.1f} L {ex + 14} {ey + (18 if ey < ref_y else -18):.1f}" stroke="{tcol}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')
    svg.append('<text x="44" y="752" font-size="28" font-weight="500" fill="#7f95aa">자료 노량진수산 경락시세 · 도매 경매가 · 상하위 5% 제외 · 가중평균</text>')
    chart = f'<svg id="{P}chart" width="1140" height="780" viewBox="0 0 1140 780" style="position:absolute;left:710px;top:70px">{"".join(svg)}</svg>'
    tank, kind = tank_svg(P, s["id"].split("-")[0] if False else s["key"], live, T["dur"])
    nm = s["short"]; fs = fit_size(nm, 590, 150); alias = s.get("alias", "")
    left = (f'<div id="{P}left" style="position:absolute;left:70px;top:0;width:600px;height:575px">'
            f'<div style="position:absolute;left:0;top:58px;height:46px;padding:0 24px;border-radius:23px;background:{acc};color:#062033;font-size:30px;font-weight:700;line-height:46px">{"활어" if live else "선어"}</div>'
            f'<div id="{P}name" style="position:absolute;left:-2px;top:104px;font-size:{fs}px;line-height:1.1;font-weight:700;white-space:nowrap">{nm}</div>'
            + (f'<div style="position:absolute;left:{min(560, int(fs * len(nm) * 0.98) + 24)}px;top:{104 + int(fs * 0.62)}px;height:44px;padding:0 18px;border-radius:22px;border:2px solid #fff6;color:#cfe0ee;font-size:30px;font-weight:500;line-height:40px;white-space:nowrap">{alias}</div>' if alias else "")
            + f'<div id="{P}plab" style="position:absolute;left:0;top:{104 + int(fs * 1.1) + 12}px;font-size:34px;font-weight:500;color:#9fb6cb">첫째 주 · kg당 평균</div>'
            f'<div style="position:absolute;left:-2px;top:{104 + int(fs * 1.1) + 52}px;white-space:nowrap"><span id="{P}big" style="font-size:112px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums">{money(Pv[0])}</span><span style="font-size:52px;font-weight:700;color:#cfe0ee;margin-left:8px">원</span></div>'
            f'<div id="{P}badge" style="position:absolute;left:0;top:{104 + int(fs * 1.1) + 172}px;height:76px;padding:0 30px;border-radius:38px;background:{tcol};font-size:46px;font-weight:700;line-height:76px;white-space:nowrap;opacity:0">'
            f'한 달 <span id="{P}bt">{tsign}0%</span></div></div>')
    css = (base_css() + f'#{P}bg{{position:absolute;inset:0;background:{"radial-gradient(1200px 800px at 20% 0%,#0f5278 0%,#082c46 55%,#061b2e 100%)" if live else "radial-gradient(1200px 800px at 20% 0%,#294864 0%,#162b40 55%,#0e1c2b 100%)"}}}')
    S = [dict(start=round(x["start"], 3), end=round(x["start"] + x["dur"], 3), sig=x["sig"]) for x in T["sents"]]
    data = dict(S=S, dur=round(T["dur"], 3), P=[round(v) for v in Pv], total=round(total), acc=acc, tcol=tcol, tsign=tsign, hi=hi, lo=lo, live=live, ORD=ORD)
    js = '''
const D = __DATA__; const P = "__P__"; const tl = gsap.timeline({ paused: true });
__SWIM__
const $ = (id) => "#" + P + id;
tl.fromTo($("left"), { x: -90, opacity: 0 }, { x: 0, opacity: 1, duration: 0.55, ease: "power3.out" }, 0);
tl.fromTo($("tank"), { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, 0.1);
tl.fromTo($("chart"), { x: 90, opacity: 0 }, { x: 0, opacity: 1, duration: 0.6, ease: "power3.out" }, 0.05);
tl.fromTo($("ref"), { opacity: 0 }, { opacity: 0, duration: 0.01 }, 0);
__MOTION__
const big = { v: D.P[0] };
function setBig() { document.getElementById(P + "big").textContent = (Math.round(big.v / 100) * 100).toLocaleString("en-US"); }
function revealPoint(k, t) {
  tl.fromTo($("dot" + k), { opacity: 0, scale: 0, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2.4)" }, t);
  tl.fromTo($("ring" + k), { opacity: 0.9, scale: 1, transformOrigin: "50% 50%", immediateRender: false }, { opacity: 0, scale: 3.4, duration: 0.8, ease: "power2.out" }, t);
  tl.fromTo($("val" + k), { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.4, ease: "back.out(2)" }, t + 0.12);
  tl.fromTo($("drop" + k), { opacity: 0 }, { opacity: 1, duration: 0.4 }, t + 0.1);
  tl.fromTo($("vol" + k), { opacity: 0 }, { opacity: 1, duration: 0.5 }, t + 0.3);
  tl.to($("wk" + k), { fill: D.acc, duration: 0.3 }, t);
  if (k > 0) {
    tl.set($("seg" + k), { opacity: 1 }, t - 0.5);
    tl.to($("seg" + k), { strokeDashoffset: 0, duration: 0.7, ease: "power2.inOut" }, t - 0.5);
    tl.fromTo($("area" + k), { opacity: 0 }, { opacity: 0.13, duration: 0.8 }, t - 0.2);
    tl.fromTo($("chip" + k), { opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2.2)" }, t + 0.2);
  }
  const o = { v: k ? D.P[k - 1] : D.P[0] };
  tl.to(big, { v: D.P[k], duration: k ? 0.8 : 0.01, ease: "power2.out", onUpdate: setBig }, t - 0.2);
  tl.set(document.getElementById(P + "plab"), { textContent: D.ORD[k] + " 주 · kg당 평균" }, t);
  tl.fromTo($("big"), { scale: 1.12, transformOrigin: "0% 60%" }, { scale: 1, duration: 0.5, ease: "power3.out" }, t);
}
D.S.forEach((s) => {
  const g = s.sig, t0 = Math.max(0.2, s.start - 0.05);
  if (g.point !== undefined) revealPoint(g.point, t0);
  if (g.final) {
    tl.fromTo($("ref"), { opacity: 0 }, { opacity: 1, duration: 0.5 }, t0 + 0.3);
    tl.fromTo($("brk"), { opacity: 0 }, { opacity: 1, duration: 0.5 }, t0 + 0.5);
    const tt = { v: 0 };
    tl.fromTo($("badge"), { opacity: 0, scale: 0.6, transformOrigin: "0% 50%" }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(2)" }, t0 + 0.5);
    tl.to(tt, { v: Math.abs(D.total), duration: 1.1, ease: "power2.out", onUpdate: () => { document.getElementById(P + "bt").textContent = D.tsign + Math.round(tt.v) + "%"; } }, t0 + 0.6);
    tl.fromTo($("ring3"), { opacity: 0.9, scale: 1, transformOrigin: "50% 50%", immediateRender: false }, { opacity: 0, scale: 4, duration: 0.9, ease: "power2.out" }, t0 + 0.9);
  }
  if (g.hilo) {
    for (const [id, k] of [["tagHi", D.hi], ["tagLo", D.lo]]) {
      tl.fromTo($(id), { opacity: 0, y: id === "tagHi" ? 12 : -12 }, { opacity: 1, y: 0, duration: 0.45, ease: "back.out(2)" }, t0 + (id === "tagHi" ? 0.2 : 0.9));
      tl.fromTo($("ring" + k), { opacity: 0.95, scale: 1, transformOrigin: "50% 50%", immediateRender: false }, { opacity: 0, scale: 3.6, duration: 0.9, ease: "power2.out" }, t0 + (id === "tagHi" ? 0.2 : 0.9));
    }
  }
  if (g.volume) for (let k = 0; k < 4; k++) {
    tl.to($("vol" + k), { fill: "#FFD640", scale: 1.18, transformOrigin: "50% 50%", duration: 0.25 }, t0 + 0.3 + k * 0.35);
    tl.to($("vol" + k), { scale: 1, duration: 0.3 }, t0 + 0.6 + k * 0.35);
  }
  if (g.thin) for (const k of g.thin) tl.fromTo($("vol" + k), { scale: 1 }, { scale: 1.2, transformOrigin: "50% 50%", duration: 0.3, yoyo: true, repeat: 1 }, t0 + 0.3);
});
tl.to($("rays"), { x: 90, duration: D.dur, ease: "none" }, 0);
tl.to($("wave"), { x: 60, duration: 2.2, ease: "none", repeat: Math.ceil(D.dur / 2.2) }, 0);
for (let i = 0; i < 5; i++) {
  const per = 2.6 + i * 0.35, n = Math.ceil(D.dur / per);
  tl.fromTo($("b" + i), { y: 0, opacity: 0.85 }, { y: -230, opacity: 0, duration: per, ease: "none", repeat: n }, i * 0.4);
}
for (let i = 0; i < 2; i++) tl.to($("w" + i), { rotation: 5 - i * 10, svgOrigin: (i ? "548 275" : "40 275"), duration: 1.6, ease: "sine.inOut", yoyo: true, repeat: Math.ceil(D.dur / 1.6) }, 0);
window.__timelines["__ID__"] = tl;
'''
    js = (js.replace("__DATA__", jdump(data)).replace("__P__", P).replace("__ID__", sid).replace("__SWIM__", SWIM_JS if live else "")
          .replace("__MOTION__", AN.motion_js(P, kind, T["dur"]) if live else ""))
    if not live:  # 선어: 수조 전용 요소가 없으므로 해당 트윈 제거(정지 상태 유지)
        js = js.replace('tl.to($("rays"), { x: 90, duration: D.dur, ease: "none" }, 0);\n', "")
        js = re.sub(r'tl\.to\(\$\("wave"\).*?\n', "", js); js = re.sub(r'for \(let i = 0; i < 5; i\+\+\) \{.*?\n\}\n', "", js, flags=re.S)
        js = re.sub(r'for \(let i = 0; i < 2; i\+\+\) tl\.to\(\$\("w".*?\n', "", js)
    html = f'<template><style>{css}</style><div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080"><div id="{P}bg"></div>{left}{tank}{chart}</div><script>{js}</script></template>'
    return html


# ---------------------------------------------------------------- 장면: 챕터
def chapter_scene(T):
    s, sid = T["s"], T["id"]; P = sid + "-"; state = s["state"]; acc = ACC[state]
    keys = [x["key"] for x in secs if x["kind"] == "species" and x["state"] == state]
    cols = 6 if state == "활" else 3; cw, ch = 300, 175
    icons = []
    for i, k in enumerate(keys):
        kind, inner = AN.markup(f"{P}i{i}-", k); cx = 960 - cols * cw / 2 + (i % cols) * cw; cy = 560 + (i // cols) * ch
        icons.append(f'<svg id="{P}ic{i}" x="{cx}" y="{cy}" width="{cw}" height="{ch}" viewBox="0 0 400 240" style="position:absolute;left:{cx}px;top:{cy}px;opacity:0;overflow:visible"><g>{inner}</g></svg>')
    css = base_css() + f'#{P}bg{{position:absolute;inset:0;background:{"radial-gradient(1400px 900px at 50% 20%,#0f5a84 0%,#082c46 60%,#061b2e 100%)" if state == "활" else "radial-gradient(1400px 900px at 50% 20%,#34536f 0%,#172c41 60%,#0e1c2b 100%)"}}}'
    txt = (f'<div id="{P}t1" style="position:absolute;left:0;right:0;top:120px;text-align:center;font-size:300px;font-weight:700;line-height:1;color:{acc};-webkit-text-stroke:4px {acc}">{"활어" if state == "활" else "선어"}</div>'
           f'<div id="{P}t2" style="position:absolute;left:0;right:0;top:450px;text-align:center;font-size:64px;font-weight:700;color:#fff">{12 if state == "활" else 6}종 한 달 시세 흐름</div>')
    n = len(keys)
    js = f'''
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#{P}t1", {{ opacity: 0, scale: 1.35, transformOrigin: "50% 50%" }}, {{ opacity: 1, scale: 1, duration: 0.55, ease: "power4.out" }}, 0.05);
tl.fromTo("#{P}t2", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.35);
for (let i = 0; i < {n}; i++) {{
  tl.fromTo("#{P}ic" + i, {{ opacity: 0, y: 40, scale: 0.7, transformOrigin: "50% 50%" }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(2)" }}, 0.55 + i * 0.28);
}}
window.__timelines["{sid}"] = tl;'''
    return f'<template><style>{css}</style><div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080"><div id="{P}bg"></div>{txt}{"".join(icons)}</div><script>{js}</script></template>'


# ---------------------------------------------------------------- 장면: 인트로
def intro_scene(T):
    s, sid = T["s"], T["id"]; P = sid + "-"; S = T["sents"]; allc = D["allc"]
    nm = {x["key"]: x.get("short") for x in secs if x["kind"] == "species"}
    # 4주 변화율 스파게티(1주=100)
    W = {x["key"]: x["P"] for x in secs if x["kind"] == "species"}
    keys = list(W); idx = {k: [v / W[k][0] * 100 for v in W[k]] for k in keys}
    CX0, CX1, CY0, CY1 = 260, 1560, 300, 800; vmin, vmax = 58, 150
    xy = lambda i, v: (CX0 + (CX1 - CX0) * i / 3, CY1 - (v - vmin) / (vmax - vmin) * (CY1 - CY0))
    dn, up = S[0]["sig"]["key"], S[1]["sig"]["key"]
    sp = []
    for k in keys:
        pts = " ".join(f"{xy(i, v)[0]:.1f},{xy(i, v)[1]:.1f}" for i, v in enumerate(idx[k]))
        col = DOWN if k == dn else (UP if k == up else ACC[k[0]]); wd = 9 if k in (dn, up) else 4; op = 1 if k in (dn, up) else .45
        sp.append(f'<polyline id="{P}ln-{k}" points="{pts}" fill="none" stroke="{col}" stroke-width="{wd}" stroke-linecap="butt" stroke-linejoin="round" opacity="0" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" data-op="{op}"/>')
    for i in range(4):
        x, _ = xy(i, 100); sp.append(f'<text x="{x}" y="{CY1 + 64}" font-size="44" font-weight="700" text-anchor="middle" fill="#cfe0ee">{WK[i]}</text><line x1="{x}" y1="{CY0 - 20}" x2="{x}" y2="{CY1 + 10}" stroke="#fff" stroke-opacity=".12" stroke-width="2"/>')
    y100 = xy(0, 100)[1]
    sp.append(f'<line x1="{CX0}" y1="{y100}" x2="{CX1}" y2="{y100}" stroke="#fff" stroke-opacity=".4" stroke-width="3" stroke-dasharray="4 10"/><text x="{CX0 - 20}" y="{y100 + 10}" font-size="30" font-weight="500" fill="#9fb6cb" text-anchor="end">1주=100</text>')
    for k, col in ((dn, DOWN), (up, UP)):
        x, y = xy(3, idx[k][3]); sp.append(f'<text id="{P}lb-{k}" x="{x + 22}" y="{y + 12}" font-size="40" font-weight="700" fill="{col}" opacity="0">{nm[k]} {int(round(allc[k])):+d}%</text>')
    spag = f'<svg id="{P}spag" width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;opacity:0">{"".join(sp)}</svg>'
    C = lambda i, big, small: f'<div class="ph" id="{P}p{i}">{big}{small}</div>'
    pc = lambda k: DOWN if allc[k] < 0 else UP
    ph0 = (f'<div class="ph" id="{P}p0" style="justify-content:flex-start;padding-top:70px"><div id="{P}h0a" style="font-size:250px;font-weight:700;line-height:1.05">{nm[dn]}</div>'
           f'<div id="{P}h0b" style="font-size:300px;font-weight:700;line-height:1.05;color:{DOWN};-webkit-text-stroke:4px {DOWN}">▼{abs(int(round(allc[dn])))}%</div>'
           f'<div style="font-size:40px;font-weight:500;color:#9fb6cb;margin-top:6px">한 달 사이 · 1주 → 4주 킬로그램당 평균 경락가</div></div>')
    ph1 = (f'<div class="ph" id="{P}p1" style="justify-content:flex-start;padding-top:70px"><div id="{P}h1a" style="font-size:230px;font-weight:700;line-height:1.05">{nm[up]}</div>'
           f'<div id="{P}h1b" style="font-size:300px;font-weight:700;line-height:1.05;color:{UP};-webkit-text-stroke:4px {UP}">▲{abs(int(round(allc[up])))}%</div>'
           f'<div style="font-size:40px;font-weight:500;color:#9fb6cb;margin-top:6px">한 달 사이 · 1주 → 4주 킬로그램당 평균 경락가</div></div>')
    ph2 = f'<div id="{P}p2" style="position:absolute;left:0;right:0;top:70px;text-align:center;opacity:0"><div style="font-size:92px;font-weight:700">10월 노량진 주간 시세 흐름</div><div style="font-size:40px;font-weight:500;color:#9fb6cb;margin-top:6px">18개 품종 · 1주 가격을 100으로 맞춘 한 달 변화</div></div>'
    ph3 = (f'<div class="ph" id="{P}p3" style="flex-direction:row;gap:70px;justify-content:center;align-items:center">'
           f'<div id="{P}c3a" style="width:640px;height:520px;border-radius:44px;background:{ACC["활"]};color:#062033;text-align:center;padding-top:60px"><div style="font-size:90px;font-weight:700">활어</div><div style="font-size:250px;font-weight:700;line-height:1.05">12<span style="font-size:90px">종</span></div></div>'
           f'<div id="{P}c3b" style="width:640px;height:520px;border-radius:44px;background:{ACC["선"]};color:#062033;text-align:center;padding-top:60px"><div style="font-size:90px;font-weight:700">선어</div><div style="font-size:250px;font-weight:700;line-height:1.05">6<span style="font-size:90px">종</span></div></div></div>')
    items = ["가장 많이 내린 품종 · 오른 품종", "품종마다 싼 주 · 비싼 주", "활어 12종 + 선어 6종 한 달 흐름"]
    ph4 = (f'<div class="ph" id="{P}p4"><div style="width:1300px;border-radius:44px;background:#ffffff14;border:2px solid #ffffff30;padding:50px 70px"><div style="font-size:64px;font-weight:700;color:{YEL};margin-bottom:34px">이 영상을 끝까지 보면</div>'
           + "".join(f'<div id="{P}ck{i}" style="font-size:76px;font-weight:700;line-height:1.5;opacity:0;white-space:nowrap"><span style="color:{ACC["활"]}">✔</span> {t}</div>' for i, t in enumerate(items)) + '</div></div>')
    ph5 = (f'<div class="ph" id="{P}p5"><div id="{P}m5a" style="font-size:96px;font-weight:700">노량진수산 경락시세</div><div id="{P}m5b" style="margin-top:36px;font-size:150px;font-weight:700;color:{YEL}">도매 경매가</div>'
           f'<div id="{P}m5c" style="margin-top:20px;font-size:64px;font-weight:700;color:#cfe0ee">가게 판매가와는 달라요</div></div>')
    chips = ["킬로그램당 가중평균", "상·하위 5% 거래 제외", "변동률 = 1주 → 4주"]
    ph6 = (f'<div class="ph" id="{P}p6" style="gap:26px">' + "".join(f'<div id="{P}m6{i}" style="min-width:1000px;text-align:center;padding:30px 60px;border-radius:30px;background:#ffffff18;border:2px solid #ffffff30;font-size:84px;font-weight:700;opacity:0">{t}</div>' for i, t in enumerate(chips)) + '</div>')
    ph7 = f'<div class="ph" id="{P}p7"><div id="{P}g7" style="font-size:260px;font-weight:700;color:{ACC["활"]};-webkit-text-stroke:4px {ACC["활"]}">활어부터 ▶</div></div>'
    css = base_css() + f'#{P}bg{{position:absolute;inset:0;background:radial-gradient(1500px 900px at 50% 0%,#0f4f78 0%,#082a44 55%,#05192b 100%)}}.ph{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;opacity:0}}'
    st = [x["start"] for x in S]; en = [x["start"] + x["dur"] + GAP for x in S]
    d = dict(st=[round(v, 3) for v in st], en=[round(v, 3) for v in en], dur=round(T["dur"], 3), keys=keys, dn=dn, up=up)
    js = '''
const D = __D__; const P = "__P__"; const tl = gsap.timeline({ paused: true }); const $ = (i) => "#" + P + i;
const show = (id, a, b) => { tl.set($(id), { opacity: 1 }, a); tl.set($(id), { opacity: 0 }, b); };
// 0: 농어 내림  1: 오름
show("p0", 0, D.en[0] + 0.05);
tl.fromTo($("h0a"), { y: -30 }, { y: 0, duration: 0.35, ease: "power3.out" }, 0);
tl.fromTo($("h0b"), { scale: 1.5, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.45, ease: "power4.out" }, 0);
show("p1", D.st[1] - 0.2, D.en[1] + 0.05);
tl.fromTo($("h1a"), { opacity: 0, y: -40 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }, D.st[1] - 0.15);
tl.fromTo($("h1b"), { opacity: 0, scale: 2.2, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.45, ease: "power4.out" }, D.st[1] + 0.15);
// 2: 스파게티 차트
tl.set($("p2"), { opacity: 1 }, D.st[2] - 0.2); tl.set($("p2"), { opacity: 0 }, D.en[2] + 0.05);
tl.fromTo($("p2"), { y: -30 }, { y: 0, duration: 0.5, ease: "power3.out" }, D.st[2] - 0.2);
tl.set($("spag"), { opacity: 1 }, D.st[2] - 0.2); tl.set($("spag"), { opacity: 0 }, D.en[2] + 0.05);
D.keys.forEach((k, i) => { const op = +document.querySelector($("ln-" + k)).getAttribute("data-op"); tl.set($("ln-" + k), { opacity: op }, D.st[2] + 0.1 + i * 0.03); tl.to($("ln-" + k), { strokeDashoffset: 0, duration: 1.6, ease: "power2.inOut" }, D.st[2] + 0.1 + i * 0.03); });
for (const k of [D.dn, D.up]) tl.fromTo($("lb-" + k), { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: 0.5, ease: "power3.out" }, D.st[2] + 1.9);
// 3: 종 수
show("p3", D.st[3] - 0.1, D.en[3] + 0.05);
tl.fromTo($("c3a"), { scale: 0.6, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2)" }, D.st[3] - 0.05);
tl.fromTo($("c3b"), { scale: 0.6, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2)" }, D.st[3] + 0.7);
// 4: 체크리스트
show("p4", D.st[4] - 0.1, D.en[4] + 0.05);
const span4 = D.en[4] - D.st[4];
[0, 1, 2].forEach((i) => tl.fromTo($("ck" + i), { opacity: 0, x: -50 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }, D.st[4] + 0.5 + i * (span4 - 1.2) / 3));
// 5: 출처 / 도매가
show("p5", D.st[5] - 0.1, D.en[5] + 0.05);
tl.fromTo($("m5a"), { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, D.st[5] - 0.05);
tl.fromTo($("m5b"), { opacity: 0, scale: 1.5, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.45, ease: "power4.out" }, D.st[5] + 0.9);
tl.fromTo($("m5c"), { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.45 }, D.st[5] + 1.9);
// 6: 계산 방법
show("p6", D.st[6] - 0.1, D.en[6] + 0.05);
const sp6 = D.en[6] - D.st[6];
[0, 1, 2].forEach((i) => tl.fromTo($("m6" + i), { opacity: 0, x: 80 }, { opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }, D.st[6] + 0.2 + i * (sp6 - 1.0) / 3));
// 7: 활어부터
show("p7", D.st[7] - 0.1, D.dur);
tl.fromTo($("g7"), { opacity: 0, x: -200 }, { opacity: 1, x: 0, duration: 0.5, ease: "power4.out" }, D.st[7] - 0.05);
tl.to($("g7"), { x: 40, duration: 0.8, ease: "sine.inOut", yoyo: true, repeat: 1 }, D.st[7] + 0.6);
window.__timelines["__ID__"] = tl;
'''.replace("__D__", jdump(d)).replace("__P__", P).replace("__ID__", sid)
    return f'<template><style>{css}</style><div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080"><div id="{P}bg"></div>{spag}{ph0}{ph1}{ph2}{ph3}{ph4}{ph5}{ph6}{ph7}</div><script>{js}</script></template>'


# ---------------------------------------------------------------- 장면: 아웃트로
def outro_scene(T):
    s, sid = T["s"], T["id"]; P = sid + "-"; S = T["sents"]; allc = D["allc"]
    info = {x["key"]: x for x in secs if x["kind"] == "species"}
    order = sorted(allc, key=allc.get); R0, RH = 118, 40; AX = 1130; sc = 9.6
    rows = []; ids = []
    for i, k in enumerate(order):
        v = allc[k]; y = R0 + i * RH; w = abs(v) * sc; col = UP if v >= 3 else (DOWN if v <= -3 else FLAT)
        x = AX if v >= 0 else AX - w; lx = (AX + w + 14) if v >= 0 else (AX - w - 14); anc = "start" if v >= 0 else "end"
        stc = ACC[k[0]]
        rows.append(f'<g id="{P}r{i}" opacity="0"><circle cx="118" cy="{y + 20}" r="9" fill="{stc}"/><text x="140" y="{y + 31}" font-size="32" font-weight="700" fill="#fff">{info[k]["name"]}</text>'
                    f'<rect id="{P}bar{i}" x="{x:.1f}" y="{y + 4}" width="{max(w, 4):.1f}" height="32" rx="6" fill="{col}"/><text x="{lx:.1f}" y="{y + 31}" font-size="30" font-weight="700" text-anchor="{anc}" fill="{col}">{"▲" if v >= 3 else ("▼" if v <= -3 else "■")}{abs(int(round(v)))}%</text></g>')
    ids = {k: i for i, k in enumerate(order)}
    svg = (f'<svg id="{P}bars" width="1920" height="900" viewBox="0 0 1920 900" style="position:absolute;left:0;top:0">'
           f'<text x="118" y="64" font-size="52" font-weight="700" fill="#fff">한 달 변화율</text><text x="520" y="64" font-size="34" font-weight="500" fill="#9fb6cb">1주 → 4주 · 킬로그램당 평균 경락가</text>'
           f'<line x1="{AX}" y1="{R0 - 8}" x2="{AX}" y2="{R0 + 18 * RH + 4}" stroke="#fff" stroke-opacity=".45" stroke-width="3"/>{"".join(rows)}</svg>')
    n_dn = sum(1 for v in allc.values() if v <= -3); n_up = sum(1 for v in allc.values() if v >= 3); n_fl = 18 - n_dn - n_up
    cards = (f'<div id="{P}cnt" style="position:absolute;right:90px;top:170px;width:420px;opacity:0">'
             f'<div style="border-radius:34px;background:{DOWNBG};padding:26px 36px;margin-bottom:22px"><div style="font-size:40px;font-weight:500">값이 내린 품종</div><div style="font-size:120px;font-weight:700;line-height:1.1">{n_dn}<span style="font-size:48px">종</span></div></div>'
             f'<div style="border-radius:34px;background:{UP};padding:26px 36px;margin-bottom:22px"><div style="font-size:40px;font-weight:500">값이 오른 품종</div><div style="font-size:120px;font-weight:700;line-height:1.1">{n_up}<span style="font-size:48px">종</span></div></div>'
             f'<div style="border-radius:34px;background:{FLATBG};padding:22px 36px"><div style="font-size:36px;font-weight:500">비슷한 품종 (±3% 안)</div><div style="font-size:84px;font-weight:700;line-height:1.1">{n_fl}<span style="font-size:40px">종</span></div></div></div>')
    disc = (f'<div id="{P}disc" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;background:#06192bdd"><div style="font-size:84px;font-weight:700;color:{YEL}">도매 경락가 ≠ 가게 판매가</div>'
            f'<div style="margin-top:28px;font-size:60px;font-weight:700;color:#cfe0ee">가게 가격은 다를 수 있어요</div></div>')
    end = (f'<div id="{P}end" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;background:radial-gradient(1200px 800px at 50% 40%,#0f4f78 0%,#06192b 100%)">'
           f'<div style="font-size:150px;font-weight:700">구독 · 좋아요</div><div style="margin-top:20px;font-size:62px;font-weight:700;color:{ACC["활"]}">다음 시세도 이어서 정리해 드려요</div></div>')
    top4 = [order[0], order[1], order[-2], order[-1]]
    css = base_css() + f'#{P}bg{{position:absolute;inset:0;background:radial-gradient(1500px 900px at 30% 0%,#0f4f78 0%,#082a44 55%,#05192b 100%)}}'
    st = [x["start"] for x in S]; en = [x["start"] + x["dur"] + GAP for x in S]
    d = dict(st=[round(v, 3) for v in st], en=[round(v, 3) for v in en], dur=round(T["dur"], 3), top=[ids[k] for k in top4], n=18)
    js = '''
const D = __D__; const P = "__P__"; const tl = gsap.timeline({ paused: true }); const $ = (i) => "#" + P + i;
tl.fromTo($("bars"), { opacity: 0 }, { opacity: 1, duration: 0.4 }, D.st[0] - 0.2);
for (let i = 0; i < D.n; i++) {
  const t = D.st[0] + 0.1 + i * 0.16;
  tl.fromTo($("r" + i), { opacity: 0 }, { opacity: 1, duration: 0.2 }, t);
  tl.fromTo($("bar" + i), { scaleX: 0, transformOrigin: i < 9 ? "right center" : "left center" }, { scaleX: 1, duration: 0.5, ease: "power3.out" }, t);
}
// 1: 가장 많이 내린·오른 4개 강조
for (let i = 0; i < D.n; i++) if (!D.top.includes(i)) tl.to($("r" + i), { opacity: 0.28, duration: 0.5 }, D.st[1] - 0.05);
D.top.forEach((i, j) => tl.fromTo($("r" + i), { scale: 1, transformOrigin: "50% 50%" }, { scale: 1.04, duration: 0.3, yoyo: true, repeat: 1 }, D.st[1] + 0.3 + j * 1.1));
// 2: 내림 / 오름 개수
for (let i = 0; i < D.n; i++) tl.to($("r" + i), { opacity: 1, duration: 0.5 }, D.st[2] - 0.05);
tl.fromTo($("cnt"), { opacity: 0, x: 120 }, { opacity: 1, x: 0, duration: 0.55, ease: "power3.out" }, D.st[2] + 0.2);
// 3: 면책
tl.set($("bars"), { opacity: 0 }, D.st[3] - 0.1); tl.set($("cnt"), { opacity: 0 }, D.st[3] - 0.1);
tl.fromTo($("disc"), { opacity: 0 }, { opacity: 1, duration: 0.35 }, D.st[3] - 0.1);
// 4: 구독
tl.set($("disc"), { opacity: 0 }, D.st[4] - 0.1);
tl.fromTo($("end"), { opacity: 0 }, { opacity: 1, duration: 0.45 }, D.st[4] - 0.1);
window.__timelines["__ID__"] = tl;
'''.replace("__D__", jdump(d)).replace("__P__", P).replace("__ID__", sid)
    return f'<template><style>{css}</style><div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080"><div id="{P}bg"></div>{svg}{cards}{disc}{end}</div><script>{js}</script></template>'


# ---------------------------------------------------------------- 자막
def one_line(x, n=18):
    out, cur = [], ""
    for w in x.split():
        if cur and len(cur) + 1 + len(w) > n: out.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    if cur: out.append(cur)
    return out


def strip_punct(x): return re.sub(r"\s{2,}", " ", re.sub(r"(?<!\d)[,.]|[,.](?!\d)", "", x)).strip()


def voice_split(wavp, lens, dur):
    n = len(lens); tot = float(sum(lens))
    if n == 1: return [dur]
    prop = [dur * l / tot for l in lens]
    if not wavp: return prop
    try:
        with wave.open(wavp) as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        if a.ndim > 1: a = a.mean(1)
        hop = int(sr * 0.02); m = len(a) // hop
        if m < 10: return prop
        e = np.sqrt((a[:m * hop].reshape(m, hop) ** 2).mean(1)); act = e > max(0.02, e.max() * 0.08); cum = np.cumsum(act); tt = cum[-1]
        if tt < 5: return prop
        cuts = []; acc = 0
        for l in lens[:-1]:
            acc += l; target = tt * acc / tot; i = int(np.searchsorted(cum, target)); cuts.append(min(m - 1, i))
        # 경계는 다음 말소리가 시작되기 직전의 쉼 가운데로
        times = [];
        for c in cuts:
            j = c
            while j < m - 1 and not act[j + 1]: j += 1
            times.append((c + j) / 2 * hop / sr)
        times = [min(max(x, 0.15), len(a) / sr - 0.1) for x in times]
        pts = [0.0] + times + [len(a) / sr]; scale = dur / (len(a) / sr)
        return [max(0.25, (pts[i + 1] - pts[i]) * scale) for i in range(n)]
    except Exception:
        return prop


def captions():
    items = []; gi = 0
    for T in TL:
        for x in T["sents"]:
            sub = strip_punct(x["sub"]); lines = one_line(sub)
            durs = voice_split(x["wav"], [len(l) for l in lines], x["dur"]); t0 = T["start"] + x["start"]
            for l, du in zip(lines, durs):
                html = re.sub(r"(\d[\d,~·.]*(?:월|위|년|배|지|개|분|kg|%|원|톤|종|킬로그램|주)?)", r'<b>\1</b>', l)
                items.append((t0, du, html)); t0 += du
    out = []
    for i, (st, du, h) in enumerate(items):
        out.append(f'<div class="clip cap" id="cap{i}" data-start="{st:.3f}" data-duration="{du:.3f}" data-track-index="1"><span>{h}</span></div>')
    css = (FONTS + '#root{position:absolute;inset:0;font-family:PX,sans-serif}.cap{position:absolute;left:0;right:0;bottom:56px;text-align:center;overflow:visible}'
           '.cap span{display:inline-block;background:rgba(0,0,0,.56);color:#fff;font-size:87px;font-weight:700;line-height:1.2;padding:6px 26px;white-space:nowrap}.cap b{color:#FFD640;font-weight:700}')
    return (f'<template><style>{css}</style><div id="root" data-composition-id="captions" data-width="1920" data-height="1080">{"".join(out)}</div>'
            '<script>const tl = gsap.timeline({ paused: true }); window.__timelines["captions"] = tl;</script></template>'), items


# ---------------------------------------------------------------- 쓰기
def main():
    if os.path.exists(HF): shutil.rmtree(HF)
    os.makedirs(f"{HF}/compositions"); os.makedirs(f"{HF}/assets/fonts")
    for f in ("hyperframes.json", "package.json"): shutil.copy(f"{SKILL_TPL}/{f}", f"{HF}/{f}")
    json.dump(dict(id="noryangjin_oct", name="noryangjin_oct", createdAt="2026-10-29T00:00:00.000Z"), open(f"{HF}/meta.json", "w"))
    for f in ("Pretendard-Bold.otf", "Pretendard-SemiBold.otf"): shutil.copy(f"{SKILL_TPL}/assets/fonts/{f}", f"{HF}/assets/fonts/{f}")
    hosts = []
    for i, T in enumerate(TL):
        k = T["s"]["kind"]
        h = {"intro": intro_scene, "chapter": chapter_scene, "species": species_scene, "outro": outro_scene}[k](T)
        open(f"{HF}/compositions/{T['id']}.html", "w", encoding="utf-8").write(h)
        hosts.append(f'<div id="{T["id"]}" data-composition-id="{T["id"]}" data-composition-src="compositions/{T["id"]}.html" data-start="{T["start"]:.3f}" data-duration="{T["dur"]:.3f}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
    cap, items = captions()
    open(f"{HF}/compositions/captions.html", "w", encoding="utf-8").write(cap)
    hosts.append(f'<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="3" data-track-kind="captions" data-width="1920" data-height="1080" style="z-index:50"></div>')
    audio = f'<audio id="narr" src="assets/audio.wav" data-start="0" data-duration="{TOTAL:.3f}" data-volume="1" data-track-index="5"></audio>'
    idx = (f'<!doctype html><html lang="ko"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>'
           f'<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
           f'<style>html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:#05192b}}</style></head><body>'
           f'<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080">{"".join(hosts)}{audio}</div>'
           f'<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = gsap.timeline({{ paused: true }});</script></body></html>')
    open(f"{HF}/index.html", "w", encoding="utf-8").write(idx)
    json.dump(dict(total=round(TOTAL, 2), sections=[dict(id=T["id"], name=T["s"]["name"], kind=T["s"]["kind"], start=round(T["start"], 2), dur=round(T["dur"], 2)) for T in TL],
                   captions=len(items)), open(f"{HERE}/timeline.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"장면 {len(TL)}개, 자막 {len(items)}큐, 총 {int(TOTAL // 60)}:{int(TOTAL % 60):02d} ({TOTAL:.1f}s) {'[추정 길이]' if EST else ''}")


if __name__ == "__main__":
    main()
