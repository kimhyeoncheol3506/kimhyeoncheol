"""Blender 헤드리스 3D 템플릿 렌더.  blender -b -P render3d.py -- <템플릿> <출력폴더> [옵션]

템플릿
  coin   : 금색 ₩ 코인이 돌며 다가온다 (썸네일·훅·B-roll)
  bars   : 3D 막대가 차례로 자라 오른다  --values 128,330,500,1050 --labels 1월,3월,5월,6월
옵션: --seconds 4 --fps 30 --res 1920x1080 --samples 32 --font <otf> --gpu --denoise 1(공식 Blender에서만)
결과: <출력폴더>/frames/####.png 와 <출력폴더>/<템플릿>.mp4 (ffmpeg 필요)
"""
import bpy, math, os, sys, subprocess

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
tmpl, out = argv[0], os.path.abspath(argv[1])
opt = {argv[i][2:]: argv[i + 1] for i in range(2, len(argv) - 1, 2) if argv[i].startswith("--")}
if "--gpu" in argv:
    opt["gpu"] = "1"
SEC, FPS = float(opt.get("seconds", 4)), int(opt.get("fps", 30))
W, H = (int(x) for x in opt.get("res", "1920x1080").split("x"))
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = opt.get("font") or os.path.normpath(os.path.join(HERE, "..", "..", "neogul-edit", "scripts", "fonts", "Pretendard-ExtraBold.otf"))
BG = (0.009, 0.008, 0.007)          # 규칙집 다크 #181614 (선형 색공간 값)
GOLD, RED, GRAY = (1.0, 0.72, 0.15), (0.88, 0.02, 0.03), (0.10, 0.095, 0.09)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"; sc.cycles.samples = int(opt.get("samples", 32)); sc.cycles.use_denoising = opt.get("denoise", "0") == "1"   # 우분투 패키지판은 OpenImageDenoise 없음
if opt.get("gpu"):
    sc.cycles.device = "GPU"
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, int(SEC * FPS)
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = os.path.join(out, "frames", "")
sc.view_settings.view_transform = "Standard"
world = bpy.data.worlds.new("W"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (*BG, 1); world.node_tree.nodes["Background"].inputs[1].default_value = 0.6


def mat(name, color, metal=0.0, rough=0.4, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = emit
    return m


def light(loc, power, size=3):
    l = bpy.data.lights.new("L", "AREA"); l.energy = power; l.size = size
    o = bpy.data.objects.new("L", l); o.location = loc; sc.collection.objects.link(o)
    o.rotation_euler = (math.atan2(math.hypot(loc[0], loc[1]), loc[2]), 0, math.atan2(loc[1], loc[0]) + math.pi / 2)


def camera(loc, target=(0, 0, 0), lens=50):
    c = bpy.data.cameras.new("C"); c.lens = lens
    o = bpy.data.objects.new("C", c); o.location = loc; sc.collection.objects.link(o); sc.camera = o
    t = bpy.data.objects.new("T", None); t.location = target; sc.collection.objects.link(t)
    k = o.constraints.new("TRACK_TO"); k.target = t; k.track_axis = "TRACK_NEGATIVE_Z"; k.up_axis = "UP_Y"
    return o


def text(body, size, mat_, extrude=0.05, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), align="CENTER"):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = body; cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = "CENTER"
    try:
        cu.font = bpy.data.fonts.load(FONT)
    except Exception:
        pass
    o = bpy.data.objects.new("txt", cu); o.location = loc; o.rotation_euler = rot; sc.collection.objects.link(o)
    o.data.materials.append(mat_)
    return o


if tmpl == "coin":
    gold = mat("gold", GOLD, metal=1.0, rough=0.22)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=1.0, depth=0.16, location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
    coin = bpy.context.object; coin.data.materials.append(gold)
    bev = coin.modifiers.new("b", "BEVEL"); bev.width = 0.03; bev.segments = 4
    bpy.ops.object.shade_smooth()
    # 자식은 코인 기준(로컬) 좌표: 코인 축 = 로컬 Z, 앞뒤 면 = z ±0.08
    for side in (1, -1):
        t = text("₩", 1.1, gold, extrude=0.03, loc=(0, 0, 0), rot=(0, 0, 0))
        t.parent = coin; t.location = (0, 0, 0.1 * side); t.rotation_euler = (0, 0 if side == -1 else math.pi, 0)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.86, minor_radius=0.035, location=(0, 0, 0))
    ring = bpy.context.object; ring.data.materials.append(gold); ring.parent = coin
    ring.location = (0, 0, 0); ring.rotation_euler = (0, 0, 0); ring.scale = (1, 1, 2.6)
    coin.rotation_mode = "XYZ"
    for f, z, y in ((1, 0, 6), (sc.frame_end, 2 * math.pi * SEC / 2.5, 0)):
        coin.rotation_euler = (math.pi / 2, 0, z); coin.keyframe_insert("rotation_euler", frame=f)
        coin.location = (0, y, 0); coin.keyframe_insert("location", frame=f)
    camera((0, -6, 0.6), (0, 0, 0), lens=55)
    light((-3, -4, 4), 900); light((4, -2, 1), 400); light((0, 3, 3), 600)
