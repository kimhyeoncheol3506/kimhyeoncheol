# -*- coding: utf-8 -*-
"""방어 대안 썸네일: 롱폼 1280×720 A·B안 + 쇼츠 세로 1080×1920 (CC BY 사진 + 큰 숫자)"""
import json, os, base64, subprocess, runpy
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.expanduser("~/.cache/ranking-video/fonts")
P = json.load(open(f"{R}/09_소재/img_final/pick.json")); img = lambda k: "data:image/jpeg;base64," + base64.b64encode(open(f"{R}/09_소재/img_final/{P[k]}.jpg", "rb").read()).decode()
font = lambda f: "data:font/otf;base64," + base64.b64encode(open(f"{F}/{f}", "rb").read()).decode()
G = runpy.run_path(f"{R}/01_대본/build_data.py", run_name="short"); gb, gs, B0, B1, DROP = G["G10"]("방어"), G["G10"]("부시리"), G["B0"], G["B1"], G["DROP"]
CSS = (f'@font-face{{font-family:BH;src:url({font("BlackHanSans-Regular.ttf")})}}@font-face{{font-family:PX;src:url({font("Pretendard-ExtraBold.otf")})}}'
       'body{margin:0;overflow:hidden;background:#0D0E11;font-family:PX}')
A = (f'<img src="{img("부시리")}" style="position:absolute;right:-60px;top:0;width:820px;height:720px;object-fit:cover">'
     '<div style="position:absolute;inset:0;background:linear-gradient(90deg,#0D0E11 0%,#0D0E11 40%,#0D0E11aa 60%,#0D0E1100 85%)"></div>'
     '<div style="position:absolute;left:44px;top:34px;font:54px BH;color:#D6B26E">노량진 경락가 · 1만 원어치 회</div>'
     f'<div style="position:absolute;left:40px;top:120px;font:150px BH;color:#fff;line-height:1.05;text-shadow:0 6px 0 #000">방어 {gb}g</div>'
     '<div style="position:absolute;left:46px;top:290px;font:70px BH;color:#8C919B">vs</div>'
     f'<div style="position:absolute;left:40px;top:360px;font:170px BH;color:#5FE0C4;line-height:1;text-shadow:0 8px 0 #000">부시리 {gs}g</div>'
     '<div style="position:absolute;left:44px;bottom:36px;padding:8px 24px;background:#FFD640;font:58px BH;color:#111">제2의 방어 5가지</div>')
B = (f'<img src="{img("방어")}" style="position:absolute;inset:0;width:1280px;height:720px;object-fit:cover;filter:brightness(.45)">'
     '<div style="position:absolute;left:0;right:0;top:36px;text-align:center;font:60px BH;color:#FFD640">노량진 방어 경락가 kg당</div>'
     f'<div style="position:absolute;left:0;right:0;top:140px;text-align:center;font:150px BH;color:#fff;text-shadow:0 6px 0 #000">{B0:,}→{B1:,}</div>'
     f'<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:200px BH;color:#FF5A3C;text-shadow:0 8px 0 #000">3주 새 {DROP}%↓</div>'
     '<div style="position:absolute;left:0;right:0;bottom:40px;text-align:center;font:66px BH;color:#F1D9A0;text-shadow:0 4px 0 #000">그래도 비싸면? 제2의 방어 5가지</div>')
V = (f'<img src="{img("부시리")}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;filter:brightness(.4)">'
     '<div style="position:absolute;left:0;right:0;top:150px;text-align:center;font:80px BH;color:#FFD640">1만 원어치 회</div>'
     f'<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:200px BH;color:#fff;text-shadow:0 8px 0 #000">방어 {gb}g</div>'
     '<div style="position:absolute;left:0;right:0;top:600px;text-align:center;font:110px BH;color:#8C919B">vs</div>'
     f'<div style="position:absolute;left:0;right:0;top:760px;text-align:center;font:220px BH;color:#5FE0C4;text-shadow:0 8px 0 #000">부시리<br>{gs}g</div>'
     '<div style="position:absolute;left:0;right:0;bottom:200px;text-align:center"><span style="padding:10px 34px;background:#FFD640;font:80px BH;color:#111">노량진 도매 경락가</span></div>')
JOBS = [("A", A, 1280, 720), ("B", B, 1280, 720), ("세로", V, 1080, 1920)]
for n, h, w, hh in JOBS:
    open(f"{R}/07_그래픽/thumb_{n}.html", "w", encoding="utf-8").write(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div style='position:relative;width:{w}px;height:{hh}px;overflow:hidden'>{h}</div></body></html>")
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const J=JSON.parse(process.argv[3]);
for(const [n,w,h] of J){const p=await b.newPage({viewport:{width:w,height:h}});await p.goto('file://'+process.argv[2]+'/thumb_'+n+'.html');await p.waitForTimeout(600);await p.screenshot({path:process.argv[2]+'/썸네일_'+n+'.png'});await p.close();}await b.close();})();"""
subprocess.run(["node", "-e", js, "x", f"{R}/07_그래픽", json.dumps([[n, w, h] for n, _, w, h in JOBS])], check=True)
for n, *_ in JOBS: os.remove(f"{R}/07_그래픽/thumb_{n}.html")
print("ok")
