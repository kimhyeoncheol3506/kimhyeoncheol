"""33편 썸네일 캔바 스타일 후보 2개 (현철님 2026-11-08 '캔바 스타일로 다시 후보군 2개')
밝은 단색 배경, 둥근 라벨·카드, 흰 테두리 스티커 캐릭터, 손그림 낙서 포인트. 렌더는 make_thumb_v2.render 재사용."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_thumb_v2 as M

STK = "drop-shadow(6px 0 0 #fff) drop-shadow(-6px 0 0 #fff) drop-shadow(0 6px 0 #fff) drop-shadow(0 -6px 0 #fff) drop-shadow(0 18px 24px rgba(0,0,0,.25))"


def sticker(name, right, bottom, w, rot=0):
    return (f'<div class="abs" style="right:{right}px;bottom:{bottom}px;width:{w}px;height:{int(w*1.25)}px;transform:rotate({rot}deg)">'
            f'<img src="assets/mascot/{name}.png" style="width:100%;height:100%;object-fit:contain;filter:{STK}"></div>')


def doodles(col):
    return (f'<svg class="abs" style="left:0;top:0" width="1920" height="1080" fill="none" stroke="{col}" stroke-width="10" stroke-linecap="round">'
            '<path d="M1270 170 l20 -60 M1310 190 l50 -40 M1330 240 l60 -10"/>'
            '<path d="M1760 120 l14 34 36 4 -28 22 10 36 -32 -20 -32 20 10 -36 -28 -22 36 -4z" stroke-width="7"/>'
            '<path d="M1180 900 q40 -40 80 0 t80 0 t80 0" stroke-width="8"/></svg>')


def design(v):
    if v == "D":  # 노랑 배경 + 검정 라벨 + 파랑 형광펜
        bg = "#FFD84D"
        dots = '<div class="abs" style="inset:0;background-image:radial-gradient(#00000014 3px,transparent 3px);background-size:36px 36px"></div>'
        body = (dots + doodles("#111") +
                '<div class="abs" style="left:80px;top:120px;padding:18px 44px 24px;border-radius:999px;background:#111;color:#FFD84D;font-family:BH;font-size:96px;transform:rotate(-2deg)">월급쟁이 필수</div>' +
                '<div class="abs" style="left:76px;top:300px;font-family:BH;font-size:270px;line-height:1;color:#111;letter-spacing:-6px">경제 지식</div>' +
                '<div class="abs" style="left:70px;top:640px;width:900px;height:120px;background:#3D7BFF;border-radius:20px;transform:rotate(-1.5deg)"></div>' +
                '<div class="abs" style="left:96px;top:580px;font-family:BH;font-size:230px;line-height:1;color:#fff;-webkit-text-stroke:0;text-shadow:8px 8px 0 #111;letter-spacing:-5px">완전정리</div>' +
                '<div class="abs" style="left:96px;top:880px;font-family:PB;font-size:46px;color:#111">통화량 · 금리 · 환율 · 부동산 · 부채 · 경제위기</div>' +
                '<div class="abs" style="right:90px;top:70px;width:230px;height:230px;border-radius:50%;background:#FF5A5F;color:#fff;font-family:BH;font-size:62px;line-height:1.05;display:flex;align-items:center;justify-content:center;text-align:center;transform:rotate(10deg);box-shadow:0 10px 0 #111">2시간<br>몰아보기</div>' +
                sticker("놀람", 90, 30, 560, -4))
    else:  # 네이비 배경 + 흰 카드 + 코랄 포인트
        bg = "linear-gradient(160deg,#1E2A5A 0%,#14193A 100%)"
        icons = "".join(f'<div style="width:118px;height:118px;border-radius:50%;background:{c};color:#fff;font-family:BH;font-size:{fs}px;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 0 rgba(0,0,0,.25)">{t}</div>'
                        for t, c, fs in [("₩", "#FF6B5B", 64), ("%", "#3DB9A4", 64), ("$", "#F2B33D", 64), ("집", "#7A6BFF", 52)])
        body = ('<div class="abs" style="left:-120px;top:-160px;width:620px;height:620px;border-radius:50%;background:#2B3A78"></div>'
                '<div class="abs" style="right:-160px;bottom:-200px;width:760px;height:760px;border-radius:50%;background:#FF6B5B"></div>' +
                '<div class="abs" style="left:70px;top:90px;width:1260px;height:900px;border-radius:48px;background:#FFFDF6;box-shadow:0 24px 0 rgba(0,0,0,.25)"></div>' +
                '<div class="abs" style="left:140px;top:150px;padding:12px 36px 16px;border-radius:16px;background:#FF6B5B;color:#fff;font-family:BH;font-size:84px">월급쟁이 필수</div>' +
                '<div class="abs" style="left:130px;top:300px;font-family:BH;font-size:250px;line-height:1;color:#1E2A5A;letter-spacing:-6px">경제 지식</div>' +
                '<div class="abs" style="left:130px;top:560px;font-family:BH;font-size:250px;line-height:1;color:#FF6B5B;letter-spacing:-6px">완전정리</div>' +
                '<svg class="abs" style="left:130px;top:815px" width="900" height="40"><path d="M5 25 Q220 5 450 22 T895 18" stroke="#1E2A5A" stroke-width="12" fill="none" stroke-linecap="round"/></svg>' +
                f'<div class="abs" style="left:140px;top:870px;display:flex;gap:26px">{icons}<div style="align-self:center;margin-left:14px;font-family:PB;font-size:52px;color:#1E2A5A">2시간 총정리</div></div>' +
                sticker("충격", 60, 20, 600, 3) + doodles("#FFFDF6").replace("M1180 900", "M2400 900"))
    return bg, body


M.design = design
if __name__ == "__main__":
    for v in (sys.argv[1:] or ["D", "E"]):
        print(M.render(v, f"/tmp/claude-0/hft/canva_{v}.png"))
