# -*- coding: utf-8 -*-
"""수율 애니메이션(롱폼·쇼츠 공용): 저울 위 생선 1kg → 머리·뼈·껍질·내장이 빠짐 → 접시 위 회 ○g
부위별 무게는 출처가 없어 숫자로 보여 주지 않는다(처음 1kg과 마지막 회 무게만)."""
GOLD, GOLD2, IVORY, MUTE, UP, INK = "#D6B26E", "#F1D9A0", "#F2EDE3", "#8C919B", "#E4775F", "#0D0E11"


def svg(P, fish="광어"):
    """viewBox 0 0 900 620 — 위: 생선(저울 판 위), 아래: 접시"""
    return f'''<svg width="100%" height="100%" viewBox="0 0 900 620" style="overflow:visible">
<defs><radialGradient id="{P}fl" cx="50%" cy="45%" r="60%"><stop offset="0" stop-color="#F7C9B8"/><stop offset="1" stop-color="#E59A86"/></radialGradient>
<linearGradient id="{P}sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7A6A4E"/><stop offset="1" stop-color="#4C4232"/></linearGradient></defs>
<rect x="80" y="300" width="740" height="20" rx="6" fill="{GOLD}"/><path d="M200 320 L700 320 L740 380 L160 380 Z" fill="#1C1F25" stroke="{GOLD}55"/>
<g id="{P}flesh"><ellipse cx="470" cy="200" rx="250" ry="92" fill="url(#{P}fl)"/>
 <g stroke="#fff" stroke-opacity=".35" stroke-width="3">{"".join(f'<path d="M{x} 125 q18 75 0 150" fill="none"/>' for x in range(300, 680, 48))}</g></g>
<g id="{P}guts"><ellipse cx="335" cy="232" rx="46" ry="30" fill="#7E3B33"/><ellipse cx="362" cy="246" rx="26" ry="16" fill="#9C4C3E"/></g>
<g id="{P}skin"><ellipse cx="470" cy="200" rx="252" ry="95" fill="url(#{P}sk)"/>{"".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#3A3226" opacity=".7"/>' for x, y in [(380, 170), (450, 230), (520, 160), (590, 220), (640, 180), (420, 205), (560, 195)])}</g>
<g id="{P}bone"><path d="M710 200 L800 140 L790 200 L800 260 Z" fill="#C9C2B2"/>
 <path d="M300 112 Q470 70 690 150 L690 162 Q470 92 300 128 Z" fill="#C9C2B2" opacity=".9"/><path d="M300 288 Q470 330 690 250 L690 238 Q470 308 300 272 Z" fill="#C9C2B2" opacity=".9"/>
 <line x1="300" y1="200" x2="720" y2="200" stroke="#E8E2D4" stroke-width="9"/>{"".join(f'<line x1="{x}" y1="200" x2="{x + 34}" y2="{y}" stroke="#E8E2D4" stroke-width="4"/>' for x in range(330, 700, 40) for y in (128, 272))}</g>
<g id="{P}head"><path d="M300 200 C300 120 250 105 205 130 C170 150 160 185 160 200 C160 215 170 250 205 270 C250 295 300 280 300 200 Z" fill="#5E5240"/>
 <circle cx="225" cy="172" r="15" fill="#F2EDE3"/><circle cx="228" cy="172" r="8" fill="#111"/><path d="M168 205 q14 8 28 0" stroke="#2A241B" stroke-width="5" fill="none"/></g>
<g font-family="PXB,PX" font-weight="800" font-size="46" text-anchor="middle">
 <text id="{P}lh" x="150" y="80" fill="{UP}" opacity="0">− 머리</text><text id="{P}lb" x="760" y="80" fill="{UP}" opacity="0">− 뼈·지느러미</text>
 <text id="{P}ls" x="470" y="60" fill="{UP}" opacity="0">− 껍질·내장</text></g>
<g id="{P}plate" opacity="0"><ellipse cx="450" cy="520" rx="300" ry="70" fill="#E9E4DA"/><ellipse cx="450" cy="512" rx="250" ry="52" fill="#F7F4EE"/>
 {"".join(f'<path d="M{x} 520 q35 -40 70 -8 q-35 10 -70 8 Z" fill="#F4B7A3" stroke="#fff" stroke-width="3" transform="rotate({-12 + k * 3} {x + 35} 505)"/>' for k, x in enumerate(range(250, 600, 52)))}</g>
</svg>'''


def html(P, left, top, width, fish="광어", y=0.40, start_kg="1kg", end_g="400g"):
    h = width * 620 / 900
    return (f'<div id="{P}yf" style="position:absolute;left:{left}px;top:{top}px;width:{width}px;height:{h:.0f}px">{svg(P, fish)}'
            f'<div id="{P}wt" style="position:absolute;left:0;right:0;top:{h * 0.62:.0f}px;text-align:center"><span class="num" style="font-size:{width * 0.075:.0f}px;color:{GOLD2};background:#0A0B0D;border:3px solid {GOLD};padding:4px 26px">{fish} {start_kg}</span></div>'
            f'<div id="{P}rs" style="position:absolute;left:0;right:0;top:{h * 0.12:.0f}px;text-align:center;opacity:0"><span class="num" style="font-size:{width * 0.13:.0f}px;color:{IVORY};text-shadow:0 6px 24px #000">회 {end_g}</span></div></div>')


def js(P, t):
    """t: dict(show, head, bone, skin, plate) — 초. 각 부위가 빠지면서 라벨이 뜬다"""
    q = lambda s: f'document.getElementById("{P}{s}")'
    return (f'tl.fromTo({q("yf")}, {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5 }}, {t["show"]});'
            f'tl.to({q("head")}, {{ x: -120, y: 160, rotation: -25, opacity: 0, duration: 0.7, ease: "power2.in" }}, {t["head"]}); tl.fromTo({q("lh")}, {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, {t["head"]});'
            f'tl.to({q("bone")}, {{ x: 140, y: 170, opacity: 0, duration: 0.7, ease: "power2.in" }}, {t["bone"]}); tl.fromTo({q("lb")}, {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, {t["bone"]});'
            f'tl.to([{q("skin")}, {q("guts")}], {{ y: -140, opacity: 0, duration: 0.7, ease: "power2.in" }}, {t["skin"]}); tl.fromTo({q("ls")}, {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, {t["skin"]});'
            f'tl.to([{q("lh")}, {q("lb")}, {q("ls")}, {q("wt")}], {{ opacity: 0, duration: 0.3 }}, {t["plate"]});'
            f'tl.to({q("flesh")}, {{ scale: 0.55, y: 300, transformOrigin: "50% 50%", opacity: 0, duration: 0.6, ease: "power2.in" }}, {t["plate"]});'
            f'tl.fromTo({q("plate")}, {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {t["plate"]} + 0.45);'
            f'tl.fromTo({q("rs")}, {{ opacity: 0, scale: 1.4 }}, {{ opacity: 1, scale: 1, duration: 0.45, ease: "back.out(2)" }}, {t["plate"]} + 0.6);')
