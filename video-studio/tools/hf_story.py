"""A4 'Cozy Storytelling' 스타일 장면 (stickman-video-director 그림 문법을 코드로 직접 구현)

그림 문법: 흰 채움 둥근 머리 + 작은 검은 타원 눈 + 눈썹 선 + 짧은 입, 가는 흰 몸통(검은 외곽선),
굵기가 일정한 검은 한 줄 팔다리, 작고 둥근 검은 손·발. 배경은 풀컬러 2D 일상 공간, 장면(컷)마다 다른 장소.
캐스트: 'ant'(주인공 개미 투자자, 머리에 더듬이 = 여의도 개미) · 'smart'(스마트머니, 정장).
사용: hf_econ KINDS["story"] → params: scene=<이름>
"""
from __future__ import annotations

import math

INK = "#35303d"
PAL = dict(cream="#F6E7CB", terracotta="#D98B5F", sage="#8FB08C", dusk="#3E5C86", mustard="#E5B84B", wood="#A06B3F",
           night="#1d2540", rose="#E9A0A0", red="#DE5B41", blue="#5B93B8", gold="#F2C14E")


def _pt(x, y, ang, L):
    a = math.radians(ang)
    return x + math.sin(a) * L, y + math.cos(a) * L


POSES = {
    # (왼팔 상완각, 하완각), (오른팔), (왼다리 대퇴, 정강), (오른다리), 몸 기울임
    "stand": dict(aL=(-14, -6), aR=(14, 6), lL=(-6, 0), lR=(6, 0), tilt=0),
    "sit": dict(aL=(-20, 10), aR=(20, -10), lL=(78, 6), lR=(84, 4), tilt=0),
    "phone": dict(aL=(-30, 70), aR=(30, -70), lL=(78, 6), lR=(84, 4), tilt=4),
    "cheer": dict(aL=(-150, -165), aR=(150, 165), lL=(-14, 0), lR=(14, 0), tilt=0),
    "toast": dict(aL=(-16, -4), aR=(70, 150), lL=(-6, 0), lR=(6, 0), tilt=0),
    "hug": dict(aL=(-30, 60), aR=(30, -60), lL=(-6, 0), lR=(6, 0), tilt=0),
    "walk": dict(aL=(30, 10), aR=(-30, -10), lL=(-26, -8), lR=(26, 10), tilt=3),
    "knife": dict(aL=(-14, -6), aR=(120, 168), lL=(-8, 0), lR=(8, 0), tilt=-3),
    "think": dict(aL=(-14, -6), aR=(40, 160), lL=(-6, 0), lR=(6, 0), tilt=0),
    "arms_wide": dict(aL=(-100, -105), aR=(100, 105), lL=(-10, 0), lR=(10, 0), tilt=0),
    "wave": dict(aL=(-14, -6), aR=(135, 160), lL=(-6, 0), lR=(6, 0), tilt=0),
    "type": dict(aL=(-40, 80), aR=(40, -80), lL=(78, 6), lR=(84, 4), tilt=3),
    "smirk": dict(aL=(-30, 40), aR=(30, -40), lL=(-6, 0), lR=(6, 0), tilt=0),
}

MOUTH = {
    "smile": '<path d="M-15,18 Q0,32 15,18" fill="none" stroke="{ink}" stroke-width="4.5" stroke-linecap="round"/>',
    "flat": '<path d="M-12,22 L12,22" fill="none" stroke="{ink}" stroke-width="4.5" stroke-linecap="round"/>',
    "frown": '<path d="M-15,28 Q0,14 15,28" fill="none" stroke="{ink}" stroke-width="4.5" stroke-linecap="round"/>',
    "open": '<ellipse cx="0" cy="24" rx="10" ry="12" fill="{ink}"/>',
    "smirk": '<path d="M-14,22 Q4,30 16,16" fill="none" stroke="{ink}" stroke-width="4.5" stroke-linecap="round"/>',
    "wobble": '<path d="M-16,24 q5,-8 10,0 t10,0 t10,0" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>',
}
BROWS = {"neutral": ((-26, -22, -8, -24), (8, -24, 26, -22)), "sad": ((-26, -16, -8, -26), (8, -26, 26, -16)),
         "angry": ((-26, -26, -8, -18), (8, -18, 26, -26)), "up": ((-26, -28, -8, -30), (8, -30, 26, -28))}


