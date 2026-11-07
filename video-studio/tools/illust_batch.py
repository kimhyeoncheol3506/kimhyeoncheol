"""34편~ AI 일러스트 일괄 생성: build.py의 illust 장면 중 그림 파일이 없는 것만 ComfyUI(PC 그래픽카드)로 만든다.

사용:
  COMFY_URL=http://<PC주소>:8188 python3 tools/illust_batch.py projects/<폴더> [--ckpt 모델.safetensors] [--placeholder]
  - 장면 작성: S("대사", "illust", path="illust/s012.png", prompt="sitting at a desk looking at a falling stock chart on a laptop, worried", bubbles=[...])
  - 캐릭터 고정 프롬프트·부정 프롬프트·기준 얼굴은 assets/character/ANT_CHARACTER.md / ant_ref.png
  - 기준 얼굴(ant_ref.png)이 있으면 IPAdapter 워크플로(tools/comfy_workflows/illust_ipadapter_api.json), 없으면 기본 txt2img
  - ComfyUI에 연결이 안 되거나 --placeholder면 '그림 대기' 임시 그림을 만들어 제작이 멈추지 않게 한다 (나중에 다시 실행하면 임시 그림만 교체)
"""
import importlib.util
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import comfy_client as C  # noqa: E402

BASE = ("semi-realistic korean webtoon illustration, cute short young korean office worker man, late 20s, round friendly face, short black hair, "
        "big expressive eyes, two thin black ant antennae with round tips on top of head, white shirt with small orange collar, navy cardigan, "
        "soft cinematic lighting, detailed background, 16:9")
NEG = "text, letters, watermark, logo, real celebrity, photo of real person, extra fingers, deformed hands, blurry, lowres"
REF = os.path.join(ROOT, "assets", "character", "ant_ref.png")
WF = os.path.join(ROOT, "tools", "comfy_workflows", "illust_ipadapter_api.json")


def scenes(pdir):
    spec = importlib.util.spec_from_file_location("b", os.path.join(pdir, "build.py"))
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    for s in b.sc:
        for k, part in enumerate(s["parts"]):
            if part["kind"] == "illust" and part["p"].get("path"):
                yield s["id"], k, part["p"]


def placeholder(out, prompt):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (1920, 1080), (46, 52, 66))
    d = ImageDraw.Draw(im)
    for y in range(1080):
        d.line([(0, y), (1920, y)], fill=(46 + y // 30, 52 + y // 40, 66 + y // 25))
    font_path = os.path.join(ROOT, "assets", "fonts", "Pretendard-Black.otf")
    f1 = ImageFont.truetype(font_path, 70) if os.path.exists(font_path) else None
    f2 = ImageFont.truetype(font_path, 34) if os.path.exists(font_path) else None
    d.text((960, 470), "AI 일러스트 대기 중", fill=(242, 193, 78), font=f1, anchor="mm")
    d.text((960, 560), prompt[:90], fill=(220, 220, 220), font=f2, anchor="mm")
    im.save(out)
    open(out + ".placeholder", "w").write(prompt)


def main(a):
    pdir = a[0]
    opt = {a[i][2:]: (a[i + 1] if i + 1 < len(a) and not a[i + 1].startswith("--") else True) for i in range(1, len(a)) if a[i].startswith("--")}
    force_ph = bool(opt.get("placeholder"))
    online = False
    if not force_ph:
        try:
            C.status()
            online = True
        except Exception as e:  # PC ComfyUI가 꺼져 있거나 주소에 닿지 않음
            print(f"ComfyUI 연결 안 됨({C.URL}): {e} → 임시 그림으로 진행")
    ckpt = opt.get("ckpt") if isinstance(opt.get("ckpt"), str) else None
    if online and not ckpt:
        ms = C.models()
        ckpt = ms[0] if ms else None
        if not ckpt:
            print("체크포인트가 없습니다 → 임시 그림으로 진행")
            online = False
    ref_name = None
    if online and os.path.exists(REF):
        ref_name = C.upload_image(REF)
    made = 0
    for sid, k, p in scenes(pdir):
        out = os.path.join(pdir, p["path"])
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if os.path.exists(out) and not os.path.exists(out + ".placeholder"):
            continue
        prompt = f'{BASE}, {p.get("prompt", "")}'
        if not online:
            placeholder(out, p.get("prompt", ""))
            print(f"{sid}p{k}: 임시 그림")
            continue
        seed = p.get("seed", random.randint(1, 2**31))
        if ref_name:
            wf = json.loads(open(WF, encoding="utf-8").read())
            wf.pop("_설명", None)
            txt = json.dumps(wf).replace("__CKPT__", ckpt).replace("__POS__", prompt.replace('"', "'")).replace("__NEG__", NEG).replace("__REF__", ref_name)
            txt = txt.replace('"__SEED__"', str(seed)).replace('"__W__"', "1344").replace('"__H__"', "768")
            wf = json.loads(txt)
        else:
            wf = C.txt2img_workflow(prompt, ckpt, 1344, 768, 28, seed, 6.0, NEG)
        paths = C.run(wf, os.path.dirname(out))
        C._save_as(paths, out)
        if os.path.exists(out + ".placeholder"):
            os.remove(out + ".placeholder")
        made += 1
        print(f"{sid}p{k}: 생성 {out}")
    print(f"완료: 새로 생성 {made}장")


if __name__ == "__main__":
    main(sys.argv[1:])
