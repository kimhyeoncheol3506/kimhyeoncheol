"""사우디 석유 썸네일 2종 — 2026-11-13 채널 새 규칙(docs/채널규칙_제목썸네일첫15초.md): 대비 구조 하나 + 큰 숫자 + 글자 6자 이하, 밝은 노랑 바탕.
A = 숫자 두 개: 적자 안 보는 유가(IMF 추정) 98달러 vs 2024년 실제 브렌트유 80달러. 글자 '필요·실제·적자'(6자). 본편 첫 판·둘째 판과 같은 숫자.
B = 전/후: 브렌트유 연평균 2013년 109달러 → 2016년 45달러. 글자 '유가 반토막'(5자). 본편 셋째 판(약 12초)과 같은 숫자.
숫자는 모두 본편 sources.facts(p4_imf_be · p4_brent) 에 있는 것. 실존 인물 얼굴 없음, 채널 배지·몰아보기 칩 없음, 개미는 작게(A 계산 · B 충격), 오른쪽 아래(재생시간 자리) 비움.
렌더 방식은 그대로(make_thumb_v2.render, ROOT=/home/user/hf/thumb). render 가 덧씌우는 어두운 가장자리 그림자는 밝은 바탕에 맞지 않아 design 안의 style 로 끈다.
렌더: python3 projects/oneshot_saudi_parts/make_thumb.py → assets/thumbs/oneshot_saudi_thumb_A.png · _B.png
60분판 썸네일(어두운 사진 + '진짜일까?')은 long60/make_thumb_long60.py 에 보존."""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
M.ROOT = "/home/user/hf/thumb"

YEL = "#FFD60A"
RED = "#E8202A"
INK = "#111111"
NOVIG = '<style>.clip[data-track-index="1"]{box-shadow:none!important}</style>'


def K(html, x, y, size, color=INK, align="left", extra=""):
    """노랑 바탕용 굵은 검정 글씨(외곽선 없음, 얕은 그림자)"""
    pos = f"left:{x}px;top:{y}px" if align == "left" else f"left:0;right:0;top:{y}px;text-align:center"
    return (f'<div style="position:absolute;{pos};font-family:BH;font-size:{size}px;line-height:1;white-space:nowrap;'
            f'letter-spacing:-3px;color:{color};{extra}">{html}</div>')


def barrel(x, y, s=1.0):
    """기름통 + 기름방울(단순 도형)"""
    return (f'<svg class="abs" style="left:{x}px;top:{y}px" width="{int(220*s)}" height="{int(300*s)}" viewBox="0 0 220 300">'
            '<path d="M110 8 C140 52 168 84 168 116 a58 58 0 0 1 -116 0 C52 84 80 52 110 8z" fill="#111"/>'
            '<rect x="30" y="150" width="160" height="140" rx="16" fill="#111"/>'
            '<rect x="30" y="182" width="160" height="12" fill="' + YEL + '"/><rect x="30" y="246" width="160" height="12" fill="' + YEL + '"/></svg>')


def mascot(name, left, top, w):
    return (f'<img class="abs" src="assets/mascot/{name}.png" style="left:{left}px;top:{top}px;width:{w}px;height:{int(w*1.25)}px;'
            'object-fit:contain;filter:drop-shadow(0 14px 18px rgba(0,0,0,.25))">')


def design(v):
    bg = YEL
    stripes = ('<div class="abs" style="inset:0;background:repeating-linear-gradient(-45deg,rgba(255,255,255,.0) 0 60px,rgba(255,255,255,.18) 60px 120px)"></div>')
    if v == "A":  # 숫자 두 개: 필요 98달러 vs 실제 80달러
        body = (NOVIG + stripes +
                # 왼쪽 카드: 필요
                '<div class="abs" style="left:70px;top:150px;width:900px;height:720px;background:#fff;border:12px solid #111;border-radius:40px;box-shadow:18px 18px 0 #111"></div>' +
                K('필요', 0, 200, 150, align="c", extra="width:1040px;right:auto") +
                K(f'<span style="color:{RED}">98</span><span style="font-size:150px">달러</span>', 0, 400, 380, align="c", extra="width:1040px;right:auto") +
                # 가운데 VS
                '<div class="abs" style="left:900px;top:430px;width:200px;height:200px;border-radius:50%;background:#111;color:' + YEL + ';'
                'font-family:BH;font-size:110px;line-height:200px;text-align:center;letter-spacing:-4px">VS</div>' +
                # 오른쪽 카드: 실제
                '<div class="abs" style="left:1060px;top:230px;width:760px;height:560px;background:#111;border-radius:40px"></div>' +
                K('실제', 1060, 280, 130, color="#fff", extra="width:760px;text-align:center") +
                K('80<span style="font-size:120px">달러</span>', 1060, 450, 280, color="#fff", extra="width:760px;text-align:center") +
                # 적자 도장
                f'<div class="abs" style="left:1350px;top:60px;padding:6px 40px 18px;border:12px solid {RED};border-radius:24px;color:{RED};'
                'font-family:BH;font-size:150px;line-height:1;transform:rotate(-8deg);background:rgba(255,255,255,.85)">적자</div>' +
                barrel(1150, 40, .55) +
                mascot("계산", 60, 790, 230))
    else:  # 전/후: 109달러 → 45달러, 유가 반토막
        body = (NOVIG + stripes +
                K('유가 <span style="color:' + RED + '">반토막</span>', 70, 70, 210) +
                # 전: 2013 109달러
                '<div class="abs" style="left:70px;top:360px;width:720px;height:470px;background:#fff;border:12px solid #111;border-radius:36px;box-shadow:14px 14px 0 #111"></div>' +
                K('2013', 70, 400, 110, extra="width:720px;text-align:center;color:#555") +
                K('109<span style="font-size:110px">달러</span>', 70, 540, 230, extra="width:720px;text-align:center") +
                # 화살표
                '<svg class="abs" style="left:800px;top:430px" width="260" height="300" viewBox="0 0 260 300">'
                '<path d="M10 60 L150 60 L150 0 L250 120 L150 240 L150 180 L10 180 Z" fill="#111" transform="rotate(18 130 120)"/></svg>' +
                # 후: 2016 45달러 (큰 숫자)
                f'<div class="abs" style="left:1060px;top:300px;width:800px;height:600px;background:{RED};border-radius:40px;box-shadow:14px 14px 0 #111"></div>' +
                K('2016', 1060, 330, 110, color="#fff", extra="width:800px;text-align:center;opacity:.9") +
                K('45<span style="font-size:140px">달러</span>', 1060, 470, 360, color="#fff", extra="width:800px;text-align:center") +
                barrel(1610, 30, .7) +
                mascot("충격", 1400, 20, 200))
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        print(M.render(v, f"{out}/oneshot_saudi_thumb_{v}.png"))
