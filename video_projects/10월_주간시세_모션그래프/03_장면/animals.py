# -*- coding: utf-8 -*-
"""품종별 SVG 모형 (viewBox 0 0 400 240, 오른쪽을 보고 있음) + 활어 전용 움직임(JS).
 - 활어: 꼬리·지느러미·몸이 계속 움직이고 수조 안을 왔다 갔다 한다.
 - 선어: 움직임 코드를 아예 만들지 않는다(정지).
모든 id는 접두어 P로 시작해 장면마다 겹치지 않는다.
"""

def _grad(P, name, c1, c2, vertical=True):
    return f'<linearGradient id="{P}{name}" x1="0" y1="0" x2="{0 if vertical else 1}" y2="{1 if vertical else 0}"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'


def fish(P, H=70, top="#c9d3da", belly="#f3f6f8", fin="#8a97a1", stripes=(), spots=(), tail="fork", body_dark="#00000022",
         eye="#ffffff", back_spots=0, snout=0.62, dorsal=True, long_body=False, lines=False):
    cy = 120; Hb = H * 0.92
    top_p = f"M 360 {cy} C 346 {cy - snout * H:.1f}, 300 {cy - H:.1f}, 238 {cy - H:.1f} C 178 {cy - H:.1f}, 132 {cy - 16}, 96 {cy - 13}"
    bot_p = f"L 96 {cy + 13} C 132 {cy + 16}, 178 {cy + Hb:.1f}, 238 {cy + Hb:.1f} C 300 {cy + Hb:.1f}, 346 {cy + snout * Hb:.1f}, 360 {cy} Z"
    body = f"{top_p} {bot_p}"
    if tail == "fork":
        tl = f'M 100 {cy - 14} L 22 {cy - 58} Q 52 {cy} 22 {cy + 58} L 100 {cy + 14} Z'
    elif tail == "round":
        tl = f'M 100 {cy - 14} C 60 {cy - 52}, 22 {cy - 40}, 26 {cy} C 22 {cy + 40}, 60 {cy + 52}, 100 {cy + 14} Z'
    else:  # lunate (고등어·삼치)
        tl = f'M 100 {cy - 12} L 30 {cy - 66} Q 62 {cy} 30 {cy + 66} L 100 {cy + 12} Z'
    s = [f'<defs>{_grad(P, "g", top, belly)}<clipPath id="{P}clip"><path d="{body}"/></clipPath></defs>']
    s.append(f'<g id="{P}tail"><path d="{tl}" fill="{fin}"/></g>')
    if dorsal:
        s.append(f'<g id="{P}dorsal"><path d="M 170 {cy - H + 6:.1f} Q 215 {cy - H - 42:.1f} 280 {cy - H + 5:.1f} Z" fill="{fin}"/></g>')
    s.append(f'<path d="M 190 {cy + Hb - 4:.1f} Q 220 {cy + Hb + 30:.1f} 262 {cy + Hb - 3:.1f} Z" fill="{fin}"/>')
    s.append(f'<g id="{P}body"><path d="{body}" fill="url(#{P}g)"/>')
    s.append(f'<g clip-path="url(#{P}clip)">')
    for x, w, c, o in stripes: s.append(f'<rect x="{x}" y="0" width="{w}" height="240" fill="{c}" opacity="{o}" transform="skewX(-8)"/>')
    for i in range(back_spots):
        s.append(f'<circle cx="{150 + i * 23}" cy="{cy - H * 0.55 + (i % 3) * 9:.1f}" r="{3.2 + (i % 2)}" fill="{spots[0] if spots else "#fff"}" opacity=".85"/>')
    if lines:
        for k in range(3): s.append(f'<path d="M 120 {cy - 20 + k * 15} Q 240 {cy - 26 + k * 15} 350 {cy - 8 + k * 11}" stroke="#ffffff" stroke-width="3" fill="none" opacity=".22"/>')
    s.append(f'<ellipse cx="250" cy="{cy - H * 0.62:.1f}" rx="92" ry="{H * 0.17:.1f}" fill="#fff" opacity=".2"/>')
    s.append('</g></g>')
    s.append(f'<path d="M 296 {cy - H * 0.7:.1f} Q 284 {cy} 296 {cy + Hb * 0.7:.1f}" stroke="#00000033" stroke-width="4" fill="none"/>')
    s.append(f'<g id="{P}fin"><path d="M 286 {cy + 8} Q 262 {cy + 30} 244 {cy + 38} Q 266 {cy + 18} 286 {cy + 8} Z" fill="{fin}" opacity=".95"/></g>')
    s.append(f'<circle cx="326" cy="{cy - H * 0.16:.1f}" r="9.5" fill="{eye}"/><circle cx="328" cy="{cy - H * 0.16:.1f}" r="5" fill="#11161b"/>')
    s.append(f'<path d="M 357 {cy + 2} Q 346 {cy + 6} 338 {cy + 2}" stroke="#00000055" stroke-width="3" fill="none" stroke-linecap="round"/>')
    return "".join(s)


