#!/usr/bin/env python3
"""훌라후프 하는 졸라맨 애니메이션 (1분 30초, 1280x720, 30fps) 생성 스크립트.

사용법:
    python3 scripts/hula-zolaman.py [출력경로.mp4]

필요: python3 + Pillow + numpy, ffmpeg
"""
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS = 30
DURATION = 122.0
J = 16.0  # 점프 구간 길이
M = 16.0  # 문워크 구간 길이
E = J + M  # 엔딩이 밀린 시간
SS = 2  # 슈퍼샘플링 배율 (안티앨리어싱)
BPM = 120
HOOP_HZ = BPM / 60.0  # 한 박자에 한 바퀴

OUT = sys.argv[1] if len(sys.argv) > 1 else "public/videos/hula-zolaman.mp4"

INK = (20, 20, 20)
GROUND_Y = 640


# ---------------------------------------------------------------- 유틸
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def seg(t, a, b):
    """t가 [a,b] 구간에서 0→1 로 부드럽게 변하는 값"""
    return smooth((t - a) / (b - a))


def lerp(a, b, k):
    return a + (b - a) * k


def mix_col(c1, c2, k):
    return tuple(int(lerp(x, y, k)) for x, y in zip(c1, c2))


HOOP_COLORS = [
    (235, 64, 52),
    (255, 160, 0),
    (40, 170, 90),
    (30, 130, 230),
    (160, 70, 210),
    (235, 64, 52),
]


def hoop_color(t):
    # 30초 이후부터 색이 천천히 바뀜
    if t < 30:
        return HOOP_COLORS[0]
    p = (t - 30) / 12.0
    i = int(p) % (len(HOOP_COLORS) - 1)
    return mix_col(HOOP_COLORS[i], HOOP_COLORS[i + 1], smooth(p - int(p)))


# ------------------------------------------------- 훌라후프 회전각 (적분)
dt = 1.0 / FPS
N = int(DURATION * FPS)


def hoop_speed(t):
    """회전 속도 배율 (1 = 박자에 맞춘 기본 속도)"""
    if t < 3.0:
        return 0.0
    if t < 6.0:
        return seg(t, 3.0, 6.0)
    if t < 75.0:
        return 1.0
    if t < 77.0:
        return lerp(1.0, 2.0, seg(t, 75, 77))
    if t < 84.0:
        return 2.0
    if t < 100.0:
        return lerp(2.0, 1.5, seg(t, 84, 86))
    if t < 116.0:
        return lerp(1.5, 1.0, seg(t, 100, 102))
    if t < 118.5:
        return lerp(1.0, 0.6, seg(t, 116, 118.5))
    return 0.0


MW_V = 72.5    # 문워크 이동 속도 (px/s)
MW_P = 2.0     # 문워크 한 사이클 시간 (초)


def moonwalk_state(t):
    """문워크 구간(101~116초): (다리 블렌드, 기준 x, 바라보는 방향, 위상, 까치발)"""
    if t < 101.0 or t >= 116.5:
        return 0.0, None, 1, 0.0, 0.0
    if t < 102.0:           # 모자 쓰기
        return 0.0, W / 2, -1, 0.0, 0.0
    if t < 106.0:           # 왼쪽 보고 오른쪽으로 미끄러지기
        mk = seg(t, 102.0, 102.4) * (1 - seg(t, 105.6, 106.0))
        return mk, W / 2 + MW_V * (t - 102.0), -1, (t - 102.0) / MW_P, 0.0
    x1 = W / 2 + MW_V * 4.0
    if t < 107.0:           # 까치발 포즈
        tip = seg(t, 106.0, 106.3) * (1 - seg(t, 106.7, 107.0))
        return 0.0, x1, (1 if t > 106.5 else -1), 0.0, tip
    if t < 115.0:           # 오른쪽 보고 왼쪽으로 미끄러지기
        mk = seg(t, 107.0, 107.4) * (1 - seg(t, 114.6, 115.0))
        return mk, x1 - MW_V * (t - 107.0), 1, (t - 107.0) / MW_P, 0.0
    x2 = x1 - MW_V * 8.0    # 가운데로 복귀
    return 0.0, lerp(x2, W / 2, seg(t, 115.0, 116.0)), 1, 0.0, 0.0


