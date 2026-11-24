# -*- coding: utf-8 -*-
"""썸네일 1280×720: 저울 그래픽 + 킹크랩(CC BY 사진) + '3kg → 2kg?' 큰 숫자. A/B 두 장."""
import json, os, base64
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.expanduser("~/.cache/ranking-video/fonts")
P = json.load(open(f"{R}/09_소재/img_final/pick.json")); img = lambda k: "data:image/jpeg;base64," + base64.b64encode(open(f"{R}/09_소재/img_final/{P[k]}.jpg", "rb").read()).decode()
font = lambda f: "data:font/otf;base64," + base64.b64encode(open(f"{F}/{f}", "rb").read()).decode()
CSS = (f'@font-face{{font-family:BH;src:url({font("BlackHanSans-Regular.ttf")})}}@font-face{{font-family:PX;src:url({font("Pretendard-ExtraBold.otf")})}}'
       'body{margin:0;width:1280px;height:720px;overflow:hidden;background:#0D0E11;font-family:PX}')
def scale(v, c, x, y, w=430, lab=""):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;text-align:center"><div style="font:44px BH;color:{c};margin-bottom:8px">{lab}</div>'
            f'<div style="background:#050506;border:5px solid {c};padding:6px 0;box-shadow:0 0 40px {c}66"><span style="font:110px PX;color:{c};letter-spacing:-2px">{v}</span><span style="font:44px PX;color:{c}">kg</span></div>'
            f'<div style="height:22px;margin-top:12px;background:linear-gradient(#F1D9A0,#D6B26E);border-radius:4px"></div>'
            f'<div style="height:70px;margin:0 30px;background:linear-gradient(#262930,#121418);clip-path:polygon(5% 0,95% 0,100% 100%,0 100%)"></div></div>')
A = (f'<img src="{img("킹크랩")}" style="position:absolute;right:-60px;top:0;width:820px;height:720px;object-fit:cover">'
     '<div style="position:absolute;inset:0;background:linear-gradient(90deg,#0D0E11 0%,#0D0E11 38%,#0D0E11cc 55%,#0D0E1100 80%)"></div>'
     '<div style="position:absolute;left:44px;top:34px;font:48px BH;color:#D6B26E">노량진수산시장 킹크랩</div>'
     '<div style="position:absolute;left:40px;top:96px;font:200px BH;color:#fff;line-height:1;text-shadow:0 8px 0 #000">3kg<span style="color:#D6B26E">→</span><span style="color:#FF5A3C">2kg?</span></div>'
     + scale("3.00", "#F1D9A0", 50, 330, 360, "가게 저울") + scale("2.00", "#FF5A3C", 450, 330, 360, "집 저울")
     + '<div style="position:absolute;right:30px;bottom:30px;padding:10px 26px;background:#FFD640;font:56px BH;color:#111;transform:rotate(-3deg)">무게 속임수 5가지</div>')
B = (f'<img src="{img("킹크랩")}" style="position:absolute;inset:0;width:1280px;height:720px;object-fit:cover;filter:brightness(.55)">'
     '<div style="position:absolute;left:0;right:0;top:30px;text-align:center;font:54px BH;color:#FFD640">노량진수산시장 킹크랩 무게</div>'
     + scale("3.00", "#F1D9A0", 90, 140, 470, "") + scale("2.00", "#FF5A3C", 720, 140, 470, "")
     + '<div style="position:absolute;left:0;right:0;top:120px;text-align:center;font:150px BH;color:#fff;text-shadow:0 6px 0 #000">→</div>'
     '<div style="position:absolute;left:0;right:0;bottom:36px;text-align:center;font:120px BH;color:#fff;text-shadow:0 8px 0 #000">1kg <span style="color:#FF5A3C">어디 갔지?</span></div>')
for n, h in (("A", A), ("B", B)):
    open(f"{R}/07_그래픽/thumb_{n}.html", "w", encoding="utf-8").write(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div style='position:relative;width:1280px;height:720px'>{h}</div></body></html>")
import subprocess
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:720}});
for(const n of ['A','B']){await p.goto('file://'+process.argv[2]+'/thumb_'+n+'.html');await p.waitForTimeout(500);await p.screenshot({path:process.argv[2]+'/썸네일_'+n+'.png'});}await b.close();})();"""
subprocess.run(["node", "-e", js, "x", f"{R}/07_그래픽"], check=True)
for n in "AB": os.remove(f"{R}/07_그래픽/thumb_{n}.html")
print("ok")