def flatfish(P):  # 넙치(광어): 위에서 본 납작한 몸, 눈 두 개가 한쪽에
    s = [f'<defs>{_grad(P, "g", "#9b8366", "#6f5a40")}<clipPath id="{P}clip"><path id="{P}bodyclip" d="M 360 128 C 340 70, 270 44, 200 46 C 130 48, 78 80, 66 122 C 78 168, 130 196, 200 198 C 270 200, 340 176, 360 128 Z"/></clipPath></defs>']
    s.append(f'<g id="{P}body"><path d="M 372 126 C 346 62, 270 34, 200 36 C 126 38, 66 74, 54 122 C 66 172, 126 204, 200 206 C 270 208, 346 184, 372 126 Z" fill="#7d6849" opacity=".9"/>')
    s.append(f'<path d="M 360 128 C 340 70, 270 44, 200 46 C 130 48, 78 80, 66 122 C 78 168, 130 196, 200 198 C 270 200, 340 176, 360 128 Z" fill="url(#{P}g)"/>')
    s.append(f'<g clip-path="url(#{P}clip)">')
    import random; r = random.Random(7)
    for _ in range(26): s.append(f'<circle cx="{r.randint(80, 340)}" cy="{r.randint(60, 190)}" r="{r.randint(4, 11)}" fill="{r.choice(["#d9c7a3", "#4e3f2b", "#b79f78"])}" opacity=".55"/>')
    s.append('</g>')
    s.append(f'<g id="{P}tail"><path d="M 70 122 L 30 98 Q 44 122 30 146 Z" fill="#7d6849"/></g></g>')
    s.append('<circle cx="320" cy="104" r="10" fill="#fff"/><circle cx="322" cy="104" r="5.5" fill="#11161b"/><circle cx="338" cy="122" r="9" fill="#fff"/><circle cx="340" cy="122" r="5" fill="#11161b"/>')
    s.append('<path d="M 366 138 Q 352 144 344 138" stroke="#00000066" stroke-width="3" fill="none" stroke-linecap="round"/>')
    return "".join(s)


def ribbon(P):  # 은갈치: 길고 납작한 은빛 리본
    s = [f'<defs>{_grad(P, "g", "#dfe8ee", "#aebdc7")}</defs>']
    path = "M 30 168 C 90 104, 150 206, 214 142 S 316 92, 352 122"
    s.append(f'<path d="{path}" stroke="#8fa2af" stroke-width="40" fill="none" stroke-linecap="round" opacity=".55" transform="translate(0,5)"/>')
    s.append(f'<path d="{path}" stroke="url(#{P}g)" stroke-width="36" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="{path}" stroke="#ffffff" stroke-width="9" fill="none" stroke-linecap="round" opacity=".7" transform="translate(0,-7)"/>')
    s.append('<path d="M 340 108 L 392 122 L 346 138 Z" fill="#c4d1da"/><path d="M 392 122 L 372 126 L 380 120 Z" fill="#7a8a95"/>')
    s.append('<circle cx="352" cy="118" r="9" fill="#fff"/><circle cx="354" cy="118" r="5" fill="#11161b"/>')
    s.append(f'<path d="M 40 160 C 100 98, 160 198, 214 134 S 318 84, 342 108" stroke="#6f8290" stroke-width="3" fill="none" opacity=".6"/>')
    return "".join(s)


