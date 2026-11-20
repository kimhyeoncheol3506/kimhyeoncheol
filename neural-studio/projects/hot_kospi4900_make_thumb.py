"""hot_kospi4900 어두운 에디토리얼 썸네일 A (긴급편 요청: 판 사람 vs 버틴 사람 + 1년 뒤 숫자, 검정 바탕, 큰 숫자, 강조색 1개, 3D·큰 개미 없음).
숫자: 2000~2024년 코스피 하루 -6% 이상 폭락일 19번, 그날 종가 → 1년 뒤 (채널 계산, 지수 기준). 판 사람 = 그날 팔고 현금 보유 0%(이자 제외), 버틴 사람 = 평균 +23.7%.
오른쪽 아래(재생시간 자리) 비움. 렌더 방식은 make_thumb_v2.render.
렌더: python3 projects/hot_kospi4900_make_thumb.py → assets/thumbs/hot_kospi4900_thumb_A.png"""
import os
import shutil
import sys

sys.path.insert(0, "/home/user/kimhyeoncheol/video-studio/projects/20261106-econ2h")
import make_thumb_v2 as M

ROOT = "/tmp/t3d_hot_kospi4900/troot"
if not os.path.exists(f"{ROOT}/hyperframes.json"):
    os.makedirs(ROOT, exist_ok=True)
    for f in ("hyperframes.json", "meta.json", "package.json"):
        shutil.copy(f"/home/user/hf/thumb/{f}", ROOT)
    if not os.path.exists(f"{ROOT}/assets"):
        os.symlink("/home/user/hf/thumb/assets", f"{ROOT}/assets")
M.ROOT = ROOT

BG = "#0B0B0D"
RED = "#FF3B3B"
WHITE = "#F4F1EA"
GRAY = "#6B6F78"
NOVIG = '<style>.clip[data-track-index="1"]{box-shadow:inset 0 0 260px rgba(0,0,0,.6)!important}</style>'


def design(v):
    glow = ('<div class="abs" style="inset:0;background:radial-gradient(ellipse 900px 700px at 76% 60%,rgba(255,59,59,.16),rgba(0,0,0,0) 70%)"></div>')
    top = ('<div class="abs" style="left:90px;top:70px;font-family:BH;font-size:150px;line-height:1;color:' + WHITE +
           ';letter-spacing:-3px">코스피 <span style="color:' + RED + '">4900</span> 붕괴</div>')
    divider = '<div class="abs" style="left:900px;top:330px;width:6px;height:600px;background:rgba(255,255,255,.18)"></div>'
    l_lab = ('<div class="abs" style="left:90px;top:330px;width:780px;text-align:center;font-family:BH;font-size:120px;line-height:1;color:' + GRAY + '">판 사람</div>')
    l_num = ('<div class="abs" style="left:90px;top:500px;width:780px;text-align:center;font-family:BH;font-size:330px;line-height:1;color:' + GRAY +
             ';letter-spacing:-8px">0%</div>')
    r_lab = ('<div class="abs" style="left:960px;top:330px;width:900px;text-align:center;font-family:BH;font-size:120px;line-height:1;color:' + WHITE + '">버틴 사람</div>')
    r_num = ('<div class="abs" style="left:930px;top:505px;width:940px;text-align:center;font-family:BH;font-size:270px;line-height:1;color:' + RED +
             ';letter-spacing:-10px;text-shadow:0 18px 40px rgba(0,0,0,.6),0 0 60px rgba(255,59,59,.35)">+23.7%</div>')
    foot = ('<div class="abs" style="left:90px;top:900px;font-family:BH;font-size:66px;line-height:1;color:' + WHITE +
            ';opacity:.85">폭락한 날 19번 · 1년 뒤 평균</div>')
    return BG, NOVIG + glow + top + divider + l_lab + l_num + r_lab + r_num + foot


M.design = design
if __name__ == "__main__":
    out = "/home/user/kimhyeoncheol/neural-studio/assets/thumbs/hot_kospi4900_thumb_A.png"
    print(M.render("hot_kospi4900_A", out))
