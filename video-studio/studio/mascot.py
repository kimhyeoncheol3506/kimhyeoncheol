"""여의도 개미 — 코드로 직접 그린 마스코트 (v1.14.0).

외부 AI 그림 없이 Pillow로 부위(머리·눈·입·팔·다리·더듬이)를 그려서 만든다.
그래서 크레딧이 들지 않고, 모든 값을 숫자로 움직일 수 있다(애니메이션·표정 12종).

사용:
    from studio.mascot import draw_ant, POSES
    img = draw_ant(POSES["고민"], height=900)        # 투명 배경 RGBA
    img = draw_ant({**POSES["기본"], "bob": 6}, 900)   # 값만 바꿔 움직임을 준다

좌표는 가상 캔버스 800x1000 (아래가 +y). 팔은 손 목표점만 주면 팔꿈치를 자동 계산(2관절 IK)한다.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 800, 1000
SS = 3  # 부드러운 선을 위한 확대 비율

OUTLINE = (92, 62, 48)
FACE = (250, 222, 186)
HAIR = (140, 92, 64)
SUIT = (150, 158, 172)       # 회색 정장 (파스텔)
SUIT_SHADE = (132, 140, 156)
SHIRT = (252, 250, 246)
TIE = (226, 96, 96)
HAND = (140, 92, 64)
SHOE = (110, 76, 60)
BLUSH = (246, 170, 160)
EYE = (60, 40, 36)
SHADOW = (0, 0, 0, 38)

SHOULDER_L = (308, 580)
SHOULDER_R = (492, 580)
HEAD_C = (400, 330)
HEAD_R = 190


def _ik(s, t, l1, l2, side):
    dx, dy = t[0] - s[0], t[1] - s[1]
    d = max(1e-6, math.hypot(dx, dy))
    d = min(d, l1 + l2 - 1)
    ux, uy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    px, py = -uy * side, ux * side
    e = (s[0] + ux * a + px * h, s[1] + uy * a + py * h)
    hand = (s[0] + ux * d, s[1] + uy * d)
    return e, hand


def _limb(dr, pts, width, fill, o=7):
    """굵은 선분(둥근 끝)을 윤곽선과 함께 그린다."""
    for w, c in ((width + 2 * o, OUTLINE), (width, fill)):
        dr.line(pts, fill=c, width=w, joint="curve")
        for p in (pts[0], pts[-1]):
            dr.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=c)
        for p in pts[1:-1]:
            dr.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=c)


def _arm(dr, shoulder, hand_t, side, bend=None):
    """어깨→손 목표점. 팔꿈치는 몸 바깥쪽으로 꺾이는 쪽을 자동으로 고른다(bend로 강제 가능)."""
    outward = -1 if side < 0 else 1          # 왼팔은 -x, 오른팔은 +x가 바깥
    best = None
    for sg in (1, -1):
        e, hnd = _ik(shoulder, hand_t, 112, 106, sg)
        score = (e[0] - shoulder[0]) * outward
        if bend is not None:
            score = sg * bend
        if best is None or score > best[0]:
            best = (score, e, hnd)
    _, e, hnd = best
    # 소매(회색)와 손목 셔츠 커프스, 손
    _limb(dr, [shoulder, e, hnd], 44, SUIT, o=6)
    ux, uy = hnd[0] - e[0], hnd[1] - e[1]
    n = math.hypot(ux, uy) or 1
    cx, cy = hnd[0] - ux / n * 22, hnd[1] - uy / n * 22
    dr.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=SHIRT, outline=OUTLINE, width=5)
    r = 25
    dr.ellipse([hnd[0] - r - 5, hnd[1] - r - 5, hnd[0] + r + 5, hnd[1] + r + 5], fill=OUTLINE)
    dr.ellipse([hnd[0] - r, hnd[1] - r, hnd[0] + r, hnd[1] + r], fill=HAND)
    return hnd, e


def _forearm(dr, e, hnd):
    """몸·머리 앞으로 나와야 하는 팔(턱 괴기 등)의 팔꿈치→손만 다시 그린다."""
    _limb(dr, [e, hnd], 44, SUIT, o=6)
    ux, uy = hnd[0] - e[0], hnd[1] - e[1]
    n = math.hypot(ux, uy) or 1
    cx, cy = hnd[0] - ux / n * 22, hnd[1] - uy / n * 22
    dr.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=SHIRT, outline=OUTLINE, width=5)
    r = 25
    dr.ellipse([hnd[0] - r - 5, hnd[1] - r - 5, hnd[0] + r + 5, hnd[1] + r + 5], fill=OUTLINE)
    dr.ellipse([hnd[0] - r, hnd[1] - r, hnd[0] + r, hnd[1] + r], fill=HAND)


def _magnifier(dr, hand):
    cx, cy = hand[0] + 40, hand[1] - 150
    dr.line([hand, (cx - 30, cy + 60)], fill=(190, 140, 70), width=20)
    dr.ellipse([cx - 86, cy - 86, cx + 86, cy + 86], fill=(214, 168, 80))
    dr.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=(205, 232, 248, 210))
    dr.arc([cx - 50, cy - 50, cx + 50, cy + 50], 200, 260, fill=(255, 255, 255), width=10)
    dr.ellipse([hand[0] - 27, hand[1] - 27, hand[0] + 27, hand[1] + 27], fill=HAND, outline=OUTLINE, width=6)


def _coin(dr, hand):
    cx, cy = hand[0], hand[1] - 62
    dr.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(244, 200, 80), outline=(176, 130, 40), width=7)
    dr.text((cx - 9, cy - 20), "₩", fill=(176, 130, 40))
    dr.ellipse([hand[0] - 27, hand[1] - 27, hand[0] + 27, hand[1] + 27], fill=HAND, outline=OUTLINE, width=6)


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _star(dr, c, r, fill):
    x, y = c
    k = r * 0.28
    dr.polygon([(x, y - r), (x + k, y - k), (x + r, y), (x + k, y + k), (x, y + r), (x - k, y + k), (x - r, y), (x - k, y - k)], fill=fill)


def _eyes(dr, p):
    open_ = p.get("eye_open", 1.0)
    look = p.get("look", (0, 0))
    kind = p.get("eyes", "normal")
    for cx in (342, 458):
        cy = 332
        rx, ry = 40, 48 * open_
        if p.get("wink") and cx == 458:
            dr.arc([cx - 36, cy - 8, cx + 36, cy + 28], 200, 340, fill=EYE, width=9)
            continue
        if p.get("happy_eyes"):
            dr.arc([cx - 38, cy - 22, cx + 38, cy + 34], 200, 340, fill=EYE, width=11)
            continue
        if kind in ("sad_closed", "sleep"):
            dr.arc([cx - 34, cy - 14, cx + 34, cy + 26], 20, 160, fill=EYE, width=10)
            continue
        if kind == "spiral":
            for r, w in ((40, 6), (27, 6), (14, 6)):
                dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=EYE, width=w)
            continue
        if kind == "dollar":
            dr.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=(244, 200, 80), outline=(176, 130, 40), width=7)
            dr.text((cx, cy), "$", fill=(150, 104, 24), font=_font(64), anchor="mm")
            continue
        if kind == "dot":
            dr.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=EYE)
            continue
        if open_ < 0.2:
            dr.line([cx - 34, cy, cx + 34, cy], fill=EYE, width=9)
            continue
        dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=EYE)
        px, py = cx + look[0] * 8, cy + look[1] * 8
        if kind == "sparkle":
            _star(dr, (px - 8, py - 10), 24, (255, 255, 255))
            _star(dr, (px + 16, py + 16), 11, (255, 255, 255))
        else:
            dr.ellipse([px - 16, py - 24 * open_ - 6, px + 8, py - 24 * open_ + 18], fill=(255, 255, 255))
            dr.ellipse([px + 8, py + 8, px + 20, py + 20], fill=(255, 255, 255))
        if kind == "tear":
            sx = -1 if cx < 400 else 1
            dr.polygon([(cx + sx * 20, cy + 40), (cx + sx * 38, cy + 40), (cx + sx * 46, cy + 130), (cx + sx * 24, cy + 130)], fill=(176, 218, 246, 230))
            xa, xb = sorted((cx + sx * 16, cx + sx * 50))
            dr.ellipse([xa, cy + 112, xb, cy + 146], fill=(176, 218, 246, 230))
    # 눈썹: (왼쪽 기울기, 오른쪽 기울기, 높이)
    if p.get("brows") is not None:
        bl, br, by = p["brows"]
        y = 268 + by
        dr.line([300, y + bl, 380, y - bl], fill=OUTLINE, width=9)
        dr.line([420, y - br, 500, y + br], fill=OUTLINE, width=9)


def _mouth(dr, kind):
    cx, cy = 400, 408
    if kind == "smile":
        dr.arc([cx - 30, cy - 22, cx + 30, cy + 18], 20, 160, fill=OUTLINE, width=8)
    elif kind == "grin":
        dr.pieslice([cx - 44, cy - 24, cx + 44, cy + 40], 0, 180, fill=(120, 60, 56), outline=OUTLINE, width=6)
    elif kind == "o":
        dr.ellipse([cx - 16, cy - 8, cx + 16, cy + 30], fill=(120, 60, 56), outline=OUTLINE, width=6)
    elif kind == "flat":
        dr.line([cx - 22, cy + 4, cx + 22, cy + 4], fill=OUTLINE, width=8)
    elif kind == "frown":
        dr.arc([cx - 28, cy + 2, cx + 28, cy + 40], 200, 340, fill=OUTLINE, width=8)
    elif kind == "small":
        dr.arc([cx - 16, cy - 8, cx + 16, cy + 12], 20, 160, fill=OUTLINE, width=7)
    elif kind == "wide":
        dr.ellipse([cx - 30, cy - 12, cx + 30, cy + 52], fill=(120, 60, 56), outline=OUTLINE, width=6)
        dr.ellipse([cx - 16, cy + 26, cx + 16, cy + 48], fill=(236, 130, 130))
    elif kind == "wavy":
        dr.arc([cx - 36, cy - 6, cx, cy + 22], 180, 360, fill=OUTLINE, width=7)
        dr.arc([cx, cy - 6, cx + 36, cy + 22], 0, 180, fill=OUTLINE, width=7)
    elif kind == "smirk":
        dr.arc([cx - 6, cy - 20, cx + 46, cy + 14], 10, 150, fill=OUTLINE, width=8)
        dr.line([cx - 24, cy + 2, cx - 4, cy + 4], fill=OUTLINE, width=7)
    elif kind == "tongue":
        dr.arc([cx - 30, cy - 22, cx + 30, cy + 18], 20, 160, fill=OUTLINE, width=8)
        dr.pieslice([cx - 4, cy + 4, cx + 30, cy + 44], 0, 180, fill=(236, 130, 130), outline=OUTLINE, width=4)
    elif kind == "grit":
        dr.rounded_rectangle([cx - 34, cy - 6, cx + 34, cy + 24], radius=8, fill=(255, 255, 255), outline=OUTLINE, width=6)
        for x in (cx - 17, cx, cx + 17):
            dr.line([x, cy - 4, x, cy + 22], fill=OUTLINE, width=4)


def _fx(dr, p):
    """머리 주변 효과(땀방울·전구·물음표·화남 표시 등). 얼굴과 함께 움직인다."""
    for f in p.get("fx", []):
        if f == "sweat":
            dr.polygon([(520, 230), (540, 270), (500, 270)], fill=(170, 214, 244), outline=(110, 160, 200))
            dr.ellipse([500, 258, 540, 290], fill=(170, 214, 244), outline=(110, 160, 200), width=3)
        elif f == "vein":
            for dx, dy in ((0, 0),):
                x, y = 520, 240
                dr.line([x - 22, y - 8, x - 6, y - 8], fill=(214, 70, 70), width=8)
                dr.line([x + 6, y - 8, x + 22, y - 8], fill=(214, 70, 70), width=8)
                dr.line([x - 8, y - 22, x - 8, y - 4], fill=(214, 70, 70), width=8)
                dr.line([x + 8, y + 2, x + 8, y + 20], fill=(214, 70, 70), width=8)
        elif f == "bulb":
            dr.ellipse([520, 60, 600, 140], fill=(255, 224, 110), outline=(200, 160, 40), width=5)
            dr.rectangle([544, 138, 576, 160], fill=(170, 170, 176), outline=OUTLINE, width=4)
            for ang in (200, 250, 290, 340):
                a = math.radians(ang)
                dr.line([560 + 58 * math.cos(a), 100 + 58 * math.sin(a), 560 + 80 * math.cos(a), 100 + 80 * math.sin(a)], fill=(220, 170, 40), width=6)
        elif f == "question":
            dr.text((572, 120), "?", fill=(110, 90, 190), font=_font(120), anchor="mm")
        elif f == "exclaim":
            dr.text((572, 120), "!", fill=(224, 80, 80), font=_font(120), anchor="mm")
        elif f == "zzz":
            dr.text((540, 150), "Z", fill=(120, 130, 190), font=_font(70), anchor="mm")
            dr.text((590, 100), "Z", fill=(120, 130, 190), font=_font(96), anchor="mm")
        elif f == "sparkle":
            _star(dr, (230, 150), 28, (255, 214, 90))
            _star(dr, (580, 130), 36, (255, 214, 90))
            _star(dr, (600, 260), 20, (255, 214, 90))
        elif f == "up":
            dr.polygon([(600, 150), (650, 210), (620, 210), (620, 280), (580, 280), (580, 210), (550, 210)], fill=(226, 90, 90), outline=OUTLINE)
        elif f == "down":
            dr.polygon([(600, 280), (650, 220), (620, 220), (620, 150), (580, 150), (580, 220), (550, 220)], fill=(96, 140, 224), outline=OUTLINE)
        elif f == "blush":
            dr.ellipse([270, 366, 342, 416], fill=BLUSH + (200,))
            dr.ellipse([458, 366, 530, 416], fill=BLUSH + (200,))
        elif f == "heart":
            x, y = 580, 150
            dr.ellipse([x - 34, y - 30, x, y + 4], fill=(240, 120, 150))
            dr.ellipse([x, y - 30, x + 34, y + 4], fill=(240, 120, 150))
            dr.polygon([(x - 33, y - 8), (x + 33, y - 8), (x, y + 40)], fill=(240, 120, 150))


def _prop(dr, kind, hand):
    x, y = hand
    if kind == "magnifier":
        _magnifier(dr, hand)
        return
    if kind == "coin":
        _coin(dr, hand)
        return
    if kind == "phone":
        dr.rounded_rectangle([x - 40, y - 150, x + 40, y + 10], radius=14, fill=(60, 66, 84), outline=OUTLINE, width=5)
        dr.rounded_rectangle([x - 32, y - 138, x + 32, y - 14], radius=8, fill=(214, 236, 250))
        dr.line([x - 24, y - 50, x - 8, y - 78, x + 6, y - 60, x + 24, y - 112], fill=(226, 90, 90), width=6)
    elif kind == "chart":
        dr.rounded_rectangle([x - 90, y - 190, x + 70, y - 40], radius=10, fill=(255, 255, 252), outline=OUTLINE, width=6)
        dr.line([x - 66, y - 70, x - 30, y - 110, x - 4, y - 90, x + 44, y - 160], fill=(226, 90, 90), width=9, joint="curve")
        dr.line([x - 70, y - 60, x + 50, y - 60], fill=(180, 180, 190), width=4)
    elif kind == "calc":
        dr.rounded_rectangle([x - 50, y - 150, x + 50, y + 10], radius=12, fill=(120, 128, 150), outline=OUTLINE, width=5)
        dr.rectangle([x - 38, y - 138, x + 38, y - 104], fill=(214, 240, 226))
        for r in range(3):
            for c in range(3):
                dr.ellipse([x - 38 + c * 28, y - 90 + r * 28, x - 38 + c * 28 + 20, y - 90 + r * 28 + 20], fill=(236, 236, 240))
    elif kind == "umbrella":
        cx, cy = x - 40, y - 170
        dr.line([x, y - 20, x, cy], fill=OUTLINE, width=10)
        dr.pieslice([cx - 150, cy - 150, cx + 150, cy + 150], 180, 360, fill=(244, 150, 160), outline=OUTLINE, width=6)
        for dx in (-75, 0, 75):
            dr.line([cx + dx, cy - 140 + abs(dx) * 0.5, cx + dx * 0.4, cy], fill=OUTLINE, width=4)
    elif kind == "bag":
        dr.rounded_rectangle([x - 70, y - 20, x + 70, y + 80], radius=12, fill=(176, 130, 90), outline=OUTLINE, width=6)
        dr.rounded_rectangle([x - 26, y - 44, x + 26, y - 14], radius=8, outline=OUTLINE, width=6)
    elif kind == "stack":
        for i in range(4):
            dr.ellipse([x - 44, y - 40 - i * 22, x + 44, y - 8 - i * 22], fill=(244, 200, 80), outline=(176, 130, 40), width=5)
    dr.ellipse([x - 27, y - 27, x + 27, y + 27], fill=HAND, outline=OUTLINE, width=6)


def draw_ant(pose, height=900):
    """pose dict → 투명 배경 RGBA 이미지 (높이 height px)."""
    p = pose
    bob = p.get("bob", 0)               # 위아래 흔들림(px, 가상 좌표)
    tilt = p.get("head_tilt", 0)        # 머리 좌우 기울임(px)
    img = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(big, "RGBA")

    # 그림자
    dr.ellipse([250, 930, 550, 972], fill=SHADOW)
    # 다리·신발
    for x in (352, 448):
        _limb(dr, [(x, 780), (x, 880 + bob / 2)], 52, SUIT_SHADE)
        dr.ellipse([x - 42, 880 + bob / 2, x + 42, 944], fill=OUTLINE)
        dr.ellipse([x - 36, 884 + bob / 2, x + 36, 938], fill=SHOE)
    # 뒤쪽 팔 (오른쪽)
    tr = p.get("hand_r", (545, 735))
    hand_r, elb_r = _arm(dr, (SHOULDER_R[0], SHOULDER_R[1] + bob), tr, 1, p.get("bend_r"))
    # 왼쪽 팔 (몸통 뒤에서 나오게 몸통보다 먼저 그린다)
    tl = p.get("hand_l", (255, 735))
    hand_l, elb_l = _arm(dr, (SHOULDER_L[0], SHOULDER_L[1] + bob), tl, -1, p.get("bend_l"))
    # 소품

    # 몸통
    top = 500 + bob
    dr.rounded_rectangle([296, top + 22, 504, 796], radius=60, fill=OUTLINE)
    dr.rounded_rectangle([303, top + 29, 497, 789], radius=54, fill=SUIT)
    dr.polygon([(366, top + 30), (434, top + 30), (400, 700)], fill=SHIRT)
    dr.polygon([(366, top + 30), (400, 700), (352, 690), (330, top + 70)], fill=SUIT_SHADE)
    dr.polygon([(434, top + 30), (400, 700), (448, 690), (470, top + 70)], fill=SUIT_SHADE)
    dr.polygon([(390, top + 34), (410, top + 34), (418, top + 80), (400, top + 200), (382, top + 80)], fill=TIE)
    dr.polygon([(384, top + 70), (416, top + 70), (408, top + 96), (392, top + 96)], fill=(200, 76, 76))
    dr.line([(336, 740), (368, 740)], fill=OUTLINE, width=5)
    dr.line([(432, 740), (464, 740)], fill=OUTLINE, width=5)
    # 머리
    hx, hy = HEAD_C[0] + tilt, HEAD_C[1] + bob
    head = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(head, "RGBA")
    ant = p.get("antenna", 0)           # 더듬이 흔들림(px)
    for sx, k in ((-1, 1), (1, -1)):
        base = (hx + sx * 70, hy - 170)
        tip = (hx + sx * 130 + ant * k, hy - 280)
        mid = (hx + sx * 120, hy - 235)
        hd.line([base, mid, tip], fill=OUTLINE, width=17, joint="curve")
        hd.line([base, mid, tip], fill=HAIR, width=8, joint="curve")
        hd.ellipse([tip[0] - 20, tip[1] - 20, tip[0] + 20, tip[1] + 20], fill=OUTLINE)
        hd.ellipse([tip[0] - 14, tip[1] - 14, tip[0] + 14, tip[1] + 14], fill=HAIR)
    hd.ellipse([hx - HEAD_R - 7, hy - HEAD_R - 7, hx + HEAD_R + 7, hy + HEAD_R + 7], fill=OUTLINE)
    hd.ellipse([hx - HEAD_R, hy - HEAD_R, hx + HEAD_R, hy + HEAD_R], fill=HAIR)
    hd.ellipse([hx - HEAD_R + 12, hy - HEAD_R + 62, hx + HEAD_R - 12, hy + HEAD_R - 4], fill=FACE)
    head.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    big.alpha_composite(head)
    # 얼굴 표정은 머리 위치(hx, hy)를 따라 이동시켜 그린다
    face = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face, "RGBA")
    fd.ellipse([284, 372, 336, 410], fill=BLUSH + (150,))
    fd.ellipse([464, 372, 516, 410], fill=BLUSH + (150,))
    _eyes(fd, p)
    _mouth(fd, p.get("mouth", "smile"))
    fxs = list(p.get("fx", []))
    if p.get("sweat") and "sweat" not in fxs:
        fxs.append("sweat")
    _fx(fd, {"fx": fxs})
    face = face.transform(face.size, Image.AFFINE, (1, 0, -tilt, 0, 1, -bob))
    big.alpha_composite(face)

    # 팔이 얼굴 앞에 오는 자세(턱 괴기 등)는 팔을 한 번 더 위에 그린다
    dr2 = ImageDraw.Draw(big, "RGBA")
    if p.get("front_l") or p.get("arm_front"):
        _forearm(dr2, elb_l, hand_l)
    if p.get("front_r"):
        _forearm(dr2, elb_r, hand_r)

    prop = p.get("prop")
    dr3 = ImageDraw.Draw(big, "RGBA")
    if prop:
        side = p.get("prop_hand", "l" if prop == "magnifier" else "r")
        _prop(dr3, prop, hand_l if side == "l" else hand_r)

    out = big.resize((int(W * height / H), height), Image.LANCZOS)
    return out

from .mascot_poses import POSES  # noqa: E402,F401  (표정·자세 48종)
