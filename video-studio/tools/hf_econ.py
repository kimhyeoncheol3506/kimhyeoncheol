"""경제 영상용 HyperFrames 모션그래픽 장면 생성기 (v1.14.0)

scene 한 장(대사 길이 D초)을 1920x1080 mp4로 렌더한다. 종류(kind):
  title  챕터 카드         kpi   큰 숫자·문구          quote 큰 문장(단어별 등장)
  chart  선 그래프(개념도)  dual  두 패널 비교 그래프    flow  흐름도(칸+화살표)
  loop   악순환 고리        compare 좌우 비교          check 번호 카드 목록
  scale  저울              timeline 연표               hub   중심+요인 칩
  signal 신호등            qa     질문 장면
강조 표기: [금색] {빨강} |초록| ‹파랑›   (화면의 숫자는 개념도·예시일 때 badge로 표시)
사용: from hf_econ import render; render(root, sid, kind, params, dur)
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")
C = dict(bg="#0A1226", card="#131E3B", line="#27386A", gold="#F6C945", red="#FF5468", teal="#2FD6A8",
         blue="#5CA9FF", text="#F3F6FF", mute="#93A4C8")
LOOK = os.environ.get("HF_LOOK", "")
if LOOK == "fiche":  # OPUSCAR 98 No.88 Spotlight: 도서관 마이크로피시 리더 — 인광 녹색 단색, 주인공만 원색
    C = dict(bg="#0c110f", card="#141d19", line="#2c4036", gold="#D97757", red="#E2634B", teal="#7fd1a0",
             blue="#6fbfb3", text="#a0dcaf", mute="#5d7d6a")
if LOOK == "sting":  # OPUSCAR 98 No.46 The Sting: 1930s 새터데이 이브닝 포스트 표지 일러스트 (석고·참나무·슬레이트·황동·잉크). 한국식 색: 빨강=수익, 파랑=손실
    C = dict(bg="#28322C", card="#323C35", line="#5a5a44", gold="#E2B046", red="#DE5B41", teal="#9DBB91",
             blue="#5B93B8", text="#F1E3C2", mute="#B3A47F")
COL = {"gold": C["gold"], "red": C["red"], "teal": C["teal"], "blue": C["blue"], "white": C["text"], "mute": C["mute"]}


TOK = r"(?:\[[^\]]+\]|\{[^}]+\}|\|[^|]+\||‹[^›]+›|[^\s\[\]{}|‹›]+)+"


def split_marked(t: str) -> str:
    """강조 괄호 안의 띄어쓰기를 어절별 괄호로 쪼갠다: [진짜 위기]는 → [진짜] [위기]는 (줄바꿈을 어절 단위로)"""
    def f(m):
        o, body, c = m.group(1), m.group(2), m.group(3)
        return " ".join(f"{o}{w}{c}" for w in body.split())
    t = re.sub(r"(\[)([^\]]+)(\])", f, t)
    t = re.sub(r"(\{)([^}]+)(\})", f, t)
    t = re.sub(r"(‹)([^›]+)(›)", f, t)
    return t


def rich(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\[(.+?)\]", r'<b class="g">\1</b>', t)
    t = re.sub(r"\{(.+?)\}", r'<b class="r">\1</b>', t)
    t = re.sub(r"\|(.+?)\|", r'<b class="t">\1</b>', t)
    t = re.sub(r"‹(.+?)›", r'<b class="b">\1</b>', t)
    return t.replace("\n", "<br>")


def smooth(pts):
    """Catmull-Rom → cubic bezier path"""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


class Scene:
    def __init__(self, D, chip=None, headline=None, ant=None, shift=0.0):
        self.shift = shift
        D = D - shift  # 콘텐츠 타임라인 길이 (챕터 카드가 앞 shift초를 차지)
        self.D = D
        self.h: list[str] = []
        self.j: list[str] = []
        self.n = 0
        self.t0 = 0.30
        self.W = max(0.9, min(D * 0.72, D - 1.1))  # 등장 연출이 끝나야 하는 시각
        self.chip, self.headline = chip, headline
        self.VT = 360 if headline else 150
        self.VB = 880

    def id(self, p="e"):
        self.n += 1
        return f"{p}{self.n}"

    def at(self, k, n):
        """n개 항목 중 k번째 등장 시각 (대사 길이에 맞춰 고르게)"""
        if n <= 1:
            return self.t0 + 0.15
        return self.t0 + (self.W - self.t0) * k / (n - 1)


def page(S: Scene, body: str, js: str, extra_css: str = "", intro=None) -> str:
    D = S.D + S.shift
    chip = f'<div id="chip" class="chip">{html.escape(S.chip)}</div>' if S.chip else ""
    head = ""
    hjs = ""
    if S.headline:
        words = re.findall(TOK, split_marked(S.headline))
        n_ch = len(re.sub(r"[\[\]{}|‹›\s]", "", S.headline))
        fs = 96 if n_ch <= 12 else 84 if n_ch <= 20 else 72
        spans = "".join(f'<span class="w" id="hw{i}">{rich(w)}&nbsp;</span>' for i, w in enumerate(words))
        head = f'<div id="head" style="font-size:{fs}px">{spans}</div>'
        hjs = f'tl.fromTo(".w",{{opacity:0,y:34}},{{opacity:1,y:0,duration:0.42,ease:"power3.out",stagger:{min(0.12, 0.9 / max(1, len(words))):.3f}}},0.12);'
    intro_html = intro_js = ""
    if intro:
        no, ttl = intro
        _sting = LOOK == "sting"
        intro_html = f'''<div id="intro" class="clip" data-start="0" data-duration="{S.shift:.2f}" data-track-index="2" style="position:absolute;left:0;top:0;width:1920px;height:1080px;z-index:50;background:{"linear-gradient(110deg,#0c110f 0%,#1b2320 100%)" if LOOK == "fiche" else "linear-gradient(110deg,#070C1B 0%,#0F1B3A 100%)"}">
<div id="inum" class="abs" style="left:150px;top:210px;font-family:PBlack;font-size:360px;line-height:1;color:{C['gold']}">{html.escape(no)}</div>
<div id="ibar" class="abs" style="left:150px;top:600px;width:560px;height:12px;border-radius:6px;background:{C['gold']}"></div>
<div id="ittl" class="abs" style="left:150px;top:650px;width:1640px;font-family:PBlack;font-size:{100 if len(re.sub(r"[^가-힣A-Za-z0-9]", "", ttl)) <= 14 else 84 if len(re.sub(r"[^가-힣A-Za-z0-9]", "", ttl)) <= 26 else 72}px;line-height:1.15">{rich(ttl)}</div></div>'''
        if _sting:
            intro_html = f'''<div id="intro" class="clip" data-start="0" data-duration="{S.shift:.2f}" data-track-index="2" style="position:absolute;left:0;top:0;width:1920px;height:1080px;z-index:50;background:#E2C492">
<div class="abs" style="left:46px;top:46px;right:46px;bottom:46px;border:10px solid #341E18"></div><div class="abs" style="left:78px;top:78px;right:78px;bottom:78px;border:3px solid #764626"></div>
<div id="inum" class="abs" style="left:0;top:170px;width:1920px;text-align:center;font-family:PBlack;font-size:330px;line-height:1;color:#764626">{html.escape(no)}</div>
<div id="ibar" class="abs" style="left:660px;top:560px;width:600px;height:10px;background:#341E18"></div>
<div id="ittl" class="abs" style="left:160px;top:620px;width:1600px;text-align:center;font-family:PBlack;font-size:{96 if len(re.sub(r"[^가-힣A-Za-z0-9]", "", ttl)) <= 14 else 80 if len(re.sub(r"[^가-힣A-Za-z0-9]", "", ttl)) <= 26 else 68}px;line-height:1.18;color:#341E18">{re.sub(r"<b class=\"[a-z]\">(.*?)</b>", r"<span style=\"color:#B2432C\">\1</span>", rich(ttl))}</div></div>'''
        intro_js = f'''M.fromTo("#intro",{{x:-1920}},{{x:0,duration:.38,ease:"power4.out"}},0);
M.fromTo("#inum",{{opacity:0,x:-80}},{{opacity:1,x:0,duration:.5,ease:"power3.out"}},0.2);
M.fromTo("#ibar",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:.5,ease:"power3.inOut"}},0.35);
M.fromTo("#ittl",{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:"power3.out"}},0.45);
M.to("#intro",{{x:1920,duration:.4,ease:"power3.in"}},{S.shift - 0.4:.2f});'''
        if _sting:
            intro_js = f'''M.fromTo("#intro",{{opacity:0,scale:1.12}},{{opacity:1,scale:1,duration:.6,ease:"power3.out"}},0);
M.fromTo("#inum",{{y:50,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"power3.out"}},0.25);
M.fromTo("#ibar",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power3.inOut"}},0.45);
M.fromTo("#ittl",{{y:30,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"power3.out"}},0.6);
M.to("#intro",{{opacity:0,duration:.4,ease:"power2.in"}},{S.shift - 0.4:.2f});'''
    CARD1, CARD2 = ("#1b2823", "#131c18") if LOOK == "fiche" else ("#3a453d", "#262f29") if LOOK == "sting" else ("#17264A", "#111B36")
    GRID = "rgba(226,176,70,.05)" if LOOK == "sting" else "rgba(92,169,255,.07)"
    ROOT_BG = ("radial-gradient(1400px 850px at 30% 20%,#3b4a40 0%,#28322C 58%,#1c231f 100%)" if LOOK == "sting" else "radial-gradient(1300px 800px at 62% 28%,#26352d 0%,#1b2320 55%,#121a17 100%)" if LOOK == "fiche"
               else "radial-gradient(1400px 800px at 70% 20%,#16254A 0%,#0A1226 62%,#070C1B 100%)")
    look_html = look_js = ""
    if LOOK == "fiche":
        import random as _r
        rr = _r.Random(S.D * 1000 + len(body))
        dust = "".join(f'<circle cx="{rr.randint(60,1860)}" cy="{rr.randint(60,1020)}" r="{rr.choice([1.2,1.6,2.4,3.2])}" fill="#a0dcaf" opacity="{rr.choice([.10,.16,.22])}"/>' for _ in range(16))
        hx, hy = rr.randint(300, 1500), rr.randint(150, 900)
        hair = f'<path d="M{hx},{hy} q40,-60 90,-20 t70,40" fill="none" stroke="#a0dcaf" stroke-width="1.4" opacity=".16"/>'
        n_bar = max(1, int(D // 4))
        look_html = f'''<div id="lk" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="9" style="position:absolute;inset:0;pointer-events:none;z-index:40">
<div style="position:absolute;inset:0;background-image:radial-gradient(circle at 50% 50%,rgba(6,12,9,.42) 1.7px,transparent 2.3px);background-size:7.7px 7.7px;opacity:.55;mix-blend-mode:multiply"></div>
<div style="position:absolute;inset:0;background-image:radial-gradient(circle at 50% 50%,rgba(6,12,9,.30) 1.4px,transparent 2.0px);background-size:7.7px 7.7px;background-position:3px 4px;opacity:.35;mix-blend-mode:multiply"></div>
<div style="position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(0,0,0,.20) 0 1px,transparent 1px 3px)"></div>
<div style="position:absolute;inset:0;background:radial-gradient(900px 600px at 64% 26%,rgba(160,220,175,.07),transparent 70%)"></div>
<div id="sbar" style="position:absolute;left:0;top:-220px;width:1920px;height:170px;background:linear-gradient(180deg,transparent,rgba(160,220,175,.08),transparent)"></div>
<svg style="position:absolute;left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">{dust}{hair}</svg>
<div style="position:absolute;left:0;top:0;width:1920px;height:1080px;box-shadow:inset 0 0 160px 40px rgba(0,0,0,.55);border-radius:26px"></div>
<div style="position:absolute;left:28px;bottom:22px;font-family:monospace;font-size:20px;letter-spacing:2px;color:#5d7d6a">FICHE 26 · {S.chip[:2] if S.chip else "--"}</div>
</div>'''
        look_js = "".join(f'M.fromTo("#sbar",{{y:0}},{{y:1400,duration:1.6,ease:"none"}},{1.0 + k * 4:.2f});' for k in range(n_bar))
        look_js += 'M.fromTo("#sheet",{x:1920},{x:0,duration:.5,ease:"power3.out"},0);'
    if LOOK == "sting":
        look_html = '''<div id="lk" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="9" style="position:absolute;inset:0;pointer-events:none;z-index:40">
<svg width="1920" height="1080" style="position:absolute;left:0;top:0;opacity:.10;mix-blend-mode:overlay"><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix type="saturate" values="0"/></filter><rect width="1920" height="1080" filter="url(#gr)"/></svg>
<div style="position:absolute;inset:0;background:radial-gradient(1000px 640px at 40% 35%,rgba(226,176,70,.06),transparent 70%)"></div>
<div style="position:absolute;inset:0;box-shadow:inset 0 0 200px 50px rgba(52,30,24,.55)"></div>
</div>'''.replace("{D:.3f}", f"{D:.3f}")
        look_js = f'M.fromTo("#sheet",{{scale:1,transformOrigin:"46% 48%"}},{{scale:1.04,duration:{D:.3f},ease:"none"}},0);'
    css = f"""
