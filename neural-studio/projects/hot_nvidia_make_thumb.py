"""hot_nvidia 어두운 에디토리얼 썸네일 A (2026-11-18, projects/_series_hot/BRIEF.md).
먹색 바탕 + 큰 숫자 하나 '+4,274억'(국내 개인 엔비디아 순매수, 세계일보 11/16 — 본편 첫 판과 같은 숫자).
글자: '서학개미 샀다'(6자) — 숫자·단위 제외 6자 이하. 빨간 붓 밑줄·채널 배지·실존 인물 얼굴 없음. 개미 작게(놀람), 오른쪽 아래 비움.
렌더: python3 projects/hot_nvidia_make_thumb.py → assets/thumbs/hot_nvidia_thumb_A.png (1280×720)"""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
M.ROOT = "/home/user/hf/thumb"

INK = "#141210"
MINT = "#3DDC97"
WHITE = "#F4F1EA"
GREY = "#8C857B"


def T(html, x, y, size, color=WHITE, extra=""):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;font-family:BH;font-size:{size}px;line-height:1;white-space:nowrap;'
            f'letter-spacing:-3px;color:{color};{extra}">{html}</div>')


def design(v):
    glow = ('<div class="abs" style="left:250px;top:300px;width:1500px;height:620px;'
            'background:radial-gradient(closest-side,rgba(61,220,151,.20),rgba(61,220,151,0));"></div>')
    # 내려가는 주가 선(배경, 흐리게)
    line = ('<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">'
            '<polyline points="0,250 300,300 520,280 760,420 980,470 1200,620 1450,700 1920,760" fill="none" '
            'stroke="rgba(255,255,255,.10)" stroke-width="16" stroke-linejoin="round"/></svg>')
    body = (line + glow +
            T(f'서학개미 <span style="color:{MINT}">샀다</span>', 110, 90, 200) +
            T(f'<span style="color:{MINT}">+4,274</span><span style="font-size:300px">억</span>', 110, 360, 470,
              extra="text-shadow:0 18px 40px rgba(0,0,0,.6)") +
            f'<img class="abs" src="assets/mascot/놀람.png" style="left:1500px;top:60px;width:240px;height:300px;object-fit:contain;'
            'filter:drop-shadow(0 12px 16px rgba(0,0,0,.45))">')
    return INK, body


M.design = design
if __name__ == "__main__":
    print(M.render("A", "/home/user/kimhyeoncheol/neural-studio/assets/thumbs/hot_nvidia_thumb_A.png"))
