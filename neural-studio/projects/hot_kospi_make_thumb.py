"""hot_kospi 어두운 에디토리얼 썸네일 A (BRIEF: 먹색·짙은 남색 바탕 + 큰 숫자 하나 + 글자 6자 이하).
숫자 '-45.5%' = 본편 첫 판과 같은 숫자(연합뉴스 11/17: 6월 22일 최고점 9,114.55 대비). 글자 '코스피 반토막'(6자).
빨간 붓 밑줄·채널 배지·실존 인물 얼굴 없음, 개미는 작게(충격), 오른쪽 아래(재생시간 자리) 비움.
렌더 방식은 make_thumb_v2.render 그대로. 다른 편과 동시에 돌려도 겹치지 않게 렌더 폴더만 /tmp/t3d_hot_kospi/troot 로 바꾼다
(hyperframes.json·meta.json·package.json 복사 + assets 는 /home/user/hf/thumb/assets 링크).
렌더: python3 projects/hot_kospi_make_thumb.py → assets/thumbs/hot_kospi_thumb_A.png"""
import os
import shutil
import sys

sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M

ROOT = "/tmp/t3d_hot_kospi/troot"
if not os.path.exists(f"{ROOT}/hyperframes.json"):
    os.makedirs(ROOT, exist_ok=True)
    for f in ("hyperframes.json", "meta.json", "package.json"):
        shutil.copy(f"/home/user/hf/thumb/{f}", ROOT)
    if not os.path.exists(f"{ROOT}/assets"):
        os.symlink("/home/user/hf/thumb/assets", f"{ROOT}/assets")
M.ROOT = ROOT

BG = "#121826"      # 짙은 남색에 가까운 먹색
RED = "#FF3B3B"
WHITE = "#F4F1EA"
NOVIG = '<style>.clip[data-track-index="1"]{box-shadow:inset 0 0 260px rgba(0,0,0,.55)!important}</style>'


def design(v):
    grid = ('<div class="abs" style="inset:0;background:'
            'radial-gradient(ellipse at 40% 45%,rgba(60,80,130,.35),rgba(0,0,0,0) 60%),'
            'repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 1px,transparent 1px 90px),'
            'repeating-linear-gradient(90deg,rgba(255,255,255,.035) 0 1px,transparent 1px 90px)"></div>')
    # 하락 꺾은선 (배경 장식, 흐리게)
    line = ('<svg class="abs" style="left:0;top:0" width="1920" height="1080" viewBox="0 0 1920 1080">'
            '<polyline points="60,520 330,470 560,400 760,405 980,640 1180,600 1380,615 1560,790 1840,900" '
            'fill="none" stroke="rgba(255,59,59,.28)" stroke-width="14" stroke-linejoin="round" stroke-linecap="round"/></svg>')
    word = ('<div class="abs" style="left:100px;top:150px;font-family:BH;font-size:175px;line-height:1;color:' + WHITE +
            ';letter-spacing:-4px">코스피 <span style="color:' + RED + '">반토막</span></div>')
    num = ('<div class="abs" style="left:70px;top:420px;font-family:BH;font-size:480px;line-height:1;color:' + RED +
           ';letter-spacing:-14px;text-shadow:0 18px 40px rgba(0,0,0,.6)">-45.5%</div>')
    ant = ('<img class="abs" src="assets/mascot/충격.png" style="left:1530px;top:110px;width:240px;height:300px;'
           'object-fit:contain;filter:drop-shadow(0 12px 18px rgba(0,0,0,.5))">')
    return BG, NOVIG + grid + line + word + num + ant


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs/hot_kospi_thumb_A.png"
    print(M.render("hot_kospi_A", out))
