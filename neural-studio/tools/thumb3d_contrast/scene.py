"""썸네일 '3D 대비형' — Blender 장면 (투명 배경 PNG 레이어 + 배치 정보 JSON).

make.py 가 부른다. 직접 돌릴 때:
  BL=/home/user/ext/blender-4.5.9-linux-x64/blender
  $BL -b -t 2 -P tools/thumb3d_contrast/scene.py -- --cfg 설정.json --out layer.png [--res 1920x1080] [--samples 40]
  → layer.png (투명) + layer.json (숫자 글자 상자 위치 px: 꼬리표·개미를 HTML 에서 얹을 때 씀)

화면 좌표: 직교 카메라, 1920×1080 기준 1 단위 = 100px.  px(x, y) → 월드 ((x-960)/100, 0, (540-y)/100)
그리는 것: 위 2줄 남색 3D 제목(흰 테) · 가운데 빨강/남색 3D 숫자 2개(흰 테) · 'arrow' 일 때 가운데 3D 화살표 · 양쪽 아래 구석 3D 소품.
(유리 구슬·'vs'·꼬리표·개미·바탕은 make.py 의 HTML 쪽)

소품 이름(PROPS): coins · cash · building · shield · oil · drums · pumpjack · chart_down · chart_up · vault · watch · pill · peso
  설정의 props_left / props_right 에 이름(문자열) 또는 {"name":..,"x":..,"y":..,"s":..,"symbol":"¥"} 로 적는다.
"""
import argparse
import json
import math
import os
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = [os.path.join(HERE, "..", "..", "assets", "fonts", "BlackHanSans.ttf"),
         "/home/user/hf/thumb/assets/fonts/BlackHanSans-Regular.ttf"]
SYM_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # ¥ ₩ $ € (Black Han Sans 에 없음)

# ── 배치(1920×1080 px) ─────────────────────────────────────────────
LAYOUT = {
    "title1": dict(c=(960, 172), maxw=1640, maxh=172, depth=0.36),
    "title2": dict(c=(960, 352), maxw=1830, maxh=104, depth=0.24),
    "left": dict(c=(540, 725), maxw=660, maxh=330, depth=0.6),
    "right": dict(c=(1440, 735), maxw=600, maxh=380, depth=0.6),
    "arrow": dict(c=(950, 690), w=240),
}
SLOTS = {  # 소품 기본 자리 (순서대로: 뒤 → 앞)
    "left": [(110, 900, 1.05), (235, 1010, 0.8), (340, 1040, 0.5)],
    "right": [(1765, 1010, 0.85), (1868, 1005, 0.55), (1690, 1040, 0.5)],
}
COL = {
    "navy": (0.008, 0.05, 0.26),
    "red": (0.72, 0.004, 0.006),
    "gray": (0.32, 0.34, 0.38),
}


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--samples", type=int, default=40)
    return ap.parse_args(argv)


def rot3(tx, tz, stand=0):
    """세우기(X stand°) → 세로축 돌리기(Z tz°) → 카메라 쪽 기울이기(X tx°). 옆으로 눕지 않게 행렬로 합성."""
    R = (Matrix.Rotation(math.radians(tx), 4, "X") @ Matrix.Rotation(math.radians(tz), 4, "Z")
         @ Matrix.Rotation(math.radians(stand), 4, "X"))
    return R.to_euler()


def W(x_px, y_px):
    return ((x_px - 960) / 100.0, (540 - y_px) / 100.0)


# ── 재질 ──────────────────────────────────────────────────────────
_M = {}