def crab(P, body="#e2553a", dark="#b83a25", king=False, spiky=True, spot="#ffffff"):
    legs = []
    L = 4
    for side in (-1, 1):
        for i in range(L):
            y0 = 128 + i * 14 - (0 if king else 2)
            ln = (118 if king else 104) - i * 6
            ang = side * (-12 + i * 12)
            legs.append(f'<g id="{P}leg{"R" if side > 0 else "L"}{i}"><path d="M {200 + side * 58} {y0} L {200 + side * (58 + ln * 0.55):.0f} {y0 - 26} L {200 + side * (58 + ln):.0f} {y0 + 24}" stroke="{dark}" stroke-width="{9 if king else 8}" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>')
    s = ["<defs>" + _grad(P, "g", body, dark) + "</defs>"]
    s.append(f'<g id="{P}legs">{"".join(legs)}</g>')
    for side, nm in ((-1, "L"), (1, "R")):
        cx = 200 + side * 62
        s.append(f'<g id="{P}claw{nm}"><path d="M {200 + side * 40} 96 L {cx + side * 14} 62" stroke="{dark}" stroke-width="12" stroke-linecap="round"/>'
                 f'<path d="M {cx + side * 14} 62 C {cx + side * 44} 22, {cx + side * 70} 44, {cx + side * 50} 78 C {cx + side * 34} 64, {cx + side * 22} 70, {cx + side * 14} 62 Z" fill="{body}" stroke="{dark}" stroke-width="3"/></g>')
    if king:
        car = "M 200 56 L 262 84 L 276 140 L 240 186 L 200 196 L 160 186 L 124 140 L 138 84 Z"
    else:
        car = "M 200 74 C 240 68, 280 84, 322 100 L 292 124 C 288 158, 252 184, 200 186 C 148 184, 112 158, 108 124 L 78 100 C 120 84, 160 68, 200 74 Z"
    s.append(f'<g id="{P}body"><path d="{car}" fill="url(#{P}g)" stroke="{dark}" stroke-width="4" stroke-linejoin="round"/>')
    if spiky:
        for k in range(5 if king else 3):
            ang = k * 36 - 72 if king else (k - 1) * 22
            s.append(f'<circle cx="{200 + ang * (1.5 if king else 1.9)}" cy="{(128 if king else 118) + abs(ang) * .2:.0f}" r="{6 if king else 5}" fill="{spot}" opacity=".5"/>')
    s.append('<ellipse cx="200" cy="120" rx="52" ry="38" fill="#ffffff" opacity=".13"/></g>')
    s.append('<circle cx="178" cy="78" r="8" fill="#fff"/><circle cx="222" cy="78" r="8" fill="#fff"/><circle cx="178" cy="76" r="4" fill="#11161b"/><circle cx="222" cy="76" r="4" fill="#11161b"/>')
    return "".join(s)


def abalone(P):
    s = [f'<defs>{_grad(P, "g", "#8a7650", "#4f4128")}</defs>']
    s.append(f'<g id="{P}foot"><ellipse cx="200" cy="130" rx="150" ry="98" fill="#e9d4b0"/><ellipse cx="200" cy="130" rx="150" ry="98" fill="none" stroke="#c9a977" stroke-width="6" stroke-dasharray="3 12" stroke-linecap="round"/></g>')
    s.append(f'<g id="{P}tent">' + "".join(f'<path d="M {330 + i * 6} {112 + i * 14} q 40 {-10 + i * 6} 64 {-14 + i * 10}" stroke="#d1b78a" stroke-width="5" fill="none" stroke-linecap="round"/>' for i in range(3)) + '</g>')
    s.append(f'<g id="{P}body"><ellipse cx="196" cy="124" rx="132" ry="84" fill="url(#{P}g)" stroke="#33291a" stroke-width="5"/>')
    for r in (110, 84, 58, 34): s.append(f'<ellipse cx="196" cy="124" rx="{r}" ry="{r * 0.64:.0f}" fill="none" stroke="#2c2315" stroke-width="3" opacity=".35"/>')
    for i in range(7): s.append(f'<ellipse cx="{300 + i * 4}" cy="{82 + i * 13}" rx="6" ry="9" fill="#11161b" opacity=".85" transform="rotate(-20 {300 + i * 4} {82 + i * 13})"/>')
    s.append('<ellipse cx="170" cy="92" rx="70" ry="22" fill="#fff" opacity=".14"/></g>')
    return "".join(s)


