"""동그라미 머리 사람 캐릭터 (벡터, 프레임마다 그림).

좌표 원점 = 발 사이 바닥. 단위 px(scale=1 기준 키 약 370px).
포즈: idle talk point shock think happy wave shrug sad walk
"""
import math
from .gfx import rgba, rounded_rect, pop_scale

R = 78           # 머리 반지름
HIP_Y = -92
BODY_TOP = -205
HEAD_Y = -275
SHOULDER = (-38, -188)
UPPER, FORE = 62, 56
LIMB_W = 12

# (위팔 각도, 아래팔 각도) 도 단위, 0 = 아래로, 양수 = 바깥(몸 밖) 위로
POSES = {
    "idle":  ((14, 8), (14, 8)),
    "talk":  ((16, 8), (55, 110)),
    "point": ((14, 8), (95, 92)),
    "shock": ((140, 165), (140, 165)),
    "think": ((14, 8), (8, 196)),
    "happy": ((125, 150), (125, 150)),
    "wave":  ((14, 8), (150, 170)),
    "shrug": ((55, 135), (55, 135)),
    "sad":   ((6, 2), (6, 2)),
    "walk":  ((20, 10), (20, 10)),
}


def _limb(ctx, x, y, a1, a2, side, ink, w=LIMB_W):
    # side: -1 왼쪽, +1 오른쪽
    r1, r2 = math.radians(a1), math.radians(a2)
    ex, ey = x + side * math.sin(r1) * UPPER, y + math.cos(r1) * UPPER
    hx, hy = ex + side * math.sin(r2) * FORE, ey + math.cos(r2) * FORE
    ctx.set_line_cap(1)  # ROUND
    ctx.set_line_join(1)
    ctx.set_line_width(w)
    ctx.set_source_rgba(*ink)
    ctx.move_to(x, y)
    ctx.line_to(ex, ey)
    ctx.line_to(hx, hy)
    ctx.stroke()
    ctx.arc(hx, hy, w * 0.95, 0, 2 * math.pi)
    ctx.fill()
    return hx, hy


