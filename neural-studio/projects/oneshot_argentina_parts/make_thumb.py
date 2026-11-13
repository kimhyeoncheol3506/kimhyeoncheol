"""(이거 한편으로 끝) 아르헨티나 썸네일 2종 — 유대인 편 make_thumb.py 와 같은 방식(어두운 역사 사진 + 아주 굵은 흰/노랑 글씨).
A: 부에노스아이레스 항구 사진(1908~1919, 퍼블릭 도메인) + 큰 질문 + 왼쪽 위 빨간 칩 '1시간 몰아보기'
B: 2001년 12월 20일 부에노스아이레스 사진(CC BY 2.5) + 통념 문구 '돈 찍어내면 다 같이 부자'(노랑) + '진짜일까?'(흰색 아주 크게) + 아래 흰 띠 팩트체크 한 줄
사진은 projects/media/oneshot_argentina(manifest.yaml 출처)에서 /home/user/hf/thumb/assets/oneshot_argentina/ 로 복사해 쓴다. 실존 인물 얼굴 없음.
렌더: video-studio/projects/20261106-econ2h/make_thumb_v2.render 재사용 → 1280x720 PNG. 오른쪽 아래(재생시간 자리)는 비운다."""
import os
import shutil
import sys

sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M

T = M.T
SRC = "/home/user/kimhyeoncheol/neural-studio/projects/media/oneshot_argentina"
DST = os.path.join(M.ROOT, "assets", "oneshot_argentina")
FILES = {"A": "01_docks_buenos_aires.jpg", "B": "20_crisis_20_dec_2001.jpg"}


def design(v):
    if v == "A":  # 1900년대 부에노스아이레스 부두 + "세계 5대 부국은 왜 몰락했나"
        bg = "#0f0c0a"
        body = (f'<img class="abs" src="assets/oneshot_argentina/{FILES["A"]}" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:grayscale(.3) contrast(1.1) brightness(.55)">'
                '<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.9) 0%,rgba(0,0,0,.55) 60%,rgba(0,0,0,.25) 100%)"></div>' +
                T('한때 <b style="color:#FFE14D">세계 5대 부국</b>이라던', 70, 250, 92) +
                T('<b style="color:#FFE14D">아르헨티나</b>는', 70, 390, 190) +
                T('왜 <b style="color:#FF3B30">몰락</b>했나?', 70, 610, 220) +
                '<div class="abs" style="left:64px;top:52px;padding:10px 28px 14px;border-radius:12px;background:#FF3B30;color:#fff;font-family:BH;font-size:58px">1시간 몰아보기</div>')
    else:  # 2001년 12월 위기 사진 + 통념 팩트체크
        bg = "#0d0b09"
        body = (f'<img class="abs" src="assets/oneshot_argentina/{FILES["B"]}" style="left:0;top:0;width:1920px;height:1080px;object-fit:cover;filter:sepia(.3) contrast(1.1) brightness(.42)">'
                '<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.92) 0%,rgba(0,0,0,.65) 60%,rgba(0,0,0,.3) 100%)"></div>' +
                T('<b style="color:#FFE14D">‘돈 찍어내면</b>', 70, 170, 150) +
                T('<b style="color:#FFE14D">다 같이 부자’</b>', 70, 345, 150) +
                T('진짜일까?', 70, 540, 240) +
                '<div class="abs" style="left:80px;top:860px;padding:12px 34px 16px;border-radius:14px;background:#fff;color:#111;font-family:BH;font-size:60px">물가 4,923%의 나라 · 아르헨티나 100년 팩트체크</div>')
    return bg, body


M.design = design
if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    vs = sys.argv[1:] or ["A", "B"]
    for f in (FILES[v] for v in vs):
        shutil.copy(os.path.join(SRC, f), os.path.join(DST, f))
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs"
    for v in vs:
        print(M.render(v, f"{out}/oneshot_argentina_thumb_{v}.png"))