def jump_state(t):
    """점프 구간(86~100초): (높이, 벌리기 0~1, 웅크리기 0~1)"""
    def hop(u, start, period, air0, air1, height):
        k = ((u - start) % period) / period
        if air0 <= k <= air1:
            a = (k - air0) / (air1 - air0)
            return height * math.sin(math.pi * a), math.sin(math.pi * a), 0.0
        # 착지/도약 전 웅크림
        dk = min(abs(k - air0), abs(k - air1), abs(k + 1 - air0), abs(k - 1 - air1))
        return 0.0, 0.0, clamp(1 - dk / 0.12)

    if 86.0 <= t < 92.0:      # 박자 맞춰 콩콩 뛰기
        h, sp, cr = hop(t, 86.0, 1.0, 0.25, 0.75, 45)
        return h, 0.0, cr * 0.6
    if 92.0 <= t < 98.0:      # 팔다리 쫙 벌리는 스타 점프
        h, sp, cr = hop(t, 92.0, 1.5, 0.25, 0.8, 130)
        return h, sp, cr
    if 98.0 <= t < 100.5:     # 마지막 슈퍼 점프
        h, sp, cr = hop(t, 98.0, 2.5, 0.16, 0.76, 150)
        return h, 0.0, cr
    if 85.0 <= t < 86.0:      # 준비 자세
        return 0.0, 0.0, 0.5 * seg(t, 85.0, 85.6) * (1 - seg(t, 85.75, 86.0))
    return 0.0, 0.0, 0.0


theta = np.zeros(N)
acc = 0.0
for i in range(N):
    theta[i] = acc
    acc += 2 * math.pi * HOOP_HZ * hoop_speed(i * dt) * dt


