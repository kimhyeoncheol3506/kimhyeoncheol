"""hot_jibun 어두운 에디토리얼 썸네일 A (2026-11-18, projects/_series_hot/BRIEF.md).
짙은 남색 바탕 + 큰 숫자 하나(20년 총액 7.8억, 채널 계산 — calc_jibun.py) + 위 작은 대비 '처음 25%'.
글자: '처음' '총액'(+단위 '20년') — 6자 이하. 빨간 붓 밑줄·채널 배지·실존 인물 없음. 개미 작게(충격), 오른쪽 아래 비움.
렌더: python3 projects/hot_jibun_make_thumb.py → assets/thumbs/hot_jibun_thumb_A.png (1280×720)"""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
M.ROOT = "/home/user/hf/thumb"

NAVY = "#0E1A33"
YEL = "#FFD23F"
RED = "#FF4B4B"
WHITE = "#F4F1EA"


def T(html, x, y, size, color=WHITE, extra=""):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;font-family:BH;font-size:{size}px;line-height:1;white-space:nowrap;'
            f'letter-spacing:-3px;color:{color};{extra}">{html}</div>')


def design(v):
    glow = ('<div class="abs" style="left:420px;top:240px;width:1300px;height:700px;'
            'background:radial-gradient(closest-side,rgba(255,75,75,.22),rgba(255,75,75,0));"></div>')
    grid = ('<div class="abs" style="inset:0;background:repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 90px),'
            'repeating-linear-gradient(90deg,rgba(255,255,255,.035) 0 2px,transparent 2px 90px)"></div>')
    body = (grid + glow +
            # 위: 처음 25%
            T(f'처음 <span style="color:{YEL}">25%</span>', 110, 90, 190) +
            # 아래 화살표(작게)
            '<svg class="abs" style="left:200px;top:330px" width="140" height="170" viewBox="0 0 140 170">'
            f'<path d="M45 0 H95 V105 H135 L70 170 L5 105 H45 Z" fill="{YEL}" opacity=".9"/></svg>' +
            # 큰 숫자
            T('20년 총액', 110, 520, 120, color="#C9CFDD") +
            T(f'<span style="color:{RED}">7.8</span><span style="font-size:300px">억</span>', 640, 330, 520,
              extra="text-shadow:0 18px 40px rgba(0,0,0,.55)") +
            f'<img class="abs" src="assets/mascot/충격.png" style="left:110px;top:720px;width:230px;height:300px;object-fit:contain;'
            'filter:drop-shadow(0 12px 16px rgba(0,0,0,.45))">')
    return NAVY, body


M.design = design
if __name__ == "__main__":
    print(M.render("A", "/home/user/kimhyeoncheol/neural-studio/assets/thumbs/hot_jibun_thumb_A.png"))