def draw_person(ctx, x, y, t, pose="idle", talk_amp=0.0, scale=1.0, shirt="#2E7CF6", skin="#FFFFFF",
                ink="#1B1B1B", outline=7, facing=1, appear_t=None, seed=0, label=None):
    """t: 장면 내 시간(초). talk_amp: 0~1 입 벌림(음성 크기). appear_t: 등장 후 경과(팝인)."""
    inkc, skinc, shirtc = rgba(ink), rgba(skin), rgba(shirt)
    s = scale
    if appear_t is not None:
        s *= pop_scale(appear_t, 0.28, 1.12)
        if appear_t <= 0:
            return
    ctx.save()
    ctx.translate(x, y)
    # 바닥 그림자
    ctx.save()
    ctx.scale(1, 0.22)
    ctx.arc(0, 0, 70 * s, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, 0.13)
    ctx.fill()

    ctx.scale(s * facing, s)
    ph = t + seed * 0.37
    talking = talk_amp > 0.05
    bob = -abs(math.sin(ph * math.pi * 1.6)) * (7 if talking else 3)
    if pose == "shock":
        bob = -6 + math.sin(ph * 40) * 2.5          # 덜덜 떨림
    if pose == "happy":
        bob = -abs(math.sin(ph * math.pi * 2.4)) * 14  # 깡총
    squash = 1 + 0.025 * math.sin(ph * math.pi * 3.2)

    (la1, la2), (ra1, ra2) = POSES.get(pose, POSES["idle"])
    if pose == "talk" or (pose == "idle" and talking):
        g = math.sin(ph * 5.0)
        ra1, ra2 = 55 + 12 * g, 110 + 22 * g
    if pose == "wave":
        ra2 = 165 + 25 * math.sin(ph * 12)
    if pose == "point":
        ra1 += 3 * math.sin(ph * 3)
    walk = pose == "walk"

    # 다리
    ctx.set_source_rgba(*inkc)
    for side in (-1, 1):
        sw = math.sin(ph * 9) * 22 * side if walk else 0
        ctx.set_line_width(LIMB_W + 1)
        ctx.set_line_cap(1)
        ctx.move_to(side * 20, HIP_Y + 8)
        fx = side * 24 + sw
        ctx.line_to(fx, -6)
        ctx.stroke()
        ctx.save()
        ctx.translate(fx + side * 9, -7)
        ctx.scale(1.6, 1)
        ctx.arc(0, 0, 9, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()

    ctx.translate(0, bob)
    ctx.save()
    ctx.translate(0, HIP_Y)
    ctx.scale(1 / squash, squash)
    ctx.translate(0, -HIP_Y)

    # 몸통 (콩 모양)
    rounded_rect(ctx, -50, BODY_TOP, 100, HIP_Y - BODY_TOP + 16, 44)
    ctx.set_source_rgba(*shirtc)
    ctx.fill_preserve()
    ctx.set_source_rgba(*inkc)
    ctx.set_line_width(outline)
    ctx.stroke()

    # 팔
    _limb(ctx, SHOULDER[0], SHOULDER[1], la1, la2, -1, inkc)
    _limb(ctx, -SHOULDER[0], SHOULDER[1], ra1, ra2, 1, inkc)

    # 머리
    tilt = {"think": -0.12, "sad": 0.10, "shrug": 0.08}.get(pose, 0.0) + (0.04 * math.sin(ph * 2.2) if talking else 0)
    ctx.save()
    ctx.translate(0, HEAD_Y + 40)
    ctx.rotate(tilt)
    ctx.translate(0, -40)
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.set_source_rgba(*skinc)
    ctx.fill_preserve()
    ctx.set_source_rgba(*inkc)
    ctx.set_line_width(outline)
    ctx.stroke()
    _face(ctx, ph, pose, talk_amp, inkc, seed)
    ctx.restore()
    ctx.restore()
    ctx.restore()


def _face(ctx, ph, pose, amp, ink, seed):
    ex, ey = R * 0.33, -R * 0.06
    period = 3.1 + seed * 0.4
    blink = (ph % period) < 0.12 and pose not in ("happy", "shock")
    look = {"think": (5, -9), "point": (7, 0), "sad": (0, 6)}.get(pose, (0, 0))
    ctx.set_source_rgba(*ink)
    if pose == "happy":
        ctx.set_line_width(6)
        for s in (-1, 1):
            ctx.arc(s * ex, ey + 6, 13, math.pi * 1.1, math.pi * 1.9)
            ctx.stroke()
    elif pose == "shock":
        for s in (-1, 1):
            ctx.arc(s * ex, ey, 19, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 1)
            ctx.fill_preserve()
            ctx.set_source_rgba(*ink)
            ctx.set_line_width(5)
            ctx.stroke()
            ctx.arc(s * ex, ey, 6, 0, 2 * math.pi)
            ctx.fill()
    else:
        for s in (-1, 1):
            ctx.save()
            ctx.translate(s * ex + look[0], ey + look[1])
            ctx.scale(1, 0.12 if blink else 1.25)
            ctx.arc(0, 0, 8.5, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
    # 눈썹
    ctx.set_line_width(5)
    if pose == "think":   # 한쪽 눈썹만 치켜올림
        ctx.arc(ex, ey - 22, 16, math.pi * 1.15, math.pi * 1.85)
        ctx.stroke()
    if pose in ("sad", "shock"):
        d = {"sad": 1, "shock": -1}[pose]
        for s in (-1, 1):
            ctx.move_to(s * ex - 14, ey - 30 - (s * d * 6 if pose != "shock" else 6))
            ctx.line_to(s * ex + 14, ey - 30 + (s * d * 6 if pose != "shock" else -2))
            ctx.stroke()
    # 볼터치
    if pose in ("happy", "wave"):
        ctx.set_source_rgba(1, 0.45, 0.5, 0.45)
        for s in (-1, 1):
            ctx.save()
            ctx.translate(s * R * 0.55, R * 0.18)
            ctx.scale(1.5, 1)
            ctx.arc(0, 0, 9, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
        ctx.set_source_rgba(*ink)
    # 입
    my = R * 0.36
    if amp > 0.05 or pose == "shock":
        h = 6 + 24 * min(amp, 1) if pose != "shock" else 20 + 4 * math.sin(ph * 30)
        w = 20 if pose != "shock" else 15
        ctx.save()
        ctx.translate(0, my)
        ctx.scale(1, h / w)
        ctx.arc(0, 0, w, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(0.35, 0.08, 0.1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgba(*ink)
        ctx.set_line_width(4)
        ctx.stroke()
    elif pose == "sad":
        ctx.set_line_width(5)
        ctx.arc(0, my + 14, 15, math.pi * 1.2, math.pi * 1.8)
        ctx.stroke()
    elif pose == "think":
        ctx.set_line_width(5)
        ctx.move_to(-10, my + 2)
        ctx.line_to(12, my - 3)
        ctx.stroke()
    else:
        ctx.set_line_width(5)
        ctx.arc(0, my - 10, 17, math.pi * 0.2, math.pi * 0.8)
        ctx.stroke()


# ------------------------------------------------------------------ 소품
def draw_prop(ctx, kind, x, y, t, scale=1.0, ink="#1B1B1B", appear_t=None):
    inkc = rgba(ink)
    s = scale * (pop_scale(appear_t, 0.25, 1.2) if appear_t is not None else 1)
    if appear_t is not None and appear_t <= 0:
        return
    ctx.save()
    ctx.translate(x, y + math.sin(t * 2.4) * 6)
    ctx.scale(s, s)
    ctx.set_line_width(6)
    ctx.set_line_cap(1)
    if kind == "coffee":
        rounded_rect(ctx, -48, -60, 96, 110, 18)
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgba(*inkc)
        ctx.stroke()
        ctx.rectangle(-48, -30, 96, 34)
        ctx.set_source_rgba(0.55, 0.33, 0.2, 1)
        ctx.fill()
        ctx.set_source_rgba(*inkc)
        ctx.arc(56, -5, 22, -math.pi / 2, math.pi / 2)
        ctx.stroke()
        for i in (-1, 0, 1):  # 김
            ctx.move_to(i * 22, -75)
            for k in range(1, 6):
                ctx.line_to(i * 22 + math.sin(t * 6 + k + i) * 7, -75 - k * 11)
            ctx.set_source_rgba(*inkc[:3], 0.5)
            ctx.stroke()
    elif kind in ("question", "exclaim"):
        from .gfx import simple_text, blit
        surf = simple_text("?" if kind == "question" else "!", "BlackHanSans.ttf", 150,
                           color="#FF4D4D" if kind == "exclaim" else "#2E7CF6", stroke=8, stroke_color="#1B1B1B")
        blit(ctx, surf, 0, 0, rot=math.sin(t * 3) * 0.12)
    elif kind == "sweat":
        ctx.move_to(0, -30)
        ctx.curve_to(22, 0, 22, 30, 0, 30)
        ctx.curve_to(-22, 30, -22, 0, 0, -30)
        ctx.set_source_rgba(0.45, 0.75, 1, 1)
        ctx.fill_preserve()
        ctx.set_source_rgba(*inkc)
        ctx.set_line_width(4)
        ctx.stroke()
    elif kind == "bulb":
        ctx.arc(0, -20, 46, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0.88, 0.3, 1)
        ctx.fill_preserve()
        ctx.set_source_rgba(*inkc)
        ctx.stroke()
        ctx.rectangle(-20, 26, 40, 26)
        ctx.fill()
        for k in range(8):
            a = k * math.pi / 4 + t
            ctx.move_to(math.cos(a) * 62, -20 + math.sin(a) * 62)
            ctx.line_to(math.cos(a) * 80, -20 + math.sin(a) * 80)
            ctx.stroke()
    elif kind == "money":
        ctx.rotate(-0.15 + math.sin(t * 2) * 0.08)
        rounded_rect(ctx, -70, -38, 140, 76, 8)
        ctx.set_source_rgba(0.55, 0.85, 0.55, 1)
        ctx.fill_preserve()
        ctx.set_source_rgba(*inkc)
        ctx.stroke()
        ctx.arc(0, 0, 20, 0, 2 * math.pi)
        ctx.stroke()
    elif kind in ("arrow_up", "arrow_down"):
        d = -1 if kind == "arrow_up" else 1
        col = (1, 0.3, 0.3, 1) if kind == "arrow_up" else (0.2, 0.5, 1, 1)
        ctx.move_to(-24, 0)
        ctx.line_to(-24, -d * 60)
        ctx.line_to(24, -d * 60)
        ctx.line_to(24, 0)
        ctx.line_to(50, 0)
        ctx.line_to(0, d * 60)
        ctx.line_to(-50, 0)
        ctx.close_path()
        ctx.set_source_rgba(*col)
        ctx.fill_preserve()
        ctx.set_source_rgba(*inkc)
        ctx.stroke()
    elif kind == "sparkle":
        for k, (dx, dy, r) in enumerate(((0, 0, 30), (55, -40, 16), (-50, -35, 12))):
            rr = r * (0.8 + 0.3 * math.sin(t * 6 + k))
            ctx.move_to(dx, dy - rr)
            for q in range(4):
                a = q * math.pi / 2
                ctx.line_to(dx + math.cos(a + math.pi / 4) * rr * 0.25, dy + math.sin(a + math.pi / 4) * rr * 0.25)
                ctx.line_to(dx + math.cos(a + math.pi / 2) * rr, dy + math.sin(a + math.pi / 2) * rr)
            ctx.close_path()
            ctx.set_source_rgba(1, 0.85, 0.2, 1)
            ctx.fill()
    elif kind == "heart":
        ctx.move_to(0, 30)
        ctx.curve_to(-70, -20, -30, -70, 0, -35)
        ctx.curve_to(30, -70, 70, -20, 0, 30)
        ctx.set_source_rgba(1, 0.35, 0.45, 1)
        ctx.fill_preserve()
        ctx.set_source_rgba(*inkc)
        ctx.stroke()
    ctx.restore()
