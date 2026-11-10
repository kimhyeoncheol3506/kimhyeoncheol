"""경제 속 유대인의 역사 썸네일 2종 (레퍼런스: 교양의 시대·역사 채널형 — 어두운 역사 그림 + 아주 굵은 흰/빨강·노랑 글씨).
그림은 위키미디어 공개 그림(projects/media/jewecon, manifest.yaml 출처). 실존 인물 얼굴 클로즈업은 쓰지 않는다.
렌더: video-studio/projects/20261106-econ2h/make_thumb_v2.render 재사용 → 1280x720 PNG"""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
T = M.T


def design(v):
    if v == "A":  # 스페인 추방(1492) 그림 + "돈은 왜 유대인을 따라다녔나"
        bg = "#120d0a"
        body = ('<img class="abs" src="assets/jew/13_sala_expulsion_spain_1492.jpg" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:grayscale(.35) contrast(1.1) brightness(.55)">'
                '<div class="abs" style="inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15) 0%,rgba(0,0,0,.35) 45%,rgba(0,0,0,.92) 100%)"></div>' +
                T('3천 년 경제사로 본', 0, 470, 96, align="c") +
                T('<b style="color:#FF3B30">돈</b>은 왜 <b style="color:#FFE14D">유대인</b>을', 0, 600, 190, align="c") +
                T('따라다녔나?', 0, 800, 190, align="c") +
                '<div class="abs" style="left:64px;top:52px;padding:10px 28px 14px;border-radius:12px;background:#FF3B30;color:#fff;font-family:BH;font-size:58px">1시간 몰아보기</div>')
    else:  # 워털루 그림 + 음모론 팩트체크
        bg = "#0d0b09"
        body = ('<img class="abs" src="assets/jew/24_battle_of_waterloo_sadler.png" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:sepia(.35) contrast(1.15) brightness(.5)">'
                '<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.92) 0%,rgba(0,0,0,.6) 55%,rgba(0,0,0,.2) 100%)"></div>' +
                T('<b style="color:#FFE14D">‘유대인이 세계 경제를</b>', 70, 250, 120) +
                T('<b style="color:#FFE14D">지배한다’</b>', 70, 400, 150) +
                T('진짜일까?', 70, 600, 230) +
                '<div class="abs" style="left:80px;top:880px;padding:12px 34px 16px;border-radius:14px;background:#fff;color:#111;font-family:BH;font-size:62px">고리대금에서 월가까지 · 3천 년 팩트체크</div>')
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        print(M.render(v, f"{out}/jewecon_thumb_{v}.png"))