# ------------------------------------------------------------ 포즈 계산
def pose(t, th):
    """몸의 각 관절 좌표(1x 해상도)와 훌라후프 정보를 반환"""
    beat = t * BPM / 60.0 * 2 * math.pi  # 박자 위상
    sp = hoop_speed(t)

    # 기준 x (60~75초 좌우로 이동)
    walk = seg(t, 60, 62) * (1 - seg(t, 73, 75))
    base_x = W / 2 + walk * 230 * math.sin((t - 60) * 2 * math.pi / 7.5)
    mk, mw_x, face, mw_u, tip = moonwalk_state(t)
    if mw_x is not None:
        base_x = mw_x

    # 허리 흔들기 (후프 위상에 맞춰)
    sway_amp = 14 * min(sp, 1.4) if t < 86.5 + E else 0
    sway_amp *= 1 - 0.6 * mk
    hip_x = base_x + sway_amp * math.cos(th)
    jump_h, spread, crouch = jump_state(t)
    hip_y = 450 + 4 * min(sp, 1.0) * math.sin(2 * th) - jump_h + crouch * 35 + 8 * mk - 18 * tip

    # 끝 인사 (88~90초)
    bow = seg(t, 87.3 + E, 88.3 + E) * (1 - seg(t, 89.0 + E, 89.8 + E))

    lean = -0.25 * sway_amp / 14 * math.cos(th) * 0.35
    torso_len = 150 * (1 - 0.35 * bow)  # 정면 인사: 상체가 앞으로 숙여져 짧아 보임
    neck_x = hip_x + torso_len * math.sin(lean)
    neck_y = hip_y - torso_len * math.cos(lean)
    head_r = 46
    head_x = neck_x + (head_r + 4) * math.sin(lean)
    head_y = neck_y - (head_r + 4) * math.cos(lean)
    # 머리 까딱 (30~45초)
    bob = seg(t, 30, 31) * (1 - seg(t, 44, 45))
    head_x += bob * 6 * math.sin(beat)
    head_y += bob * 4 * abs(math.sin(beat))

    sh_x = neck_x + 20 * math.sin(lean)
    sh_y = neck_y - 20 * math.cos(lean) + 22

    # ---- 다리
    stance = 55 + spread * 70
    lf_x, rf_x = base_x - stance, base_x + stance
    lf_y = rf_y = GROUND_Y - jump_h + spread * 40
    if jump_h > 0 and spread < 0.1:
        # 공중에서 다리 살짝 접기
        lf_y -= 0.25 * jump_h
        rf_y -= 0.25 * jump_h
    if walk > 0.01:
        step = math.sin((t - 60) * 2 * math.pi * 2)
        lf_y -= walk * 18 * max(0, step)
        rf_y -= walk * 18 * max(0, -step)
    knee_bend = 10 * min(sp, 1.0)
    knee_out = 10 + crouch * 30 + (0.25 * jump_h if spread < 0.1 else 0)
    lk = ((hip_x + lf_x) / 2 - knee_out - knee_bend * math.cos(th), (hip_y + lf_y) / 2 + 5)
    rk = ((hip_x + rf_x) / 2 + knee_out - knee_bend * math.cos(th), (hip_y + rf_y) / 2 + 5)
    legs = [[(hip_x, hip_y), lk, (lf_x, lf_y), (lf_x, lf_y)],
            [(hip_x, hip_y), rk, (rf_x, rf_y), (rf_x, rf_y)]]

    # ---- 문워크 다리: 한 발은 뒤꿈치 들고 제자리, 다른 발은 바닥에 붙여 뒤로 쭉
    if mk > 0.001:
        a = MW_V * MW_P / 4
        mw_legs = []
        for off in (0.0, 0.5):
            u = mw_u + off
            tri = 2 * abs((u % 1.0) - 0.5)
            r = a * (1 - 2 * tri)
            raised = clamp(0.5 + 1.5 * math.sin(2 * math.pi * u))
            fx = hip_x + face * r
            flat = [(fx - face * 6, GROUND_Y - 6), (fx + face * 24, GROUND_Y)]
            up = [(fx - face * 4, GROUND_Y - 22), (fx + face * 14, GROUND_Y)]
            ank = (lerp(flat[0][0], up[0][0], raised), lerp(flat[0][1], up[0][1], raised))
            toe = (lerp(flat[1][0], up[1][0], raised), GROUND_Y)
            knee = ((hip_x + ank[0]) / 2 + face * lerp(4, 34, raised), (hip_y + ank[1]) / 2)
            mw_legs.append([(hip_x, hip_y), knee, ank, toe])
        legs = [[(lerp(p[0], q[0], mk), lerp(p[1], q[1], mk)) for p, q in zip(l1, l2)]
                for l1, l2 in zip(legs, mw_legs)]
    # ---- 까치발 포즈
    if tip > 0.001:
        tp_legs = []
        for sd in (-1, 1):
            ax = hip_x + sd * 14
            ank = (ax - face * 4, GROUND_Y - 30)
            tp_legs.append([(hip_x, hip_y), ((hip_x + ank[0]) / 2, (hip_y + ank[1]) / 2), ank,
                            (ax + face * 12, GROUND_Y)])
        legs = [[(lerp(p[0], q[0], tip), lerp(p[1], q[1], tip)) for p, q in zip(l1, l2)]
                for l1, l2 in zip(legs, tp_legs)]

    # ---- 팔 (각도: 0=오른쪽 수평, 양수=위쪽)
    def arm(side, up, elbow_rel):
        # side: -1 왼팔, +1 오른팔
        a1 = math.radians(up)
        ex = sh_x + side * 75 * math.cos(a1)
        ey = sh_y - 75 * math.sin(a1)
        a2 = a1 + math.radians(elbow_rel)
        hx = ex + side * 70 * math.cos(a2)
        hy = ey - 70 * math.sin(a2)
        return ((sh_x, sh_y), (ex, ey), (hx, hy))

    # 기본: 팔 내림 → 6초 이후 V자로 올림
    up_v = lerp(-65, 45, seg(t, 5, 7))
    up_l = up_r = up_v
    el_l = el_r = lerp(-10, 10, seg(t, 5, 7))
    # 15~30초: 손 흔들기
    wave_k = seg(t, 15, 16) * (1 - seg(t, 29, 30))
    up_l += wave_k * 20 * math.sin(beat)
    up_r += wave_k * 20 * math.sin(beat + math.pi)
    el_l += wave_k * 30 * math.sin(beat * 2)
    el_r += wave_k * 30 * math.sin(beat * 2 + math.pi)
    # 30~45초: 허리에 손 (허리 짚기 포즈)
    hips_k = seg(t, 30, 31.5) * (1 - seg(t, 44, 45))
    up_l = lerp(up_l, -35, hips_k)
    up_r = lerp(up_r, -35, hips_k)
    el_l = lerp(el_l, -110, hips_k)
    el_r = lerp(el_r, -110, hips_k)
    # 45~60초: 팔 수평으로 펴고 비행기
    plane_k = seg(t, 45, 46.5) * (1 - seg(t, 59, 60))
    up_l = lerp(up_l, 5 + 15 * math.sin(beat / 2), plane_k)
    up_r = lerp(up_r, 5 - 15 * math.sin(beat / 2), plane_k)
    el_l = lerp(el_l, 0, plane_k)
    el_r = lerp(el_r, 0, plane_k)
    # 60~75초: 걸으면서 팔 앞뒤로 흔들기
    walk_arm = walk
    up_l = lerp(up_l, -60 + 25 * math.sin((t - 60) * 2 * math.pi * 2), walk_arm)
    up_r = lerp(up_r, -60 - 25 * math.sin((t - 60) * 2 * math.pi * 2), walk_arm)
    el_l = lerp(el_l, 20, walk_arm)
    el_r = lerp(el_r, 20, walk_arm)
    # 75~85초: 오른팔 위로 쭉 (팔에도 후프), 왼팔 허리
    trick_k = seg(t, 75, 76.5) * (1 - seg(t, 84, 85.5))
    up_r = lerp(up_r, 85, trick_k)
    el_r = lerp(el_r, 0, trick_k)
    up_l = lerp(up_l, -35, trick_k)
    el_l = lerp(el_l, -110, trick_k)
    # 끝: 만세 → 인사
    # 86~100초: 점프할 때 팔 동작
    jk = seg(t, 85.0, 86.0) * (1 - seg(t, 100.3, 101.0))
    if jk > 0:
        if t < 92.0:      # 콩콩: 팔꿈치 접고 박자 맞춰 흔들기
            ja_l, je_l = -40 + 25 * (jump_h / 45), 90
            ja_r, je_r = ja_l, je_l
        elif t < 98.0:    # 스타 점프: 공중에서 팔 쫙
            ja_l = ja_r = lerp(-50, 55, spread)
            je_l = je_r = lerp(40, 0, spread)
        else:             # 슈퍼 점프: 만세
            ja_l = ja_r = lerp(-50, 60, clamp(jump_h / 60))
            je_l = je_r = 5
        up_l, up_r = lerp(up_l, ja_l, jk), lerp(up_r, ja_r, jk)
        el_l, el_r = lerp(el_l, je_l, jk), lerp(el_r, je_r, jk)
    # 101~116초: 문워크 팔 (팔꿈치 굽혀 리듬), 까치발 땐 한 손 모자
    mwa = seg(t, 101.0, 101.8) * (1 - seg(t, 115.5, 116.3))
    if mwa > 0:
        sw = 12 * math.sin(beat / 2)
        up_l, up_r = lerp(up_l, -55 + sw, mwa), lerp(up_r, -55 - sw, mwa)
        el_l, el_r = lerp(el_l, 60, mwa), lerp(el_r, 60, mwa)
    # 모자 쓸 때 / 까치발 포즈 때 오른손이 모자로
    hat_hand = max(seg(t, 100.8, 101.3) * (1 - seg(t, 101.8, 102.3)), tip)
    up_r, el_r = lerp(up_r, 55, hat_hand), lerp(el_r, 105, hat_hand)
    end_k = seg(t, 86.0 + E, 87.0 + E)
    up_l = lerp(up_l, 60, end_k)
    up_r = lerp(up_r, 60, end_k)
    el_l = lerp(el_l, 15, end_k)
    el_r = lerp(el_r, 15, end_k)
    up_l = lerp(up_l, -70, bow)
    up_r = lerp(up_r, -70, bow)
    el_l = lerp(el_l, 0, bow)
    el_r = lerp(el_r, 0, bow)

    arms = [arm(-1, up_l, el_l), arm(1, up_r, el_r)]

    # ---- 훌라후프
    R = 105
    # 높이: 기본 허리, 47~57초에 가슴/목까지 올라갔다 내려옴
    up_k = seg(t, 47, 50) * (1 - seg(t, 54, 57))
    waist_y = lerp(hip_y - 35, neck_y + 25, up_k)
    waist_x = lerp(hip_x, neck_x, up_k)
    body_r = lerp(26, 16, up_k)
    d = (R - body_r) * 0.55
    hoop_cx = waist_x + d * math.cos(th)
    hoop_cy = waist_y + d * 0.22 * math.sin(th)
    tilt = 0.08 * math.sin(th)

    # 0~3초: 위에서 떨어지며 허리에 걸림
    if t < 3.0:
        k = seg(t, 0.3, 2.6)
        bounce = math.sin(seg(t, 2.2, 3.0) * math.pi) * 8
        hoop_cy = lerp(-140, waist_y, k) - bounce
        hoop_cx = waist_x + d
        tilt = lerp(0.6, 0.0, k)
    # 끝: 바닥으로 떨어짐
    fall = seg(t, 85.8 + E, 87.2 + E)
    if fall > 0:
        hoop_cx = lerp(hoop_cx, base_x, fall)
        hoop_cy = lerp(hoop_cy, GROUND_Y + 2, fall * fall)
        tilt = lerp(tilt, 0.0, fall)
    hoop = dict(cx=hoop_cx, cy=hoop_cy, R=R, squash=lerp(0.22, 0.12, fall), tilt=tilt, th=th)

    # ---- 팔 후프 (75~85초)
    arm_hoop = None
    if trick_k > 0.02:
        (_, (ex, ey), (hx, hy)) = arms[1]
        ax, ay = lerp(ex, hx, 0.55), lerp(ey, hy, 0.55)
        a_th = th * 1.5
        arm_hoop = dict(cx=ax + 38 * math.cos(a_th), cy=ay, R=55, squash=0.3,
                        tilt=0.0, th=a_th, alpha=trick_k)

    return dict(head=(head_x, head_y, head_r), neck=(neck_x, neck_y), hip=(hip_x, hip_y),
                legs=legs, arms=arms, hoop=hoop, arm_hoop=arm_hoop, base_x=base_x, bow=bow,
                jump_h=jump_h, hat=seg(t, 100.8, 101.8), tip=tip)


