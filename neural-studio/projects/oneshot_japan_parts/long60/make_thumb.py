"""(이거 한편으로 끝) 일본 30년 썸네일 2종 — 유대인 편 make_thumb.py 와 같은 방식(make_thumb_v2.render 재사용, 1280x720).
A: 1984년 도쿄 사진(위키미디어 CC BY 2.0, David Wipf) + 큰 질문 + 왼쪽 위 빨간 칩 '1시간 몰아보기'
B: 긴자 사진(위키미디어 CC BY-SA 4.0, Basile Morin) + 통념 문구(노랑) + '진짜일까?'(흰색) + 흰 띠 팩트체크 한 줄
실존 인물 얼굴 없음. 오른쪽 아래(재생시간 자리)는 비운다.
렌더: python3 projects/oneshot_japan_parts/make_thumb.py → assets/thumbs/oneshot_japan_thumb_A.png · _B.png"""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
M.ROOT = "/home/user/hf/thumb"
T = M.T


def design(v):
    if v == "A":  # 1984년 도쿄 + "일본은 왜 30년 동안 월급이 안 올랐을까?"
        bg = "#0b0d12"
        body = ('<img class="abs" src="assets/oneshot_japan/02_minato_tokyo_1984.jpg" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:grayscale(.25) contrast(1.1) brightness(.55)">'
                '<div class="abs" style="inset:0;background:linear-gradient(180deg,rgba(0,0,0,.2) 0%,rgba(0,0,0,.35) 40%,rgba(0,0,0,.92) 100%)"></div>' +
                T('일본 잃어버린 30년', 0, 360, 96, align="c") +
                T('일본은 왜 <b style="color:#FFE14D">30년</b> 동안', 0, 500, 170, align="c") +
                T('<b style="color:#FF3B30">월급</b>이 안 올랐을까?', 0, 700, 170, align="c") +
                '<div class="abs" style="left:64px;top:52px;padding:10px 28px 14px;border-radius:12px;background:#FF3B30;color:#fff;font-family:BH;font-size:58px">1시간 몰아보기</div>')
    else:  # 긴자 야경 + '한국이 제2의 일본?' 진짜일까?
        bg = "#0b0a09"
        body = ('<img class="abs" src="assets/oneshot_japan/03_ginza_fujiya.jpg" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:saturate(.8) contrast(1.1) brightness(.5)">'
                '<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.93) 0%,rgba(0,0,0,.65) 55%,rgba(0,0,0,.25) 100%)"></div>' +
                T('<b style="color:#FFE14D">‘한국이 제2의 일본?’</b>', 70, 230, 150) +
                T('진짜일까?', 70, 450, 250) +
                '<div class="abs" style="left:80px;top:850px;padding:12px 34px 16px;border-radius:14px;background:#fff;color:#111;font-family:BH;font-size:60px">출산율 · 빚 · 월급 · 금리, 숫자로 팩트체크</div>')
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        print(M.render(v, f"{out}/oneshot_japan_thumb_{v}.png"))
