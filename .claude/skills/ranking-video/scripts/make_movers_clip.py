# -*- coding: utf-8 -*-
"""HyperFrames로 '많이 내린·오른 품목' 막대 차트 클립 만들기 (ranking-video v2.9.0)

사용법: python3 -I make_movers_clip.py <대본데이터.json> <작업폴더> [--out 섹션이름]
입력: 대본데이터.json의 graphics.movers_items(내린 것 큰 순서 → 오른 것 작은 순서)와 graphics.info_cards의 movers 카드 sub(기간 문구)
출력: <작업폴더>/09_소재/video/<섹션이름>__NN.mp4 (기본 섹션 '한눈에', 1920x1080 30fps 9초, 소리 없음) → render_video.py가 사진 사이에 자동으로 넣는다
필요: Node 22+, ffmpeg, 인터넷(HyperFrames CLI 0.8.214와 GSAP를 npm/CDN에서 받음). 템플릿: templates/hyperframes_movers/
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); TPL = os.path.join(HERE, "..", "templates", "hyperframes_movers")
D = json.load(open(sys.argv[1], encoding="utf-8")); proj = sys.argv[2]
sec = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "한눈에"
items = D["graphics"]["movers_items"]; sub = next((c.get("sub", "") for c in D["graphics"].get("info_cards", []) if c.get("kind") == "movers"), "")
data = json.dumps([[x["name"], x["change"]] for x in items], ensure_ascii=False)
work = tempfile.mkdtemp(prefix="hf_movers_"); shutil.copytree(TPL, work, dirs_exist_ok=True)
p = os.path.join(work, "index.html"); s = open(p, encoding="utf-8").read()
s = s.replace("/*DATA*/[]", data).replace("/*SUB*/", f"{sub} · kg당 경락 중앙값 변동률")
open(p, "w", encoding="utf-8").write(s)
V = "hyperframes@0.8.214"
for cmd in (["check", "--json"], ["render"]):
    r = subprocess.run(["npx", "--yes", V] + cmd, cwd=work, capture_output=True, text=True)
    if cmd[0] == "check":
        ok = json.loads(r.stdout).get("ok") if r.stdout.strip().startswith("{") else False
        if not ok: sys.exit("HyperFrames check 실패:\n" + r.stdout[-1500:])
    elif r.returncode != 0: sys.exit("render 실패:\n" + (r.stdout + r.stderr)[-1500:])
out = sorted(f for f in os.listdir(os.path.join(work, "renders")) if f.endswith(".mp4"))[-1]
vdir = os.path.join(proj, "09_소재", "video"); os.makedirs(vdir, exist_ok=True)
n = len([f for f in os.listdir(vdir) if f.startswith(sec + "__")]) + 1
dst = os.path.join(vdir, f"{sec}__{n:02d}.mp4"); shutil.copy(os.path.join(work, "renders", out), dst); shutil.rmtree(work, ignore_errors=True); print(dst)
