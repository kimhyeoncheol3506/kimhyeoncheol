# layout: orbit (2026-11-10, 챗GPT 닷츠): 호박색·검정 밤하늘 바탕 + 오른쪽 크게 빛나는 주황 동그라미 캐릭터(눈 두 개, 직접 그림)
#   + 그 둘레를 도는 궤도 두 줄과 일 아이콘(메일·달력·코드·문서·말풍선) + 초승달·Zzz(잠든 사이) + 왼쪽 아주 큰 크림/주황 제목 + 검정 알약
# 대본 thumbnail: {layout: orbit, badge, line1, line2, line3("[[강조]]" 가능), pill_html, orbit_icons: [..5개]}
# 실제 회사 로고는 그리지 않는다.
import html as _h
import re


def _mark(s):
    return re.sub(r"\[\[(.+?)\]\]", r'<em>\1</em>', _h.escape(s or ""))


def page(t, fonts_uri, W, H):
    esc = _h.escape
    icons = t.get("orbit_icons") or ["✉️", "⏰", "💻", "📄", "💬"]
    n = len(icons)
    sats = "".join(
        f'<div class="sat" style="--a:{-120 + i * (250 / max(1, n - 1))}deg"><span>{esc(g)}</span></div>' for i, g in enumerate(icons))
    stars = "".join(
        f'<i style="left:{(i * 137) % 1900}px;top:{(i * 71) % 520}px;opacity:{0.25 + (i % 5) * 0.12}"></i>' for i in range(46))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts_uri}/Pretendard-Black.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:#0B0603}}
#bg{{position:absolute;inset:0;background:radial-gradient(circle at 72% 48%,#5A2A06 0%,#2A1204 32%,#0B0603 68%)}}
#stars i{{position:absolute;width:6px;height:6px;border-radius:50%;background:#FFE0B0}}
#stripe{{position:absolute;left:0;right:0;bottom:0;height:150px;background:repeating-linear-gradient(-45deg,#FF8A1F 0 46px,#0B0603 46px 92px);opacity:.9}}
#moon{{position:absolute;left:1690px;top:70px;width:120px;height:120px;border-radius:50%;box-shadow:-26px 14px 0 0 #FFE0B0;transform:rotate(-20deg)}}
#zz{{position:absolute;left:1560px;top:60px;font-size:64px;color:#FFE0B0;letter-spacing:4px;transform:rotate(-12deg)}}
#zz b{{font-size:44px;opacity:.7}}
.ring{{position:absolute;left:1330px;top:520px;border:4px dashed rgba(255,170,90,.55);border-radius:50%;transform:translate(-50%,-50%) rotate(-14deg)}}
#dot{{position:absolute;left:1330px;top:520px;width:430px;height:430px;margin:-215px 0 0 -215px;border-radius:50%;
  background:radial-gradient(circle at 34% 28%,#FFD39A 0%,#FF8A1F 48%,#B44E00 100%);box-shadow:0 0 120px #FF8A1Fcc,0 0 260px #FF8A1F66,inset -30px -40px 70px #8A3A0055}}
#dot .e{{position:absolute;top:150px;width:44px;height:78px;border-radius:30px;background:#2A1404}}
#dot .e:after{{content:"";position:absolute;left:10px;top:12px;width:14px;height:18px;border-radius:50%;background:#fff}}
#dot .c{{position:absolute;top:235px;width:56px;height:30px;border-radius:50%;background:#FF6A3D;opacity:.55}}
#dot .m{{position:absolute;left:180px;top:270px;width:70px;height:34px;border-bottom:10px solid #2A1404;border-radius:0 0 50px 50px}}
.sat{{position:absolute;left:1330px;top:520px;width:0;height:0;transform:rotate(var(--a)) translateX(330px)}}
.sat span{{position:absolute;left:-58px;top:-58px;width:116px;height:116px;border-radius:30px;background:#1A0D05;border:5px solid #FF8A1F;
  display:flex;align-items:center;justify-content:center;font-size:62px;transform:rotate(calc(-1 * var(--a)));box-shadow:0 10px 30px #000c}}
#badge{{position:absolute;left:80px;top:72px;font-size:52px;color:#140A04;background:#FF8A1F;padding:10px 34px 16px;border-radius:16px;letter-spacing:-1px;
  box-shadow:0 8px 0 #000}}
#t1,#t2,#t3{{position:absolute;left:72px;line-height:1;white-space:nowrap;letter-spacing:-8px;-webkit-text-stroke:14px #000;paint-order:stroke fill;text-shadow:0 12px 0 #000}}
#t1{{top:200px;font-size:{t.get('size1', 150)}px;color:#FFF4E6}}
#t2{{top:370px;font-size:{t.get('size2', 190)}px;color:#FFF4E6}}
#t3{{top:585px;font-size:{t.get('size3', 170)}px;color:#FFE0B0}}
em{{font-style:normal;color:#FF8A1F}}
#pill{{position:absolute;left:80px;top:810px;font-size:56px;color:#FFE0B0;background:#000;padding:14px 38px 20px;border-radius:24px;border:4px solid #FF8A1F;letter-spacing:-1px}}
#pill b{{color:#FF8A1F}}
</style></head><body><div id="bg"></div><div id="stars">{stars}</div>
<div class="ring" style="width:680px;height:420px"></div><div class="ring" style="width:880px;height:600px;opacity:.6"></div>
<div id="dot"><div class="e" style="left:130px"></div><div class="e" style="left:250px"></div><div class="c" style="left:70px"></div><div class="c" style="left:305px"></div><div class="m"></div></div>
{sats}
<div id="moon"></div><div id="zz">Z<b>z</b><b>z</b></div>
<div id="stripe"></div>
<div id="badge">{esc(t.get('badge', ''))}</div>
<div id="t1">{_mark(t.get('line1'))}</div>
<div id="t2">{_mark(t.get('line2'))}</div>
<div id="t3">{_mark(t.get('line3'))}</div>
<div id="pill">{t.get('pill_html') or esc(t.get('pill', ''))}</div>
<script>for(const id of ['t1','t2','t3']){{const e=document.getElementById(id);let f=parseFloat(getComputedStyle(e).fontSize);while(e.getBoundingClientRect().right>1000&&f>70){{f-=6;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""
