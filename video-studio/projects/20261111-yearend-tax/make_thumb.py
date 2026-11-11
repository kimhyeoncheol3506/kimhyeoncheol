"""34편 연말정산 썸네일 후보 3개 (현철님 참고 썸네일 6장: 초록 배너 '연말정산' 큰 글씨, 흰·노랑 글자 검정 외곽, 큰 금액, 13월의 월급 vs 세금 폭탄 대비).
실존 인물 얼굴 대신 개미 마스코트 + 원천징수영수증·카드 실물 소품. 렌더는 33편 make_thumb_v2.render 재사용(/home/user/hf/thumb)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "20261106-econ2h"))
import make_thumb_v2 as M  # noqa: E402

T = M.T
STK = "drop-shadow(7px 0 0 #fff) drop-shadow(-7px 0 0 #fff) drop-shadow(0 7px 0 #fff) drop-shadow(0 -7px 0 #fff) drop-shadow(0 18px 24px rgba(0,0,0,.3))"


def ant(name, right, bottom, w, rot=0, flip=False):
    tf = f"rotate({rot}deg)" + (" scaleX(-1)" if flip else "")
    return (f'<div class="abs" style="right:{right}px;bottom:{bottom}px;width:{w}px;height:{int(w * 1.25)}px;transform:{tf}">'
            f'<img src="assets/mascot/{name}.png" style="width:100%;height:100%;object-fit:contain;filter:{STK}"></div>')


def receipt(x, y, w, rot, line, amount, col):
    """근로소득 원천징수영수증 모양 종이 (실물 증거 소품)"""
    rows = "".join(f'<div style="height:16px;margin:16px 0;border-radius:8px;background:#D9D4C7;width:{p}%"></div>' for p in (90, 70, 84, 60))
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;padding:34px 38px 40px;background:#FFFEF8;border-radius:10px;transform:rotate({rot}deg);'
            f'box-shadow:0 22px 40px rgba(0,0,0,.35);font-family:PB">'
            f'<div style="font-size:34px;color:#333;border-bottom:4px solid #333;padding-bottom:12px">근로소득 원천징수영수증</div>{rows}'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-top:18px;font-size:36px;color:#333">{line}'
            f'<span style="font-family:BH;font-size:70px;color:{col}">{amount}</span></div></div>')


def design(v):
    if v == "A":  # 참고 1: 크림 바탕 + 초록 배너 '연말정산' + 순서 아이콘
        bg = "#F7F4EA"
        icons = "".join(
            f'<div style="width:150px;height:150px;border-radius:30px;border:9px solid #3E6B2E;background:#fff;color:#3E6B2E;font-family:BH;font-size:{fs}px;display:flex;align-items:center;justify-content:center">{t}</div>'
            + ('<div style="font-family:BH;font-size:80px;color:#7FA36A;align-self:center">›</div>' if k < 2 else "")
            for k, (t, fs) in enumerate([("소득", 50), ("공제", 50), ("환급", 50)]))
        body = ('<div class="abs" style="left:70px;top:60px;padding:10px 34px 14px;background:#3E6B2E;color:#fff;font-family:BH;font-size:76px;border-radius:8px">2026년 귀속</div>'
                '<div class="abs" style="left:610px;top:66px;font-family:BH;font-size:76px;color:#3E6B2E">미리 준비</div>'
                '<div class="abs" style="left:70px;top:200px;width:1780px;height:430px;background:#3E6B2E"></div>'
                '<div class="abs" style="left:0;right:0;top:205px;text-align:center;font-family:BH;font-size:400px;line-height:1.05;color:#fff;letter-spacing:-6px">연말정산</div>'
                '<div class="abs" style="left:640px;top:780px;width:540px;height:60px;background:#CFE3BF"></div>'
                '<div class="abs" style="left:620px;top:672px;font-family:BH;font-size:180px;line-height:1;color:#1F1F1F;letter-spacing:-4px">이 순서로 하세요</div>'
                f'<div class="abs" style="left:900px;top:880px;display:flex;gap:22px">{icons}</div>'
                + ant("가리킴", 1420, -40, 520, -3, True))
    elif v == "B":  # 참고 3·5: 어두운 바탕 + 노랑 큰 금액 + 빨강 둘째 줄 + 영수증 증거
        bg = "radial-gradient(circle at 70% 30%,#3A2A1A 0%,#120D09 70%)"
        body = ('<div class="abs" style="inset:0;background:repeating-linear-gradient(135deg,rgba(255,255,255,.03) 0 18px,transparent 18px 36px)"></div>'
                + receipt(1080, 70, 760, 5, "추가 납부", "117만 원", "#E02A2A")
                + '<div class="abs" style="left:1180px;top:520px;padding:10px 26px;border:8px solid #E02A2A;color:#E02A2A;font-family:BH;font-size:64px;transform:rotate(-12deg);background:rgba(255,255,255,.85)">역대 최대</div>'
                + T('<span style="color:#FFE14D">377만 명</span>이 더 냈다', 70, 90, 120)
                + T('연말정산', 60, 330, 300)
                + T('<span style="color:#FF3B3B">세금 폭탄</span> 피하는', 64, 640, 175)
                + T('<span style="color:#FFE14D">순서</span> 있습니다', 64, 840, 175)
                + ant("충격", 40, -30, 470, 4))
    else:  # 참고 4: 13월의 월급 vs 세금 폭탄 반반
        bg = "linear-gradient(90deg,#9FD3F2 0 50%,#8A8F99 50% 100%)"
        rays = "".join(f'<line x1="480" y1="560" x2="{480 + 600 * __import__("math").cos(a / 9 * 3.1416)}" y2="{560 - 600 * __import__("math").sin(a / 9 * 3.1416)}" stroke="#FFE36E" stroke-width="14" stroke-linecap="round"/>' for a in range(0, 10))
        drops = "".join(f'<line x1="{1060 + (k * 97) % 800}" y1="{300 + (k * 53) % 300}" x2="{1052 + (k * 97) % 800}" y2="{340 + (k * 53) % 300}" stroke="#D8E4F2" stroke-width="8" stroke-linecap="round"/>' for k in range(30))
        body = (f'<svg class="abs" style="left:0;top:0" width="1920" height="1080">{rays}<circle cx="480" cy="560" r="150" fill="#FFF3A8"/>'
                '<ellipse cx="1440" cy="230" rx="330" ry="120" fill="#5D626B"/><ellipse cx="1300" cy="200" rx="170" ry="110" fill="#5D626B"/><ellipse cx="1580" cy="190" rx="190" ry="120" fill="#5D626B"/>'
                f'{drops}</svg>'
                + '<div class="abs" style="left:958px;top:0;width:6px;height:1080px;background:#222"></div>'
                + ant("환호", 1500, 300, 360, -3)
                + ant("충격", 80, 300, 360, 3)
                + T('13월의 월급', 0, 70, 150, extra="width:960px;text-align:center")
                + T('<span style="color:#FF3B3B">세금 폭탄</span>', 960, 70, 150, extra="width:960px;text-align:center")
                + '<div class="abs" style="left:0;right:0;top:690px;height:300px;background:rgba(0,0,0,.72)"></div>'
                + T('연말정산, 딱 <span style="color:#FFE14D">이 순서</span> 차이', 0, 715, 140, align="center")
                + T('2026년 귀속 · 바뀐 것 7가지', 0, 875, 80, align="center"))
    return bg, body


M.design = design
if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thumbs")
    os.makedirs(out, exist_ok=True)
    for v in (sys.argv[1:] or ["A", "B", "C"]):
        print(M.render(v, os.path.join(out, f"thumbnail_{v}.png")))