# ------------------------------------------------------------ 그리기
def S(p):
    return (p[0] * SS, p[1] * SS)


def thick_line(dr, pts, width, col):
    w = int(width * SS)
    pts2 = [S(p) for p in pts]
    dr.line(pts2, fill=col, width=w, joint="curve")
    r = w / 2
    for x, y in (pts2[0], pts2[-1]):
        dr.ellipse([x - r, y - r, x + r, y + r], fill=col)


def hoop_points(h, n=120):
    pts = []
    c, s = math.cos(h["tilt"]), math.sin(h["tilt"])
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        x = h["R"] * math.cos(a)
        y = h["R"] * h["squash"] * math.sin(a)
        depth = math.sin(a)  # >0 이면 앞쪽(관객 쪽)
        pts.append((h["cx"] + x * c - y * s, h["cy"] + x * s + y * c, depth))
    return pts


def draw_hoop(dr, h, col, front, width=9):
    pts = hoop_points(h)
    w = int(width * SS)
    stripe = mix_col(col, (255, 255, 255), 0.55)
    for i in range(len(pts) - 1):
        (x1, y1, d1), (x2, y2, d2) = pts[i], pts[i + 1]
        dm = (d1 + d2) / 2
        if (dm >= 0) != front:
            continue
        a = 2 * math.pi * i / (len(pts) - 1)
        # 회전하는 줄무늬 (후프가 도는 느낌)
        striped = int(((a - h["th"] * 0.5) / (2 * math.pi) * 12) % 2) == 0
        c = col if striped else stripe
        if not front:
            c = mix_col(c, (120, 120, 120), 0.25)
        dr.line([S((x1, y1)), S((x2, y2))], fill=c, width=w)
        r = w / 2
        X, Y = S((x2, y2))
        dr.ellipse([X - r, Y - r, X + r, Y + r], fill=c)


