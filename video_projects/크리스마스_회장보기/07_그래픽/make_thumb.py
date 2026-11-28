# -*- coding: utf-8 -*-
"""크리스마스·연말 회 장보기 썸네일 1280×720 A/B (CC BY 회 사진 + 큰 숫자)"""
import json, os, base64, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/patterns"); import theme as TH
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.expanduser("~/.cache/ranking-video/fonts")
P = json.load(open(f"{R}/09_소재/img_final/pick.json")); img = lambda k: "data:image/jpeg;base64," + base64.b64encode(open(f"{R}/09_소재/img_final/{P[k]}.jpg", "rb").read()).decode()
font = lambda f: "data:font/otf;base64," + base64.b64encode(open(f"{F}/{f}", "rb").read()).decode()
CSS = (f'@font-face{{font-family:BH;src:url({font("BlackHanSans-Regular.ttf")})}}@font-face{{font-family:PX;src:url({font("Pretendard-ExtraBold.otf")})}}'
       'body{margin:0;overflow:hidden;background:#0D0E11;font-family:PX}')
def scale(v, c, x, y, w=430, lab=""):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;text-align:center"><div style="font:44px BH;color:{c};margin-bottom:8px">{lab}</div>'
            f'<div style="background:#050506;border:5px solid {c};padding:6px 0;box-shadow:0 0 40px {c}66"><span style="font:110px PX;color:{c};letter-spacing:-2px">{v}</span><span style="font:44px PX;color:{c}">kg</span></div>'
            f'<div style="height:22px;margin-top:12px;background:linear-gradient(#F1D9A0,#D6B26E);border-radius:4px"></div>'
            f'<div style="height:70px;margin:0 30px;background:linear-gradient(#262930,#121418);clip-path:polygon(5% 0,95% 0,100% 100%,0 100%)"></div></div>')
G = json.load(open(f"{R}/01_대본/대본데이터.json", encoding="utf-8"))["sections"][0]["vis"]; d = G["won"]
dk = (lambda r: (f"{r // 10}만" if r >= 10 else "") + (f" {r % 10}천" if r % 10 else ""))(int(d / 1000 + 0.5)).strip()
A = (f'<img src="{img("회")}" style="position:absolute;right:-40px;top:0;width:760px;height:720px;object-fit:cover">'
     '<div style="position:absolute;inset:0;background:linear-gradient(90deg,#0D0E11 0%,#0D0E11 42%,#0D0E11bb 60%,#0D0E1100 85%)"></div>'
     '<div style="position:absolute;left:44px;top:36px;font:50px BH;color:#D6B26E">노량진수산시장 크리스마스 회</div>'
     '<div style="position:absolute;left:44px;top:110px;font:92px BH;color:#fff;line-height:1.15">크리스마스 주에 사면</div>'
     f'<div style="position:absolute;left:36px;top:220px;font:210px BH;color:#FF5A3C;line-height:1;text-shadow:0 8px 0 #000">+{dk}원</div>'
     '<div style="position:absolute;left:46px;top:470px;font:52px PX;color:#F1D9A0">작년 10명 농어 5kg · 12월 첫 주 대비</div>'
     '<div style="position:absolute;left:44px;bottom:40px;padding:10px 26px;background:#FFD640;font:60px BH;color:#111">언제 사러 갈까?</div>')
B = (f'<img src="{img("회")}" style="position:absolute;inset:0;width:1280px;height:720px;object-fit:cover;filter:brightness(.5)">'
     '<div style="position:absolute;left:0;right:0;top:34px;text-align:center;font:56px BH;color:#FFD640">노량진수산시장 연말 회 장보기</div>'
     '<div style="position:absolute;left:0;right:0;top:150px;text-align:center;font:120px BH;color:#fff;text-shadow:0 6px 0 #000">12월 첫 주 <span style="color:#D6B26E">vs</span><br>크리스마스 주</div>'
     f'<div style="position:absolute;left:0;right:0;bottom:50px;text-align:center;font:110px BH;color:#FF5A3C;text-shadow:0 6px 0 #000">10명 +{dk}원</div>')
TM = TH.load(R)   # 패턴 색으로 바꿈 (patterns/theme.py remap)
V = (f'<img src="{img("회")}" style="position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;filter:brightness(.42)">'
     '<div style="position:absolute;left:0;right:0;top:200px;text-align:center;font:84px BH;color:#FFD640">노량진 크리스마스 회</div>'
     '<div style="position:absolute;left:0;right:0;top:380px;text-align:center;font:150px BH;color:#fff;line-height:1.15;text-shadow:0 8px 0 #000">크리스마스 주에<br>사면</div>'
     f'<div style="position:absolute;left:0;right:0;top:900px;text-align:center;font:220px BH;color:#FF5A3C;text-shadow:0 8px 0 #000">+{dk}원</div>'
     '<div style="position:absolute;left:0;right:0;top:1200px;text-align:center;font:64px PX;color:#F1D9A0">작년 10명 농어 5kg · 12월 첫 주 대비</div>'
     '<div style="position:absolute;left:0;right:0;bottom:260px;text-align:center"><span style="padding:10px 34px;background:#FFD640;font:80px BH;color:#111">언제 사러 갈까?</span></div>')
for n, h, w, hh in (("A", A, 1280, 720), ("B", B, 1280, 720), ("세로", V, 1080, 1920)):
    open(f"{R}/07_그래픽/thumb_{n}.html", "w", encoding="utf-8").write(TH.remap(TM, f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div style='position:relative;width:{w}px;height:{hh}px;overflow:hidden'>{h}</div></body></html>"))
import subprocess
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:720}});
for(const [n,w,h] of [['A',1280,720],['B',1280,720],['세로',1080,1920]]){await p.setViewportSize({width:w,height:h});await p.goto('file://'+process.argv[2]+'/thumb_'+n+'.html');await p.waitForTimeout(500);await p.screenshot({path:process.argv[2]+'/썸네일_'+n+'.png'});}await b.close();})();"""
subprocess.run(["node", "-e", js, "x", f"{R}/07_그래픽"], check=True)
for n in ("A", "B", "세로"): os.remove(f"{R}/07_그래픽/thumb_{n}.html")
print("ok")
