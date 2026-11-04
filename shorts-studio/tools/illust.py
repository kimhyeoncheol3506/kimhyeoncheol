"""장면별 삽화 생성 (ComfyUI, 로컬 CPU).

script.json 의 장면에 "illust_prompt"(영어 장면 묘사)가 있으면 projects/X/illust/<id>.png 를 만든다.
이미 있는 파일은 건너뜀 (프롬프트를 바꿨으면 해당 png 삭제 후 재실행).
렌더러(studio/short.py)는 illust/<id>.png 가 있으면 그 장면 앞부분에 삽화를 띄운다.

모델: DreamShaper 8 (SD1.5) + LCM LoRA, 6스텝 · 576x576 · CPU 약 30~60초/장.
서버: ComfyUI 를 --cpu 로 127.0.0.1:8188 에 띄워 두고 /prompt API 로 호출 (없으면 자동 기동 시도).
사용: python3 tools/illust.py projects/short_067_xxx
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HOST = os.environ.get("COMFY_HOST", "127.0.0.1:8188")
CKPT = os.environ.get("COMFY_CKPT", "dreamshaper_8.safetensors")
LORA = os.environ.get("COMFY_LORA", "lcm_sd15.safetensors")
COMFY_DIR = os.environ.get("COMFY_DIR")          # 서버 자동 기동용 (ComfyUI 폴더)
COMFY_PY = os.environ.get("COMFY_PY", "python3")  # ComfyUI venv 의 python
SIZE = 576

# 채널 통일 화풍: 한국 웹툰풍 · 얼굴 단순 · 글자 없음 (실존 인물/브랜드 X)
STYLE = ("flat 2d anime illustration, korean webtoon panel, bold clean line art, cel shading, vivid pastel colors, "
         "adult characters in their 30s, modest casual clothes, upper body shot, simple background, no text")
NEG = ("photo, photorealistic, realistic, 3d render, text, letters, watermark, logo, signature, nsfw, nude, "
       "cleavage, bare shoulders, off shoulder, bare legs, lying on top, intimate, kissing, bed, lingerie, gore, blood, child, teenager, school uniform, deformed, extra fingers, bad hands, lowres, blurry")


def _req(path, data=None):
    req = urllib.request.Request(f"http://{HOST}{path}", data=json.dumps(data).encode() if data is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def alive():
    try:
        _req("/system_stats")
        return True
    except Exception:
        return False


def ensure_server():
    if alive():
        return
    if not COMFY_DIR:
        sys.exit("ComfyUI 서버가 꺼져 있음 (COMFY_DIR/COMFY_PY 를 지정하면 자동 기동)")
    log = open(Path(COMFY_DIR) / "server.log", "a")
    subprocess.Popen([COMFY_PY, "main.py", "--cpu", "--listen", "127.0.0.1", "--port", HOST.split(":")[1],
                      "--disable-auto-launch"], cwd=COMFY_DIR, stdout=log, stderr=log, start_new_session=True)
    for _ in range(90):
        time.sleep(2)
        if alive():
            return
    sys.exit("ComfyUI 기동 실패")


def workflow(prompt, seed):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1", 0], "clip": ["1", 1], "lora_name": LORA,
                                                     "strength_model": 1.0, "strength_clip": 1.0}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": f"{STYLE}, {prompt}"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": NEG}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": SIZE, "height": SIZE, "batch_size": 1}},
        "6": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0],
                                                   "latent_image": ["5", 0], "seed": seed, "steps": 6, "cfg": 2.0,
                                                   "sampler_name": "lcm", "scheduler": "sgm_uniform", "denoise": 1.0}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": "shorts_illust"}},
    }


def generate(prompt, out: Path, seed):
    pid = json.loads(_req("/prompt", {"prompt": workflow(prompt, seed)}))["prompt_id"]
    for _ in range(600):
        time.sleep(2)
        h = json.loads(_req(f"/history/{pid}"))
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise RuntimeError(f"ComfyUI 오류: {st}")
            img = h[pid]["outputs"]["8"]["images"][0]
            q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
            out.write_bytes(_req(f"/view?{q}"))
            return
    raise TimeoutError("삽화 생성 시간 초과")


def main(proj):
    import urllib.parse  # noqa: F401  (generate 에서 사용)
    proj = Path(proj)
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    todo = [s for s in script.get("scenes", []) if s.get("illust_prompt")
            and not (proj / "illust" / f"{s['id']}.png").exists()]
    if not todo:
        print("삽화: 생성할 것 없음")
        return
    ensure_server()
    (proj / "illust").mkdir(exist_ok=True)
    base = random.Random(proj.name).randrange(1, 10**9)
    for s in todo:
        t0 = time.time()
        generate(s["illust_prompt"], proj / "illust" / f"{s['id']}.png", base + int(s.get("illust_seed", 0)))
        print(f"삽화 {s['id']} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    import urllib.parse  # noqa: F401
    main(sys.argv[1])
