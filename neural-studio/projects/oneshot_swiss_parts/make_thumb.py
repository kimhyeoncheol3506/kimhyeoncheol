"""(이거 한편으로 끝) 스위스 편 썸네일 2종 (유대인 편 make_thumb.py 와 같은 방식 · 1280x720).
A = 알프스 골짜기 사진 + 큰 질문 + 왼쪽 위 빨간 칩 "1시간 몰아보기"
B = 통념 문구(노랑) + "진짜일까?"(흰색 아주 크게) + 아래 흰 띠 팩트체크 한 줄
사진은 위키미디어 공용(projects/media/oneshot_swiss, manifest.yaml 출처)을 /home/user/hf/thumb/assets/oneshot_swiss/ 로 복사해 쓴다.
실존 인물 얼굴 없음. 오른쪽 아래(재생시간 자리)는 비운다.
렌더: python3 projects/oneshot_swiss_parts/make_thumb.py → assets/thumbs/oneshot_swiss_thumb_A.png · _B.png"""
import os, shutil, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M
T = M.T
HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(os.path.dirname(HERE), "media", "oneshot_swiss")
DST = os.path.join(M.ROOT, "assets", "oneshot_swiss")
PHOTO_A = "alps_valley.jpg"
PHOTO_B = "paradeplatz.jpg"


def copy_photos():
    os.makedirs(DST, exist_ok=True)
    for f in (PHOTO_A, PHOTO_B):
        src = os.path.join(MEDIA, f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(DST, f))


def design(v):
    if v == "A":  # 알프스 골짜기 + "산밖에 없는 나라가 왜 세계 최고 부자가 됐나?"
        bg = "#0b0f14"
        body = (f'<img class="abs" src="assets/oneshot_swiss/{PHOTO_A}" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:contrast(1.08) brightness(.62) saturate(.9)">'
                '<div class="abs" style="inset:0;background:linear-gradient(180deg,rgba(0,0,0,.1) 0%,rgba(0,0,0,.35) 40%,rgba(0,0,0,.92) 100%)"></div>' +
                T('땅의 절반이 해발 1,080m', 0, 420, 92, align="c") +
                T('<b style="color:#FFE14D">산</b>밖에 없는 나라가', 0, 540, 170, align="c") +
                T('왜 <b style="color:#FF3B30">최고 부자</b>가 됐나?', 0, 730, 190, align="c") +
                '<div class="abs" style="left:64px;top:52px;padding:10px 28px 14px;border-radius:12px;background:#FF3B30;color:#fff;font-family:BH;font-size:58px">1시간 몰아보기</div>')
    else:  # 통념 팩트체크
        bg = "#0b0b0d"
        body = (f'<img class="abs" src="assets/oneshot_swiss/{PHOTO_B}" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:grayscale(.5) contrast(1.1) brightness(.42)">'
                '<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.93) 0%,rgba(0,0,0,.7) 55%,rgba(0,0,0,.35) 100%)"></div>' +
                T('<b style="color:#FFE14D">‘스위스는 비밀 은행으로</b>', 70, 200, 118) +
                T('<b style="color:#FFE14D">부자가 됐다’</b>', 70, 345, 150) +
                T('진짜일까?', 70, 540, 240) +
                '<div class="abs" style="left:80px;top:870px;padding:12px 34px 16px;border-radius:14px;background:#fff;color:#111;font-family:BH;font-size:60px">금융은 GDP의 9% · 수출 절반은 약과 화학</div>')
    return bg, body


M.design = design
if __name__ == "__main__":
    copy_photos()
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in (sys.argv[1:] or ["A", "B"]):
        print(M.render(v, f"{out}/oneshot_swiss_thumb_{v}.png"))
