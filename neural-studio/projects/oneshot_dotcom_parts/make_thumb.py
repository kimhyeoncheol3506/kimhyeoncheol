"""닷컴버블 썸네일 2종 — 채널 규칙(docs/채널규칙_제목썸네일첫15초.md · _series_oneshot/BRIEF_v2.md 5번): 대비 구조 하나 + 큰 숫자 하나 + 글자 6자 이하, 밝은 바탕.
배경색은 기존 편(흰·파랑·노랑·민트/하늘)과 겹치지 않게: A = 연보라(라벤더), B = 연주황.
A = 전/후(숫자 두 개): 나스닥 꼭대기→바닥 −78% vs 본전까지 15년. 글자 '폭락·본전까지'(6자). 본편 첫 판·둘째 판과 같은 숫자. (head.yaml c_ixic)
B = 전/후: 코스닥 2000년 3월 2,834 → 12월 −81%. 글자 '코스닥'(3자, 숫자·단위 제외). 본편 셋째 판과 같은 숫자. (head.yaml dealsite_kosdaq · c_kosdaq)
숫자는 모두 본편 sources.facts 에 있는 것. 실존 인물 얼굴 없음, 채널 배지·몰아보기 칩 없음, 개미는 작게(충격), 오른쪽 아래(재생시간 자리) 비움.
렌더 방식은 사우디 편과 같음(make_thumb_v2.render, ROOT=/home/user/hf/thumb). 어두운 가장자리 그림자는 밝은 바탕에 맞지 않아 끈다.
렌더: python3 projects/oneshot_dotcom_parts/make_thumb.py → assets/thumbs/oneshot_dotcom_thumb_A.png · _B.png"""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
M.ROOT = "/home/user/hf/thumb"

LAV = "#E4DAFB"     # 라벤더 바탕
PUR = "#2B1660"     # 짙은 보라 글씨
ORA = "#FFCF9A"     # 연주황 바탕
RED = "#E8202A"
INK = "#111111"
YEL = "#FFD60A"
NOVIG = '<style>.clip[data-track-index="1"]{box-shadow:none!important}</style>'


def K(html, x, y, size, color=INK, w=None, extra=""):
    width = f"width:{w}px;text-align:center;" if w else ""
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;{width}font-family:BH;font-size:{size}px;line-height:1;white-space:nowrap;'
            f'letter-spacing:-3px;color:{color};{extra}">{html}</div>')


def mascot(name, left, top, w):
    return (f'<img class="abs" src="assets/mascot/{name}.png" style="left:{left}px;top:{top}px;width:{w}px;height:{int(w*1.25)}px;'
            'object-fit:contain;filter:drop-shadow(0 14px 18px rgba(0,0,0,.25))">')


def crash_line(x, y, w, h, color):
    """꼭대기까지 오르다 꺾여 떨어지는 주가 선(단순 도형)"""
    return (f'<svg class="abs" style="left:{x}px;top:{y}px" width="{w}" height="{h}" viewBox="0 0 600 300">'
            f'<polyline points="0,270 90,230 160,200 230,140 290,40 330,90 380,170 440,230 520,265 600,250" fill="none" stroke="{color}" stroke-width="16" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="290" cy="40" r="18" fill="{color}"/></svg>')


def design(v):
    if v == "A":  # 전/후: 폭락 −78% → 본전까지 15년
        bg = LAV
        dots = '<div class="abs" style="inset:0;background:radial-gradient(rgba(43,22,96,.10) 3px,transparent 3px) 0 0/44px 44px"></div>'
        body = (NOVIG + dots +
                                # 왼쪽 카드: 폭락 −78%
                f'<div class="abs" style="left:70px;top:250px;width:760px;height:560px;background:#fff;border:12px solid {PUR};border-radius:40px;box-shadow:16px 16px 0 {PUR}"></div>' +
                K('폭락', 70, 300, 150, color=PUR, w=760) +
                K(f'<span style="color:{RED}">-78</span><span style="font-size:150px;color:{RED}">%</span>', 70, 480, 270, w=760) +
                # 가운데 화살표
                f'<svg class="abs" style="left:850px;top:430px" width="200" height="220" viewBox="0 0 200 220">'
                f'<path d="M0 70 L110 70 L110 10 L200 110 L110 210 L110 150 L0 150 Z" fill="{PUR}"/></svg>' +
                # 오른쪽 카드: 본전까지 15년 (가장 큰 숫자)
                f'<div class="abs" style="left:1070px;top:90px;width:790px;height:760px;background:{PUR};border-radius:44px;box-shadow:16px 16px 0 rgba(43,22,96,.35)"></div>' +
                K('본전까지', 1070, 150, 150, color="#fff", w=790) +
                K(f'<span style="color:{YEL}">15</span><span style="font-size:190px;color:#fff">년</span>', 1070, 340, 420, w=790) +
                mascot("충격", 90, 835, 180))
    else:  # 전/후: 코스닥 2,834 → −81%
        bg = ORA
        stripes = '<div class="abs" style="inset:0;background:repeating-linear-gradient(-45deg,rgba(255,255,255,0) 0 60px,rgba(255,255,255,.22) 60px 120px)"></div>'
        body = (NOVIG + stripes +
                K('코스닥', 80, 60, 230) +
                # 전: 2000년 3월 2,834
                f'<div class="abs" style="left:80px;top:360px;width:720px;height:440px;background:#fff;border:12px solid {INK};border-radius:36px;box-shadow:14px 14px 0 {INK}"></div>' +
                K('2000년 3월', 80, 400, 100, color="#666", w=720) +
                K('2,834', 80, 550, 210, w=720) +
                # 화살표(아래로 꺾임)
                '<svg class="abs" style="left:835px;top:420px" width="220" height="260" viewBox="-20 -20 240 260">'
                f'<path d="M0 70 L110 70 L110 10 L200 110 L110 210 L110 150 L0 150 Z" fill="{INK}" transform="rotate(22 100 110)"/></svg>' +
                # 후: 9개월 뒤 −81% (가장 큰 숫자)
                f'<div class="abs" style="left:1080px;top:150px;width:780px;height:680px;background:{RED};border-radius:44px;box-shadow:14px 14px 0 {INK}"></div>' +
                K('9개월 뒤', 1080, 200, 130, color="#fff", w=780, extra="opacity:.95") +
                K('-81<span style="font-size:190px">%</span>', 1080, 380, 360, color="#fff", w=780) +
                mascot("충격", 860, 40, 190))
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        print(M.render(v, f"{out}/oneshot_dotcom_thumb_{v}.png"))
