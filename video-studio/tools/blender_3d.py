"""Blender 3D 장면 (2026-11-11 도입, 헤드리스 CPU 렌더).

쓰는 곳:
- 영상: 핵심 숫자·키워드를 금빛 3D 글자로 세우고 동전이 쏟아지는 3~5초 강조 컷 → build.py 에서 S("대사", "file", path="<mp4>")
- 썸네일: 같은 장면을 투명 배경 PNG 한 장으로(--still) → make_thumb 에서 <img> 로 얹기 (사이버·3D 썸네일 재료)

사용 (blender 는 setup_blender.sh 가 ~/ext 에 설치):
  BL=/home/user/ext/blender-4.5.9-linux-x64/blender
  $BL -b -P tools/blender_3d.py -- --text "117만 원" --sub "추가 납부 평균" --out clip.mp4 [--dur 4] [--coins 40] [--color gold|red|blue] [--engine cycles|workbench] [--samples 24]
  $BL -b -P tools/blender_3d.py -- --text "117만 원" --still --out title3d.png     # 투명 배경 1장
- 색은 sting 팔레트(금 #F2C14E · 빨강 #DE5B41 · 파랑 #5B93B8), 배경 #1b2330 (영상) / 투명 (썸네일).
- 위쪽 150px·아래 200px(칩·자막 자리)를 비우도록 글자를 가운데 약간 위에 둔다.
- 속도(4코어 CPU, 실측): 썸네일 1장 cycles 32샘플 ≈ 45초. 영상 workbench(밋밋하지만 빠름, 소프트웨어 GL) 3초 ≈ 2분,
  cycles 는 1080p 프레임당 30~45초라 4초 컷이면 --res 1280x720 --samples 12 로 30분 안팎 → 백그라운드로 돌리고 ffmpeg 로 1080p 확대.
"""
import argparse
import math
import os
import random
import sys

import bpy

FONT_DIRS = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "neural-studio", "assets", "fonts"),
             "/home/user/hf/thumb/assets/fonts"]
COLORS = {"gold": (0.95, 0.70, 0.22), "red": (0.87, 0.30, 0.22), "blue": (0.30, 0.55, 0.78), "white": (0.95, 0.95, 0.95)}


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dur", type=float, default=4.0)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--coins", type=int, default=36)
    ap.add_argument("--color", default="gold", choices=list(COLORS))
    ap.add_argument("--engine", default="cycles", choices=["cycles", "workbench"])
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--still", action="store_true")
    ap.add_argument("--res", default="1920x1080")
    ap.add_argument("--seed", type=int, default=7)
    return ap.parse_args(argv)


def font():
    for d in FONT_DIRS:
        for n in ("BlackHanSans.ttf", "BlackHanSans-Regular.ttf"):
            p = os.path.abspath(os.path.join(d, n))
            if os.path.exists(p):
                return bpy.data.fonts.load(p)
    return None


