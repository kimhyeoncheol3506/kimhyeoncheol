# -*- coding: utf-8 -*-
"""가락시장 시리즈 썸네일: 롱폼 1280×720 A·B안 + 쇼츠 세로 1080×1920 (topic.json thumb 문구 + CC 사진)"""
import json, os, base64, subprocess, runpy, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/patterns"); import theme as TH
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.expanduser("~/.cache/ranking-video/fonts")
P = json.load(open(f"{R}/09_소재/img_final/pick.json")); img = lambda k: "data:image/jpeg;base64," + base64.b64encode(open(f"{R}/09_소재/img_final/{P[k]}.jpg", "rb").read()).decode()
font = lambda f: "data:font/otf;base64," + base64.b64encode(open(f"{F}/{f}", "rb").read()).decode()
G = runpy.run_path(f"{R}/01_대본/build_data.py", run_name="short"); T = G["CFG"]["thumb"]   # {top, big, sub, tag, b_top, b_big, b_sub, v_lines}
CSS = (f'@font-face{{font-family:BH;src:url({font("BlackHanSans-Regular.ttf")})}}@font-face{{font-family:PX;src:url({font("Pretendard-ExtraBold.otf")})}}body{{margin:0;overflow:hidden;background:#0D0E11;font-family:PX}}')
ph = G["CFG"]["photo_main"]; ph2 = G["CFG"].get("photo_b", ph)
A = (f'<img src="{img(ph)}" style="position:absolute;right:-40px;top:0;width:760px;height:720px;object-fit:cover">'
     '<div style="position:absolute;inset:0;background:linear-gradient(90deg,#0D0E11 0%,#0D0E11 42%,#0D0E11aa 62%,#0D0E1100 88%)"></div>'
     f'<div style="position:absolute;left:44px;top:34px;font:54px BH;color:#D6B26E">{T["top"]}</div>'
     f'<div style="position:absolute;left:36px;top:120px;font:{T.get("bigsize", 190)}px BH;color:#fff;line-height:1.02;text-shadow:0 8px 0 #000">{T["big"]}</div>'
     f'<div style="position:absolute;left:44px;top:{500 if "<br>" in T["big"] else 400}px;font:78px BH;color:{T.get("subcol", "#5FE0C4")};text-shadow:0 6px 0 #000">{T["sub"]}</div>'
     f'<div style="position:absolute;left:44px;bottom:36px;padding:8px 24px;background:#FFD640;font:58px BH;color:#111">{T["tag"]}</div>')
B = (f'<img src="{img(ph2)}" style="position:absolute;inset:0;width:1280px;height:720px;object-fit:cover;filter:brightness(.42)">'
     f'<div style="position:absolute;left:0;right:0;top:34px;text-align:center;font:60px BH;color:#FFD640">{T["b_top"]}</div>'
     f'<div style="position:absolute;left:0;right:0;top:150px;text-align:center;font:{T.get("b_bigsize", 170)}px BH;color:#fff;line-height:1.1;text-shadow:0 8px 0 #000">{T["b_big"]}</div>'
     f'<div style="position:absolute;left:0;right:0;bottom:50px;text-align:center;font:90px BH;color:#FF5A3C;text-shadow:0 6px 0 #000">{T["b_sub"]}</div>')
V = (f'<img src="{img(ph)}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;filter:brightness(.4)">'
     f'<div style="position:absolute;left:0;right:0;top:170px;text-align:center;font:84px BH;color:#FFD640">{T["top"]}</div>'
     f'<div style="position:absolute;left:0;right:0;top:360px;text-align:center;font:200px BH;color:#fff;line-height:1.1;text-shadow:0 8px 0 #000">{T["v_big"]}</div>'
     f'<div style="position:absolute;left:0;right:0;top:1150px;text-align:center;font:120px BH;color:#5FE0C4;text-shadow:0 6px 0 #000">{T.get("v_sub", T["sub"])}</div>'
     f'<div style="position:absolute;left:0;right:0;bottom:240px;text-align:center"><span style="padding:10px 34px;background:#FFD640;font:80px BH;color:#111">{T["tag"]}</span></div>')
JOBS = [("A", A, 1280, 720), ("B", B, 1280, 720), ("세로", V, 1080, 1920)]
for k, X in enumerate(G["CFG"].get("thumb_shorts", []), 2):   # 쇼츠 2·3편 세로 썸네일
    JOBS.append((f"세로{k}", (f'<img src="{img(X.get("photo", ph))}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;filter:brightness(.4)">'
     f'<div style="position:absolute;left:0;right:0;top:170px;text-align:center;font:84px BH;color:#FFD640">{X["top"]}</div>'
     f'<div style="position:absolute;left:0;right:0;top:360px;text-align:center;font:{X.get("size", 200)}px BH;color:#fff;line-height:1.1;text-shadow:0 8px 0 #000">{X["v_big"]}</div>'
     f'<div style="position:absolute;left:0;right:0;top:1150px;text-align:center;font:110px BH;color:#5FE0C4;text-shadow:0 6px 0 #000">{X["sub"]}</div>'
     f'<div style="position:absolute;left:0;right:0;bottom:240px;text-align:center"><span style="padding:10px 34px;background:#FFD640;font:80px BH;color:#111">{X["tag"]}</span></div>'), 1080, 1920))
TM = TH.load(R)
if TM["num"]:   # 패턴 썸네일 틀: A안 = 패턴 틀(CFG["thumb"]의 패턴별 키 사용), 나머지는 패턴 색으로
    JOBS = [(n, TH.remap(TM, h), w, hh) for n, h, w, hh in JOBS]
    PA = TH.thumb_html(TM, T, img(ph), img(ph2) if ph2 != ph else None, fontdir=f"file://{F}/")
for n, h, w, hh in JOBS:
    if TM["num"] and n == "A":
        open(f"{R}/07_그래픽/thumb_A.html", "w", encoding="utf-8").write(PA); continue
    open(f"{R}/07_그래픽/thumb_{n}.html", "w", encoding="utf-8").write(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div style='position:relative;width:{w}px;height:{hh}px;overflow:hidden'>{h}</div></body></html>")
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const J=JSON.parse(process.argv[3]);
for(const [n,w,h] of J){const p=await b.newPage({viewport:{width:w,height:h}});await p.goto('file://'+process.argv[2]+'/thumb_'+n+'.html');await p.waitForTimeout(600);await p.screenshot({path:process.argv[2]+'/썸네일_'+n+'.png'});await p.close();}await b.close();})();"""
subprocess.run(["node", "-e", js, "x", f"{R}/07_그래픽", json.dumps([[n, w, h] for n, _, w, h in JOBS])], check=True)
for n, *_ in JOBS: os.remove(f"{R}/07_그래픽/thumb_{n}.html")
print("ok")
