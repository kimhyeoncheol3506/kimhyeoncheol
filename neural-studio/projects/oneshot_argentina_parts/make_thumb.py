"""아르헨티나 경제 몰락 썸네일 2종 — 채널 새 규칙(docs/채널규칙_제목썸네일첫15초.md, 2026-11-13) 적용판.
대비 구조 하나 · 큰 숫자 하나 + 글자 6자 이하(숫자·단위 제외) · 밝은 배경(이 편은 민트/하늘) · 채널 배지·몰아보기 칩 없음 ·
개미 마스코트는 작게 · 실존 인물 얼굴 없음 · 오른쪽 아래(재생시간 자리) 비움. 숫자는 본편 sources.facts 에 있는 것만.
A (민트): 전/후 순위 — 1896년 6위 → 2022년 64위 (매디슨 프로젝트 2023 추정, 자료 있는 40개국 / 165개국 중). 글자: '아르헨티나'(5자)
B (하늘): 전/후 가격표 — 100원 → 5,000원 (1989년 소비자물가 +4,923%, 전년 12월 대비를 원화로 바꾼 예시). 글자: '물가', '만에'(4자)
렌더: video-studio/projects/20261106-econ2h/make_thumb_v2.render 그대로(ROOT=/home/user/hf/thumb) → 1280x720 PNG.
60분판 썸네일 코드는 long60/make_thumb.py 에 보존."""
import os
import sys

sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M

NAVY = "#0E2340"
RED = "#E5322D"
# render() 가 덧씌우는 어두운 가장자리(비네팅)는 밝은 배경에서 지저분해 보여 끈다(렌더 방식은 그대로, 이 디자인에서만)
NOVIG = '<style>.clip[data-track-index="1"]{box-shadow:none!important}</style>'


def txt(html, x, y, size, color=NAVY, extra=""):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;font-family:BH;font-size:{size}px;line-height:1;white-space:nowrap;'
            f'letter-spacing:-3px;color:{color};{extra}">{html}</div>')


def note(text, x=70, y=1010):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;font-family:PB;font-size:28px;color:{NAVY};opacity:.62;'
            f'letter-spacing:-.5px">{text}</div>')


def ant(name, left, top, w):
    return (f'<img class="abs" src="assets/mascot/{name}.png" style="left:{left}px;top:{top}px;width:{w}px;height:{int(w * 1.25)}px;'
            'object-fit:contain;filter:drop-shadow(0 14px 18px rgba(14,35,64,.25))">')


def arrow(x, y, w=230, color=NAVY):
    return (f'<svg class="abs" style="left:{x}px;top:{y}px" width="{w}" height="120" viewBox="0 0 {w} 120">'
            f'<path d="M6 60 H{w - 60}" stroke="{color}" stroke-width="26" stroke-linecap="round"/>'
            f'<path d="M{w - 92} 14 L{w - 12} 60 L{w - 92} 106" fill="none" stroke="{color}" stroke-width="26" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def card(inner, x, y, w, h, bg="#fff", rot=0, border=NAVY):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{bg};border:8px solid {border};border-radius:36px;'
            f'transform:rotate({rot}deg);box-shadow:0 18px 0 rgba(14,35,64,.18);display:flex;flex-direction:column;align-items:center;justify-content:center">{inner}</div>')


def design(v):
    if v == "A":  # 민트 · 순위 전/후
        bg = "linear-gradient(160deg,#C9F5E4 0%,#A9EDD3 100%)"
        before = card(f'<div style="font-family:PB;font-size:54px;color:{NAVY};opacity:.75">1896년</div>'
                      f'<div style="font-family:BH;font-size:250px;line-height:1;color:{NAVY};letter-spacing:-6px">6<span style="font-size:130px">위</span></div>',
                      70, 330, 470, 500, rot=-3)
        after = (f'<div class="abs" style="left:820px;top:250px;font-family:PB;font-size:64px;color:{RED}">2022년</div>' +
                 txt(f'64<span style="font-size:250px">위</span>', 800, 300, 560, RED, "letter-spacing:-18px;text-shadow:0 16px 0 rgba(14,35,64,.16)"))
        body = (NOVIG +
                txt("아르헨티나", 70, 70, 190) +
                before + arrow(565, 520) + after +
                ant("충격", 1520, 60, 260) +
                note("1인당 소득 순위 · 매디슨 프로젝트 2023 추정 (1896년 40개국 중, 2022년 165개국 중)"))
    else:  # 하늘 · 가격표 전/후
        bg = "linear-gradient(160deg,#CFEBFF 0%,#A8D8FA 100%)"

        def tag(price, x, y, w, h, size, color, rot, unit):
            hole = f'<div style="position:absolute;left:34px;top:50%;width:44px;height:44px;margin-top:-22px;border-radius:50%;background:#BFE2FC;border:7px solid {NAVY}"></div>'
            return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#fff;border:9px solid {NAVY};'
                    f'border-radius:40px 120px 120px 40px;transform:rotate({rot}deg);box-shadow:0 20px 0 rgba(14,35,64,.18);'
                    f'display:flex;align-items:center;justify-content:center;padding-left:70px;white-space:nowrap">{hole}'
                    f'<span style="font-family:BH;font-size:{size}px;line-height:1;color:{color};letter-spacing:-6px">{price}<span style="font-size:{unit}px">원</span></span></div>')
        body = (NOVIG +
                txt(f'물가 <span style="color:{RED}">1년</span> 만에', 70, 70, 190) +
                tag("100", 60, 440, 460, 220, 150, NAVY, -4, 90) +
                arrow(545, 485, 200) +
                tag("5,000", 760, 330, 1080, 430, 330, RED, 3, 170) +
                ant("놀람", 1560, 40, 250) +
                note("1989년 아르헨티나 소비자물가 +4,923% (1989년 12월, 전년 12월 대비)를 원화로 바꿔 본 예시 · 아르헨티나 중앙은행 1989년 보고서"))
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in sys.argv[1:] or ["A", "B"]:
        print(M.render(v, f"{out}/oneshot_argentina_thumb_{v}.png"))
