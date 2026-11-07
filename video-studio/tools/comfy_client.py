"""ComfyUI HTTP API 클라이언트 (영상 파이프라인용).

서버 주소는 COMFY_URL (기본 http://127.0.0.1:8188). 현철님 PC(GPU)에서 ComfyUI를 켜 두면
COMFY_URL=http://<PC주소>:8188 로 같은 코드가 그대로 돈다.

  python tools/comfy_client.py status
  python tools/comfy_client.py models
  python tools/comfy_client.py txt2img "<프롬프트>" out.png [--ckpt 이름] [--w 1920 --h 1080] [--steps 20] [--seed 1]
  python tools/comfy_client.py run workflow_api.json out_dir      # ComfyUI에서 'Export (API)'로 저장한 워크플로
  python tools/comfy_client.py selftest out.png                    # 모델 없이 API 왕복만 확인
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid

URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188").rstrip("/")


def _get(path):
    with urllib.request.urlopen(URL + path, timeout=30) as r:
        return r.read()


def _post(path, data):
    req = urllib.request.Request(URL + path, json.dumps(data).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def status():
    return json.loads(_get("/system_stats"))


def models(folder="checkpoints"):
    return json.loads(_get(f"/models/{folder}"))


def upload_image(path):
    """기준 이미지(IPAdapter용)를 ComfyUI input 폴더로 올리고 서버 쪽 파일 이름을 돌려준다"""
    boundary = uuid.uuid4().hex
    name = os.path.basename(path)
    data = open(path, "rb").read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}\"\r\nContent-Type: image/png\r\n\r\n").encode() + data + \
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(URL + "/upload/image", body, {"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["name"]


def run(workflow, out_dir, timeout=3600):
    """API 형식 워크플로를 큐에 넣고 끝나면 출력 이미지를 out_dir에 저장, 경로 목록 반환"""
    pid = _post("/prompt", {"prompt": workflow, "client_id": uuid.uuid4().hex})["prompt_id"]
    t0 = time.time()
    while True:
        h = json.loads(_get(f"/history/{pid}"))
        if pid in h:
            break
        if time.time() - t0 > timeout:
            raise TimeoutError(pid)
        time.sleep(1)
    st = h[pid].get("status", {})
    if st.get("status_str") == "error":
        raise RuntimeError(json.dumps(st.get("messages", [])[-1:], ensure_ascii=False)[:800])
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for node in h[pid]["outputs"].values():
        for im in node.get("images", []):
            q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im["subfolder"], "type": im["type"]})
            p = os.path.join(out_dir, im["filename"])
            open(p, "wb").write(_get("/view?" + q))
            paths.append(p)
    return paths


def txt2img_workflow(prompt, ckpt, w=1024, h=576, steps=20, seed=1, cfg=7.0, negative="text, watermark, blurry"):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
                                                    "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "vs"}},
    }


def _save_as(paths, out):
    if not paths:
        raise RuntimeError("출력 이미지 없음")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    os.replace(paths[0], out)
    return out


def main(a):
    cmd = a[0] if a else "status"
    opt = {a[i][2:]: a[i + 1] for i in range(len(a) - 1) if a[i].startswith("--")}
    if cmd == "status":
        s = status()["system"]
        print("ComfyUI", s["comfyui_version"], "| 장치:", [d["type"] for d in status()["devices"]], "| 주소:", URL)
    elif cmd == "models":
        print("\n".join(models(opt.get("folder", "checkpoints"))) or "(체크포인트 없음: ComfyUI/models/checkpoints 에 넣기)")
    elif cmd == "txt2img":
        ck = opt.get("ckpt") or (models() or [None])[0]
        if not ck:
            sys.exit("체크포인트가 없습니다. ComfyUI/models/checkpoints 에 .safetensors 를 넣으세요.")
        wf = txt2img_workflow(a[1], ck, int(opt.get("w", 1024)), int(opt.get("h", 576)), int(opt.get("steps", 20)), int(opt.get("seed", 1)))
        out = a[2]
        print(_save_as(run(wf, os.path.dirname(os.path.abspath(out))), out))
    elif cmd == "run":
        print("\n".join(run(json.load(open(a[1], encoding="utf-8")), a[2])))
    elif cmd == "selftest":
        wf = {"1": {"class_type": "EmptyImage", "inputs": {"width": 320, "height": 180, "batch_size": 1, "color": 0xE2B046}},
              "2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0], "filename_prefix": "selftest"}}}
        out = a[1] if len(a) > 1 else "comfy_selftest.png"
        print("OK", _save_as(run(wf, os.path.dirname(os.path.abspath(out))), out))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