def metal(name, rgb, rough=0.25, metallic=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    m.diffuse_color = (*rgb, 1)  # workbench 용
    return m


def text_obj(body, size, z, depth, mat, fnt):
    bpy.ops.object.text_add(location=(0, 0, z))
    t = bpy.context.object
    t.data.body = body
    if fnt:
        t.data.font = fnt
    t.data.size = size
    t.data.align_x = "CENTER"
    t.data.align_y = "CENTER"
    t.data.extrude = depth
    t.data.bevel_depth = depth * 0.18
    t.data.bevel_resolution = 3
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(mat)
    return t


def main():
    a = args()
    random.seed(a.seed)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    w, h = map(int, a.res.split("x"))
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.fps = a.fps
    n = 1 if a.still else max(1, int(a.dur * a.fps))
    sc.frame_start, sc.frame_end = 1, n
    fnt = font()
    col = COLORS[a.color]
    gold, coin_m = metal("main", col), metal("coin", COLORS["gold"], 0.3)
    sub_m = metal("sub", COLORS["white"], 0.5, 0.0)

    # 글자: 앞으로 튀어나오며 살짝 회전하다 멈춤
    main_t = text_obj(a.text, 1.55, 0.35, 0.28, gold, fnt)
    if a.sub:
        text_obj(a.sub, 0.5, 1.55, 0.06, sub_m, fnt)
    if not a.still:
        main_t.scale = (0.2, 0.2, 0.2)
        main_t.keyframe_insert("scale", frame=1)
        main_t.rotation_euler[2] = math.radians(-25)
        main_t.keyframe_insert("rotation_euler", frame=1)
        main_t.scale = (1, 1, 1)
        main_t.keyframe_insert("scale", frame=int(a.fps * 0.6))
        main_t.rotation_euler[2] = math.radians(6)
        main_t.keyframe_insert("rotation_euler", frame=int(a.fps * 0.6))
        main_t.rotation_euler[2] = math.radians(-4)
        main_t.keyframe_insert("rotation_euler", frame=n)
        for fc in main_t.animation_data.action.fcurves if hasattr(main_t.animation_data.action, "fcurves") else []:
            for k in fc.keyframe_points:
                k.interpolation = "BACK" if k.co[0] <= a.fps * 0.6 else "SINE"

    # 동전: 위에서 떨어지며 돌다 바닥(z=-1.6) 근처에 쌓임 (물리 없이 키프레임 → 빠르고 재현 가능)
    for i in range(a.coins):
        x = random.uniform(-4.2, 4.2)
        y = random.uniform(-0.8, 1.6)
        if abs(x) < 3.4:  # 글자 폭 안의 동전은 글자 뒤로 (숫자를 가리지 않게)
            y = random.uniform(0.6, 2.2)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.06, vertices=40, location=(x, y, 0))
        c = bpy.context.object
        c.data.materials.append(coin_m)
        bev = c.modifiers.new("b", "BEVEL")
        bev.width, bev.segments = 0.015, 2
        rot = [random.uniform(0, 6.28) for _ in range(3)]
        if a.still:
            c.location.z = random.uniform(-1.7, 2.6)
            c.rotation_euler = rot
            continue
        t0 = int(random.uniform(0, 0.55) * n)
        t1 = min(n, t0 + int(random.uniform(0.8, 1.2) * a.fps))
        c.location.z = random.uniform(3.6, 5.5)
        c.rotation_euler = rot
        c.keyframe_insert("location", frame=max(1, t0))
        c.keyframe_insert("rotation_euler", frame=max(1, t0))
        c.location.z = -1.65 + random.uniform(0, 0.25)
        c.rotation_euler = (math.radians(random.uniform(-12, 12)), math.radians(random.uniform(-12, 12)), rot[2] + random.uniform(4, 9))
        c.keyframe_insert("location", frame=t1)
        c.keyframe_insert("rotation_euler", frame=t1)

    # 카메라: 살짝 아래에서 올려다보며 천천히 다가감
    bpy.ops.object.camera_add(location=(0, -11, 0.6), rotation=(math.radians(88), 0, 0))
    cam = bpy.context.object
    cam.data.lens = 40
    sc.camera = cam
    if not a.still:
        cam.keyframe_insert("location", frame=1)
        cam.location = (0.3, -9.6, 0.8)
        cam.keyframe_insert("location", frame=n)

    # 조명: 키·림·채움
    for loc, en, sz, c_ in (((-4, -6, 5), 900, 4, (1, 0.95, 0.85)), ((5, 3, 4), 700, 3, (0.6, 0.75, 1)), ((0, -8, -2), 250, 6, (1, 1, 1))):
        bpy.ops.object.light_add(type="AREA", location=loc)
        L = bpy.context.object
        L.data.energy, L.data.size, L.data.color = en, sz, c_
        d = -L.location
        L.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.012, 0.017, 0.027, 1)  # #1b2330 선형값 근사
    bg.inputs["Strength"].default_value = 1.0
    world.color = (0.012, 0.017, 0.027)  # workbench 는 노드 대신 이 색을 배경으로 씀

    if a.engine == "cycles":
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = a.samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 4
    else:
        sc.render.engine = "BLENDER_WORKBENCH"
        sc.display.shading.light = "STUDIO"
        sc.display.shading.color_type = "MATERIAL"
        sc.display.shading.show_specular_highlight = True
    sc.view_settings.view_transform = "Standard" if a.engine == "workbench" else "AgX"

    out = os.path.abspath(a.out)
    if a.still:
        sc.render.film_transparent = True
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGBA"
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True)
    else:
        sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"
        sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "HIGH"
        sc.render.filepath = out
        bpy.ops.render.render(animation=True)
    print("저장:", out)


main()