@font-face{{font-family:PBlack;src:url("assets/fonts/Pretendard-Black.otf")}}
@font-face{{font-family:PXB;src:url("assets/fonts/Pretendard-ExtraBold.otf")}}
@font-face{{font-family:PBold;src:url("assets/fonts/Pretendard-Bold.otf")}}
@font-face{{font-family:PMed;src:url("assets/fonts/Pretendard-Medium.otf")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:{C['bg']}}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;color:{C['text']};font-family:PBold,sans-serif;
 background:{ROOT_BG}}}
#grid{{position:absolute;inset:0;opacity:.5;background-image:linear-gradient({GRID} 1px,transparent 1px),linear-gradient(90deg,{GRID} 1px,transparent 1px);background-size:96px 96px}}
.chip{{position:absolute;z-index:6;left:90px;top:56px;padding:10px 26px;border-radius:40px;border:2px solid {C['gold']};color:{C['gold']};font-family:PXB;font-size:30px;letter-spacing:1px;background:rgba(246,201,69,.08)}}
#head{{position:absolute;left:90px;top:132px;width:1560px;font-family:PBlack;line-height:1.16;color:{C['text']};text-shadow:0 4px 18px rgba(0,0,0,.45)}}
.w,.qw{{display:inline-block}}
b.g{{color:{C['gold']}}} b.r{{color:{C['red']}}} b.t{{color:{C['teal']}}} b.b{{color:{C['blue']}}} b{{font-weight:inherit}}
.card{{position:absolute;border-radius:28px;background:linear-gradient(160deg,{CARD1},{CARD2});border:2px solid {C['line']};box-shadow:0 18px 50px rgba(0,0,0,.35)}}
.abs{{position:absolute}}
.badge{{position:absolute;right:90px;font-family:PXB;font-size:26px;color:{C['mute']};padding:8px 20px;border-radius:30px;border:2px dashed {C['line']}}}
{extra_css}
"""
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920, height=1080">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1920" data-height="1080">
<div id="sheet" style="position:absolute;inset:0"><div id="grid" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="0"></div>
<div id="stage" class="clip" data-start="0" data-duration="{D:.3f}" data-track-index="1" style="position:absolute;inset:0">
{chip}{head}
{body}
</div>{intro_html}</div>{look_html}</div>
<script>
const M=gsap.timeline({{paused:true}});
M.fromTo("#grid",{{backgroundPosition:"0px 0px"}},{{backgroundPosition:"-96px -96px",duration:{D:.3f},ease:"none"}},0);
{intro_js}{look_js}
const tl=gsap.timeline();
tl.fromTo("#chip",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.4,ease:"power3.out"}},0);
{hjs}
{js}
M.add(tl,{S.shift:.2f});
window.__timelines["main"]=M;M.seek(0);
</script></body></html>
"""


