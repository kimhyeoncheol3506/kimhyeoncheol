"""34편 썸네일 3D판 (2026-11-13 현철님: 기존 A안 내용 그대로 + 'Blender 117만 원' 느낌, 그래픽 중시).
Blender 로 금빛 3D '연말정산' · 흰 3D '이 순서로 하세요' · 초록 3D 타일 '소득 › 공제 › 환급' · 동전을 투명 배경으로 렌더 →
make_thumb3d.py 가 남색 배경·광채·'2026년 귀속/미리 준비' 칩·개미(가리킴)를 얹어 1280×720 으로 마감.

  BL=/home/user/ext/blender-4.5.9-linux-x64/blender
  $BL -b -P projects/20261111-yearend-tax/thumb3d_blender.py -- --out thumbs/3d_layer.png [--res 1920x1080] [--samples 64]
좌표: 카메라 (0,-14,0.3) 40mm → 화면 가로 약 12.6 단위, 1단위 ≈ 152px(1080p). px→x=(px-960)/152, z=(540-py)/152+0.3
"""
import argparse
import math
import os
import random
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = [os.path.join(HERE, "..", "..", "..", "neural-studio", "assets", "fonts", "BlackHanSans.ttf"),
         "/home/user/hf/thumb/assets/fonts/BlackHanSans-Regular.ttf"]


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--samples", type=int, default=64)
    ap.add_argument("--seed", type=int, default=11)
    return ap.parse_args(argv)


def px(x_px, y_px):
    return (x_px - 960) / 152.0, (540 - y_px) / 152.0 + 0.3


