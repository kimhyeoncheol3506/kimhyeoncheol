# -*- coding: utf-8 -*-
"""김장배추 썸네일: 롱폼 1280×720 A·B안 + 쇼츠 세로 1080×1920 (CC BY 사진 + 큰 숫자)"""
import json, os, base64, subprocess, runpy
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.expanduser("~/.cache/ranking-video/fonts")
P = json.load(open(f"{R}/09_소재/img_final/pick.json")); img = lambda k: "data:image/jpeg;base64," + base64.b64encode(open(f"{R}/09_소재/img_final/{P[k]}.jpg", "rb").read()).decode()
font = lambda f: "data:font/otf;base64," + base64.b64encode(open(f"{F}/{f}", "rb").read()).decode()
G = runpy.run_path(f"{R}/01_대본/build_data.py", run_name="short"); MPC = round((G["A"](2025, "배추", "10키로망대", "중") - G["A"](2026, "배추", "10키로망대", "중")) / G["A"](2025, "배추", "10키로망대", "중") * 100); BM, B26, B25, H10, AT20, r1 = G["BM26"], G["B26"], G["B25"], G["H10"], G["AT20"], G["r1000"]
CSS = (f'@font-face{{font-family:BH;src:url({font("BlackHanSans-Regular.ttf")})}}@font-face{{font-family:PX;src:url({font("Pretendard-ExtraBold.otf")})}}'
       'body{margin:0;overflow:hidden;background:#0D0E11;font-family:PX}')
A = (f'<img src="{img("배추")}" style="position:absolute;right:-40px;top:0;width:760px;height:720px;object-fit:cover">'
     '<div style="position:absolute;inset:0;background:linear-gradient(90deg,#0D0E11 0%,#0D0E11 42%,#0D0E11aa 62%,#0D0E1100 88%)"></div>'
     '<div style="position:absolute;left:44px;top:34px;font:56px BH;color:#D6B26E">가락시장 경매가 · 배추 중품 한 포기</div>'
     f'<div style="position:absolute;left:36px;top:130px;font:200px BH;color:#fff;line-height:1;text-shadow:0 8px 0 #000">{round(BM, -2):,.0f}원</div>'
     f'<div style="position:absolute;left:44px;top:360px;font:80px BH;color:#5FE0C4;text-shadow:0 6px 0 #000">작년보다 {MPC}%↓</div>'
     '<div style="position:absolute;left:44px;bottom:36px;padding:8px 24px;background:#FFD640;font:58px BH;color:#111">올해 김장 진짜 비용</div>')
B = (f'<img src="{img("김치")}" style="position:absolute;inset:0;width:1280px;height:720px;object-fit:cover;filter:brightness(.4)">'
     '<div style="position:absolute;left:0;right:0;top:34px;text-align:center;font:62px BH;color:#FFD640">김장 10포기 · 가장 큰 지출은?</div>'
     f'<div style="position:absolute;left:0;right:0;top:150px;text-align:center;font:150px BH;color:#FF5A3C;text-shadow:0 8px 0 #000">고춧가루 {r1(H10["고춧가루"])}원</div>'
     '<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:100px BH;color:#fff">&gt;</div>'
     f'<div style="position:absolute;left:0;right:0;top:450px;text-align:center;font:120px BH;color:#5FE0C4;text-shadow:0 6px 0 #000">배추 {r1(H10["배추"])}원</div>')
V = (f'<img src="{img("배추")}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;filter:brightness(.4)">'
     '<div style="position:absolute;left:0;right:0;top:160px;text-align:center;font:84px BH;color:#FFD640">가락시장 경매가 · 중품</div>'
     '<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:190px BH;color:#fff;line-height:1.1;text-shadow:0 8px 0 #000">배추<br>한 포기</div>'
     f'<div style="position:absolute;left:0;right:0;top:820px;text-align:center;font:230px BH;color:#5FE0C4;text-shadow:0 8px 0 #000">{round(BM, -2):,.0f}원</div>'
     f'<div style="position:absolute;left:0;right:0;top:1120px;text-align:center;font:110px BH;color:#fff">작년보다 {MPC}%↓</div>'
     '<div style="position:absolute;left:0;right:0;bottom:240px;text-align:center"><span style="padding:10px 34px;background:#FFD640;font:80px BH;color:#111">올해 김장 진짜 비용</span></div>')
JOBS = [("A", A, 1280, 720), ("B", B, 1280, 720), ("세로", V, 1080, 1920)]
for n, h, w, hh in JOBS:
    open(f"{R}/07_그래픽/thumb_{n}.html", "w", encoding="utf-8").write(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div style='position:relative;width:{w}px;height:{hh}px;overflow:hidden'>{h}</div></body></html>")
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const J=JSON.parse(process.argv[3]);
for(const [n,w,h] of J){const p=await b.newPage({viewport:{width:w,height:h}});await p.goto('file://'+process.argv[2]+'/thumb_'+n+'.html');await p.waitForTimeout(600);await p.screenshot({path:process.argv[2]+'/썸네일_'+n+'.png'});await p.close();}await b.close();})();"""
subprocess.run(["node", "-e", js, "x", f"{R}/07_그래픽", json.dumps([[n, w, h] for n, _, w, h in JOBS])], check=True)
for n, *_ in JOBS: os.remove(f"{R}/07_그래픽/thumb_{n}.html")
print("ok")
