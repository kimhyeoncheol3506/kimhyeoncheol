"""Real-ESRGAN 화질 키우기 (2026-11-11 도입, CPU용).

쓰는 곳:
- 썸네일·장면에 넣을 작은 실물 사진·스크린샷·로고(누끼 소품)를 1280×720/1920×1080에 맞게 선명하게 키우기
- ComfyUI(PC)에서 만든 1024px 일러스트를 1080p 켄 번스용으로 2배 키우기 (확대해도 뭉개지지 않게)
- 짧은 클립(참고·자료 화면) 프레임 단위 업스케일 — CPU라 느리니 10초 이하만

사용:
  /home/user/ext/esrgan-venv/bin/python tools/upscale.py <입력 png/jpg/mp4> [-o 출력] [--scale 2|4] [--model photo|anime]
  · photo = RealESRGAN_x4plus(실사·스크린샷), anime = RealESRGAN_x4plus_anime_6B(일러스트·마스코트·글자)
  · 처음 한 번: bash setup_esrgan.sh  (CPU torch + spandrel + 가중치 2개, ~/ext 아래)
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
import torch
from PIL import Image
from spandrel import ModelLoader

MODELS = os.environ.get("ESRGAN_MODELS", "/home/user/ext/esrgan-models")
WEIGHTS = {"photo": "RealESRGAN_x4plus.pth", "anime": "RealESRGAN_x4plus_anime_6B.pth"}


def load(kind):
    m = ModelLoader().load_from_file(os.path.join(MODELS, WEIGHTS[kind]))
    m.model.eval()
    torch.set_num_threads(max(1, (os.cpu_count() or 2) - 1))
    return m


@torch.inference_mode()
def up_array(model, rgb, tile=256, pad=16):
    """타일로 나눠 처리(메모리 절약) 후 이어 붙임. rgb: HxWx3 uint8"""
    h, w = rgb.shape[:2]
    s = model.scale
    x = torch.from_numpy(rgb).permute(2, 0, 1).float().div(255).unsqueeze(0)
    out = torch.zeros(1, 3, h * s, w * s)
    for y0 in range(0, h, tile):
        for x0 in range(0, w, tile):
            y1, x1 = min(y0 + tile, h), min(x0 + tile, w)
            ya, xa, yb, xb = max(y0 - pad, 0), max(x0 - pad, 0), min(y1 + pad, h), min(x1 + pad, w)
            o = model(x[:, :, ya:yb, xa:xb]).clamp(0, 1)
            out[:, :, y0 * s:y1 * s, x0 * s:x1 * s] = o[:, :, (y0 - ya) * s:(y0 - ya + y1 - y0) * s, (x0 - xa) * s:(x0 - xa + x1 - x0) * s]
    return (out[0].permute(1, 2, 0).numpy() * 255).round().astype(np.uint8)


def up_image(model, src, dst, scale):
    im = Image.open(src)
    alpha = im.getchannel("A") if im.mode in ("RGBA", "LA") else None
    rgb = im.convert("RGB")
    if alpha is not None:  # 투명 부분 밑의 검은 픽셀이 테두리에 번지지 않게 흰 바탕에 얹어서 키움
        bg = Image.new("RGB", im.size, "white")
        bg.paste(rgb, mask=alpha)
        rgb = bg
    big = Image.fromarray(up_array(model, np.array(rgb)))
    if scale != model.scale:  # 4배 모델 결과를 원하는 배율로 줄임 (2배가 4배→축소보다 선명)
        big = big.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    if alpha is not None:  # 누끼 투명도는 그대로 키워서 붙임
        big.putalpha(alpha.resize(big.size, Image.LANCZOS))
    big.save(dst)
    return dst


def up_video(model, src, dst, scale):
    fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", src],
                         capture_output=True, text=True).stdout.strip() or "30"
    td = tempfile.mkdtemp()
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-i", src, os.path.join(td, "f%05d.png")], check=True)
        fr = sorted(f for f in os.listdir(td) if f.startswith("f"))
        for i, f in enumerate(fr):
            up_image(model, os.path.join(td, f), os.path.join(td, "u" + f[1:]), scale)
            print(f"\r프레임 {i + 1}/{len(fr)}", end="", flush=True)
        print()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", fps, "-i", os.path.join(td, "u%05d.png"), "-i", src,
                        "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], check=True)
    finally:
        shutil.rmtree(td, ignore_errors=True)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--scale", type=int, default=2, choices=[2, 3, 4])
    ap.add_argument("--model", default="photo", choices=list(WEIGHTS))
    a = ap.parse_args()
    base, ext = os.path.splitext(a.src)
    dst = a.out or f"{base}_x{a.scale}{'.png' if ext.lower() in ('.jpg', '.jpeg', '.webp') else ext}"
    model = load(a.model)
    if ext.lower() in (".mp4", ".mov", ".mkv", ".webm"):
        up_video(model, a.src, dst, a.scale)
    else:
        up_image(model, a.src, dst, a.scale)
    print("저장:", dst)


if __name__ == "__main__":
    sys.exit(main())