def squid(P):  # 무늬오징어(선어, 정지)
    s = [f'<defs>{_grad(P, "g", "#f3d6c8", "#cf9b8f")}</defs>']
    s.append(f'<path d="M 94 120 C 120 70, 150 70, 168 98 L 168 142 C 150 170, 120 170, 94 120 Z" fill="#e4b9aa" opacity=".9"/>')
    s.append(f'<path d="M 60 120 C 96 56, 190 60, 262 98 L 262 142 C 190 180, 96 184, 60 120 Z" fill="url(#{P}g)"/>')
    s.append(f'<path d="M 74 120 C 100 76, 180 78, 246 106 Q 250 120 246 134 C 180 162, 100 164, 74 120 Z" fill="#fff" opacity=".12"/>')
    import random; r = random.Random(3)
    for _ in range(30): s.append(f'<circle cx="{r.randint(90, 250)}" cy="{r.randint(92, 150)}" r="{r.randint(2, 4)}" fill="#a8635a" opacity=".6"/>')
    s.append('<ellipse cx="266" cy="120" rx="26" ry="30" fill="#dba998"/>')
    for k in range(8): s.append(f'<path d="M 280 {100 + k * 5} Q {330 + k * 4} {92 + k * 9} {384} {104 + k * 4}" stroke="#d29c8c" stroke-width="7" fill="none" stroke-linecap="round"/>')
    s.append('<circle cx="262" cy="108" r="9" fill="#fff"/><circle cx="264" cy="108" r="5" fill="#11161b"/>')
    return "".join(s)


def oyster(P):  # 깐굴(선어, 정지): 접시 위의 굴살
    s = ['<ellipse cx="200" cy="170" rx="170" ry="46" fill="#f4f6f8"/><ellipse cx="200" cy="164" rx="150" ry="36" fill="#e3e8ec"/>']
    for cx, cy, rx, ry, rot in ((140, 150, 56, 36, -8), (240, 156, 60, 38, 6), (196, 118, 54, 34, -2)):
        s.append(f'<g transform="rotate({rot} {cx} {cy})"><ellipse cx="{cx}" cy="{cy}" rx="{rx + 6}" ry="{ry + 5}" fill="#6d6c6a"/><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#efe6d6"/>'
                 f'<ellipse cx="{cx - 8}" cy="{cy - 8}" rx="{rx * .55:.0f}" ry="{ry * .45:.0f}" fill="#fff" opacity=".45"/><path d="M {cx - rx * .6:.0f} {cy + 4} q {rx * .6:.0f} {ry * .5:.0f} {rx * 1.2:.0f} 0" stroke="#cdbfa6" stroke-width="3" fill="none"/></g>')
    return "".join(s)


SPECS = {  # 품종 → (종류, 모양 인자)
    "활참돔": ("fish", dict(H=84, top="#ef6a63", belly="#ffd0c8", fin="#d9483f", spots=("#5ed0ff",), back_spots=9, tail="fork")),
    "활왕게": ("crab", dict(body="#e65a3c", dark="#a93220", king=True)),
    "활넙치": ("flat", {}),
    "활수꽃게": ("crab", dict(body="#4f93d8", dark="#27598f", spot="#d9efff")),
    "활농어": ("fish", dict(H=58, top="#8fa1ad", belly="#f1f5f7", fin="#6b7c88", spots=("#27323a",), back_spots=12, tail="fork")),
    "활전복": ("abalone", {}),
    "활암꽃게": ("crab", dict(body="#98a65a", dark="#5e6b2c", spot="#f3f1c0")),
    "활참숭어": ("fish", dict(H=46, top="#78909a", belly="#e8eff1", fin="#566a74", tail="fork", lines=True, snout=0.5)),
    "활민어": ("fish", dict(H=56, top="#b9a073", belly="#f0e5c8", fin="#8f7a4f", tail="round")),
    "활감성돔": ("fish", dict(H=82, top="#4d5964", belly="#bcc6cd", fin="#38424b", tail="fork")),
    "활줄돔": ("fish", dict(H=76, top="#cfd3c5", belly="#f4f2e0", fin="#47483f", tail="fork", stripes=((150, 20, "#1e2024", .85), (196, 20, "#1e2024", .85), (242, 20, "#1e2024", .85), (288, 16, "#1e2024", .85)))),
    "활감숭어": ("fish", dict(H=46, top="#8b8f6b", belly="#eef0dc", fin="#6c704f", tail="fork", lines=True, snout=0.5)),
    "선은갈치": ("ribbon", {}),
    "선오징어": ("squid", {}),
    "선삼치": ("fish", dict(H=50, top="#4f7a94", belly="#e6eef3", fin="#3d6177", tail="lunate", spots=("#c9dbe6",), back_spots=8, stripes=((150, 6, "#1f3b4c", .4), (190, 6, "#1f3b4c", .4), (230, 6, "#1f3b4c", .4)))),
    "선참조기": ("fish", dict(H=54, top="#e7b53f", belly="#fff0b8", fin="#c4902a", tail="round")),
    "선깐굴": ("oyster", {}),
    "선고등어": ("fish", dict(H=52, top="#2f7285", belly="#eaf3f5", fin="#245866", tail="lunate", stripes=((140, 8, "#0f2a33", .55), (172, 8, "#0f2a33", .55), (204, 8, "#0f2a33", .55), (236, 8, "#0f2a33", .55), (268, 8, "#0f2a33", .55)))),
}


