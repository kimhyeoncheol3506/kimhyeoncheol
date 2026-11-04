# -*- coding: utf-8 -*-
"""ComfyUI 워크플로(API 형식 JSON) 만들기 (ranking-video v2.12.0)

ComfyUI(https://github.com/Comfy-Org/ComfyUI, GPL-3.0)는 GPU에서 돌리는 이미지 생성 앱이라 클라우드 세션에서는 돌리지 않는다.
이 스크립트가 프롬프트별 워크플로 JSON을 만들고, 사용자가 PC의 ComfyUI에서 실행한다(파일을 창에 끌어다 놓거나 API로 전송).

사용:
  python3 -I make_comfy_workflow.py <프롬프트.json> <출력폴더> [--ckpt 모델파일명] [--w 1344 --h 768] [--steps 25] [--submit http://127.0.0.1:8188]
  <프롬프트.json> = [{"name": "썸네일_배경", "prompt": "...", "negative": "..."(선택), "seed": 1(선택)}, ...]
출력: <출력폴더>/<name>.json (ComfyUI API 형식). --submit을 주면 해당 주소의 /prompt로 바로 보낸다(사용자 PC가 이 세션에 연결됐을 때만).
결과 이미지는 ComfyUI output 폴더에 <name>_00001_.png로 저장된다 → 영상 폴더 09_소재/ai_img/로 옮긴다.
"""
import argparse, json, os, urllib.request

NEG = ("text, letters, watermark, logo, signage, store sign, brand name, price tag, human face, close-up face, person, "
       "blurry, lowres, deformed, extra fingers")


def workflow(prompt, negative, seed, ckpt, w, h, steps, name):
    return {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": steps, "cfg": 6.5, "sampler_name": "dpmpp_2m", "scheduler": "karras",
                                                    "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["8", 0]}},
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("prompts"); ap.add_argument("out")
    ap.add_argument("--ckpt", default="sd_xl_base_1.0.safetensors"); ap.add_argument("--w", type=int, default=1344); ap.add_argument("--h", type=int, default=768)
    ap.add_argument("--steps", type=int, default=25); ap.add_argument("--submit"); a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for i, p in enumerate(json.load(open(a.prompts, encoding="utf-8"))):
        wf = workflow(p["prompt"], p.get("negative", NEG), p.get("seed", 1000 + i), a.ckpt, a.w, a.h, a.steps, p["name"])
        f = os.path.join(a.out, p["name"] + ".json"); json.dump(wf, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("워크플로:", f)
        if a.submit:
            req = urllib.request.Request(a.submit.rstrip("/") + "/prompt", data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
            print("  전송:", urllib.request.urlopen(req, timeout=30).read().decode()[:120])


if __name__ == "__main__":
    main()