def mat(name, rgb, metallic=0.0, rough=0.3, coat=0.0, emit=0.0, spec=None):
    key = (name, rgb, metallic, rough, coat, emit)
    if key in _M:
        return _M[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if spec is not None:
        b.inputs["Specular IOR Level"].default_value = spec
    if coat:
        b.inputs["Coat Weight"].default_value = coat
        b.inputs["Coat Roughness"].default_value = 0.08
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    _M[key] = m
    return m


def M():
    return dict(
        navy=mat("navy", COL["navy"], 0.3, 0.3, coat=0.5),
        navyt=mat("navyt", (0.012, 0.075, 0.33), 0.0, 0.55, coat=0.0, spec=0.25),
        red=mat("red", COL["red"], 0.15, 0.28, coat=0.6),
        gray=mat("gray", COL["gray"], 0.2, 0.3, coat=0.8),
        white=mat("white", (0.96, 0.96, 0.98), 0.0, 0.35, coat=0.4, emit=0.35),
        gold=mat("gold", (1.0, 0.68, 0.22), 1.0, 0.28),
        golddark=mat("golddark", (0.75, 0.45, 0.10), 1.0, 0.35),
        green=mat("green", (0.10, 0.42, 0.20), 0.0, 0.45, coat=0.3),
        greenl=mat("greenl", (0.45, 0.72, 0.45), 0.0, 0.5),
        paper=mat("paper", (0.93, 0.86, 0.62), 0.0, 0.5),
        concrete=mat("concrete", (0.62, 0.62, 0.64), 0.0, 0.6),
        concrete2=mat("concrete2", (0.48, 0.48, 0.50), 0.0, 0.6),
        window=mat("window", (0.08, 0.16, 0.30), 0.3, 0.15, coat=1.0),
        dark=mat("dark", (0.03, 0.03, 0.04), 0.0, 0.5),
        blue=mat("blue", (0.05, 0.25, 0.75), 0.2, 0.25, coat=1.0),
        steel=mat("steel", (0.55, 0.58, 0.62), 0.85, 0.32),
        steeld=mat("steeld", (0.25, 0.27, 0.30), 0.85, 0.35),
        drum=mat("drum", (0.06, 0.12, 0.30), 0.4, 0.3, coat=0.8),
        drumr=mat("drumr", (0.70, 0.08, 0.05), 0.3, 0.3, coat=0.8),
        black=mat("black", (0.04, 0.04, 0.05), 0.4, 0.35, coat=0.6),
        orange=mat("orange", (0.95, 0.45, 0.05), 0.1, 0.35, coat=0.6),
        redg=mat("redg", (0.85, 0.05, 0.04), 0.1, 0.25, coat=1.0),
        greeng=mat("greeng", (0.05, 0.62, 0.22), 0.1, 0.25, coat=1.0),
        brown=mat("brown", (0.18, 0.08, 0.03), 0.0, 0.45),
        face=mat("face", (0.97, 0.97, 0.95), 0.0, 0.3, emit=0.2),
        peso=mat("peso", (0.42, 0.62, 0.80), 0.0, 0.5),
        pesob=mat("pesob", (0.30, 0.45, 0.65), 0.0, 0.5),
        purple=mat("purple", (0.55, 0.30, 0.65), 0.0, 0.5),
    )


# ── 글자 ──────────────────────────────────────────────────────────
def world_bbox(objs):
    bpy.context.view_layer.update()
    xs, zs = [], []
    for o in objs:
        for c in o.bound_box:
            v = o.matrix_world @ Vector(c)
            xs.append(v.x)
            zs.append(v.z)
    return min(xs), max(xs), min(zs), max(zs)


def to_px(bb):
    x0, x1, z0, z1 = bb
    return [x0 * 100 + 960, 540 - z1 * 100, x1 * 100 + 960, 540 - z0 * 100]  # left, top, right, bottom


def text3d(body, fnt, lay, face, rim, rim_w, tilt=(-9, 10), bevel=0.14, spacing=0.98):
    """자동 크기 맞춤 3D 글자 + 뒤에 깐 흰 테. tilt=(x축, z축 회전 도) — 돌출 옆면이 오른쪽 아래로 보이게."""
    bpy.ops.object.text_add(location=(0, 0, 0))
    t = bpy.context.object
    t.data.body = body
    t.data.font = fnt
    t.data.size = 1.0
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.space_character = spacing
    t.data.extrude = lay["depth"]
    t.data.bevel_depth = lay["depth"] * bevel
    t.data.bevel_resolution = 3
    t.data.materials.append(face)
    t.rotation_euler = rot3(tilt[0], tilt[1], 90)
    bpy.context.view_layer.update()
    x0, x1, z0, z1 = world_bbox([t])
    k = min(lay["maxw"] / 100 / (x1 - x0), lay["maxh"] / 100 / (z1 - z0))
    t.data.size = k
    t.data.extrude = lay["depth"]
    t.data.bevel_depth = lay["depth"] * bevel
    # 흰 테: 같은 글자를 두껍게(offset) 해서 뒤에
    o = t.copy()
    o.data = t.data.copy()
    o.data.offset = 0  # offset 은 일부 글자(몰·디)에서 구멍이 생겨, 둥근 베벨로 바깥 테를 만든다
    o.data.bevel_depth = rim_w
    o.data.bevel_resolution = 2
    o.data.extrude = lay["depth"] * 0.5
    o.data.materials.clear()
    o.data.materials.append(rim)
    bpy.context.collection.objects.link(o)
    o.location = (0, lay["depth"] * 1.2, 0)
    bpy.context.view_layer.update()
    x0, x1, z0, z1 = world_bbox([t])
    cx, cz = W(*lay["c"])
    dx, dz = cx - (x0 + x1) / 2, cz - (z0 + z1) / 2
    for ob in (t, o):
        ob.location.x += dx
        ob.location.z += dz
    return t, o


# ── 도형 도우미 ────────────────────────────────────────────────────
def box(loc, size, m, bevel=0.04, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=[math.radians(a) for a in rot])
    c = bpy.context.object
    c.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    if bevel:
        b = c.modifiers.new("b", "BEVEL")
        b.width, b.segments = bevel, 3
        b.limit_method = "NONE"
    c.data.materials.append(m)
    return c


def cyl(loc, r, d, m, rot=(0, 0, 0), bevel=0.02, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=verts, location=loc,
                                        rotation=[math.radians(a) for a in rot])
    c = bpy.context.object
    if bevel:
        b = c.modifiers.new("b", "BEVEL")
        b.width, b.segments = bevel, 2
        b.limit_method = "ANGLE"
    bpy.ops.object.shade_smooth()
    c.data.materials.append(m)
    return c


def sphere(loc, r, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    bpy.ops.object.shade_smooth()
    s = bpy.context.object
    s.data.materials.append(m)
    return s


def prism(pts, depth, m, y=0.0, bevel=0.03):
    """x-z 평면 다각형 pts 를 y 방향(카메라 쪽 앞면)으로 두께 depth 만큼 세운다."""
    me = bpy.data.meshes.new("prism")
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, z in pts]
    f = bm.faces.new(vs)
    bmesh.ops.recalc_face_normals(bm, faces=[f])
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=nv, vec=(0, depth, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("prism", me)
    bpy.context.collection.objects.link(o)
    if bevel:
        b = o.modifiers.new("b", "BEVEL")
        b.width, b.segments = bevel, 3
        b.limit_method = "ANGLE"
    o.data.materials.append(m)
    return o


def symbol(ch, loc, size, m, depth=0.04, rot=(90, 0, 0), fnt=None):
    bpy.ops.object.text_add(location=loc, rotation=[math.radians(a) for a in rot])
    t = bpy.context.object
    t.data.body = ch
    t.data.font = fnt or SYMF
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.extrude = depth
    t.data.bevel_depth = depth * 0.4
    t.data.materials.append(m)
    return t


class Group:
    """소품 하나: 원점 기준으로 만들고 끝에 위치·회전·크기를 한꺼번에."""

    def __enter__(self):
        self.before = set(bpy.data.objects)
        return self

    def __exit__(self, *a):
        self.objs = [o for o in bpy.data.objects if o not in self.before]

    def place(self, x_px, y_px, s, rot=(18, 0, -16)):
        bpy.ops.object.empty_add(location=(0, 0, 0))
        e = bpy.context.object
        for o in self.objs:
            o.parent = e
        e.rotation_euler = rot3(rot[0], rot[2])
        e.scale = (s, s, s)
        bpy.context.view_layer.update()
        # 소품의 화면상 바닥 가운데를 (x_px, y_px) 에
        x0, x1, z0, z1 = world_bbox(self.objs)
        tx, tz = W(x_px, y_px)
        e.location = (tx - (x0 + x1) / 2, -2.0, tz - z0)
        return e


# ── 소품 ──────────────────────────────────────────────────────────
def p_coins(mm, symbol_ch="$", **_):
    with Group() as g:
        r, d = 0.62, 0.15
        for sx, sy, n in ((-0.75, 0.35, 7), (0.55, 0.55, 5), (0.0, -0.45, 3)):
            for i in range(n):
                cyl((sx + (i % 2) * 0.03, sy, d / 2 + i * d * 1.02), r, d, mm["gold"], bevel=0.03)
        # 앞에 세운 동전 + 기호
        cyl((0.95, -0.9, 0.62), 0.62, 0.16, mm["gold"], rot=(90, 0, 0), bevel=0.035)
        cyl((0.95, -0.99, 0.62), 0.47, 0.02, mm["golddark"], rot=(90, 0, 0), bevel=0)
        symbol(symbol_ch, (0.95, -1.01, 0.60), 0.62, mm["gold"], depth=0.03)
    return g


def p_cash(mm, **_):
    with Group() as g:
        for i, (dx, dy, rz) in enumerate(((0, 0, 0), (0.12, -0.08, 6), (-0.1, 0.05, -5), (0.05, -0.1, 3))):
            z = 0.2 + i * 0.4
            box((dx, dy, z), (2.5, 1.15, 0.38), mm["green"], bevel=0.03, rot=(0, 0, rz))
            box((dx, dy, z), (0.42, 1.19, 0.41), mm["paper"], bevel=0.01, rot=(0, 0, rz))
            box((dx - 0.75, dy - 0.58, z), (0.55, 0.02, 0.2), mm["greenl"], bevel=0, rot=(0, 0, rz))
    return g


def p_peso(mm, **_):  # 하늘색 페소 지폐 다발
    with Group() as g:
        for i, (dx, dy, rz) in enumerate(((0, 0, 0), (0.15, -0.1, 7), (-0.12, 0.05, -6), (0.06, -0.06, 2), (-0.05, 0.02, -3))):
            z = 0.2 + i * 0.4
            box((dx, dy, z), (2.4, 1.1, 0.38), mm["peso"] if i % 2 == 0 else mm["pesob"], bevel=0.03, rot=(0, 0, rz))
            box((dx, dy, z), (0.4, 1.14, 0.41), mm["paper"], bevel=0.01, rot=(0, 0, rz))
    return g


def p_building(mm, **_):
    with Group() as g:
        w, d, h = 1.8, 1.3, 3.6
        me = bpy.data.meshes.new("bld")
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= w
            v.co.y *= d
            v.co.z = (v.co.z + 0.5) * h
            if v.co.z > h * 0.9 and v.co.x > 0:  # 윗부분 비스듬히 잘림
                v.co.z = h * 0.70
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("bld", me)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(mm["concrete"])
        o.modifiers.new("b", "BEVEL").width = 0.03
        # 창문 격자 (앞면·옆면)
        for col in range(4):
            for row in range(8):
                x = -w / 2 + 0.28 + col * 0.42
                z = 0.35 + row * 0.42
                top = h if x < 0 else h * 0.70 - (x / (w / 2)) * 0.0
                if z + 0.3 > (h if x + 0.1 < 0 else h * 0.70 + (w / 2 - x) / w * h * 0.25) - 0.05:
                    continue
                box((x, -d / 2 - 0.01, z), (0.24, 0.04, 0.28), mm["window"], bevel=0.01)
        for col in range(3):
            for row in range(5):
                box((w / 2 + 0.01, -d / 2 + 0.3 + col * 0.38, 0.35 + row * 0.42), (0.04, 0.2, 0.28), mm["window"], bevel=0.01)
        # 금(균열): 앞면에 지그재그 검은 선
        crack = [(0.1, 2.9), (-0.15, 2.4), (0.15, 2.0), (-0.1, 1.5), (0.1, 1.15)]
        for (x1, z1), (x2, z2) in zip(crack, crack[1:]):
            L = math.hypot(x2 - x1, z2 - z1)
            ang = math.degrees(math.atan2(z2 - z1, x2 - x1))
            box(((x1 + x2) / 2, -d / 2 - 0.03, (z1 + z2) / 2), (L, 0.04, 0.07), mm["dark"], bevel=0, rot=(0, -ang, 0))
        # 떨어진 조각
        box((w / 2 + 0.35, -0.5, 0.15), (0.35, 0.3, 0.28), mm["concrete2"], rot=(10, 20, 35))
        box((w / 2 + 0.75, -0.9, 0.1), (0.22, 0.2, 0.18), mm["concrete2"], rot=(30, 10, 10))
        box((-w / 2 - 0.2, -0.8, 0.08), (0.16, 0.15, 0.14), mm["concrete2"], rot=(20, 40, 5))
    return g


def shield_pts(sc=1.0):
    pts = []
    for i in range(0, 11):  # 위 가장자리(살짝 볼록)
        t = i / 10
        pts.append(((-1 + 2 * t) * sc, (1.2 + 0.12 * math.sin(math.pi * t)) * sc))
    right = []
    for i in range(1, 17):  # 오른쪽: 곧게 → 곡선으로 아래 꼭짓점
        t = i / 16
        x = 1.0 - (t ** 1.8)
        z = 1.2 - 2.65 * t
        right.append((x * sc, z * sc))
    right[-1] = (0, right[-1][1])
    pts += right
    pts += [(-x, z) for x, z in reversed(right[:-1])]
    return pts


def p_shield(mm, symbol_ch="₩", **_):
    with Group() as g:
        prism(shield_pts(1.13), 0.30, mm["gold"], y=-0.10, bevel=0.06)
        prism(shield_pts(1.0), 0.30, mm["blue"], y=-0.28, bevel=0.06)
        symbol(symbol_ch, (0, -0.35, -0.05), 1.35, mm["white"], depth=0.07)
    return g


def p_drums(mm, **_):
    with Group() as g:
        for (x, y, z, m, rot) in ((-0.7, 0.3, 0.9, "drum", (0, 0, 0)), (0.75, 0.0, 0.9, "drumr", (0, 0, 0)),
                                  (0.1, -1.0, 0.62, "drum", (0, 90, 25))):
            c = cyl((x, y, z), 0.62, 1.8, mm[m], rot=rot, bevel=0.03)
            for k in (-0.55, 0.0, 0.55):
                v = Vector((0, 0, k))
                v.rotate(c.rotation_euler)
                cyl((x + v.x, y + v.y, z + v.z), 0.645, 0.07, mm["black"], rot=rot, bevel=0.01)
            v = Vector((0, 0, 0.91))
            v.rotate(c.rotation_euler)
            cyl((x + v.x, y + v.y, z + v.z), 0.5, 0.03, mm["steeld"], rot=rot, bevel=0)
    return g


def p_pumpjack(mm, **_):
    with Group() as g:
        box((0, 0, 0.1), (3.0, 0.9, 0.2), mm["steeld"])
        for s in (-1, 1):  # A자 기둥
            box((0.15 + s * 0.35, 0, 1.0), (0.14, 0.14, 1.9), mm["black"], rot=(0, s * 12, 0))
        bm_ = box((0.15, 0, 1.95), (3.0, 0.22, 0.26), mm["black"], rot=(0, -8, 0))
        # 말머리(오른쪽 끝)
        hp = [(0, 0.35), (0.35, 0.25), (0.55, -0.1), (0.5, -0.55), (0.2, -0.7), (0, -0.2)]
        h = prism([(x + 1.55, z + 2.15) for x, z in hp], 0.32, mm["orange"], y=-0.16)
        h.rotation_euler = (0, math.radians(-8), 0)
        h.location = (0.15 - 0.3, 0, 0.2)
        # 평형추(왼쪽)
        cyl((-1.2, 0, 1.5), 0.42, 0.25, mm["orange"], rot=(90, 0, 0))
        box((1.5, 0, 0.9), (0.06, 0.06, 1.0), mm["steeld"], bevel=0)  # 막대
        cyl((1.5, -0.1, 0.3), 0.2, 0.3, mm["steeld"])
        _ = bm_
    return g


def arrow_pts(L=3.0, t=0.55, hw=1.25, hl=1.1):
    return [(0, t / 2), (L - hl, t / 2), (L - hl, hw / 2), (L, 0), (L - hl, -hw / 2), (L - hl, -t / 2), (0, -t / 2)]


def p_chart(mm, down=True, **_):
    with Group() as g:
        # 꺾인 선(굵은 띠) + 화살촉
        pts = [(-1.6, 1.4), (-0.7, 0.4), (0.0, 0.9), (1.0, -0.6)] if down else [(-1.6, -0.6), (-0.7, 0.4), (0.0, -0.1), (1.0, 1.4)]
        m = mm["redg"] if down else mm["greeng"]
        for (x1, z1), (x2, z2) in zip(pts, pts[1:]):
            L = math.hypot(x2 - x1, z2 - z1)
            ang = math.degrees(math.atan2(z2 - z1, x2 - x1))
            box(((x1 + x2) / 2, 0, (z1 + z2) / 2), (L + 0.3, 0.4, 0.38), m, bevel=0.05, rot=(0, -ang, 0))
        x1, z1 = pts[-2]
        x2, z2 = pts[-1]
        ang = math.atan2(z2 - z1, x2 - x1)
        head = [(0, 0.55), (0.75, 0), (0, -0.55)]
        hp = [(x2 + px_ * math.cos(ang) - pz * math.sin(ang), z2 + px_ * math.sin(ang) + pz * math.cos(ang)) for px_, pz in head]
        prism(hp, 0.4, m, y=-0.2, bevel=0.05)
        # 바닥 막대그래프(옅게)
        for i, hh in enumerate((1.6, 1.2, 1.4, 0.7) if down else (0.6, 1.0, 0.9, 1.6)):
            box((-1.5 + i * 0.85, 0.5, -1.2 + hh / 2), (0.55, 0.5, hh), mm["concrete"], bevel=0.04)
    return g


def p_vault(mm, **_):
    with Group() as g:
        box((0, 0, 1.25), (2.4, 2.0, 2.3), mm["steel"], bevel=0.12)
        for s in (-1, 1):
            box((s * 0.9, 0, 0.06), (0.35, 1.6, 0.14), mm["steeld"])
        cyl((0, -1.02, 1.25), 0.85, 0.12, mm["steeld"], rot=(90, 0, 0), bevel=0.03)
        cyl((0, -1.1, 1.25), 0.72, 0.08, mm["steel"], rot=(90, 0, 0), bevel=0.02)
        for k in range(8):  # 볼트
            a = k * math.pi / 4
            sphere((0.78 * math.cos(a), -1.1, 1.25 + 0.78 * math.sin(a)), 0.06, mm["gold"])
        cyl((0, -1.2, 1.25), 0.14, 0.18, mm["gold"], rot=(90, 0, 0))
        for k in range(3):  # 손잡이 바퀴살
            box((0, -1.24, 1.25), (0.95, 0.06, 0.07), mm["gold"], bevel=0.02, rot=(0, k * 60, 0))
        for z in (0.55, 1.95):  # 경첩
            cyl((1.22, -0.7, z), 0.1, 0.4, mm["steeld"])
    return g


def p_watch(mm, **_):
    with Group() as g:
        box((0, 0.05, 1.95), (0.75, 0.2, 1.1), mm["brown"], bevel=0.08)  # 줄 위
        box((0, 0.05, -0.15), (0.75, 0.2, 1.1), mm["brown"], bevel=0.08)  # 줄 아래
        cyl((0, 0, 0.9), 0.75, 0.3, mm["gold"], rot=(90, 0, 0), bevel=0.06)
        cyl((0, -0.12, 0.9), 0.62, 0.1, mm["face"], rot=(90, 0, 0), bevel=0.01)
        cyl((0.8, 0, 0.9), 0.1, 0.18, mm["gold"], rot=(0, 90, 0))
        for k in range(12):
            a = k * math.pi / 6
            box((0.5 * math.cos(a), -0.18, 0.9 + 0.5 * math.sin(a)), (0.05, 0.02, 0.1 if k % 3 else 0.16), mm["dark"], bevel=0,
                rot=(0, -math.degrees(a) + 90, 0))
        box((0.12, -0.2, 1.05), (0.06, 0.02, 0.4), mm["dark"], bevel=0, rot=(0, 35, 0))
        box((0.2, -0.21, 0.85), (0.5, 0.02, 0.06), mm["dark"], bevel=0, rot=(0, 20, 0))
    return g


def p_pill(mm, **_):
    with Group() as g:
        for (x, z, rz) in ((0, 0.5, 30),):
            c1 = cyl((0, 0, -0.4), 0.42, 0.8, mm["redg"], bevel=0)
            s1 = sphere((0, 0, -0.8), 0.42, mm["redg"])
            c2 = cyl((0, 0, 0.4), 0.42, 0.8, mm["face"], bevel=0)
            s2 = sphere((0, 0, 0.8), 0.42, mm["face"])
            for o in (c1, s1, c2, s2):
                o.rotation_euler.rotate_axis("Y", math.radians(rz + 30))
                o.location.rotate(o.rotation_euler)
                o.location.x += x
                o.location.z += z + 0.9
    return g


PROPS = {
    "coins": (p_coins, dict()),
    "cash": (p_cash, dict()),
    "peso": (p_peso, dict()),
    "building": (p_building, dict(rot=(12, 0, -22))),
    "shield": (p_shield, dict(rot=(8, 0, -18))),
    "drums": (p_drums, dict()),
    "oil": (p_drums, dict()),
    "pumpjack": (p_pumpjack, dict(rot=(10, 0, -12))),
    "chart_down": (lambda mm, **k: p_chart(mm, True, **k), dict(rot=(10, 0, -14))),
    "chart_up": (lambda mm, **k: p_chart(mm, False, **k), dict(rot=(10, 0, -14))),
    "vault": (p_vault, dict(rot=(10, 0, -24))),
    "watch": (p_watch, dict(rot=(6, 0, -14))),
    "pill": (p_pill, dict(rot=(0, 0, 0))),
}
BASE_PX = 300  # 소품 크기 1.0 일 때 가로·세로 중 긴 쪽(px)


def build_prop(item, side, idx, mm):
    if isinstance(item, str):
        item = {"name": item}
    name = item["name"]
    fn, opt = PROPS[name]
    sx, sy, ss = SLOTS[side][min(idx, len(SLOTS[side]) - 1)]
    x, y, s = item.get("x", sx), item.get("y", sy), item.get("s", ss)
    kw = {}
    if "symbol" in item:
        kw["symbol_ch"] = item["symbol"]
    g = fn(mm, **kw)
    rot = list(item.get("rot", opt.get("rot", (18, 0, -16))))
    if side == "right" and "rot" not in item:
        rot[2] = -rot[2]  # 오른쪽 소품은 안쪽(가운데)을 보게
    # 크기: 그룹 높이를 BASE_PX*s 로 맞춤
    e = g.place(x, y, 1.0, rot)
    x0, x1, z0, z1 = world_bbox(g.objs)
    k = (BASE_PX * s / 100) / max(z1 - z0, x1 - x0, 0.01)
    e.scale = (k, k, k)
    g.place_e = e
    bpy.context.view_layer.update()
    x0, x1, z0, z1 = world_bbox(g.objs)
    tx, tz = W(x, y)
    e.location.x += tx - (x0 + x1) / 2
    e.location.z += tz - z0
    e.location.y = -3.0 - idx * 0.5  # 뒤에 놓인 것 먼저, 앞은 더 앞으로
    return to_px(world_bbox(g.objs))


# ── 장면 ──────────────────────────────────────────────────────────
def lights_world():
    for loc, en, sz, col in (((-8, -14, 9), 2600, 8, (1, 0.97, 0.92)),   # 키: 왼쪽 위 앞
                             ((9, -10, 3), 900, 6, (0.85, 0.9, 1.0)),     # 채움: 오른쪽
                             ((0, -12, -8), 500, 10, (1, 1, 1)),          # 아래 채움
                             ((2, 8, 8), 1500, 6, (1, 1, 1))):            # 뒤 림
        bpy.ops.object.light_add(type="AREA", location=loc)
        L = bpy.context.object
        L.data.energy, L.data.size, L.data.color = en, sz, col
        L.rotation_euler = (-L.location).to_track_quat("-Z", "Y").to_euler()
    world = bpy.data.worlds.new("w")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    ramp.color_ramp.elements[0].color = (0.25, 0.27, 0.32, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.28


def main():
    a = args()
    cfg = json.load(open(a.cfg, encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    w, h = map(int, a.res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    fnt = next(bpy.data.fonts.load(os.path.abspath(f)) for f in FONTS if os.path.exists(f))
    global SYMF
    SYMF = bpy.data.fonts.load(SYM_FONT)
    mm = M()
    lay = json.loads(json.dumps(LAYOUT))
    for k, v in cfg.get("layout", {}).items():  # 설정에서 배치 덮어쓰기
        lay[k].update(v)
    info = {}

    t, _ = text3d(cfg["title1"], fnt, lay["title1"], mm["navyt"], mm["white"], 0.085, tilt=(-7, -6))
    info["title1"] = to_px(world_bbox([t]))
    t, _ = text3d(cfg["title2"], fnt, lay["title2"], mm["navyt"], mm["white"], 0.065, tilt=(-7, -5))
    info["title2"] = to_px(world_bbox([t]))
    for side in ("left", "right"):
        s = cfg[side]
        t, _ = text3d(s["value"], fnt, lay[side], mm[s.get("color", "navy")], mm["white"], 0.07,
                      tilt=tuple(s.get("tilt", (-9, -15))), bevel=0.12, spacing=0.92)
        info[side] = to_px(world_bbox([t]))
    if cfg.get("connector") == "arrow":
        A = lay["arrow"]
        gap = info["right"][0] - info["left"][2]
        if "c" not in cfg.get("layout", {}).get("arrow", {}):  # 두 숫자 사이 가운데
            A["c"] = ((info["left"][2] + info["right"][0]) / 2 - 10, A["c"][1])
        L = min(A["w"], gap - 90) / 100
        pts = arrow_pts(L, 0.62, 1.5, 0.95)
        cx, cz = W(*A["c"])
        ar = prism([(x - L / 2 + cx, z + cz) for x, z in pts], 0.5, mm[cfg.get("arrow_color", "gray")], y=-0.25, bevel=0.06)
        rim = prism([(x - L / 2 + cx, z + cz) for x, z in arrow_pts(L + 0.2, 0.82, 1.82, 1.1)], 0.2, mm["white"], y=0.4, bevel=0.02)
        rim.location.x -= 0.1
        for o in (ar, rim):
            o.rotation_euler = rot3(-9, -15)
        info["arrow"] = to_px(world_bbox([ar]))
    info["props"] = []
    for side in ("left", "right"):
        for i, item in enumerate(cfg.get("props_" + side, [])):
            info["props"].append(build_prop(item, side, i, mm))

    bpy.ops.object.camera_add(location=(0, -60, 0), rotation=(math.radians(90), 0, 0))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 19.2
    cam.data.clip_end = 200
    sc.camera = cam
    lights_world()

    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = a.samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = os.path.abspath(a.out)
    json.dump(info, open(os.path.splitext(a.out)[0] + ".json", "w"), ensure_ascii=False, indent=1)
    if os.environ.get("NO_RENDER"):
        print("배치만:", info)
        return
    bpy.ops.render.render(write_still=True)
    print("저장:", sc.render.filepath)


SYMF = None
main()