def pop(sel, t, dur=0.45, y=26, scale=0.92):
    return f'tl.fromTo("{sel}",{{opacity:0,y:{y},scale:{scale}}},{{opacity:1,y:0,scale:1,duration:{dur},ease:"back.out(1.6)"}},{t:.3f});'


def ant_html(S, ant, side="l"):
    if not ant:
        return "", ""
    pose, h = ant if isinstance(ant, (list, tuple)) else (ant, 520)
    w = int(h * 0.8)
    x = 90 if side == "l" else 1830 - w
    i = S.id("ant")
    top = S.VB - h + 40
    html_ = f'<img id="{i}" class="abs" src="assets/mascot/{pose}.png" style="left:{x}px;top:{top}px;width:{w}px;height:{h}px;filter:{'saturate(.8) contrast(.9) brightness(.88) ' if LOOK == 'fiche' else ''}drop-shadow(0 12px 24px rgba(0,0,0,.45))">'
    js = f'tl.fromTo("#{i}",{{opacity:0,y:80,scale:.9}},{{opacity:1,y:0,scale:1,duration:.6,ease:"back.out(1.5)"}},0.2);'
    js += f'tl.to("#{i}",{{y:-10,duration:{max(1.0, S.D):.2f},ease:"sine.inOut",yoyo:true,repeat:{max(0, int(S.D / 1.6))}}},0.9);'
    return html_, js


# ───────────────────────── 종류별 장면 ─────────────────────────
def k_title(S, p):
    no, title, sub = p.get("no", ""), p["title"], p.get("sub", "")
    b = f"""<div id="tno" class="abs" style="left:150px;top:250px;font-family:PBlack;font-size:300px;line-height:1;color:{C['gold']};opacity:.95">{html.escape(no)}</div>
<div id="tbar" class="abs" style="left:150px;top:590px;width:520px;height:10px;border-radius:6px;background:{C['gold']}"></div>
<div id="tt" class="abs" style="left:150px;top:640px;width:1500px;font-family:PBlack;font-size:96px;line-height:1.12">{rich(title)}</div>
<div id="ts" class="abs" style="left:154px;top:800px;font-family:PMed;font-size:42px;color:{C['mute']}">{rich(sub)}</div>"""
    j = f"""tl.fromTo("#tno",{{opacity:0,x:-120,scale:.9}},{{opacity:.95,x:0,scale:1,duration:.7,ease:"power4.out"}},0.1);
tl.fromTo("#tbar",{{scaleX:0,transformOrigin:"0% 50%"}},{{scaleX:1,duration:.6,ease:"power3.inOut"}},0.5);
tl.fromTo("#tt",{{opacity:0,y:40}},{{opacity:1,y:0,duration:.6,ease:"power3.out"}},0.7);
tl.fromTo("#ts",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.5,ease:"power3.out"}},1.0);"""
    return b, j


def k_kpi(S, p):
    """kicker + big(+counter) + unit + sub"""
    col = COL.get(p.get("color", "gold"), C["gold"])
    side = p.get("ant_side", "r")
    ah, aj = ant_html(S, p.get("ant"), side)
    x0, w = (90, 1740) if not p.get("ant") else ((90, 1160) if side == "r" else (560, 1260))
    y0 = S.VT + (40 if S.headline else 120)
    big = p["big"]
    fs = p.get("size", 230 if len(big) <= 6 else 170 if len(big) <= 9 else 130)
    cnt = p.get("count")  # [시작, 끝]
    b = f"""<div id="kk" class="abs" style="left:{x0}px;top:{y0}px;width:{w}px;text-align:center;font-family:PXB;font-size:44px;color:{C['mute']}">{rich(p.get('kicker',''))}</div>
<div id="kb" class="abs" style="left:{x0}px;top:{y0+60}px;width:{w}px;text-align:center;font-family:PBlack;font-size:{fs}px;line-height:1.1;color:{col};text-shadow:0 0 40px {col}55">{html.escape(big) if not cnt else cnt[0]}</div>
<div id="ku" class="abs" style="left:{x0}px;top:{y0+60+int(fs*1.15)}px;width:{w}px;text-align:center;font-family:PXB;font-size:52px">{rich(p.get('unit',''))}</div>
<div id="ks" class="abs" style="left:{x0}px;top:{y0+60+int(fs*1.15)+80}px;width:{w}px;text-align:center;font-family:PMed;font-size:40px;color:{C['mute']}">{rich(p.get('sub',''))}</div>{ah}"""
    j = f"""tl.fromTo("#kk",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45}},0.3);
tl.fromTo("#kb",{{opacity:0,scale:.7}},{{opacity:1,scale:1,duration:.6,ease:"back.out(1.8)"}},0.5);
tl.fromTo("#ku",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45}},0.9);
tl.fromTo("#ks",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.45}},1.2);{aj}"""
    if cnt:
        a, z = cnt
        fmt = p.get("fmt", "int")
        j += f"""const st={{p:0}};tl.to(st,{{p:1,duration:{max(1.0, S.W - 0.5):.2f},ease:"power2.out",onUpdate:()=>{{const v={a}+({z}-{a})*st.p;document.getElementById("kb").textContent={'v.toFixed(1)' if fmt == 'f1' else 'Math.round(v)'}+{json.dumps(p.get('suffix', ''))};}}}},0.5);"""
    return b, j


