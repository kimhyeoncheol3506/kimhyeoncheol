"""HyperFrames 숫자 카운터 클립 생성기: python make_clip.py <이름> <제목> <시작> <끝> <단위> <배지> <글자크기> [log]"""
import os, shutil, subprocess, sys
name, title, a, b, unit, badge, fsz = sys.argv[1:8]
use_log = len(sys.argv) > 8
root = f"/home/user/hf/{name}"
if not os.path.exists(root):
    subprocess.run(["npx", "-y", "hyperframes", "init", name, "--example", "blank", "--non-interactive"], cwd="/home/user/hf", check=True, capture_output=True)
os.makedirs(f"{root}/assets/fonts", exist_ok=True)
shutil.copy("/home/user/kimhyeoncheol/video-studio/assets/fonts/Pretendard-Black.otf", f"{root}/assets/fonts/")
interp = "Math.exp(Math.log(%s) + (Math.log(%s) - Math.log(%s)) * st.p)" % (a, b, a) if use_log else "%s + (%s - %s) * st.p" % (a, b, a)
html = f"""<!doctype html>
<html lang="ko"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "PretendardBlack"; src: url("assets/fonts/Pretendard-Black.otf"); font-weight: 900; }}
:root {{ --ground: #fcf4e0; --ink: #4a2e24; --red: #d64c4c; --font-display: "PretendardBlack", sans-serif; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: var(--ground); }}
#root {{ width: 100%; height: 100%; position: relative; font-family: var(--font-display); color: var(--ink); }}
.label {{ position: absolute; left: 0; width: 100%; text-align: center; }}
#l1 {{ top: 170px; font-size: 76px; }}
#price {{ top: 330px; font-size: {fsz}px; white-space: nowrap; }}
#unit {{ top: 690px; font-size: 80px; }}
#badge {{ position: absolute; left: 50%; margin-left: -230px; top: 820px; width: 460px; text-align: center; padding: 18px 0; border-radius: 80px; background: var(--red); color: #fff; font-size: 90px; }}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="6" data-width="1920" data-height="1080">
<div id="l1" class="clip label" data-start="0" data-duration="6" data-track-index="0">{title}</div>
<div id="price" class="clip label" data-start="0" data-duration="6" data-track-index="1">{a}</div>
<div id="unit" class="clip label" data-start="0" data-duration="6" data-track-index="2">{unit}</div>
<div id="badge" class="clip" data-start="0" data-duration="6" data-track-index="3">{badge}</div>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
const st = {{ p: 0 }};
const fmt = (n) => Math.round(n).toLocaleString("en-US");
tl.fromTo("#l1", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0);
tl.fromTo("#price", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.2);
tl.to(st, {{ p: 1, duration: 2.6, ease: "power2.inOut", onUpdate: () => {{ document.getElementById("price").textContent = fmt({interp}); }} }}, 1.0);
tl.fromTo("#price", {{ color: "#4a2e24" }}, {{ color: "#d64c4c", duration: 0.6 }}, 2.8);
tl.fromTo("#badge", {{ scale: 0, opacity: 0, transformOrigin: "50% 50%" }}, {{ scale: 1, opacity: 1, duration: 0.5, ease: "back.out(2.4)" }}, 3.0);
window.__timelines["main"] = tl;
tl.seek(0);
</script></body></html>
"""
open(f"{root}/index.html", "w", encoding="utf-8").write(html)
os.makedirs(f"{root}/out", exist_ok=True)
r = subprocess.run(["npx", "-y", "hyperframes", "check", "--json"], cwd=root, capture_output=True, text=True)
import json
d = json.loads(r.stdout[r.stdout.index("{"):])
errs = [f for k in ("layout", "lint", "runtime") for f in (d.get(k) or {}).get("findings", []) if f["severity"] == "error"]
print(name, "check ok" if d["ok"] else "check FAIL", [e["code"] + ":" + e["message"][:80] for e in errs])
subprocess.run(["npx", "-y", "hyperframes", "render", "-o", "out/clip.mp4", "-f", "30", "-q", "looks"], cwd=root, check=True, capture_output=True)
print("rendered", f"{root}/out/clip.mp4")