def draw_figure(dr, p):
    for leg in p["legs"]:
        thick_line(dr, leg, 9, INK)
    thick_line(dr, [p["hip"], p["neck"]], 9, INK)
    for a in p["arms"]:
        thick_line(dr, a, 8, INK)
    hx, hy, hr = p["head"]
    dr.ellipse([S((hx - hr, hy - hr)), S((hx + hr, hy + hr))], fill=INK)
    # 문워크 중절모 (위에서 떨어져 머리에 쏙)
    if p["hat"] > 0:
        k = p["hat"]
        top = hy - hr * 0.55 - (1 - k) * 420
        hat_col, band = (55, 55, 65), (240, 240, 240)
        dr.rounded_rectangle([S((hx - 38, top - 44)), S((hx + 38, top))], radius=10 * SS, fill=hat_col)
        dr.rectangle([S((hx - 38, top - 14)), S((hx + 38, top - 5))], fill=band)
        dr.rounded_rectangle([S((hx - 66, top - 6)), S((hx + 66, top + 5))], radius=5 * SS, fill=hat_col)


def make_background():
    img = Image.new("RGB", (W * SS, H * SS))
    top, bot = np.array([200, 232, 255], float), np.array([255, 248, 230], float)
    k = np.linspace(0, 1, GROUND_Y * SS)[:, None]
    sky = (top * (1 - k) + bot * k).astype(np.uint8)
    arr = np.zeros((H * SS, W * SS, 3), np.uint8)
    arr[: GROUND_Y * SS] = sky[:, None, :]
    arr[GROUND_Y * SS:] = (225, 210, 180)
    img = Image.fromarray(arr)
    dr = ImageDraw.Draw(img)
    dr.line([S((0, GROUND_Y)), S((W, GROUND_Y))], fill=(150, 130, 100), width=3 * SS)
    # 구름
    for cx, cy, s in [(200, 120, 1.0), (980, 90, 1.3), (640, 170, 0.7)]:
        for dx, dy, r in [(-40, 10, 35), (0, 0, 48), (45, 8, 38), (85, 15, 28)]:
            x, y, rr = cx + dx * s, cy + dy * s, r * s
            dr.ellipse([S((x - rr, y - rr)), S((x + rr, y + rr))], fill=(255, 255, 255))
    return img


