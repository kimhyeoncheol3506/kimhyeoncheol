"""마스코트 동작 연출 (v1.14.0): 자세와 자세 사이를 부드럽게 이어 주는 키프레임 보간.

    from studio.mascot_anim import render_clip
    frames = render_clip([("기본", 0.0), ("고민", 1.0), ("놀람", 2.2)], seconds=3.5, fps=30, height=900)

각 키프레임은 (자세 이름 또는 pose dict, 시작 시각). 숫자·좌표는 완만하게(ease) 이어지고,
입 모양·소품처럼 바뀌는 값은 중간 지점에서 바뀐다. 기본으로 숨쉬기·깜빡임·더듬이 흔들림이 얹힌다.
"""
import math
from .mascot import POSES, draw_ant

NEUTRAL = dict(mouth="smile", brows=None, hand_l=(266, 790), hand_r=(534, 790),
               look=(0, 0), eye_open=1.0, head_tilt=0, bob=0, antenna=0)


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _mix(a, b, k):
    out = {}
    for key in set(a) | set(b):
        va, vb = a.get(key, NEUTRAL.get(key)), b.get(key, NEUTRAL.get(key))
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
            out[key] = va + (vb - va) * k
        elif isinstance(va, tuple) and isinstance(vb, tuple) and len(va) == len(vb):
            out[key] = tuple(x + (y - x) * k for x, y in zip(va, vb))
        elif va is None and isinstance(vb, tuple):
            out[key] = tuple(vb) if k > 0.5 else None
        else:
            out[key] = vb if k >= 0.5 else va
    return out


def pose_at(keys, t):
    keys = [(POSES[p] if isinstance(p, str) else p, ts) for p, ts in keys]
    if t <= keys[0][1]:
        return dict(keys[0][0])
    for (pa, ta), (pb, tb) in zip(keys, keys[1:]):
        if ta <= t < tb:
            return _mix(pa, pb, _ease((t - ta) / max(1e-6, tb - ta)))
    return dict(keys[-1][0])


def render_clip(keys, seconds, fps=30, height=900, blink_every=3.1):
    frames = []
    for f in range(int(seconds * fps)):
        t = f / fps
        p = pose_at(keys, t)
        p["bob"] = p.get("bob", 0) + 4 * math.sin(t * 2 * math.pi * 0.7)
        p["antenna"] = p.get("antenna", 0) + 8 * math.sin(t * 2 * math.pi * 1.2)
        ph = t % blink_every
        if ph < 0.12 and not p.get("happy_eyes"):
            p["eye_open"] = 0.05
        frames.append(draw_ant(p, height))
    return frames