def fig(who: str, x: float, y: float, s: float, pose: str = "stand", mouth: str = "smile", brows: str = "neutral",
        flip: bool = False, fid: str = "f", closed_eyes: bool = False, extra_hand_r: str = "", extra_hand_l: str = "") -> str:
    """원점 = 골반 중앙. y = 발 바닥 기준이 아니라 골반 y 좌표. 반환: SVG <g>"""
    P = POSES[pose]
    smart = who == "smart"
    sx = -1 if flip else 1
    body_fill = "#2f3a4f" if smart else "#ffffff"
    limb = INK
    out = [f'<g id="{fid}" transform="translate({x},{y}) scale({s * sx},{s})">']
    # 다리
    for side, key in ((-1, "lL"), (1, "lR")):
        a1, a2 = P[key]
        hx, hy = side * 13, -30
        kx, ky = _pt(hx, hy, a1 * side if side == 1 else a1, 54)
        fx, fy = _pt(kx, ky, a2, 52)
        out.append(f'<path d="M{hx},{hy} L{kx:.1f},{ky:.1f} L{fx:.1f},{fy:.1f}" fill="none" stroke="{limb}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<path d="M{fx:.1f},{fy:.1f} l{side * 4 + 8},0" stroke="{limb}" stroke-width="9" stroke-linecap="round"/>')
    # 몸통
    out.append(f'<path d="M-30,-112 Q-34,-60 -20,-28 L20,-28 Q34,-60 30,-112 Q0,-122 -30,-112 Z" fill="{body_fill}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    if smart:
        out.append('<path d="M-10,-114 L0,-80 L10,-114 Z" fill="#fff"/><path d="M0,-100 l-6,8 l6,34 l6,-34 z" fill="#c0392b"/>')
    else:
        out.append(f'<path d="M-8,-114 L0,-100 L8,-114" fill="none" stroke="{PAL["terracotta"]}" stroke-width="5" stroke-linecap="round"/>')
    # 팔 (어깨 = 몸통 위, 두 팔 모두 몸통 뒤/앞 순서 단순화)
    for side, key, extra in ((-1, "aL", extra_hand_l), (1, "aR", extra_hand_r)):
        a1, a2 = P[key]
        shx, shy = side * 27, -104
        ex, ey = _pt(shx, shy, a1, 50)
        hx2, hy2 = _pt(ex, ey, a2, 48)
        out.append(f'<g class="arm{"L" if side < 0 else "R"}"><path d="M{shx},{shy} L{ex:.1f},{ey:.1f} L{hx2:.1f},{hy2:.1f}" fill="none" stroke="{limb}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<circle cx="{hx2:.1f}" cy="{hy2:.1f}" r="8.5" fill="{limb}"/>{extra.replace("{hx}", f"{hx2:.1f}").replace("{hy}", f"{hy2:.1f}")}</g>')
    # 머리
    out.append('<g class="head" transform="translate(0,-160)">')
    if who == "ant":
        out.append(f'<path d="M-14,-42 Q-26,-84 -42,-92" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><circle cx="-43" cy="-93" r="6.5" fill="{INK}"/>'
                   f'<path d="M14,-42 Q26,-84 42,-92" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><circle cx="43" cy="-93" r="6.5" fill="{INK}"/>')
    out.append(f'<circle cx="0" cy="0" r="47" fill="#ffffff" stroke="{INK}" stroke-width="5"/>')
    if smart:
        out.append(f'<path d="M-46,-12 Q-40,-52 0,-50 Q40,-52 46,-12 Q30,-30 0,-30 Q-30,-30 -46,-12 Z" fill="#23293a"/>')
    bl, br = BROWS[brows]
    if smart:
        out.append(f'<rect x="-36" y="-12" width="30" height="18" rx="8" fill="#12151f"/><rect x="6" y="-12" width="30" height="18" rx="8" fill="#12151f"/><path d="M-6,-6 h12" stroke="#12151f" stroke-width="4"/>')
    else:
        if closed_eyes:
            out.append(f'<path d="M-24,-2 Q-16,6 -8,-2 M8,-2 Q16,6 24,-2" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>')
        else:
            out.append(f'<ellipse cx="-16" cy="-2" rx="4.6" ry="7" fill="{INK}"/><ellipse cx="16" cy="-2" rx="4.6" ry="7" fill="{INK}"/>')
        out.append(f'<path d="M{bl[0]},{bl[1]} L{bl[2]},{bl[3]}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/><path d="M{br[0]},{br[1]} L{br[2]},{br[3]}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    out.append(MOUTH[mouth].replace("{ink}", INK))
    out.append("</g></g>")
    return "".join(out)


# ───────────────────────── 환경 (풀컬러 2D) ─────────────────────────
def _defs():
    return ('<defs><linearGradient id="gWall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F8EAD0"/><stop offset="1" stop-color="#EBD2A8"/></linearGradient>'
            '<linearGradient id="gNight" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26305a"/><stop offset="1" stop-color="#171d3a"/></linearGradient>'
            '<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfe3f2"/><stop offset="1" stop-color="#f7ecd0"/></linearGradient>'
            '<linearGradient id="gFloor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b98558"/><stop offset="1" stop-color="#8a5c38"/></linearGradient>'
            '<radialGradient id="gLamp" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd98a" stop-opacity=".9"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="gPhone" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#7db8ff" stop-opacity=".8"/><stop offset="1" stop-color="#7db8ff" stop-opacity="0"/></radialGradient></defs>')


def env_bedroom():
    return (f'<rect width="1920" height="1080" fill="url(#gNight)"/>'
            f'<rect x="1180" y="120" width="420" height="380" rx="14" fill="#0f1530" stroke="{PAL["wood"]}" stroke-width="16"/>'
            '<circle cx="1440" cy="250" r="62" fill="#f6e9b8"/><circle cx="1462" cy="236" r="56" fill="#0f1530"/>'
            '<g fill="#f6e9b8"><circle cx="1280" cy="190" r="4"/><circle cx="1340" cy="330" r="3"/><circle cx="1530" cy="400" r="4"/><circle cx="1230" cy="420" r="3"/></g>'
            f'<rect y="760" width="1920" height="320" fill="#2c2540"/><rect x="180" y="640" width="900" height="190" rx="30" fill="{PAL["dusk"]}"/>'
            f'<rect x="180" y="610" width="900" height="70" rx="30" fill="#5a78a6"/><rect x="150" y="470" width="70" height="350" rx="20" fill="{PAL["wood"]}"/>'
            f'<rect x="1500" y="640" width="280" height="40" rx="8" fill="{PAL["wood"]}"/><rect x="1530" y="680" width="20" height="150" fill="{PAL["wood"]}"/><rect x="1730" y="680" width="20" height="150" fill="{PAL["wood"]}"/>'
            '<circle cx="1640" cy="560" r="170" fill="url(#gLamp)"/><path d="M1600,640 l20,-70 h40 l20,70 z" fill="#f2c14e"/><rect x="1632" y="640" width="16" height="0" fill="#f2c14e"/>')


def env_cafe():
    return (f'<rect width="1920" height="1080" fill="url(#gWall)"/><rect x="1100" y="110" width="640" height="420" rx="18" fill="url(#gSky)" stroke="{PAL["wood"]}" stroke-width="18"/>'
            f'<path d="M1100,320 H1740 M1420,110 V530" stroke="{PAL["wood"]}" stroke-width="10"/>'
            f'<circle cx="1300" cy="230" r="46" fill="#fff2b8" opacity=".9"/><ellipse cx="1560" cy="260" rx="90" ry="30" fill="#fff" opacity=".8"/>'
            f'<rect y="800" width="1920" height="280" fill="url(#gFloor)"/>'
            f'<rect x="80" y="520" width="520" height="30" rx="8" fill="{PAL["wood"]}"/><rect x="110" y="550" width="16" height="260" fill="{PAL["wood"]}"/><rect x="556" y="550" width="16" height="260" fill="{PAL["wood"]}"/>'
            f'<rect x="130" y="450" width="60" height="70" rx="10" fill="{PAL["terracotta"]}"/><rect x="220" y="470" width="50" height="50" rx="8" fill="{PAL["sage"]}"/>'
            f'<rect x="1280" y="660" width="460" height="26" rx="8" fill="{PAL["wood"]}"/><rect x="1480" y="686" width="22" height="130" fill="{PAL["wood"]}"/>'
            f'<rect x="1390" y="610" width="48" height="50" rx="8" fill="#fff"/><path d="M1438,625 q22,8 0,26" fill="none" stroke="#fff" stroke-width="7"/>'
            f'<path d="M80,800 q10,-110 -10,-180 q60,40 52,180 z" fill="{PAL["sage"]}"/><rect x="60" y="780" width="80" height="60" rx="10" fill="{PAL["terracotta"]}"/>'
            '<circle cx="960" cy="420" r="320" fill="url(#gLamp)" opacity=".35"/>')


def env_street():
    return (f'<rect width="1920" height="1080" fill="url(#gSky)"/>'
            f'<g><rect x="120" y="260" width="360" height="560" fill="#d9a77a"/><rect x="520" y="180" width="300" height="640" fill="#c98d6c"/><rect x="1300" y="220" width="320" height="600" fill="#cfa77f"/><rect x="1640" y="320" width="260" height="500" fill="#b97f62"/></g>'
            '<g fill="#fdf1c9"><rect x="160" y="310" width="60" height="70"/><rect x="260" y="310" width="60" height="70"/><rect x="160" y="420" width="60" height="70"/><rect x="560" y="240" width="60" height="70"/><rect x="660" y="240" width="60" height="70"/><rect x="1340" y="280" width="60" height="70"/><rect x="1440" y="280" width="60" height="70"/></g>'
            f'<rect y="800" width="1920" height="280" fill="#8d8d93"/><rect y="800" width="1920" height="16" fill="#b9b9be"/><g fill="#f0ede3"><rect x="140" y="940" width="160" height="14"/><rect x="520" y="940" width="160" height="14"/><rect x="900" y="940" width="160" height="14"/><rect x="1280" y="940" width="160" height="14"/></g>'
            f'<path d="M860,420 h360 l30,90 h-420 z" fill="{PAL["red"]}"/><rect x="880" y="510" width="320" height="290" fill="#e9d6b0"/><rect x="930" y="560" width="100" height="240" fill="#6b4b36"/>')


def env_livingroom():
    return (f'<rect width="1920" height="1080" fill="url(#gWall)"/><rect y="790" width="1920" height="290" fill="url(#gFloor)"/>'
            f'<rect x="1380" y="150" width="360" height="300" rx="10" fill="#fff" stroke="{PAL["wood"]}" stroke-width="14"/>'
            f'<g transform="translate(1440,180) scale(.9)"><path d="M0,200 L80,120 L140,170 L240,60" fill="none" stroke="{PAL["red"]}" stroke-width="10"/></g>'
            f'<rect x="130" y="180" width="140" height="180" rx="8" fill="#fff" stroke="{PAL["wood"]}" stroke-width="10"/><circle cx="200" cy="250" r="30" fill="#f1e1c3" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="330" y="200" width="130" height="160" rx="8" fill="#fff" stroke="{PAL["wood"]}" stroke-width="10"/><circle cx="395" cy="265" r="28" fill="#f1e1c3" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="1260" y="640" width="520" height="190" rx="40" fill="{PAL["terracotta"]}"/><rect x="1260" y="560" width="520" height="130" rx="40" fill="#e9a785"/>'
            f'<rect x="560" y="780" width="800" height="40" rx="20" fill="#7b9c7d" opacity=".5"/><circle cx="960" cy="400" r="380" fill="url(#gLamp)" opacity=".28"/>')


def env_office(screen=True, monitor=True):
    return (f'<rect width="1920" height="1080" fill="#EFE0C0"/><rect y="800" width="1920" height="280" fill="#cba77d"/>'
            f'<rect x="1240" y="150" width="540" height="330" rx="14" fill="#e8f2f7" stroke="{PAL["wood"]}" stroke-width="14"/><path d="M1240,480 L1780,150" stroke="{PAL["wood"]}" stroke-width="8" opacity=".5"/>'
            f'<rect x="120" y="610" width="1100" height="34" rx="10" fill="{PAL["wood"]}"/><rect x="170" y="644" width="26" height="190" fill="{PAL["wood"]}"/><rect x="1130" y="644" width="26" height="190" fill="{PAL["wood"]}"/>'
            + (f'<rect x="680" y="300" width="520" height="310" rx="18" fill="#232a3a" stroke="#4b536b" stroke-width="10"/>' if monitor else '')
            + ('<g transform="translate(700,320)"><rect width="480" height="270" rx="8" fill="#10161f"/>'
               f'<path d="M20,210 L100,150 L160,185 L240,95 L320,120 L440,40" fill="none" stroke="{PAL["red"]}" stroke-width="8" stroke-linejoin="round"/>'
               f'<path d="M20,70 L110,90 L180,130 L260,190 L340,170 L440,235" fill="none" stroke="{PAL["blue"]}" stroke-width="8" stroke-linejoin="round"/></g>' if (screen and monitor) else '')
            + f'<circle cx="1000" cy="460" r="300" fill="url(#gLamp)" opacity=".2"/>')


def env_meadow():
    return (f'<rect width="1920" height="1080" fill="url(#gSky)"/><circle cx="1560" cy="200" r="90" fill="#fff0a8"/>'
            f'<path d="M0,700 Q420,560 900,680 T1920,640 V1080 H0 Z" fill="#a6c98b"/><path d="M0,830 Q500,740 1000,820 T1920,790 V1080 H0 Z" fill="#8fb878"/>'
            f'<rect x="1380" y="560" width="220" height="190" fill="#c98d6c"/><path d="M1360,570 L1490,470 L1620,570 Z" fill="{PAL["red"]}"/><rect x="1450" y="640" width="70" height="110" fill="#6b4b36"/>'
            f'<g fill="#fff" opacity=".85"><ellipse cx="400" cy="190" rx="110" ry="36"/><ellipse cx="520" cy="170" rx="80" ry="30"/><ellipse cx="1100" cy="260" rx="120" ry="34"/></g>')


def env_vault():
    return (f'<rect width="1920" height="1080" fill="#3a2a22"/><rect x="360" y="150" width="1200" height="660" rx="10" fill="#8a5a3a"/>'
            f'<g stroke="#6a4129" stroke-width="10"><path d="M360,300 H1560 M360,450 H1560 M360,600 H1560"/><path d="M660,150 V810 M960,150 V810 M1260,150 V810"/></g>'
            f'<rect x="420" y="210" width="530" height="600" fill="#2a1d17"/><rect x="970" y="210" width="530" height="600" fill="#2a1d17"/>'
            f'<g fill="{PAL["gold"]}"><ellipse cx="690" cy="780" rx="230" ry="46"/><ellipse cx="1240" cy="780" rx="240" ry="50"/></g>'
            '<g fill="#fff0a0" opacity=".9"><circle cx="600" cy="740" r="16"/><circle cx="690" cy="715" r="16"/><circle cx="780" cy="745" r="16"/><circle cx="1180" cy="735" r="16"/><circle cx="1280" cy="715" r="16"/><circle cx="1360" cy="745" r="16"/></g>'
            f'<rect y="810" width="1920" height="270" fill="#5b3d2b"/><circle cx="960" cy="520" r="420" fill="url(#gLamp)" opacity=".4"/>')


ENVS = dict(bedroom=env_bedroom, cafe=env_cafe, street=env_street, livingroom=env_livingroom, office=env_office, office_off=lambda: env_office(False, False), meadow=env_meadow, vault=env_vault)


# ───────────────────────── 소품 ─────────────────────────
def prop_phone(x, y, rot=0, col="#5B93B8", label="−31%"):
    return (f'<g transform="translate({x},{y}) rotate({rot})"><circle cx="0" cy="0" r="150" fill="url(#gPhone)" opacity=".9"/>'
            f'<rect x="-34" y="-58" width="68" height="116" rx="12" fill="#22262f"/><rect x="-28" y="-50" width="56" height="98" rx="8" fill="{col}"/>'
            f'<text x="0" y="6" text-anchor="middle" font-family="PBlack" font-size="20" fill="#fff">{label}</text></g>')


def prop_goose(x, y, s=1.0, sweat=True):
    return (f'<g transform="translate({x},{y}) scale({s})"><ellipse cx="0" cy="0" rx="110" ry="70" fill="#fff" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M80,-30 Q130,-90 100,-150" fill="none" stroke="#fff" stroke-width="34" stroke-linecap="round"/><path d="M80,-30 Q130,-90 100,-150" fill="none" stroke="{INK}" stroke-width="5" opacity=".0"/>'
            f'<circle cx="104" cy="-160" r="30" fill="#fff" stroke="{INK}" stroke-width="5"/><path d="M128,-158 l36,10 l-36,12 z" fill="{PAL["mustard"]}" stroke="{INK}" stroke-width="3"/>'
            f'<circle cx="112" cy="-168" r="5" fill="{INK}"/><path d="M-30,-10 q50,-60 90,10 q-50,40 -90,-10" fill="#f1eadb" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M-60,66 v40 M-10,70 v40" stroke="{PAL["mustard"]}" stroke-width="9" stroke-linecap="round"/>'
            + ('<path d="M150,-210 q8,16 0,26" fill="#8ad0f0" stroke="#8ad0f0" stroke-width="8" stroke-linecap="round"/>' if sweat else '') + '</g>')


def prop_egg(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><ellipse cx="0" cy="0" rx="26" ry="34" fill="{PAL["gold"]}" stroke="#b8872b" stroke-width="4"/><path d="M-10,-12 q6,-10 14,-8" stroke="#fff6c4" stroke-width="5" fill="none" stroke-linecap="round"/></g>'


def prop_knife(hx, hy):
    return f'<g transform="translate({hx},{hy}) rotate(-35)"><rect x="-6" y="-8" width="12" height="40" rx="5" fill="{PAL["wood"]}"/><path d="M-9,-8 L0,-92 L9,-8 Z" fill="#dfe6ea" stroke="{INK}" stroke-width="3"/></g>'


def prop_scroll(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><rect x="-120" y="-80" width="240" height="160" rx="10" fill="#fff6dc" stroke="{PAL["wood"]}" stroke-width="8"/>'
            f'<path d="M-90,50 L-50,10 L-10,30 L40,-30 L90,-50" fill="none" stroke="{PAL["blue"]}" stroke-width="9" stroke-linejoin="round"/>'
            f'<rect x="-132" y="-92" width="22" height="184" rx="10" fill="{PAL["wood"]}"/><rect x="110" y="-92" width="22" height="184" rx="10" fill="{PAL["wood"]}"/></g>')


def prop_laptop(x, y, glow=True, screen="#9fd0ff"):
    return (f'<g transform="translate({x},{y})">' + (f'<circle cx="0" cy="-90" r="200" fill="url(#gPhone)" opacity=".5"/>' if glow else '') +
            f'<rect x="-120" y="-150" width="240" height="150" rx="10" fill="#2a2f3b"/><rect x="-108" y="-140" width="216" height="128" rx="6" fill="{screen}"/>'
            f'<path d="M-90,-34 L-50,-70 L-10,-52 L40,-110 L90,-90" fill="none" stroke="{PAL["red"]}" stroke-width="6" stroke-linejoin="round"/><rect x="-150" y="0" width="300" height="16" rx="8" fill="#c9ced6"/></g>')


def prop_magnifier(x, y, rot=-30):
    return f'<g transform="translate({x},{y}) rotate({rot})"><circle cx="0" cy="-34" r="34" fill="#cfe9f5" fill-opacity=".6" stroke="{INK}" stroke-width="6"/><rect x="-5" y="0" width="10" height="56" rx="5" fill="{PAL["wood"]}"/></g>'


def prop_coin(x, y, r=20):
    return f'<g transform="translate({x},{y})"><circle r="{r}" fill="{PAL["gold"]}" stroke="#b8872b" stroke-width="4"/><text y="{r * .38:.0f}" text-anchor="middle" font-family="PBlack" font-size="{r * 1.1:.0f}" fill="#b8872b">₩</text></g>'


def prop_cup(hx, hy):
    return f'<g transform="translate({hx},{hy})"><rect x="-16" y="-34" width="32" height="34" rx="6" fill="#fff" stroke="{INK}" stroke-width="4"/><path d="M16,-26 q16,6 0,18" fill="none" stroke="{INK}" stroke-width="4"/></g>'


# ───────────────────────── 장면 사전 ─────────────────────────
def build(name: str, S, p: dict):
    """반환: (svg 본문, 추가 JS). S는 hf_econ.Scene (id 생성용)"""
    js = []
    A = lambda s: S.id(s)

    def sway(fid, amp=6, per=2.2):
        js.append(f'tl.to("#{fid}",{{y:"+={amp}",duration:{per / 2:.2f},ease:"sine.inOut",yoyo:true,repeat:{max(1, int(S.D / per))}}},0.3);')

    def appear(sel, t=0.3, y=30):
        js.append(f'tl.fromTo("{sel}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:.6,ease:"power3.out"}},{t:.2f});')

    env = ""
    body = ""
    d = _defs()
    if name == "bed_phone":
        env = env_bedroom()
        f1 = A("fg")
        body += fig("ant", 520, 678, 1.95, "phone", "frown", "sad", fid=f1)
        body += prop_phone(640, 520, 8, PAL["blue"], "−31%").replace('r="150"', 'r="230"')
        sg = A("sigh")
        body += f'<g id="{sg}"><circle cx="760" cy="330" r="14" fill="#fff" opacity=".8"/><circle cx="810" cy="290" r="22" fill="#fff" opacity=".8"/><ellipse cx="900" cy="230" rx="86" ry="52" fill="#fff" opacity=".85"/><text x="900" y="246" text-anchor="middle" font-family="PBlack" font-size="52" fill="{INK}">후…</text></g>'
        sway(f1, 5, 2.6)
        js.append(f'tl.fromTo("#{sg}",{{opacity:0,y:30}},{{opacity:1,y:-30,duration:1.6,ease:"sine.out"}},{S.t0 + 0.6:.2f});')
    elif name == "cheers":
        env = env_cafe()
        f1 = A("fg")
        body += fig("ant", 900, 700, 1.95, "toast", "smirk", "up", fid=f1, extra_hand_r=prop_cup("{hx}", "{hy}"))
        conf = "".join(f'<rect id="cf{i}" x="{110 + i * 71 % 1700}" y="-40" width="14" height="22" rx="3" fill="{[PAL["red"], PAL["gold"], PAL["blue"], PAL["sage"], PAL["rose"]][i % 5]}" transform="rotate({i * 37 % 90})"/>' for i in range(26))
        body += conf
        for i in range(26):
            js.append(f'tl.fromTo("#cf{i}",{{y:-60}},{{y:{900 + i * 13 % 160},rotation:{(i * 53) % 360},duration:{2.2 + (i % 5) * .3:.2f},ease:"sine.in"}},{0.3 + (i % 9) * .22:.2f});')
        sway(f1, 4, 2.0)
    elif name == "market_sucker":
        env = env_street()
        f1, f2 = A("fa"), A("fs")
        body += fig("ant", 560, 700, 1.95, "walk", "smile", "up", fid=f1, extra_hand_l=f'<g transform="translate({{hx}},{{hy}})"><path d="M-22,0 q-6,46 22,56 q28,-10 22,-56 z" fill="{PAL["sage"]}" stroke="{INK}" stroke-width="4"/><text y="38" text-anchor="middle" font-family="PBlack" font-size="30" fill="#fff">₩</text></g>')
        body += fig("smart", 1520, 700, 1.95, "smirk", "smirk", "angry", flip=True, fid=f2)
        js.append(f'tl.fromTo("#{f1}",{{x:260}},{{x:560,duration:{max(1.5, S.W):.2f},ease:"power1.out"}},0.2);')
        js.append(f'tl.fromTo("#{f2}",{{opacity:0}},{{opacity:1,duration:.6}},0.6);')
        sway(f2, 4, 2.4)
    elif name == "heirloom":
        env = env_livingroom()
        f1 = A("fg")
        body += fig("ant", 700, 700, 1.95, "hug", "wobble", "sad", fid=f1)
        body += f'<g id="{A("sc")}">{prop_scroll(760, 560, 0.95)}</g>'
        sway(f1, 4, 3.0)
    elif name == "cheer_sell":
        env = env_office()
        f1 = A("fg")
        body += fig("ant", 1450, 700, 1.95, "cheer", "open", "up", fid=f1)
        for i in range(10):
            body += f'<g id="cn{i}">{prop_coin(1300 + (i * 61) % 340, 300, 22)}</g>'
            js.append(f'tl.fromTo("#cn{i}",{{y:-40,opacity:0}},{{y:{330 + (i * 29) % 160},opacity:1,duration:.9,ease:"bounce.out"}},{0.3 + i * .18:.2f});')
        js.append(f'tl.to("#{f1}",{{y:"-=34",duration:.35,ease:"power2.out",yoyo:true,repeat:{max(3, int(S.D / .7))}}},0.3);')
    elif name == "goose":
        env = env_meadow()
        f1 = A("fg")
        body += fig("ant", 620, 700, 1.95, "knife", "wobble", "sad", fid=f1, extra_hand_r=prop_knife("{hx}", "{hy}"))
        body += f'<g id="{A("gs")}">{prop_goose(1250, 740, 1.3)}</g>'
        body += f'<g id="eg">{prop_egg(1010, 830, 1.1)}</g><g id="eg2">{prop_egg(1100, 850, 0.9)}</g>'
        js.append('tl.fromTo("#eg",{y:-30,opacity:0},{y:0,opacity:1,duration:.5,ease:"bounce.out"},0.5);tl.fromTo("#eg2",{y:-30,opacity:0},{y:0,opacity:1,duration:.5,ease:"bounce.out"},1.0);')
        sway(f1, 5, 1.2)
    elif name == "charity":
        env = env_cafe()
        f1 = A("fs")
        body += fig("smart", 940, 700, 1.95, "arms_wide", "smirk", "angry", fid=f1)
        sg = A("sign")
        body += f'<g id="{sg}" transform="translate(1450,600)"><rect x="-130" y="-90" width="260" height="180" rx="14" fill="#fff" stroke="{INK}" stroke-width="6"/><text y="-8" text-anchor="middle" font-family="PBlack" font-size="52" fill="{INK}">자선</text><text y="52" text-anchor="middle" font-family="PBlack" font-size="52" fill="{INK}">사업</text><path d="M-130,-90 L130,90 M130,-90 L-130,90" stroke="{PAL["red"]}" stroke-width="16" stroke-linecap="round"/></g>'
        js.append(f'tl.fromTo("#{sg}",{{opacity:0,scale:.4,svgOrigin:"1450 600"}},{{opacity:1,scale:1,duration:.6,ease:"back.out(2)"}},0.5);')
        sway(f1, 4, 2.2)
    elif name == "vault":
        env = env_vault()
        f1 = A("fs")
        body += fig("smart", 960, 700, 2.05, "arms_wide", "smile", "up", fid=f1)
        for i in range(12):
            body += f'<g id="vc{i}">{prop_coin(160 + (i * 37) % 120, 560, 20)}</g>'
            js.append(f'tl.fromTo("#vc{i}",{{x:0,opacity:0}},{{x:{520 + (i * 23) % 120},y:{(i % 3) * 18},opacity:1,duration:1.4,ease:"power1.inOut"}},{0.2 + i * .28:.2f});')
        sway(f1, 4, 2.0)
    elif name == "hacked":
        env = env_office(False, False)
        f1 = A("fg")
        body += prop_laptop(800, 612, True, "#112018")
        rain = "".join(f'<text id="bn{i}" x="{720 + (i * 41) % 420}" y="520" font-family="monospace" font-size="26" fill="#6bff9a" opacity="0">{"0110 1001 1100"[(i % 4) * 3:(i % 4) * 3 + 3]}</text>' for i in range(14))
        body += rain
        body += fig("ant", 520, 690, 1.95, "type", "open", "sad", fid=f1)
        for i in range(14):
            js.append(f'tl.fromTo("#bn{i}",{{y:60,opacity:0}},{{y:{-160 - (i * 17) % 80},opacity:.9,duration:1.6,ease:"none"}},{0.3 + i * .15:.2f});')
        sway(f1, 3, 1.6)
    elif name == "check_account":
        env = env_office()
        f1 = A("fg")
        body += fig("ant", 560, 700, 1.95, "think", "flat", "neutral", fid=f1, extra_hand_r=prop_magnifier("{hx}", "{hy}", -20))
        sway(f1, 4, 2.6)
    elif name == "wave":
        env = env_cafe()
        f1 = A("fg")
        body += fig("ant", 960, 700, 1.95, "wave", "smile", "up", fid=f1)
        for i in range(8):
            body += f'<text id="ht{i}" x="{1080 + i * 52}" y="470" font-size="44" fill="{PAL["red"]}" opacity="0">♥</text>'
            js.append(f'tl.fromTo("#ht{i}",{{y:0,opacity:0}},{{y:-120,opacity:1,duration:1.4,ease:"sine.out"}},{0.4 + i * .3:.2f});')
        js.append(f'tl.to("#{f1} .armR",{{rotation:18,svgOrigin:"1013 {700 - 104 * 1.95:.0f}",duration:.4,yoyo:true,repeat:{max(3, int(S.D / .8))},ease:"sine.inOut"}},0.4);')
        sway(f1, 4, 2.4)
    else:
        raise KeyError(name)
    return f'<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">{d}{env}{body}</svg>', "\n".join(js)


def k_story(S, p):
    return build(p["scene"], S, p)