BG = make_background()


def load_font(size):
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(f):
            return ImageFont.truetype(f, size * SS)
    return ImageFont.load_default()


FONT = load_font(34)
FONT_BIG = load_font(70)


def render(i):
    t = i * dt
    th = theta[i]
    p = pose(t, th)
    img = BG.copy()
    dr = ImageDraw.Draw(img)

    # 그림자
    bx = p["base_x"]
    sh = 1 - clamp(p["jump_h"] / 300) * 0.6  # 높이 뛸수록 그림자 작게
    dr.ellipse([S((bx - 110 * sh, GROUND_Y - 10 * sh)), S((bx + 110 * sh, GROUND_Y + 12 * sh))],
               fill=(200, 185, 155))

    col = hoop_color(t)
    sp = hoop_speed(t)
    # 빠를 때 잔상
    ghosts = []
    if sp > 1.2:
        for g in range(1, 4):
            gth = th - g * 0.35
            gp = pose(t, gth)
            ghosts.append((gp["hoop"], mix_col(col, (255, 255, 255), 0.45 + 0.15 * g)))

    for gh, gc in ghosts:
        draw_hoop(dr, gh, gc, front=False, width=6)
    draw_hoop(dr, p["hoop"], col, front=False)
    if p["arm_hoop"]:
        draw_hoop(dr, p["arm_hoop"], (255, 200, 0), front=False, width=7)
    draw_figure(dr, p)
    for gh, gc in ghosts:
        draw_hoop(dr, gh, gc, front=True, width=6)
    draw_hoop(dr, p["hoop"], col, front=True)
    if p["arm_hoop"]:
        draw_hoop(dr, p["arm_hoop"], (255, 200, 0), front=True, width=7)

    # 회전 수 카운터 + 남은 시간
    spins = int(th / (2 * math.pi))
    dr.text((S((W - 40, 36))), f"SPINS {spins}", font=FONT, fill=(40, 40, 40), anchor="ra")
    remain = max(0, int(math.ceil(DURATION - t)))
    dr.text((S((40, 36))), f"{remain // 60}:{remain % 60:02d}", font=FONT, fill=(40, 40, 40), anchor="la")

    # 시작 카운트다운 & 엔딩 문구
    if t < 2.6:
        n = 3 - int(t / 0.87)
        dr.text(S((W / 2, 110)), str(max(1, n)), font=FONT_BIG, fill=(235, 64, 52), anchor="mm")
    if t > 87.5 + E:
        a = seg(t, 87.5 + E, 88.2 + E)
        dr.text(S((W / 2, 120)), f"{spins} SPINS!", font=FONT_BIG,
                fill=mix_col((255, 248, 235), (235, 64, 52), a), anchor="mm")

    img = img.resize((W, H), Image.LANCZOS)
    # 마지막 0.6초 페이드아웃
    fo = seg(t, DURATION - 0.6, DURATION)
    if fo > 0:
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), fo)
    return img