def mat(name, rgb, metallic=1.0, rough=0.22, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    return m


def text(body, size, x_px, y_px, depth, m, fnt, y=0.0, bevel=0.18):
    x, z = px(x_px, y_px)
    bpy.ops.object.text_add(location=(x, y, z))
    t = bpy.context.object
    t.data.body = body
    t.data.font = fnt
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.extrude = depth
    t.data.bevel_depth = depth * bevel
    t.data.bevel_resolution = 4
    t.data.space_character = 0.96
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(m)
    return t


def outline(t, width, m, dy=0.06):
    """글자 뒤에 같은 글자를 width 만큼 두껍게(어두운 재질) 깔아 외곽선을 만든다 — 작은 화면에서도 글자가 또렷하게"""
    o = t.copy()
    o.data = t.data.copy()
    o.data.offset = width
    o.data.bevel_depth = 0
    o.data.extrude = t.data.extrude
    o.location.y += t.data.extrude + dy
    o.data.materials.clear()
    o.data.materials.append(m)
    bpy.context.collection.objects.link(o)
    return o


def tile(label, x_px, y_px, fnt, body_m, rim_m, txt_m, w=1.55, h=0.98):
    x, z = px(x_px, y_px)
    # 금테(뒤, 조금 크게) + 초록 몸통 + 흰 글자
    for (sx, sz, dy, m, d) in ((w + 0.16, h + 0.16, 0.12, rim_m, 0.22), (w, h, 0.0, body_m, 0.30)):
        bpy.ops.mesh.primitive_cube_add(location=(x, dy, z))
        c = bpy.context.object
        c.scale = (sx / 2, d / 2, sz / 2)
        bev = c.modifiers.new("b", "BEVEL")
        bev.width, bev.segments = 0.16, 6
        c.data.materials.append(m)
    t = text(label, 0.74, x_px, y_px + 4, 0.10, txt_m, fnt, y=-0.24, bevel=0.10)
    outline(t, 0.035, OUT, 0.02)
    return t


def chevron(x_px, y_px, m):
    x, z = px(x_px, y_px)
    for s in (1, -1):
        bpy.ops.mesh.primitive_cube_add(location=(x, -0.05, z + s * 0.11))
        c = bpy.context.object
        c.scale = (0.13, 0.06, 0.045)
        c.rotation_euler = (0, math.radians(s * 42), 0)
        c.modifiers.new("b", "BEVEL").width = 0.03
        c.data.materials.append(m)


def main():
    a = args()
    random.seed(a.seed)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    w, h = map(int, a.res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    fnt = next(bpy.data.fonts.load(os.path.abspath(f)) for f in FONTS if os.path.exists(f))

    global OUT
    OUT = mat("outline", (0.012, 0.014, 0.025), 0.0, 0.6)
    gold = mat("gold", (0.98, 0.66, 0.18), 1.0, 0.34)
    coin = mat("coin", (1.0, 0.70, 0.28), 1.0, 0.28)
    white = mat("white", (0.97, 0.96, 0.93), 0.0, 0.32, coat=0.6)
    wb = white.node_tree.nodes["Principled BSDF"]
    wb.inputs["Emission Color"].default_value = (1, 0.98, 0.94, 1)
    wb.inputs["Emission Strength"].default_value = 0.45
    green = mat("green", (0.012, 0.13, 0.045), 0.0, 0.3, coat=1.0)

    # 1) 연말정산 — 큰 금빛 3D (기존 A안의 초록 배너 자리)
    outline(text("연말정산", 2.15, 1075, 372, 0.42, gold, fnt), 0.075, OUT)
    # 2) 이 순서로 하세요 — 흰 3D, 금 대신 흰색으로 무게 차이
    outline(text("이 순서로 하세요", 1.08, 1080, 668, 0.20, white, fnt, bevel=0.10), 0.06, OUT)
    # 3) 소득 › 공제 › 환급 — 초록 3D 타일 + 금테 + 금 화살표 (오른쪽 아래 재생시간 자리는 비움)
    for lab, xp in (("소득", 750), ("공제", 1080), ("환급", 1410)):
        tile(lab, xp, 880, fnt, green, gold, white)
    for xp in (915, 1245):
        chevron(xp, 880, gold)

    # 4) 동전: 글자 뒤 공간에 흩날림 + 아래쪽 바닥에 몇 개 (글자·타일을 가리지 않게 y>0.8 또는 가장자리)
    zones = [(40, 20, 900, 190), (480, 150, 1680, 520), (520, 570, 1680, 780), (600, 760, 1580, 1000), (1650, 930, 1920, 1080)]  # 글자·타일·재생시간 자리
    placed = 0
    while placed < 44:
        xp, yp = random.uniform(330, 1890), random.uniform(30, 1050)
        if any(x0 - 30 < xp < x1 + 30 and y0 - 30 < yp < y1 + 30 for x0, y0, x1, y1 in zones):
            continue
        placed += 1
        behind = True
        if (xp < 470 or xp > 1720) and random.random() < 0.6:
            behind = False  # 화면 가장자리 몇 개는 앞으로 (깊이감)
        x, z = px(xp, yp)
        y = random.uniform(1.2, 4.5) if behind else random.uniform(-2.5, -0.8)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.30, depth=0.07, vertices=48, location=(x, y, z))
        c = bpy.context.object
        c.rotation_euler = [random.uniform(0, 6.28) for _ in range(3)]
        c.modifiers.new("b", "BEVEL").width = 0.018
        c.data.materials.append(coin)

    # 카메라
    bpy.ops.object.camera_add(location=(0, -14, 0.3), rotation=(math.radians(90), 0, 0))
    cam = bpy.context.object
    cam.data.lens = 40
    sc.camera = cam
    # 조명: 키(왼위 따뜻) · 림(오른뒤 차가움) · 아래 채움
    for loc, en, sz, col in (((-5, -7, 6), 650, 5, (1, 0.93, 0.82)), ((6, 4, 5), 900, 4, (0.55, 0.7, 1)),
                             ((0, -9, -4), 220, 8, (1, 1, 1)), ((2, -6, 2), 90, 2, (1, 0.85, 0.6))):
        bpy.ops.object.light_add(type="AREA", location=loc)
        L = bpy.context.object
        L.data.energy, L.data.size, L.data.color = en, sz, col
        L.rotation_euler = (-L.location).to_track_quat("-Z", "Y").to_euler()
    # 금속 반사를 위한 하늘: 남색 + 위쪽 밝은 띠
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    grad = nt.nodes.new("ShaderNodeTexGradient")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    ramp.color_ramp.elements[0].color = (0.01, 0.015, 0.035, 1)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = (0.55, 0.48, 0.38, 1)
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.55
    _ = grad

    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = a.samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = os.environ.get("BL_LOOK", "None")
    sc.view_settings.view_transform = os.environ.get("BL_VT", "Standard")
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = os.path.abspath(a.out)
    bpy.ops.render.render(write_still=True)
    print("저장:", sc.render.filepath)


main()
