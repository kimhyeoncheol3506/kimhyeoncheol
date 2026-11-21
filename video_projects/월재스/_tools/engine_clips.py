#!/usr/bin/env python3
"""월재스 엔진 클립: HyperFrames로 '큰 숫자 카운트업 + 키네틱 문구' 클립을 찍어 낸다.

  python engine_clips.py counter <설정.json> <출력.mp4>
설정 예: {"kicker":"2008년 10월, 아이슬란드","label":"크로나 가치","from":0,"to":-50,"unit":"%","decimals":0,
          "color":"#3d97e5","caption":"유로 대비, 1년 사이","tags":["은행 3곳 파산","IMF 구제금융"],"seconds":6}
화면 규칙: 1920x1080, 다크 #181614, Pretendard, 글자는 y 880 위(아래는 neogul-edit 자막 자리), 무음.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HF = os.path.join(REPO, "video_projects", "_engines", "hyperframes")
FONT = os.path.join(REPO, ".claude", "skills", "neogul-edit", "scripts", "fonts", "Pretendard-ExtraBold.otf")
CHS = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell"


def counter_html(c):
    tags = "".join("<span class='tag'>%s</span>" % t for t in c.get("tags", []))
    sec = float(c.get("seconds", 6))
    return """<!doctype html>
<html lang="ko" data-resolution="landscape"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
@font-face { font-family: "Pretendard"; src: url("Pretendard-ExtraBold.otf"); font-weight: 900; }
*{margin:0;padding:0;box-sizing:border-box} html,body{width:1920px;height:1080px;overflow:hidden;background:#181614}
#root{position:absolute;inset:0;font-family:"Pretendard",sans-serif;color:#fff}
.t{position:absolute}
#kicker{left:140px;top:120px;font-size:42px;color:#e3c04b;font-weight:900}
#label{left:140px;top:190px;font-size:76px;font-weight:900;letter-spacing:-3px}
#num{left:130px;top:300px;font-size:300px;font-weight:900;letter-spacing:-10px;color:%(color)s}
#num small{font-size:120px;letter-spacing:-3px}
#bar{left:140px;top:690px;width:1640px;height:16px;background:%(color)s;transform-origin:left center}
#cap{left:140px;top:735px;font-size:44px;color:#a39d94;font-weight:900}
#tags{left:140px;top:805px;display:flex;gap:18px}
.tag{background:#24221f;border:2px solid #3d3b37;color:#fff;font-size:36px;font-weight:900;padding:8px 22px;border-radius:10px}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="%(sec)s" data-width="1920" data-height="1080">
 <div id="kicker" class="t clip" data-start="0" data-duration="%(sec)s" data-track-index="0">%(kicker)s</div>
 <div id="label" class="t clip" data-start="0" data-duration="%(sec)s" data-track-index="1">%(label)s</div>
 <div id="num" class="t clip" data-start="0" data-duration="%(sec)s" data-track-index="2"><span id="n">%(start)s</span><small>%(unit)s</small></div>
 <div id="bar" class="t clip" data-start="0" data-duration="%(sec)s" data-track-index="3"></div>
 <div id="cap" class="t clip" data-start="0" data-duration="%(sec)s" data-track-index="4">%(caption)s</div>
 <div id="tags" class="t clip" data-start="0" data-duration="%(sec)s" data-track-index="5">%(tags)s</div>
</div>
<script>
const tl = gsap.timeline({ paused: true });
const c = { v: %(frm)s };
const fmt = v => { const s = Math.abs(v).toFixed(%(dec)d).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ","); return (v < 0 ? "-" : (%(plus)s && v > 0 ? "+" : "")) + s; };
tl.fromTo("#kicker", {opacity:0, x:-30}, {opacity:1, x:0, duration:0.35, ease:"power3.out"}, 0);
tl.fromTo("#label", {opacity:0, y:40}, {opacity:1, y:0, duration:0.4, ease:"back.out(1.8)"}, 0.15);
tl.fromTo("#num", {opacity:0, scale:0.88}, {opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}, 0.45);
tl.to(c, {v: %(to)s, duration: 1.8, ease:"power2.out", onUpdate: () => { document.getElementById("n").textContent = fmt(c.v); }}, 0.55);
tl.fromTo("#bar", {scaleX:0}, {scaleX:1, duration:0.8, ease:"power4.out"}, 2.3);
tl.fromTo("#cap", {opacity:0}, {opacity:1, duration:0.4}, 2.6);
tl.fromTo(".tag", {opacity:0, y:20}, {opacity:1, y:0, duration:0.3, stagger:0.25}, 3.0);
tl.to({}, {duration: %(rest)s}, 3.6);
window.__timelines["main"] = tl; tl.seek(0);
</script></body></html>""" % dict(color=c.get("color", "#f2262b"), sec=sec, kicker=c.get("kicker", ""), label=c.get("label", ""),
                                 start=c.get("from", 0), unit=c.get("unit", ""), caption=c.get("caption", ""), tags=tags,
                                 frm=c.get("from", 0), to=c["to"], dec=int(c.get("decimals", 0)), plus="true" if c.get("plus") else "false",
                                 rest=max(0.5, sec - 3.6))


def render(html, out):
    d = tempfile.mkdtemp(prefix="hf_")
    for f in ("hyperframes.json", "meta.json", "package.json"):
        shutil.copy(os.path.join(HF, "econ-test", f), d)
    shutil.copy(FONT, d)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
    env = dict(os.environ, DO_NOT_TRACK="1", HYPERFRAMES_SKIP_SKILLS="1")
    if os.path.exists(CHS):
        env["HYPERFRAMES_BROWSER_PATH"] = CHS
    r = subprocess.run(["npx", "hyperframes", "render", d, "-o", os.path.abspath(out)], cwd=HF, env=env, capture_output=True, text=True)
    if r.returncode or not os.path.exists(out):
        raise SystemExit("HyperFrames 렌더 실패:\n" + r.stdout[-1500:] + r.stderr[-1500:])
    print("[clip]", out)


if __name__ == "__main__":
    if sys.argv[1] == "counter":
        render(counter_html(json.load(open(sys.argv[2], encoding="utf-8"))), sys.argv[3])