# ------------------------------------------------------------ 음악 합성
def make_music(path):
    sr = 44100
    n = int(sr * DURATION)
    out = np.zeros(n)
    beat_len = 60.0 / BPM
    tt = np.arange(int(sr * 0.5)) / sr

    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
    rng = np.random.default_rng(1)
    hat = rng.standard_normal(len(tt)) * np.exp(-tt * 60) * 0.25
    snare = (rng.standard_normal(len(tt)) * 0.5 + np.sin(2 * np.pi * 190 * tt)) * np.exp(-tt * 18) * 0.45

    def add(sample, start, gain=1.0):
        s = int(start * sr)
        e = min(n, s + len(sample))
        if s < n:
            out[s:e] += sample[: e - s] * gain

    # 코드 진행 (C - Am - F - G), 베이스 + 멜로디 (펜타토닉)
    roots = [130.81, 110.0, 87.31, 98.0]
    scale = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25]
    mel = [0, 2, 3, 2, 4, 3, 2, 0, 1, 2, 3, 5, 4, 3, 2, 1]
    note_t = np.arange(int(sr * beat_len / 2)) / sr
    env = np.exp(-note_t * 6)

    beats = int(DURATION / beat_len)
    for b in range(beats):
        start = b * beat_len
        if start < 3.0 or start > 86.5 + E:
            # 시작/끝은 하이햇만
            if start <= 88 + E:
                add(hat, start, 0.6)
            continue
        intense = 1.0 + (0.4 if 75 <= start < 100 else 0)
        add(kick, start, 0.9)
        if b % 2 == 1:
            add(snare, start, 0.7 * intense)
        add(hat, start + beat_len / 2, 0.8)
        if intense > 1:
            add(hat, start + beat_len / 4, 0.5)
            add(hat, start + 3 * beat_len / 4, 0.5)
        root = roots[(b // 4) % 4]
        bass = np.sign(np.sin(2 * np.pi * root * note_t)) * env * 0.18
        add(bass, start)
        add(bass, start + beat_len / 2, 0.8)
        if start >= 6.0:
            for half in range(2):
                f = scale[mel[(b * 2 + half) % len(mel)]]
                tone = (np.sin(2 * np.pi * f * note_t) + 0.3 * np.sin(4 * np.pi * f * note_t)) * env * 0.16
                add(tone, start + half * beat_len / 2)

    # 엔딩 코드
    end_t = np.arange(int(sr * 2.5)) / sr
    chord = sum(np.sin(2 * np.pi * f * end_t) for f in [261.63, 329.63, 392.0, 523.25])
    add(chord * np.exp(-end_t * 1.5) * 0.12, 87.3 + E)

    # 점프 효과음 (뛰어오를 때 '뿅')
    def boing(length, f0, f1, gain):
        bt = np.arange(int(sr * length)) / sr
        f = np.linspace(f0, f1, len(bt))
        return np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-bt * 4 / length) * gain

    for k in range(6):
        add(boing(0.25, 300, 700, 0.25), 86.0 + k * 1.0 + 0.25)
    for k in range(4):
        add(boing(0.5, 250, 900, 0.3), 92.0 + k * 1.5 + 0.375)
    add(boing(1.2, 200, 1400, 0.35), 98.0 + 0.4)

    fade = np.ones(n)
    fl = int(sr * 0.6)
    fade[-fl:] = np.linspace(1, 0, fl)
    out *= fade
    out = out / max(1e-9, np.max(np.abs(out))) * 0.85
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def main():
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    tmpdir = tempfile.mkdtemp()
    wav = os.path.join(tmpdir, "music.wav")
    make_music(wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", OUT]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(N):
        proc.stdin.write(render(i).tobytes())
        if i % 300 == 0:
            print(f"{i}/{N} frames", flush=True)
    proc.stdin.close()
    proc.wait()
    print("done:", OUT)


if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        for ts in map(float, os.environ["PREVIEW"].split(",")):
            render(int(ts * FPS)).save(f"{OUT}.{ts:g}.png")
    else:
        main()
