#!/usr/bin/env python3
"""Real-ESRGAN 업스케일(이미지·폴더·영상). 가중치는 공식 릴리스에서 자동으로 받는다.

  upscale.py in.jpg out.png [--model x4plus|general] [--scale 2|4] [--tile 256]
  upscale.py in_dir/ out_dir/
  upscale.py in.mp4 out.mp4 --video [--fps 30]     (CPU에서는 매우 느림: 1080p 1프레임 수십 초)
"""
import argparse, glob, os, subprocess, sys, time, urllib.request
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(os.path.dirname(HERE), "models")
URLS = {"x4plus": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        "general": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"}


def model_path(name):
    os.makedirs(MODELS, exist_ok=True)
    p = os.path.join(MODELS, os.path.basename(URLS[name]))
    if not os.path.exists(p):
        print("[model] 내려받는 중:", URLS[name]); urllib.request.urlretrieve(URLS[name], p)
    return p


def load(name, device):
    import torch
    from spandrel import ModelLoader
    m = ModelLoader(device=device).load_from_file(model_path(name))  # spandrel은 가중치만 안전하게 읽는다
    m.eval()
    return m, torch


def run(m, torch, img, tile, device):
    x = torch.from_numpy(np.asarray(img.convert("RGB"), np.float32) / 255.0).permute(2, 0, 1)[None].to(device)
    s = m.scale; _, _, H, W = x.shape
    out = torch.zeros((1, 3, H * s, W * s), device=device)
    pad = 16
    with torch.no_grad():
        for y in range(0, H, tile):
            for xx in range(0, W, tile):
                y0, x0 = max(0, y - pad), max(0, xx - pad)
                y1, x1 = min(H, y + tile + pad), min(W, xx + tile + pad)
                o = m(x[:, :, y0:y1, x0:x1])
                oy, ox = (y - y0) * s, (xx - x0) * s
                hh, ww = (min(H, y + tile) - y) * s, (min(W, xx + tile) - xx) * s
                out[:, :, y * s:y * s + hh, xx * s:xx * s + ww] = o[:, :, oy:oy + hh, ox:ox + ww]
    arr = (out[0].clamp(0, 1).permute(1, 2, 0).cpu().numpy() * 255).round().astype(np.uint8)
    return Image.fromarray(arr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--model", choices=list(URLS), default="x4plus")
    ap.add_argument("--scale", type=int, default=4, help="최종 배율(2면 4배로 키운 뒤 절반으로 줄임)")
    ap.add_argument("--tile", type=int, default=256); ap.add_argument("--device", default="cpu")
    ap.add_argument("--video", action="store_true"); ap.add_argument("--fps", type=float, default=0)
    a = ap.parse_args()
    m, torch = load(a.model, a.device)
    torch.set_num_threads(os.cpu_count() or 4)

    def one(src, dst):
        t0 = time.time(); im = Image.open(src)
        up = run(m, torch, im, a.tile, a.device)
        if a.scale != m.scale:
            up = up.resize((im.width * a.scale, im.height * a.scale), Image.LANCZOS)
        up.save(dst); print("  %s %dx%d → %dx%d (%.1f초)" % (os.path.basename(src), im.width, im.height, up.width, up.height, time.time() - t0), flush=True)

    if a.video:
        tmp = a.dst + "_frames"; os.makedirs(tmp + "/in", exist_ok=True); os.makedirs(tmp + "/out", exist_ok=True)
        fps = a.fps or eval(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", a.src], capture_output=True, text=True).stdout.strip())
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-vf", "fps=%s" % fps, tmp + "/in/%06d.png"], check=True)
        for f in sorted(glob.glob(tmp + "/in/*.png")):
            o = tmp + "/out/" + os.path.basename(f)
            if not os.path.exists(o): one(f, o)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", tmp + "/out/%06d.png", "-i", a.src, "-map", "0:v", "-map", "1:a?",
                        "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", a.dst], check=True)
        print("[video]", a.dst)
    elif os.path.isdir(a.src):
        os.makedirs(a.dst, exist_ok=True)
        for f in sorted(glob.glob(os.path.join(a.src, "*"))):
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                one(f, os.path.join(a.dst, os.path.splitext(os.path.basename(f))[0] + ".png"))
    else:
        one(a.src, a.dst)


if __name__ == "__main__":
    main()
