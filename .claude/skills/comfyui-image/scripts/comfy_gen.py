#!/usr/bin/env python3
"""현철님 PC의 ComfyUI(기본 http://127.0.0.1:8188)에 워크플로를 넣고 결과 이미지를 받아 온다.

  python comfy_gen.py "프롬프트" --out <폴더> [--size 16:9|9:16|1:1|WxH] [--n 4] [--seed 7] [--ckpt <모델 파일명>]
                      [--workflow workflows/sdxl_txt2img.json] [--steps 30] [--cfg 6.5] [--neg "..."] [--style econ]
워크플로 파일은 ComfyUI에서 'Save (API Format)'로 저장한 JSON에 {{PROMPT}} {{NEG}} {{SEED}} {{W}} {{H}} {{CKPT}} {{STEPS}} {{CFG}} {{BATCH}} {{PREFIX}} 자리표시자를 넣은 것.
"""
import argparse, json, os, random, sys, time, urllib.parse, urllib.request, uuid

HERE = os.path.dirname(os.path.abspath(__file__))
URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
SIZES = {"16:9": (1344, 768), "9:16": (768, 1344), "1:1": (1024, 1024), "4:3": (1152, 896)}
STYLES = {
    "econ": "editorial illustration, clean composition, cinematic lighting, dark warm background #181614, high detail, no text, no watermark",
    "history": "oil painting style, 17th century european scene, museum quality, warm tones, no text, no watermark",
    "photo": "documentary photograph, natural light, realistic, high detail, no text, no watermark",
    "none": ""}
NEG = "text, letters, watermark, logo, signature, brand, celebrity, real person likeness, deformed hands, extra fingers, blurry, low quality, jpeg artifacts"


def http(path, data=None, raw=False, timeout=60):
    req = urllib.request.Request(URL + path, data=json.dumps(data).encode() if data is not None else None,
                                 headers={"Content-Type": "application/json"} if data is not None else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
    return b if raw else json.loads(b or b"{}")


def fill(obj, rep):
    if isinstance(obj, dict):
        return {k: fill(v, rep) for k, v in obj.items()}
    if isinstance(obj, list):
        return [fill(v, rep) for v in obj]
    if isinstance(obj, str) and obj.startswith("{{") and obj.endswith("}}") and obj[2:-2] in rep:
        return rep[obj[2:-2]]                     # 숫자 자리는 숫자로 바뀐다
    if isinstance(obj, str):
        for k, v in rep.items():
            obj = obj.replace("{{%s}}" % k, str(v))
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt"); ap.add_argument("--out", default="comfy_out")
    ap.add_argument("--size", default="16:9"); ap.add_argument("--n", type=int, default=4); ap.add_argument("--seed", type=int)
    ap.add_argument("--ckpt", default=os.environ.get("COMFY_CKPT", "sd_xl_base_1.0.safetensors"))
    ap.add_argument("--workflow", default=os.path.join(HERE, "..", "workflows", "sdxl_txt2img.json"))
    ap.add_argument("--steps", type=int, default=30); ap.add_argument("--cfg", type=float, default=6.5)
    ap.add_argument("--neg", default=NEG); ap.add_argument("--style", choices=list(STYLES), default="econ")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    W, H = SIZES.get(a.size) or tuple(int(x) for x in a.size.lower().split("x"))
    seed = a.seed if a.seed is not None else random.randint(1, 2 ** 31)
    prompt = ", ".join(x for x in (a.prompt, STYLES[a.style]) if x)
    try:
        http("/system_stats", timeout=5)
    except Exception as e:
        sys.exit("[오류] ComfyUI(%s)에 연결할 수 없습니다. PC에서 ComfyUI를 먼저 켜 주세요: %s" % (URL, e))
    wf = fill(json.load(open(a.workflow, encoding="utf-8")), {"PROMPT": prompt, "NEG": a.neg, "SEED": seed, "W": W, "H": H, "CKPT": a.ckpt,
                                                               "STEPS": a.steps, "CFG": a.cfg, "BATCH": a.n, "PREFIX": "econ2"})
    cid = str(uuid.uuid4())
    pid = http("/prompt", {"prompt": wf, "client_id": cid})["prompt_id"]
    print("[comfy] 대기열 등록 %s (seed %d, %dx%d x%d)" % (pid, seed, W, H, a.n), flush=True)
    t0 = time.time()
    while True:
        h = http("/history/" + pid)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                sys.exit("[오류] 생성 실패: %s" % json.dumps(st.get("messages", ""))[:500])
            outs = h[pid].get("outputs", {})
            if outs:
                break
        if time.time() - t0 > a.timeout:
            sys.exit("[오류] %d초 안에 끝나지 않았습니다" % a.timeout)
        time.sleep(2)
    os.makedirs(a.out, exist_ok=True); n = 0
    for node in outs.values():
        for im in node.get("images", []):
            q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im.get("type", "output")})
            p = os.path.join(a.out, "%s_%d_%02d.png" % (time.strftime("%m%d_%H%M%S"), seed, n))
            open(p, "wb").write(http("/view?" + q, raw=True)); n += 1; print("  저장:", p)
    json.dump({"prompt": prompt, "neg": a.neg, "seed": seed, "size": [W, H], "ckpt": a.ckpt, "workflow": os.path.basename(a.workflow)},
              open(os.path.join(a.out, "comfy_%d.json" % seed), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("[comfy] %d장, %.0f초" % (n, time.time() - t0))


if __name__ == "__main__":
    main()