def k_quote(S, p):
    ant = p.get("ant")
    side = p.get("ant_side", "r")
    ah, aj = ant_html(S, (ant if not ant or isinstance(ant, (list, tuple)) else (ant, 600)), side)
    lines = p["lines"] if isinstance(p["lines"], list) else [p["lines"]]
    x0, w = (130, 1700) if not ant else ((130, 1180) if side == "r" else (600, 1230))
    fs = p.get("size", 104)
    spans, k = "", 0
    for ln in lines:
        ws = re.findall(TOK, split_marked(ln))
        spans += '<div style="display:block">' + "".join(f'<span class="qw" id="q{(k := k + 1)}">{rich(w_)}&nbsp;</span>' for w_ in ws) + "</div>"
    top = S.VT if S.headline else 150
    h = S.VB - top
    b = (f'<div id="qbar" class="abs" style="left:{x0 - 40}px;top:{top + h // 2 - 150}px;width:14px;height:300px;border-radius:7px;background:linear-gradient(180deg,{C["gold"]},{C["red"]})"></div>'
         f'<div id="qt" class="abs" style="left:{x0}px;top:{top}px;width:{w}px;height:{h}px;display:flex;flex-direction:column;justify-content:center;'
         f'font-family:PBlack;font-size:{fs}px;line-height:1.28;text-align:{p.get("align", "left")}">{spans}</div>{ah}')
    j = (f'tl.fromTo("#qbar",{{scaleY:0,transformOrigin:"50% 50%"}},{{scaleY:1,duration:.5,ease:"power3.out"}},0.2);'
         f'tl.fromTo(".qw",{{opacity:0,y:40,scale:.9}},{{opacity:1,y:0,scale:1,duration:.4,ease:"back.out(1.5)",stagger:{max(0.08, min(0.22, (S.W - 0.3) / max(1, k))):.3f}}},0.3);') + aj
    return b, j


def k_qa(S, p):
    b = f"""<div id="qm" class="abs" style="left:110px;top:200px;font-family:PBlack;font-size:620px;line-height:1;color:{C['gold']};opacity:.95;text-shadow:0 0 80px rgba(246,201,69,.35)">?</div>
<div id="qq" class="abs" style="left:640px;top:300px;width:1180px;font-family:PBlack;font-size:{p.get('size', 92)}px;line-height:1.25">{rich(p['q'])}</div>"""
    j = f"""tl.fromTo("#qm",{{opacity:0,scale:.3,rotation:-18}},{{opacity:.95,scale:1,rotation:0,duration:.8,ease:"elastic.out(1,.55)"}},0.15);
tl.to("#qm",{{rotation:4,duration:{max(1.0, S.D):.2f},ease:"sine.inOut",yoyo:true,repeat:{max(0, int(S.D / 1.4))}}},0.95);
tl.fromTo("#qq",{{opacity:0,x:60}},{{opacity:1,x:0,duration:.6,ease:"power3.out"}},0.5);"""
    return b, j