elif tmpl == "bars":
    vals = [float(v) for v in opt.get("values", "128,330,500,1050").split(",")]
    labels = opt.get("labels", "").split(",") if opt.get("labels") else [""] * len(vals)
    mx = max(vals); n = len(vals); gap = 1.6
    mats = [mat("g%d" % i, GRAY, rough=0.5) for i in range(n - 1)] + [mat("r", RED, rough=0.35)]
    white = mat("w", (1, 1, 1), emit=1.0); yel = mat("y", (0.89, 0.75, 0.29), emit=1.0)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0)); bpy.context.object.data.materials.append(mat("floor", (0.004, 0.0037, 0.0033), rough=0.9))
    for i, v in enumerate(vals):
        x = (i - (n - 1) / 2) * gap; h = 3.2 * v / mx
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 0)); b = bpy.context.object; b.data.materials.append(mats[i])
        b.scale = (0.55, 0.55, 0.001); b.location.z = 0
        start = 1 + int(i * 0.35 * FPS); end = start + int(0.9 * FPS)
        b.keyframe_insert("scale", frame=start); b.keyframe_insert("location", frame=start)
        b.scale = (0.55, 0.55, h); b.location.z = h / 2
        b.keyframe_insert("scale", frame=end); b.keyframe_insert("location", frame=end)
        num = text("{:,}".format(int(v)) if v == int(v) else str(v), 0.42, yel if i == n - 1 else white, extrude=0.02, loc=(x, 0, h + 0.4))
        num.scale = (0.001, 0.001, 0.001); num.keyframe_insert("scale", frame=end); num.scale = (1, 1, 1); num.keyframe_insert("scale", frame=end + 6)
        if labels[i]:
            text(labels[i], 0.36, white, extrude=0.0, loc=(x, -0.7, 0.05), rot=(math.pi / 2 - 0.5, 0, 0))
    for o in bpy.data.objects:
        if o.animation_data and o.animation_data.action:
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "BACK" if fc.data_path == "scale" else "BEZIER"
    span = (n - 1) * gap + 1.2                        # 막대 전체 너비에 맞춰 카메라 거리를 정한다
    dist = max(8.5, span * 1.9)
    cam = camera((1.6, -dist, 3.1), (0, 0, 1.75), lens=35)
    cam.keyframe_insert("location", frame=1); cam.location = (0.9, -dist * 0.93, 2.9); cam.keyframe_insert("location", frame=sc.frame_end)
    light((-4, -5, 7), 450, 5); light((6, -2, 4), 150); light((0, 4, 5), 250, 4)
else:
    sys.exit("알 수 없는 템플릿: " + tmpl)

os.makedirs(out, exist_ok=True)
bpy.ops.render.render(animation=True)
mp4 = os.path.join(out, tmpl + ".mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(out, "frames", "%04d.png"),
                "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", mp4], check=True)
print("[blender] %s (%d프레임)" % (mp4, sc.frame_end))
