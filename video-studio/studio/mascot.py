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
from PIL import Image, ImageDraw

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


def _eyes(dr, p):
    open_ = p.get("eye_open", 1.0)
    look = p.get("look", (0, 0))
    for cx in (342, 458):
        cy = 332
        rx, ry = 40, 48 * open_
        if p.get("wink") and cx == 458:
            dr.arc([cx - 36, cy - 8, cx + 36, cy + 28], 200, 340, fill=EYE, width=9)
            continue
        if p.get("happy_eyes"):
            dr.arc([cx - 38, cy - 22, cx + 38, cy + 34], 200, 340, fill=EYE, width=11)
            continue
        if open_ < 0.2:
            dr.line([cx - 34, cy, cx + 34, cy], fill=EYE, width=9)
            continue
        dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=EYE)
        px, py = cx + look[0] * 8, cy + look[1] * 8
        dr.ellipse([px - 16, py - 24 * open_ - 6, px + 8, py - 24 * open_ + 18], fill=(255, 255, 255))
        dr.ellipse([px + 8, py + 8, px + 20, py + 20], fill=(255, 255, 255))
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
    if p.get("sweat"):
        fd.polygon([(520, 230), (540, 270), (500, 270)], fill=(170, 214, 244), outline=(110, 160, 200))
        fd.ellipse([500, 258, 540, 290], fill=(170, 214, 244), outline=(110, 160, 200), width=3)
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
    if prop == "magnifier":
        _magnifier(dr3, hand_l)
    elif prop == "coin":
        _coin(dr3, hand_r)

    out = big.resize((int(W * height / H), height), Image.LANCZOS)
    return out


# 표정·자세 12종 (손 목표점은 가상 좌표)
POSES = {
    "기본": dict(mouth="smile", brows=None, hand_l=(266, 790), hand_r=(534, 790)),
    "고민": dict(mouth="flat", brows=(-6, 6, 0), look=(1, -1), hand_l=(372, 515), hand_r=(534, 790), arm_front=True),
    "놀람": dict(mouth="o", eye_open=1.15, brows=(-8, 8, -14), sweat=True, hand_l=(205, 650), hand_r=(595, 650), bend_l=-1, bend_r=1),
    "환호": dict(mouth="grin", happy_eyes=True, brows=None, hand_l=(205, 400), hand_r=(595, 400), antenna=14),
    "의심": dict(mouth="flat", eye_open=0.8, brows=(8, -2, 0), look=(1, 0), hand_l=(250, 600),
                 hand_r=(534, 790), prop="magnifier"),
    "설명": dict(mouth="smile", brows=None, hand_l=(266, 790), hand_r=(640, 570)),
    "걱정": dict(mouth="frown", brows=(-10, 10, -6), sweat=True, hand_l=(362, 650), hand_r=(438, 650), front_l=True, front_r=True),
    "자신감": dict(mouth="grin", brows=(4, -4, 0), hand_l=(262, 690), hand_r=(538, 690)),
    "슬픔": dict(mouth="frown", eye_open=0.7, brows=(-12, 12, -4), hand_l=(268, 792), hand_r=(532, 792), head_tilt=-6),
    "화남": dict(mouth="flat", eye_open=0.75, brows=(14, -14, 4), hand_l=(262, 700), hand_r=(538, 700)),
    "윙크": dict(mouth="smile", wink=True, brows=None, hand_l=(266, 790), hand_r=(610, 520), prop=None),
    "동전": dict(mouth="smile", brows=None, hand_l=(266, 790), hand_r=(585, 590), prop="coin"),
}
