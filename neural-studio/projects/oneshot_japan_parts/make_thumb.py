"""일본 잃어버린 30년 썸네일 2종 (2026-11-13 v2, docs/채널규칙_제목썸네일첫15초.md 적용)
렌더는 기존과 같은 방식(make_thumb_v2.render 재사용, ROOT=/home/user/hf/thumb, 1920x1080 → 1280x720). 디자인만 새 규칙으로:
  흰 바탕 + 빨강 포인트(일본 편 색), 대비 구조 하나, 큰 숫자 하나 + 글자 6자 이하, 채널 배지·'몰아보기' 칩 없음,
  개미 마스코트는 작게(표정이 맞을 때만), 실존 인물 얼굴 없음, 오른쪽 아래(재생시간 자리) 비움.
A: 숫자 두 개 — 일본 -1% vs 한국 2배 (35년 실질 평균 연봉, OECD) · 글자: 월급·일본·한국(6자) · 본편 첫 장면 N1·N2 와 일치
B: 전/후 — 1989년 꼭대기 → 본전까지 34년 (닛케이 평균, 배당 제외) · 글자: 주식 본전까지(6자) · 본편 N3 와 일치
렌더: python3 projects/oneshot_japan_parts/make_thumb.py → assets/thumbs/oneshot_japan_thumb_A.png · _B.png"""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
M.ROOT = "/home/user/hf/thumb"

RED, INK, NAVY, GRAY = "#E60012", "#141414", "#1D3557", "#8A8A8A"
# render() 가 덮는 어두운 가장자리 그림자를 흰 바탕에서는 끈다(렌더 방식은 그대로)
NOVIG = '<style>.clip[data-track-index="1"]{box-shadow:none!important}</style>'


def D(html, x, y, size, color=INK, font="BH", extra=""):
    pos = f"left:{x}px;top:{y}px" if x is not None else f"left:0;right:0;top:{y}px;text-align:center"
    return (f'<div class="abs" style="{pos};font-family:{font};font-size:{size}px;line-height:1;white-space:nowrap;'
            f'letter-spacing:-3px;color:{color};{extra}">{html}</div>')


def mascot(name, x, y, h):
    return f'<img class="abs" src="assets/mascot/{name}.png" style="left:{x}px;top:{y}px;height:{h}px">'


def design(v):
    bg = "#FFFFFF"
    if v.endswith("A"):  # 숫자 두 개: 일본 -1% vs 한국 2배
        body = (NOVIG +
                '<div class="abs" style="left:0;top:0;width:1920px;height:26px;background:%s"></div>' % RED +
                D('35년 <span style="color:%s">월급</span>' % RED, None, 70, 150) +
                # 왼쪽: 일본 (옅은 빨간 원 위에 큰 숫자)
                '<div class="abs" style="left:150px;top:300px;width:700px;height:700px;border-radius:50%;background:#FDE4E6"></div>' +
                D('일본', 395, 330, 130) +
                D('-1%', 150, 520, 380, RED, extra="width:700px;text-align:center;letter-spacing:-12px") +
                # 가운데 vs
                D('vs', 900, 610, 110, GRAY, font="PB", extra="letter-spacing:0") +
                # 오른쪽: 한국
                D('한국', 1300, 330, 130) +
                D('2배', 1140, 560, 300, NAVY, extra="width:560px;text-align:center") +
                mascot("놀람", 1660, 300, 230))
    else:  # 전/후: 1989 꼭대기 → 본전까지 34년 (닛케이 평균 마감, 실제 점 4개만 이은 단순 그림)
        # x: 1984→2024 를 130..1010px, y: 지수 0..40000 을 1000..420px
        def px(year, val):
            return 130 + (year - 1984) / 40 * 880, 1000 - val / 40000 * 580
        pts = [(1984, 10000), (1989, 38915), (2008, 6995), (2024, 39098)]
        xy = [px(*p) for p in pts]
        path = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in xy)
        (x89, y89), (x24, y24) = xy[1], xy[3]
        svg = (f'<svg class="abs" style="left:0;top:0" width="1920" height="1080">'
               f'<line x1="{x89:.0f}" y1="{y89:.0f}" x2="{x24:.0f}" y2="{y89:.0f}" stroke="{GRAY}" stroke-width="8" stroke-dasharray="26 18"/>'
               f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="22" stroke-linejoin="round" stroke-linecap="round"/>'
               f'<circle cx="{x89:.0f}" cy="{y89:.0f}" r="30" fill="{RED}"/><circle cx="{x24:.0f}" cy="{y24:.0f}" r="30" fill="{NAVY}"/></svg>')
        body = (NOVIG +
                '<div class="abs" style="left:0;top:0;width:1920px;height:26px;background:%s"></div>' % RED +
                svg +
                D('1989', x89 - 60, y89 - 140, 96, RED, font="PB", extra="letter-spacing:-2px") +
                D('2024', x24 - 120, y24 - 140, 96, NAVY, font="PB", extra="letter-spacing:-2px") +
                D('주식 본전까지', 110, 70, 150) +
                D('34<span style="font-size:250px">년</span>', 1100, 330, 470, RED, extra="letter-spacing:-14px") +
                mascot("충격", 1260, 70, 230))
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        # 출력 임시 폴더 이름이 다른 편 작업과 겹치지 않게 'jp' 를 붙여 렌더한다(render 의 /tmp/claude-0/hft/v2<이름>)
        print(M.render("jp" + v, f"{out}/oneshot_japan_thumb_{v}.png"))
