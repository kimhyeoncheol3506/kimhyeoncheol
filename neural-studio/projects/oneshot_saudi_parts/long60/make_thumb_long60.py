"""(이거 한편으로 끝) 사우디 썸네일 2종 — 유대인 편 make_thumb.py 와 같은 방식.
A = 역사 사진(1938년 담맘 7호정, 퍼블릭 도메인) + 큰 질문 + 왼쪽 위 빨간 칩 '1시간 몰아보기'
B = 통념 문구(노랑) + '진짜일까?'(흰색 아주 크게) + 아래 흰 띠 팩트체크 한 줄. 실존 인물 얼굴 없음, 오른쪽 아래(재생시간 자리) 비움.
사진은 /home/user/hf/thumb/assets/oneshot_saudi/ 로 복사해 쓴다(projects/media/oneshot_saudi, manifest.yaml 출처).
렌더: python3 projects/oneshot_saudi_parts/make_thumb.py → assets/thumbs/oneshot_saudi_thumb_A.png · _B.png"""
import sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
M.ROOT = "/home/user/hf/thumb"
T = M.T


def design(v):
    if v == "A":  # 1938년 담맘 7호정 + "석유 돈은 어디로 갔나?"
        bg = "#120d08"
        body = ('<img class="abs" src="assets/oneshot_saudi/01_dammam7_1938.jpg" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:sepia(.45) contrast(1.1) brightness(.55)">'
                '<div class="abs" style="inset:0;background:linear-gradient(180deg,rgba(0,0,0,.1) 0%,rgba(0,0,0,.35) 40%,rgba(0,0,0,.92) 100%)"></div>' +
                T('1938년, 사막에서 터진 석유', 0, 450, 92, align="c") +
                T('<b style="color:#FFE14D">석유 돈</b>은 어디로 갔고,', 0, 580, 150, align="c") +
                T('<b style="color:#FF3B30">석유가 끝나면?</b>', 0, 770, 170, align="c") +
                '<div class="abs" style="left:64px;top:52px;padding:10px 28px 14px;border-radius:12px;background:#FF3B30;color:#fff;font-family:BH;font-size:58px">1시간 몰아보기</div>')
    else:  # 통념 문구 + 팩트체크
        bg = "#0d0a07"
        body = ('<img class="abs" src="assets/oneshot_saudi/01_dammam7_1938.jpg" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;object-position:30% 50%;transform:scaleX(-1);filter:sepia(.4) contrast(1.15) brightness(.5)">'
                '<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.93) 0%,rgba(0,0,0,.65) 55%,rgba(0,0,0,.25) 100%)"></div>' +
                T('<b style="color:#FFE14D">‘석유만 있으면</b>', 70, 210, 130) +
                T('<b style="color:#FFE14D">평생 부자’</b>', 70, 370, 160) +
                T('진짜일까?', 70, 570, 240) +
                '<div class="abs" style="left:80px;top:880px;padding:12px 34px 16px;border-radius:14px;background:#fff;color:#111;font-family:BH;font-size:58px">정부 수입 60%가 석유 · 1938~2026 팩트체크</div>')
    return bg, body


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        print(M.render(v, f"{out}/oneshot_saudi_thumb_{v}.png"))
