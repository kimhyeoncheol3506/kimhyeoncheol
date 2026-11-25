# -*- coding: utf-8 -*-
"""광어 수율편 썸네일: 롱폼 1280×720(A·B안) + 쇼츠 세로 1080×1920 — 저울 위 광어 1kg → 접시 위 회 400g, 숫자 크게 (그래픽만, 사진 없음)"""
import json, os, base64, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.expanduser("~/.cache/ranking-video/fonts")
sys.path.insert(0, f"{R}/03_장면"); import yieldfx
font = lambda f: "data:font/otf;base64," + base64.b64encode(open(f"{F}/{f}", "rb").read()).decode()
P = json.load(open(f"{R}/00_data/prices.json")); TG = P["two"]["items"]["넙치(활)"]["med"]; c100 = TG / 0.4 / 10
ck = (lambda r: (f"{r // 10}만" if r >= 10 else "") + (f" {r % 10}천" if r % 10 else ""))(int(c100 / 1000 + 0.5)).strip()
CSS = (f'@font-face{{font-family:BH;src:url({font("BlackHanSans-Regular.ttf")})}}@font-face{{font-family:PXB;src:url({font("Pretendard-ExtraBold.otf")})}}@font-face{{font-family:PX;src:url({font("Pretendard-ExtraBold.otf")})}}'
       'body{margin:0;overflow:hidden;background:#0D0E11;font-family:PX}.num{font-family:PXB}')
fish = lambda P_, w: (f'<div style="width:{w}px;height:{w * 620 / 900:.0f}px">{yieldfx.svg(P_)}</div>'
                      f'<style>#{P_}plate{{display:none}}</style>')
plate = lambda w: (f'<svg width="{w}" height="{w * 0.42:.0f}" viewBox="140 430 620 190">{yieldfx.svg("p-").split("<g id=\"p-plate\" opacity=\"0\">")[1].split("</g>")[0]}</svg>')
BG = 'background:radial-gradient(900px 700px at 50% 40%,#1C1F26 0%,#0D0E11 70%)'
SCALE_TAG = lambda size: f'<div style="display:inline-block;background:#050506;border:5px solid #F1D9A0;padding:4px 26px;box-shadow:0 0 40px #F1D9A066"><span class="num" style="font-size:{size}px;color:#F1D9A0">1.00</span><span class="num" style="font-size:{size * 0.45:.0f}px;color:#F1D9A0">kg</span></div>'
A = (f'<div style="position:absolute;inset:0;{BG}"></div>'
     '<div style="position:absolute;left:0;right:0;top:22px;text-align:center;font:58px BH;color:#D6B26E">노량진수산시장 · 도매가로 계산</div>'
     f'<div style="position:absolute;left:10px;top:150px">{fish("a-", 640)}</div>'
     f'<div style="position:absolute;left:150px;top:420px">{SCALE_TAG(80)}</div>'
     '<div style="position:absolute;left:600px;top:250px;font:150px BH;color:#FF5A3C">→</div>'
     f'<div style="position:absolute;left:760px;top:430px">{plate(500)}</div>'
     '<div style="position:absolute;left:700px;top:170px;width:580px;text-align:center;font:175px BH;color:#fff;line-height:1;text-shadow:0 8px 0 #000">400g?</div>'
     '<div style="position:absolute;left:60px;top:110px;font:110px BH;color:#fff;text-shadow:0 6px 0 #000">광어 1kg</div>'
     f'<div style="position:absolute;left:40px;bottom:28px;padding:8px 26px;background:#FFD640;font:60px BH;color:#111">회 100g 원가 약 {ck}원</div>')
B = (f'<div style="position:absolute;inset:0;{BG}"></div>'
     '<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:64px BH;color:#FFD640">노량진수산시장 회 한 접시</div>'
     '<div style="position:absolute;left:0;right:0;top:150px;text-align:center;font:150px BH;color:#fff;line-height:1.05;text-shadow:0 8px 0 #000">진짜 원가<br><span style="color:#FF5A3C">계산했습니다</span></div>'
     f'<div style="position:absolute;left:0;right:0;bottom:40px;text-align:center;font:96px BH;color:#F1D9A0;text-shadow:0 6px 0 #000">광어 1kg → 회 400g</div>')
V = (f'<div style="position:absolute;inset:0;{BG}"></div>'
     '<div style="position:absolute;left:0;right:0;top:110px;text-align:center;font:64px BH;color:#D6B26E">노량진수산시장 · 도매가로 계산</div>'
     '<div style="position:absolute;left:0;right:0;top:210px;text-align:center;font:190px BH;color:#fff;line-height:1.05;text-shadow:0 8px 0 #000">광어 1kg<br>= 회 <span style="color:#FF5A3C">400g?</span></div>'
     f'<div style="position:absolute;left:90px;top:640px">{fish("v-", 900)}</div>'
     f'<div style="position:absolute;left:0;right:0;top:1010px;text-align:center">{SCALE_TAG(100)}</div>'
     '<div style="position:absolute;left:0;right:0;top:1150px;text-align:center;font:140px BH;color:#FF5A3C">↓</div>'
     f'<div style="position:absolute;left:190px;top:1300px">{plate(700)}</div>'
     f'<div style="position:absolute;left:0;right:0;bottom:120px;text-align:center"><span style="padding:10px 34px;background:#FFD640;font:80px BH;color:#111">회 100g 원가 약 {ck}원</span></div>')
JOBS = [("A", A, 1280, 720), ("B", B, 1280, 720), ("세로", V, 1080, 1920)]
for n, h, w, hh in JOBS:
    open(f"{R}/07_그래픽/thumb_{n}.html", "w", encoding="utf-8").write(f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body><div style='position:relative;width:{w}px;height:{hh}px;overflow:hidden'>{h}</div></body></html>")
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const J=JSON.parse(process.argv[3]);
for(const [n,w,h] of J){const p=await b.newPage({viewport:{width:w,height:h}});await p.goto('file://'+process.argv[2]+'/thumb_'+n+'.html');await p.waitForTimeout(600);await p.screenshot({path:process.argv[2]+'/썸네일_'+n+'.png'});await p.close();}await b.close();})();"""
subprocess.run(["node", "-e", js, "x", f"{R}/07_그래픽", json.dumps([[n, w, h] for n, _, w, h in JOBS])], check=True)
for n, *_ in JOBS: os.remove(f"{R}/07_그래픽/thumb_{n}.html")
print("ok")
