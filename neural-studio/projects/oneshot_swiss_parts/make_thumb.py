"""스위스 부자 이유 썸네일 2종 — 2026-11-13 채널 규칙 v2(대비 구조 · 큰 숫자 하나 + 글자 6자 이하 · 밝은 파랑 배경 · 배지/칩 없음).
A = 숫자 두 개 대비: 금융 9%(GDP) vs 제약 52.7%(수출, BAZG '화학·제약') — '약'만 쓰면 '약(約)'으로 읽혀 '제약'        ← 본편 첫 문장·첫 10초 화면과 같은 숫자
B = A vs B 대비: 1인당 GDP 스위스 vs 한국 막대 + 큰 '3배' (작은 개미 '놀람')
숫자는 모두 본편 sources.facts(SIF·SECO 2024 · BAZG 2024 · World Bank 2024). 실존 인물 없음. 오른쪽 아래(재생시간 자리) 비움.
렌더 방식은 그대로: make_thumb_v2.render (ROOT=/home/user/hf/thumb) → 1280x720.
사용: python3 projects/oneshot_swiss_parts/make_thumb.py → assets/thumbs/oneshot_swiss_thumb_A.png · _B.png  (60분판 썸네일 코드는 long60/make_thumb.py)"""
import os, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
T = M.T
Y = "#FFE14D"
BG = "linear-gradient(155deg,#4A97FF 0%,#2A73EE 55%,#1B5FD8 100%)"   # 스위스 편 = 파랑
LIGHT = ('<div class="abs" style="left:-200px;top:-300px;width:1400px;height:1100px;border-radius:50%;'
         'background:radial-gradient(circle,rgba(255,255,255,.28),rgba(255,255,255,0) 65%)"></div>')


def pill(text, x, y, size=54, bg="#0E2F6B", fg="#fff"):
    return (f'<div class="abs" style="left:{x}px;top:{y}px;padding:6px 26px 10px;border-radius:999px;background:{bg};color:{fg};'
            f'font-family:PB;font-size:{size}px;letter-spacing:-1px">{text}</div>')


def capsule(x, y, w=230, rot=-28):
    h = w * .42
    return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:{h}px;overflow:hidden;transform:rotate({rot}deg);'
            f'box-shadow:0 0 0 8px #111,0 18px 0 rgba(0,0,0,.35)"><div style="position:absolute;left:0;top:0;width:50%;height:100%;background:#FF4A4A"></div>'
            f'<div style="position:absolute;right:0;top:0;width:50%;height:100%;background:#fff"></div></div>')


def design(v):
    if v == "A":  # 금융 9% vs 약 52.7%
        body = (LIGHT +
                # 왼쪽: 금융 9% (작게, 회색빛 카드)
                '<div class="abs" style="left:70px;top:170px;width:640px;height:700px;border-radius:40px;background:rgba(9,32,80,.35)"></div>' +
                pill("GDP", 110, 210) +
                T('금융', 0, 330, 190, extra="left:70px;right:auto;width:640px;text-align:center") +
                T('9%', 0, 560, 260, extra="left:70px;right:auto;width:640px;text-align:center") +
                # 가운데 vs
                '<div class="abs" style="left:700px;top:440px;width:150px;height:150px;border-radius:50%;background:#111;color:#fff;'
                'font-family:BH;font-size:84px;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 0 rgba(0,0,0,.35)">vs</div>' +
                # 오른쪽: 약 52.7% (아주 크게, 노랑)
                pill("수출", 900, 150, bg="#111") +
                capsule(1480, 150) +
                T(f'<b style="color:{Y}">제약</b>', 880, 250, 230) +
                T(f'<b style="color:{Y}">52.7%</b>', 860, 500, 330))
    else:  # 스위스 vs 한국 3배
        base = 900
        def bar(x, h, color, label, flag=False):
            cross = ('<div style="position:absolute;left:50%;top:70px;width:150px;height:150px;transform:translateX(-50%)">'
                     '<div style="position:absolute;left:52px;top:0;width:46px;height:150px;background:#fff"></div>'
                     '<div style="position:absolute;left:0;top:52px;width:150px;height:46px;background:#fff"></div></div>') if flag else ""
            return (f'<div class="abs" style="left:{x}px;top:{base-h}px;width:300px;height:{h}px;background:{color};border-radius:18px 18px 0 0;'
                    f'box-shadow:0 0 0 8px #111">{cross}</div>' + T(label, x - 60, base + 20, 96, extra="width:420px;text-align:center"))
        body = (LIGHT +
                '<div class="abs" style="left:40px;top:897px;width:1100px;height:10px;background:#111"></div>' +
                bar(110, 720, "#E8202A", "스위스", flag=True) +
                bar(560, 240, "#F4F4F4", "한국") +
                '<div class="abs" style="left:610px;top:590px;width:200px;height:50px"></div>' +
                T(f'<b style="color:{Y}">3배</b>', 960, 170, 470) +
                pill("1인당 GDP", 1030, 700, size=64, bg="#111") +
                '<div class="abs" style="left:840px;top:640px;width:190px;height:240px">'
                '<img src="assets/mascot/놀람.png" style="width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))"></div>')
    return BG, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        print(M.render(v, f"{out}/oneshot_swiss_thumb_{v}.png"))
