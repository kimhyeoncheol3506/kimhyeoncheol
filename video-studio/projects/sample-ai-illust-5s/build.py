"""AI 일러스트 5초 샘플 (2026-11-11, 참고: '돈의 뒷마음' 동화풍 일러스트 영상).
그림 = Fish Audio gpt-image-2(1K) → Real-ESRGAN 2배(tools/upscale.py) / 움직임 = hf_econ illust v2(2컷·펀치인·빛 입자·해 광채·그레인)
목소리 = 여의도남자. 사용: python3 projects/sample-ai-illust-5s/build.py → make_video.py 로 마감."""
import json
import os
import subprocess
import sys

os.environ.setdefault("HF_LOOK", "sting")
os.environ.setdefault("HF_BG", "scenery")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PJ = "projects/sample-ai-illust-5s"
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)
import hf_econ as H  # noqa: E402
from studio import tts  # noqa: E402

pj = json.load(open(os.path.join(HERE, "project.json"), encoding="utf-8"))
s = pj["scenes"][0]
audio, _ = tts.scene_audio(s, pj, os.path.join(HERE, "audio"), False)
D = round((tts.duration(audio) + 0.45) * 30) / 30
cut = round(D * 0.52, 2)  # '원천징수영수증' 무렵 반응 컷
params = dict(
    shots=[dict(path=f"{PJ}/illust/s001.png", at=0, zoom=(1.04, 1.13), pan=(-40, -10), origin="35% 55%"),
           dict(path=f"{PJ}/illust/s002.png", at=cut, zoom=(1.0, 1.07), pan=(20, -12), origin="40% 40%")],
    glow=(1690, 470), motes=28,
    bubbles=[dict(t="어? 이게 얼마라고?", x=1160, y=190, w=600, tail="left", at=cut + 0.35, size=62)],
)
out = H.render(os.environ.get("HF_ROOT", "/home/user/hf/crisis"), "s001p0", "illust", params, D, os.path.join(HERE, "clips", "parts"), force=True)
os.makedirs(os.path.join(HERE, "clips"), exist_ok=True)
subprocess.run(["cp", out, os.path.join(HERE, "clips", "s001.mp4")], check=True)
s["visual"] = {"type": "clip", "path": f"{PJ}/clips/s001.mp4"}
json.dump(pj, open(os.path.join(HERE, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("clip", D, out)
