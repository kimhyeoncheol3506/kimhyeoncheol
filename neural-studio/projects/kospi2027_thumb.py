"""2027 코스피 전망(모델 2) 캔바 스타일 썸네일 후보 2개 (현철님 2026-11-08 '썸네일도 캔바스타일로').
렌더는 video-studio/projects/20261106-econ2h/make_thumb_v2.render 재사용(HyperFrames 스냅샷 → 1280x720).
실존 인물 얼굴 없음, 개미 마스코트 스티커만. 숫자는 대본 sources 에 있는 값만(국내 하단 5,000~상단 10,500, 해외 7,500~10,000)."""
import os, sys
VS = "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h"
sys.path.insert(0, VS)
import make_thumb_v2 as M

STK = "drop-shadow(6px 0 0 #fff) drop-shadow(-6px 0 0 #fff) drop-shadow(0 6px 0 #fff) drop-shadow(0 -6px 0 #fff) drop-shadow(0 18px 24px rgba(0,0,0,.25))"


def sticker(name, right, bottom, w, rot=0):
    return (f'<div class="abs" style="right:{right}px;bottom:{bottom}px;width:{w}px;height:{int(w*1.25)}px;transform:rotate({rot}deg)">'
            f'<img src="assets/mascot/{name}.png" style="width:100%;height:100%;object-fit:contain;filter:{STK}"></div>')


def design(v):
    if v == "F":  # 크림 바탕 + 큰 검정 제목 + 노랑 형광펜 + 오른쪽 '밴드 카드' 두 장
        bg = "#FFF6E5"
        grid = '<div class="abs" style="inset:0;background-image:linear-gradient(#0000000d 2px,transparent 2px),linear-gradient(90deg,#0000000d 2px,transparent 2px);background-size:60px 60px"></div>'
        card = lambda top, rot, lab, num, col: (f'<div class="abs" style="right:110px;top:{top}px;width:680px;padding:26px 34px 30px;border-radius:30px;background:#fff;border:6px solid #111;'
                                               f'box-shadow:12px 12px 0 #111;transform:rotate({rot}deg)"><div style="font-family:PB;font-size:44px;color:{col}">{lab}</div>'
                                               f'<div style="font-family:BH;font-size:84px;line-height:1.05;white-space:nowrap;color:#111;letter-spacing:-3px">{num}</div></div>')
        body = (grid +
                '<div class="abs" style="left:80px;top:90px;padding:14px 38px 20px;border-radius:999px;background:#111;color:#FFD84D;font-family:BH;font-size:74px">증권사 13곳 총정리</div>' +
                '<div class="abs" style="left:74px;top:250px;font-family:BH;font-size:250px;line-height:1;color:#111;letter-spacing:-8px">2027</div>' +
                '<div class="abs" style="left:74px;top:500px;font-family:BH;font-size:210px;line-height:1;color:#111;letter-spacing:-6px">코스피</div>' +
                '<div class="abs" style="left:64px;top:800px;width:900px;height:120px;background:#FFD84D;border-radius:18px;transform:rotate(-1.5deg)"></div>' +
                '<div class="abs" style="left:92px;top:770px;font-family:BH;font-size:160px;line-height:1;color:#111;letter-spacing:-5px">어디까지?</div>' +
                card(130, 3, "국내 9곳 밴드", "5,000~10,500", "#E8483B") + card(430, -3, "해외 4곳 목표", "7,500~10,000", "#2F6BFF") +
                sticker("놀람", 60, -70, 360, 6))
    else:  # 민트 바탕 + 흰 카드 속 '범위 막대' + 남색 제목 + 빨간 스탬프
        bg = "#7FE0C4"
        bar = ('<div class="abs" style="left:150px;top:690px;width:1060px;height:46px;border-radius:999px;background:#E9EEF5"></div>'
               '<div class="abs" style="left:150px;top:690px;width:1060px;height:46px;border-radius:999px;background:linear-gradient(90deg,#3D7BFF,#FFC23D 55%,#FF5A5F)"></div>'
               '<div class="abs" style="left:150px;top:760px;font-family:BH;font-size:66px;color:#1E2A5A">5,000</div>'
               '<div class="abs" style="left:980px;top:760px;font-family:BH;font-size:66px;color:#1E2A5A">10,500</div>'
               '<div class="abs" style="left:520px;top:770px;font-family:PB;font-size:44px;color:#5B6B8C">증권사 밴드</div>')
        body = ('<div class="abs" style="inset:0;background-image:radial-gradient(#ffffff55 4px,transparent 4px);background-size:44px 44px"></div>' +
                '<div class="abs" style="left:70px;top:80px;width:1240px;height:920px;border-radius:52px;background:#fff;box-shadow:0 22px 0 #1E2A5A"></div>' +
                '<div class="abs" style="left:140px;top:140px;padding:12px 34px 16px;border-radius:16px;background:#1E2A5A;color:#fff;font-family:BH;font-size:70px">국내 9 · 해외 4</div>' +
                '<div class="abs" style="left:130px;top:290px;font-family:BH;font-size:200px;line-height:1;color:#1E2A5A;letter-spacing:-6px">2027 코스피</div>' +
                '<div class="abs" style="left:130px;top:490px;font-family:BH;font-size:150px;line-height:1;color:#FF5A5F;letter-spacing:-5px">어디까지 가나?</div>' + bar +
                '<div class="abs" style="right:80px;top:70px;width:300px;height:300px;border-radius:50%;background:#FF5A5F;color:#fff;font-family:BH;font-size:64px;line-height:1.08;display:flex;align-items:center;justify-content:center;text-align:center;transform:rotate(12deg);box-shadow:0 12px 0 #1E2A5A">리서치<br>센터<br>뷰</div>' +
                sticker("충격", 40, 0, 560, -3))
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["F", "G"]):
        print(M.render(v, f"{out}/kospi2027_canva_{v}.png"))