def k_chart(S, p):
    """lines:[{name,color,pts:[0..1],end:'라벨',dash}], marks:[{x:0..1,text,color}], xlab:[..], badge"""
    x0, y0, w, h = 90, S.VT, 1740, S.VB - S.VT
    px0, px1, py0, py1 = 90, w - 140, 78, h - 74
    gid = S.id("g")
    body = f'<div id="{gid}" class="card" style="left:{x0}px;top:{y0}px;width:{w}px;height:{h}px"></div>'
    svg = [f'<svg class="abs" style="left:{x0}px;top:{y0}px" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    for g in range(5):
        yy = py0 + (py1 - py0) * g / 4
        svg.append(f'<line x1="{px0}" y1="{yy:.0f}" x2="{px1}" y2="{yy:.0f}" stroke="{C["line"]}" stroke-width="1.5" stroke-dasharray="6 10" opacity=".6"/>')
    js = [f'tl.fromTo("#{gid}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.5,ease:"power3.out"}},0.15);']
    lab = []
    for li, ln in enumerate(p["lines"]):
        pts = [(px0 + (px1 - px0) * i / (len(ln["pts"]) - 1), py1 - (py1 - py0) * v) for i, v in enumerate(ln["pts"])]
        col = COL.get(ln.get("color", "gold"), ln.get("color", C["gold"]))
        pid = S.id("ln")
        svg.append(f'<path id="{pid}" d="{smooth(pts)}" fill="none" stroke="{col}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" opacity="0.95"/>')
        t_a = 0.5 + li * 0.25
        dur = max(0.8, S.W - t_a - 0.1)
        js.append(f'tl.fromTo("#{pid}",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:{dur:.2f},ease:"power1.inOut"}},{t_a:.2f});')
        ex, ey = pts[-1]
        eid = S.id("end")
        lab.append(f'<div id="{eid}" class="abs" style="left:{x0 + ex + 22:.0f}px;top:{y0 + ey - 30:.0f}px;font-family:PBlack;font-size:40px;color:{col};white-space:nowrap">{rich(ln.get("end", ""))}</div>')
        js.append(f'tl.fromTo("#{eid}",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.4}},{t_a + dur:.2f});')
        dot = S.id("dot")
        svg.append(f'<circle id="{dot}" cx="{ex:.0f}" cy="{ey:.0f}" r="15" fill="{col}" opacity="0"/>')
        js.append(f'tl.fromTo("#{dot}",{{opacity:0,scale:0,svgOrigin:"{ex:.0f} {ey:.0f}"}},{{opacity:1,scale:1,duration:.35,ease:"back.out(3)"}},{t_a + dur:.2f});')
        # 범례
        lg = S.id("lg")
        lab.append(f'<div id="{lg}" class="abs" style="left:{x0 + 60 + li * 380}px;top:{y0 + 18}px;font-family:PXB;font-size:32px;color:{col}"><span style="display:inline-block;width:34px;height:10px;border-radius:5px;background:{col};margin-right:12px"></span>{rich(ln["name"])}</div>')
        js.append(f'tl.fromTo("#{lg}",{{opacity:0}},{{opacity:1,duration:.4}},{0.3 + li * 0.2:.2f});')
    for mi, m in enumerate(p.get("marks", [])):
        mx = px0 + (px1 - px0) * m["x"]
        col = COL.get(m.get("color", "gold"), C["gold"])
        mid = S.id("mk")
        svg.append(f'<line id="{mid}" x1="{mx:.0f}" y1="{py0 - 10}" x2="{mx:.0f}" y2="{py1 + 10}" stroke="{col}" stroke-width="4" stroke-dasharray="10 10" opacity="0"/>')
        ta = 0.5 + (S.W - 0.5) * m["x"]
        js.append(f'tl.fromTo("#{mid}",{{opacity:0}},{{opacity:.9,duration:.3}},{ta:.2f});')
        tid = S.id("mt")
        lab.append(f'<div id="{tid}" class="abs" style="left:{x0 + mx - 150:.0f}px;top:{y0 + h - 64}px;width:300px;text-align:center;font-family:PXB;font-size:32px;color:{col}">{rich(m["text"])}</div>')
        js.append(f'tl.fromTo("#{tid}",{{opacity:0,y:14}},{{opacity:1,y:0,duration:.4}},{ta + 0.05:.2f});')
    svg.append("</svg>")
    if p.get("badge"):
        lab.append(f'<div class="badge" style="top:{y0 - 54}px">{html.escape(p["badge"])}</div>')
    return body + "".join(svg) + "".join(lab), "\n".join(js)


def k_dual(S, p):
    """panels:[{title,color,pts,tag,note}] 2개"""
    n = len(p["panels"])
    gap = 40
    w = (1740 - gap * (n - 1)) // n
    y0, h = S.VT, S.VB - S.VT
    body, js = [], []
    for i, pn in enumerate(p["panels"]):
        x0 = 90 + i * (w + gap)
        col = COL.get(pn.get("color", "gold"), C["gold"])
        cid = S.id("pc")
        px0, px1, py0, py1 = 50, w - 50, 150, h - 80
        pts = [(px0 + (px1 - px0) * k / (len(pn["pts"]) - 1), py1 - (py1 - py0) * v) for k, v in enumerate(pn["pts"])]
        pid = S.id("pl")
        body.append(f'<div id="{cid}" class="card" style="left:{x0}px;top:{y0}px;width:{w}px;height:{h}px"></div>')
        body.append(f'<div id="{cid}t" class="abs" style="left:{x0 + 40}px;top:{y0 + 26}px;font-family:PBlack;font-size:50px;color:{col}">{rich(pn["title"])}</div>')
        body.append(f'<svg class="abs" style="left:{x0}px;top:{y0}px" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><path id="{pid}" d="{smooth(pts)}" fill="none" stroke="{col}" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
        body.append(f'<div id="{cid}g" class="abs" style="left:{x0 + w - 330}px;top:{y0 + 30}px;width:290px;text-align:center;padding:10px 0;border-radius:40px;background:{col};color:#0A1226;font-family:PBlack;font-size:40px">{rich(pn.get("tag", ""))}</div>')
        body.append(f'<div id="{cid}n" class="abs" style="left:{x0 + 40}px;top:{y0 + h - 70}px;width:{w - 80}px;font-family:PMed;font-size:34px;color:{C["mute"]}">{rich(pn.get("note", ""))}</div>')
        t_a = 0.45 + i * 0.35
        js.append(f'tl.fromTo("#{cid}",{{opacity:0,y:40}},{{opacity:1,y:0,duration:.5,ease:"power3.out"}},{0.15 + i * 0.2:.2f});')
        js.append(f'tl.fromTo("#{cid}t",{{opacity:0}},{{opacity:1,duration:.4}},{t_a:.2f});')
        js.append(f'tl.fromTo("#{pid}",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:{max(0.8, S.W - t_a - 0.5):.2f},ease:"power1.inOut"}},{t_a + 0.1:.2f});')
        js.append(f'tl.fromTo("#{cid}g",{{opacity:0,scale:.5}},{{opacity:1,scale:1,duration:.45,ease:"back.out(2.4)"}},{S.W:.2f});')
        js.append(f'tl.fromTo("#{cid}n",{{opacity:0}},{{opacity:1,duration:.5}},{S.W + 0.1:.2f});')
    if p.get("badge"):
        body.append(f'<div class="badge" style="top:{y0 - 54}px">{html.escape(p["badge"])}</div>')
    return "".join(body), "\n".join(js)


def _node(S, x, y, w, h, nd, k, n):
    col = COL.get(nd.get("c", "gold"), C["gold"])
    i = S.id("nd")
    ic = nd.get("icon", "")
    b = f"""<div id="{i}" class="card" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-color:{col};text-align:center">
<div style="position:absolute;left:0;top:{18 if ic else 40}px;width:100%;font-family:PBlack;font-size:{64 if ic else 0}px;color:{col};height:{70 if ic else 0}px;line-height:70px">{html.escape(ic)}</div>
<div style="position:absolute;left:14px;right:14px;top:{98 if ic else 36}px;font-family:PBlack;font-size:{nd.get('fs', 42)}px;line-height:1.2;color:{C['text']}">{rich(nd['t'])}</div>
<div style="position:absolute;left:14px;right:14px;bottom:20px;font-family:PMed;font-size:30px;line-height:1.25;color:{C['mute']}">{rich(nd.get('s', ''))}</div></div>"""
    return i, b


def _arrow(S, x1, y1, x2, y2, col, t):
    i = S.id("ar")
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    L = math.hypot(x2 - x1, y2 - y1)
    b = f'<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><line id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/><polygon id="{i}h" points="0,-18 34,0 0,18" fill="{col}" opacity="0" transform="translate({x2 + 6 * math.cos(math.radians(ang)):.0f},{y2 + 6 * math.sin(math.radians(ang)):.0f}) rotate({ang:.1f})"/></svg>'
    j = f'tl.fromTo("#{i}",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:.35,ease:"power2.out"}},{t:.2f});tl.fromTo("#{i}h",{{opacity:0}},{{opacity:1,duration:.15}},{t + 0.28:.2f});'
    return b, j


def k_flow(S, p):
    nodes = p["nodes"]
    n = len(nodes)
    per_row = p.get("per_row", n if n <= 4 else 3)
    rows = math.ceil(n / per_row)
    h = p.get("h", 250 if rows == 1 else 215)
    area_h = S.VB - S.VT
    gap = 110 if per_row <= 4 else 70
    w = (1740 - gap * (per_row - 1)) // per_row
    body, js = [], []
    pos = []
    for k in range(n):
        r, c = divmod(k, per_row)
        in_row = min(per_row, n - r * per_row)
        row_w = in_row * w + (in_row - 1) * gap
        x = 90 + (1740 - row_w) // 2 + c * (w + gap)
        y = S.VT + (area_h - (rows * h + (rows - 1) * 90)) // 2 + r * (h + 90)
        pos.append((x, y))
    for k, nd in enumerate(nodes):
        i, b = _node(S, pos[k][0], pos[k][1], w, h, nd, k, n)
        t = S.at(k, n)
        body.append(b)
        js.append(pop(f"#{i}", t))
        if k > 0:
            (xa, ya), (xb, yb) = pos[k - 1], pos[k]
            col = COL.get(nodes[k].get("c", "gold"), C["gold"])
            if ya == yb:
                ab, aj = _arrow(S, xa + w + 14, ya + h // 2, xb - 22, yb + h // 2, col, t - 0.28)
            else:  # 줄바꿈: 아래로 꺾이는 화살표
                ab, aj = _arrow(S, xa + w // 2, ya + h + 8, xb + w // 2, yb - 22, col, t - 0.28)
            body.append(ab)
            js.append(aj)
    if p.get("badge"):
        body.append(f'<div class="badge" style="top:{S.VT - 54}px">{html.escape(p["badge"])}</div>')
    return "".join(body), "\n".join(js)


def k_loop(S, p):
    """nodes 3~5개를 타원에 배치, 사이를 호 화살표로. center: 가운데 문구"""
    nodes = p["nodes"]
    n = len(nodes)
    cx, cy = 960, (S.VT + S.VB) // 2 + 5
    rx, ry = 640, (S.VB - S.VT) // 2 - 82
    w, h = 400, 150
    body, js = [], []
    P = []
    for k in range(n):
        a = -math.pi / 2 + 2 * math.pi * k / n
        P.append((cx + rx * math.cos(a), cy + ry * math.sin(a), a))
    svg = ['<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">']
    for k in range(n):
        a0 = P[k][2] + 0.42
        a1 = P[(k + 1) % n][2] - 0.46 + (2 * math.pi if (k + 1) % n == 0 else 0)
        rx2, ry2 = rx, ry
        pts = [(cx + rx2 * math.cos(a0 + (a1 - a0) * s / 8), cy + ry2 * math.sin(a0 + (a1 - a0) * s / 8)) for s in range(9)]
        col = COL.get(nodes[(k + 1) % n].get("c", "red"), C["red"])
        aid = S.id("la")
        ex, ey = pts[-1]
        ang = math.degrees(math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]))
        svg.append(f'<path id="{aid}" d="{smooth(pts)}" fill="none" stroke="{col}" stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
        svg.append(f'<polygon id="{aid}h" points="0,-18 34,0 0,18" fill="{col}" opacity="0" transform="translate({ex:.0f},{ey:.0f}) rotate({ang:.1f})"/>')
        t = S.at(k, n) + 0.30
        js.append(f'tl.fromTo("#{aid}",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:.45,ease:"power2.inOut"}},{t:.2f});tl.fromTo("#{aid}h",{{opacity:0}},{{opacity:1,duration:.15}},{t + 0.38:.2f});')
    svg.append("</svg>")
    body.append("".join(svg))
    for k, nd in enumerate(nodes):
        x, y, _ = P[k]
        i, b = _node(S, int(x - w / 2), int(y - h / 2), w, h, dict(nd, s="", icon="", fs=nd.get("fs", 40)), k, n)
        body.append(b.replace(f'top:{36}px', 'top:30px'))
        js.append(pop(f"#{i}", S.at(k, n)))
    if p.get("center"):
        body.append(f'<div id="lc" class="abs" style="left:{cx - 330}px;top:{cy - 70}px;width:660px;text-align:center;font-family:PBlack;font-size:{p.get("cfs", 70)}px;line-height:1.2;color:{C["red"]};text-shadow:0 0 40px rgba(255,84,104,.4)">{rich(p["center"])}</div>')
        js.append(f'tl.fromTo("#lc",{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.6,ease:"back.out(2)"}},{S.W:.2f});')
        js.append(f'tl.to("#lc",{{scale:1.06,duration:.8,ease:"sine.inOut",yoyo:true,repeat:{max(0, int((S.D - S.W) / 1.6))}}},{S.W + 0.7:.2f});')
    return "".join(body), "\n".join(js)


def k_compare(S, p):
    L, R = p["left"], p["right"]
    y0, h = S.VT, S.VB - S.VT
    w = 800
    body, js = [], []
    for si, (side, x) in enumerate(((L, 90), (R, 1030))):
        col = COL.get(side.get("c", "gold"), C["gold"])
        cid = S.id("cp")
        body.append(f'<div id="{cid}" class="card" style="left:{x}px;top:{y0}px;width:{w}px;height:{h}px;border-color:{col}"></div>')
        body.append(f'<div id="{cid}t" class="abs" style="left:{x}px;top:{y0 + 26}px;width:{w}px;text-align:center;font-family:PBlack;font-size:58px;color:{col}">{rich(side["title"])}</div>')
        body.append(f'<div class="abs" style="left:{x + 60}px;top:{y0 + 112}px;width:{w - 120}px;height:4px;background:{col};opacity:.6"></div>')
        js.append(f'tl.fromTo("#{cid}",{{opacity:0,x:{-60 if si == 0 else 60}}},{{opacity:1,x:0,duration:.55,ease:"power3.out"}},0.2);')
        js.append(f'tl.fromTo("#{cid}t",{{opacity:0}},{{opacity:1,duration:.4}},0.5);')
        rows = side["rows"]
        rh = min(120, (h - 150) // max(1, len(rows)))
        for ri, r in enumerate(rows):
            rid = S.id("rw")
            body.append(f'<div id="{rid}" class="abs" style="left:{x + 50}px;top:{y0 + 140 + ri * rh}px;width:{w - 100}px;font-family:PXB;font-size:44px;line-height:1.25;"><span style="color:{col}">●</span>&nbsp; {rich(r)}</div>')
            js.append(f'tl.fromTo("#{rid}",{{opacity:0,x:{-30 if si == 0 else 30}}},{{opacity:1,x:0,duration:.4,ease:"power3.out"}},{S.at(ri, len(rows)) + si * 0.12 + 0.2:.2f});')
    body.append(f'<div id="vs" class="abs" style="left:{960 - 55}px;top:{y0 + h // 2 - 55}px;width:110px;height:110px;border-radius:55px;background:{C["gold"]};color:#0A1226;text-align:center;line-height:110px;font-family:PBlack;font-size:48px;z-index:5">VS</div>')
    js.append(f'tl.fromTo("#vs",{{opacity:0,scale:0,rotation:-90}},{{opacity:1,scale:1,rotation:0,duration:.5,ease:"back.out(2.6)"}},0.55);')
    return "".join(body), "\n".join(js)


def k_check(S, p):
    items = p["items"]
    n = len(items)
    gap = 28
    h = min(190, (S.VB - S.VT - gap * (n - 1)) // n)
    body, js = [], []
    for k, it in enumerate(items):
        y = S.VT + k * (h + gap)
        col = COL.get(it.get("c", "gold"), C["gold"])
        i = S.id("ck")
        num = it.get("no", str(k + 1))
        body.append(f"""<div id="{i}" class="card" style="left:90px;top:{y}px;width:1740px;height:{h}px">
<div style="position:absolute;left:34px;top:{(h - 100) // 2}px;width:100px;height:100px;border-radius:50px;background:{col};color:#0A1226;text-align:center;line-height:100px;font-family:PBlack;font-size:56px">{html.escape(num)}</div>
<div style="position:absolute;left:176px;top:{h // 2 - (60 if it.get('s') else 34)}px;width:1500px;font-family:PBlack;font-size:56px;line-height:1.2">{rich(it['t'])}</div>
<div style="position:absolute;left:178px;top:{h // 2 + 14}px;width:1500px;font-family:PMed;font-size:36px;color:{C['mute']}">{rich(it.get('s', ''))}</div></div>""")
        js.append(pop(f"#{i}", S.at(k, n), y=40))
    return "".join(body), "\n".join(js)


def k_scale(S, p):
    """저울: left/right {t, c}, tilt(+이면 오른쪽이 무거움), 라벨"""
    cx, cy = 960, S.VT + 70
    Lb = 400
    th = float(p.get("tilt", 0))
    L, R = p["left"], p["right"]
    cl, cr = COL.get(L.get("c", "teal"), C["teal"]), COL.get(R.get("c", "red"), C["red"])
    body = f"""<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">
<polygon points="{cx - 70},{S.VB - 20} {cx + 70},{S.VB - 20} {cx},{cy + 20}" fill="{C['line']}"/><circle cx="{cx}" cy="{cy}" r="22" fill="{C['gold']}"/>
<line id="beam" x1="{cx - Lb}" y1="{cy}" x2="{cx + Lb}" y2="{cy}" stroke="{C['gold']}" stroke-width="16" stroke-linecap="round"/>
<line id="rl" x1="0" y1="0" x2="0" y2="0" stroke="{C['mute']}" stroke-width="5"/><line id="rr" x1="0" y1="0" x2="0" y2="0" stroke="{C['mute']}" stroke-width="5"/></svg>
<div id="pl" class="card" style="left:0;top:0;width:520px;height:170px;border-color:{cl};text-align:center"><div style="padding-top:22px;font-family:PBlack;font-size:44px;line-height:1.2;color:{cl}">{rich(L['t'])}</div><div style="font-family:PMed;font-size:30px;color:{C['mute']};margin-top:6px">{rich(L.get('s', ''))}</div></div>
<div id="pr" class="card" style="left:0;top:0;width:520px;height:170px;border-color:{cr};text-align:center"><div style="padding-top:22px;font-family:PBlack;font-size:44px;line-height:1.2;color:{cr}">{rich(R['t'])}</div><div style="font-family:PMed;font-size:30px;color:{C['mute']};margin-top:6px">{rich(R.get('s', ''))}</div></div>"""
    js = f"""const sc={{a:{p.get("from", 0)}}};
function place(){{const a=sc.a*Math.PI/180;const lx={cx}-{Lb}*Math.cos(a),ly={cy}-{Lb}*Math.sin(a),rx={cx}+{Lb}*Math.cos(a),ry={cy}+{Lb}*Math.sin(a);
document.getElementById("beam").setAttribute("transform","rotate("+sc.a+" {cx} {cy})");
const rl=document.getElementById("rl"),rr=document.getElementById("rr");const drop=140;
rl.setAttribute("x1",lx);rl.setAttribute("y1",ly);rl.setAttribute("x2",lx);rl.setAttribute("y2",ly+drop);
rr.setAttribute("x1",rx);rr.setAttribute("y1",ry);rr.setAttribute("x2",rx);rr.setAttribute("y2",ry+drop);
const pl=document.getElementById("pl"),pr=document.getElementById("pr");
pl.style.left=(lx-260)+"px";pl.style.top=(ly+drop)+"px";pr.style.left=(rx-260)+"px";pr.style.top=(ry+drop)+"px";}}
place();
tl.fromTo(["#pl","#pr"],{{opacity:0}},{{opacity:1,duration:.5}},0.3);
sc.a={p.get("from", 0)};place();
tl.to(sc,{{a:{th},duration:{max(1.0, S.W):.2f},ease:"{p.get("ease", "elastic.out(1,.6)")}",onUpdate:place}},0.7);"""
    return body, js


def k_timeline(S, p):
    ev = p["events"]
    n = len(ev)
    y = (S.VT + S.VB) // 2 + 10
    body, js = [], []
    body.append(f'<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080"><line id="tlx" x1="140" y1="{y}" x2="1780" y2="{y}" stroke="{C["line"]}" stroke-width="10" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
    js.append(f'tl.fromTo("#tlx",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:{max(0.8, S.W):.2f},ease:"power1.inOut"}},0.2);')
    for k, e in enumerate(ev):
        x = 140 + (1640) * (k + 0.5) / n
        col = COL.get(e.get("c", "gold"), C["gold"])
        i = S.id("tv")
        up = k % 2 == 0
        cy_ = y - 250 if up else y + 40
        body.append(f'<div id="{i}d" class="abs" style="left:{x - 24:.0f}px;top:{y - 24}px;width:48px;height:48px;border-radius:24px;background:{col};box-shadow:0 0 0 10px {C["bg"]}"></div>')
        body.append(f"""<div id="{i}" class="card" style="left:{x - 270:.0f}px;top:{cy_}px;width:540px;height:210px;border-color:{col};text-align:center">
<div style="padding-top:20px;font-family:PBlack;font-size:66px;color:{col};line-height:1">{html.escape(e['when'])}</div>
<div style="font-family:PXB;font-size:44px;margin-top:10px">{rich(e['t'])}</div><div style="font-family:PMed;font-size:32px;color:{C['mute']};margin-top:6px">{rich(e.get('s', ''))}</div></div>""")
        t = S.at(k, n) + 0.2
        js.append(f'tl.fromTo("#{i}d",{{scale:0}},{{scale:1,duration:.35,ease:"back.out(3)"}},{t:.2f});')
        js.append(pop(f"#{i}", t + 0.1, y=30 if not up else -30))
    return "".join(body), "\n".join(js)


def k_hub(S, p):
    """가운데 문구 + 주변 칩"""
    chips = p["chips"]
    n = len(chips)
    cx, cy = 960, (S.VT + S.VB) // 2
    rx, ry = 700, (S.VB - S.VT) // 2 - 62
    body, js = [], []
    svg = ['<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">']
    pos = []
    for k in range(n):
        a = -math.pi / 2 + 2 * math.pi * (k + (0.5 if n % 2 == 0 else 0)) / n
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        pos.append((x, y))
        lid = S.id("hl")
        svg.append(f'<line id="{lid}" x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{C["line"]}" stroke-width="5" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>')
        js.append(f'tl.fromTo("#{lid}",{{attr:{{"stroke-dashoffset":1}}}},{{attr:{{"stroke-dashoffset":0}},duration:.4}},{S.at(k, n) - 0.15:.2f});')
    svg.append("</svg>")
    body.append("".join(svg))
    body.append(f'<div id="hc" class="abs" style="left:{cx - 230}px;top:{cy - 75}px;width:460px;height:150px;border-radius:75px;background:{C["gold"]};color:#0A1226;text-align:center;font-family:PBlack;font-size:{p.get("cfs", 56)}px;line-height:1.2;display:flex;align-items:center;justify-content:center;padding:0 24px">{rich(p["center"])}</div>')
    js.append(f'tl.fromTo("#hc",{{opacity:0,scale:.4}},{{opacity:1,scale:1,duration:.55,ease:"back.out(2.2)"}},0.2);')
    for k, ch in enumerate(chips):
        x, y = pos[k]
        col = COL.get(ch.get("c", "blue"), C["blue"])
        i = S.id("hp")
        body.append(f'<div id="{i}" class="card" style="left:{x - 240:.0f}px;top:{y - 48:.0f}px;width:480px;height:96px;border-color:{col};text-align:center;font-family:PBlack;font-size:40px;line-height:92px;color:{col}">{rich(ch["t"])}</div>')
        js.append(pop(f"#{i}", S.at(k, n)))
    return "".join(body), "\n".join(js)


def k_signal(S, p):
    """lamps:[{c, t, s}] 가로 카드 + 램프. lit: 켜질 번호(없으면 전부)"""
    lamps = p["lamps"]
    n = len(lamps)
    gap = 40
    w = (1740 - gap * (n - 1)) // n
    h = 560
    y0 = S.VT + (S.VB - S.VT - h) // 2
    body, js = [], []
    for k, lp in enumerate(lamps):
        col = COL.get(lp.get("c", "gold"), C["gold"])
        x = 90 + k * (w + gap)
        i = S.id("sg")
        body.append(f"""<div id="{i}" class="card" style="left:{x}px;top:{y0}px;width:{w}px;height:{h}px;border-color:{col}">
<div id="{i}l" style="position:absolute;left:{w // 2 - 90}px;top:46px;width:180px;height:180px;border-radius:90px;background:{col};box-shadow:0 0 80px {col}99"></div>
<div style="position:absolute;left:20px;right:20px;top:270px;text-align:center;font-family:PBlack;font-size:56px;line-height:1.2;color:{col}">{rich(lp['t'])}</div>
<div style="position:absolute;left:24px;right:24px;top:410px;text-align:center;font-family:PMed;font-size:38px;line-height:1.35;color:{C['text']}">{rich(lp.get('s', ''))}</div></div>""")
        t = S.at(k, n)
        js.append(pop(f"#{i}", t, y=50))
        js.append(f'tl.fromTo("#{i}l",{{scale:.5,opacity:.2}},{{scale:1,opacity:1,duration:.5,ease:"back.out(2.4)"}},{t + 0.25:.2f});')
    return "".join(body), "\n".join(js)


def k_ledger(S, p):
    """계좌 목록(예시): rows=[{n,v,g}] g=True 수익(빨강) / False 손실(파랑). sell=[인덱스] 매도 도장+밀려남, hold=[인덱스] 존버 도장, show_only=[인덱스]"""
    rows = p["rows"]
    show = p.get("show_only") or list(range(len(rows)))
    sell, hold = set(p.get("sell", [])), set(p.get("hold", []))
    n = len(show)
    y0, h = S.VT, S.VB - S.VT
    rh = min(96, (h - 90) // max(1, n))
    cid = S.id("lg")
    body = [f'<div id="{cid}" class="card" style="left:290px;top:{y0}px;width:1340px;height:{h}px"></div>',
            f'<div class="abs" style="left:340px;top:{y0 + 18}px;font-family:PXB;font-size:32px;color:{C["mute"]}">내 계좌 (예시 · 실제 종목 아님)</div>']
    js = [f'tl.fromTo("#{cid}",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.5,ease:"power3.out"}},0.15);']
    ts = S.t0 + (S.W - S.t0) * float(p.get("t_sell", 0.6))
    for k, idx in enumerate(show):
        r = rows[idx]
        col = C["red"] if r["g"] else C["blue"]
        y = y0 + 80 + k * rh
        rid = S.id("rw")
        body.append(f'<div id="{rid}" class="abs" style="left:320px;top:{y}px;width:1280px;height:{rh - 12}px;border-radius:16px;background:rgba(0,0,0,.18);border-left:12px solid {col}">'
                    f'<div class="abs" style="left:40px;top:0;line-height:{rh - 12}px;font-family:PXB;font-size:44px">{html.escape(r["n"])}</div>'
                    f'<div class="abs" style="right:60px;top:0;line-height:{rh - 12}px;font-family:PBlack;font-size:52px;color:{col}">{html.escape(r["v"])}</div>'
                    f'<div id="{rid}s" class="abs" style="left:640px;top:{(rh - 12) // 2 - 28}px;padding:2px 22px;border:5px solid {C["red"] if idx in sell else C["gold"]};border-radius:10px;font-family:PBlack;font-size:38px;color:{C["red"] if idx in sell else C["gold"]};opacity:0">{"매도" if idx in sell else "존버"}</div></div>')
        js.append(pop(f"#{rid}", S.at(k, n), y=24))
        if idx in sell:
            js.append(f'tl.fromTo("#{rid}s",{{opacity:0,scale:2.4,rotation:-14}},{{opacity:1,scale:1,rotation:-6,duration:.3,ease:"back.out(2)"}},{ts + k * 0.08:.2f});')
            js.append(f'tl.to("#{rid}",{{x:520,opacity:0,duration:.7,ease:"power2.in"}},{ts + 0.5 + k * 0.08:.2f});')
        elif idx in hold:
            js.append(f'tl.fromTo("#{rid}s",{{opacity:0,scale:2.0}},{{opacity:1,scale:1,duration:.3,ease:"back.out(2)"}},{ts + 0.2:.2f});')
            js.append(f'tl.to("#{rid}",{{x:6,duration:.08,yoyo:true,repeat:5,ease:"sine.inOut"}},{ts + 0.5:.2f});')
    if p.get("sigh"):
        sg = S.id("sg")
        body.append(f'<div id="{sg}" class="abs" style="left:1660px;top:{y0 + 120}px;font-family:PBlack;font-size:56px;color:{C["mute"]}">후…</div>')
        js.append(f'tl.fromTo("#{sg}",{{opacity:0,y:20}},{{opacity:1,y:-24,duration:1.0,ease:"sine.out"}},{ts:.2f});')
    return "".join(body), "\n".join(js)


KINDS = {"title": k_title, "kpi": k_kpi, "quote": k_quote, "qa": k_qa, "chart": k_chart, "dual": k_dual, "flow": k_flow,
         "loop": k_loop, "compare": k_compare, "check": k_check, "scale": k_scale, "timeline": k_timeline, "hub": k_hub, "signal": k_signal, "ledger": k_ledger}


def build_html(kind, params, D):
    intro = params.get("intro")
    S = Scene(D, chip=params.get("chip"), headline=params.get("headline"), shift=2.0 if intro else 0.0)
    body, js = KINDS[kind](S, params)
    if kind not in ("quote", "kpi") and params.get("ant"):
        ah, aj = ant_html(S, params["ant"], params.get("ant_side", "r"))
        body += ah
        js += aj
    return page(S, body, js, intro=intro)


def key_of(kind, params, D):
    return hashlib.sha1(json.dumps([kind, params, round(D, 2), LOOK], ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:10]


def ensure_project(root):
    if not os.path.exists(os.path.join(root, "hyperframes.json")):
        os.makedirs(os.path.dirname(root), exist_ok=True)
        subprocess.run(["npx", "-y", "hyperframes", "init", os.path.basename(root), "--example", "blank", "--non-interactive"],
                       cwd=os.path.dirname(root), check=True, capture_output=True)
    fd = os.path.join(root, "assets", "fonts")
    os.makedirs(fd, exist_ok=True)
    for f in ("Pretendard-Black.otf", "Pretendard-ExtraBold.otf", "Pretendard-Bold.otf", "Pretendard-Medium.otf"):
        if not os.path.exists(os.path.join(fd, f)):
            shutil.copy(os.path.join(FONT_DIR, f), fd)


def export_ants(root, poses, height=640):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from studio.mascot import draw_ant
    from studio.mascot_poses import POSES
    d = os.path.join(root, "assets", "mascot")
    os.makedirs(d, exist_ok=True)
    for pz in poses:
        f = os.path.join(d, f"{pz}.png")
        if not os.path.exists(f):
            draw_ant(POSES[pz], height).save(f)


def render(root, sid, kind, params, D, out_dir, quality="looks", force=False):
    """장면 한 장 렌더 → out_dir/<sid>_<key>.mp4 (같은 내용이면 건너뜀). 경로 반환"""
    ensure_project(root)
    if params.get("ant"):
        pz = params["ant"][0] if isinstance(params["ant"], (list, tuple)) else params["ant"]
        export_ants(root, [pz])
    key = key_of(kind, params, D)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{sid}_{key}.mp4")
    if os.path.exists(out) and not force:
        return out
    open(os.path.join(root, "index.html"), "w", encoding="utf-8").write(build_html(kind, params, D))
    r = subprocess.run(["npx", "-y", "hyperframes", "check", "--json"], cwd=root, capture_output=True, text=True)
    try:
        d = json.loads(r.stdout[r.stdout.index("{"):])
        errs = [f"{f['code']}: {f['message'][:140]}" for k in ("layout", "lint", "runtime") for f in (d.get(k) or {}).get("findings", []) if f["severity"] == "error"]
    except Exception:
        errs = ["check 출력 해석 실패: " + r.stdout[-200:]]
    if errs:
        print(f"  ⚠ {sid} {kind} check:", errs[:3])
    tmp = os.path.join(root, "out", "tmp.mp4")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes", "render", "-o", "out/tmp.mp4", "-f", "30", "-q", quality], cwd=root, check=True, capture_output=True)
    shutil.move(tmp, out)
    return out


import hf_story  # noqa: E402  (A4 Cozy Storytelling 장면)
KINDS["story"] = hf_story.k_story