def markup(P, key):
    kind, kw = SPECS[key]
    f = dict(fish=lambda: fish(P, **kw), flat=lambda: flatfish(P), ribbon=lambda: ribbon(P), crab=lambda: crab(P, **kw), abalone=lambda: abalone(P), squid=lambda: squid(P), oyster=lambda: oyster(P))[kind]
    return kind, f()


def motion_js(P, kind, dur):
    """활어 전용 움직임. dur(초) 동안 반복 횟수를 계산해 넣는다(repeat:-1 금지)."""
    n = lambda period: max(1, int(dur / period) + 1)
    org = lambda x, y: f'svgOrigin: "{x} {y}"'
    if kind == "fish":
        return f'''
  tl.to("#{P}tail", {{ rotation: 16, {org(100, 120)}, duration: 0.22, ease: "sine.inOut", yoyo: true, repeat: {n(0.22) * 2} }}, 0);
  tl.to("#{P}fin", {{ rotation: -18, {org(286, 120)}, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: {n(0.3) * 2} }}, 0);
  tl.to("#{P}dorsal", {{ skewX: 6, {org(225, 60)}, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: {n(0.4) * 2} }}, 0);
  tl.to("#{P}body", {{ rotation: 3.2, {org(200, 120)}, duration: 0.55, ease: "sine.inOut", yoyo: true, repeat: {n(0.55) * 2} }}, 0);
  swim("#{P}animal", {dur});'''
    if kind == "flat":
        return f'''
  tl.to("#{P}tail", {{ rotation: 14, {org(70, 122)}, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: {n(0.3) * 2} }}, 0);
  tl.to("#{P}body", {{ scaleY: 1.06, scaleX: 0.985, {org(200, 122)}, duration: 0.7, ease: "sine.inOut", yoyo: true, repeat: {n(0.7) * 2} }}, 0);
  swim("#{P}animal", {dur});'''
    if kind == "crab":
        return f'''
  for (const s of ["L", "R"]) for (let i = 0; i < 4; i++) {{
    tl.to("#{P}leg" + s + i, {{ rotation: (s === "L" ? -1 : 1) * (i % 2 ? 9 : -9), svgOrigin: (s === "L" ? "142 " : "258 ") + (128 + i * 14), duration: 0.18, ease: "sine.inOut", yoyo: true, repeat: {n(0.18) * 2} }}, 0);
  }}
  tl.to("#{P}clawL", {{ rotation: -12, {org(160, 96)}, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: {n(0.45) * 2} }}, 0);
  tl.to("#{P}clawR", {{ rotation: 12, {org(240, 96)}, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: {n(0.45) * 2} }}, 0.2);
  tl.to("#{P}body", {{ y: -3, duration: 0.18, ease: "sine.inOut", yoyo: true, repeat: {n(0.18) * 2} }}, 0);
  sidestep("#{P}animal", {dur});'''
    if kind == "abalone":
        return f'''
  tl.to("#{P}foot", {{ scaleX: 1.035, scaleY: 1.05, {org(200, 130)}, duration: 0.9, ease: "sine.inOut", yoyo: true, repeat: {n(0.9) * 2} }}, 0);
  tl.to("#{P}tent", {{ rotation: 7, {org(330, 112)}, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: {n(0.6) * 2} }}, 0);
  tl.to("#{P}body", {{ rotation: 2.4, {org(196, 124)}, duration: 1.1, ease: "sine.inOut", yoyo: true, repeat: {n(1.1) * 2} }}, 0);
  sidestep("#{P}animal", {dur}, 38);'''
    return ""
