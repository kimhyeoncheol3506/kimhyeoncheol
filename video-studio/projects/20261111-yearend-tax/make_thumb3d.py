"""34편 썸네일 G (3D판): 기존 A안 내용(2026년 귀속 · 미리 준비 · 연말정산 · 이 순서로 하세요 · 소득›공제›환급 · 가리키는 개미)을
'Blender 117만 원' 느낌(남색 바탕 · 금빛 3D 글자 · 쏟아지는 동전)으로 옮긴 판. 2026-11-13 현철님 요청 "그래픽이 중요해".
순서: blender thumb3d_blender.py → thumbs/3d_layer.png (투명) → 이 스크립트가 배경·광채·칩·개미를 얹어 thumbs/thumbnail_G.png"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "20261106-econ2h"))
import make_thumb_v2 as M  # noqa: E402

STK = ("drop-shadow(8px 0 0 #fff) drop-shadow(-8px 0 0 #fff) drop-shadow(0 8px 0 #fff) drop-shadow(0 -8px 0 #fff) "
       "drop-shadow(0 22px 30px rgba(0,0,0,.55))")


def design(v):
    bg = "radial-gradient(1100px 700px at 62% 40%,#24345A 0%,#141D33 55%,#0A0F1C 100%)"
    body = (
        # 연말정산 뒤 따뜻한 광채 + 위에서 떨어지는 빛줄기
        '<div class="abs" style="left:520px;top:80px;width:1200px;height:560px;border-radius:50%;'
        'background:radial-gradient(closest-side,rgba(255,196,90,.42),rgba(255,160,60,.12) 60%,rgba(255,160,60,0))"></div>'
        # 3D 레이어 (Blender)
        '<img class="abs" src="assets/3d_layer.png" style="left:0;top:0;width:1920px;height:1080px">'
        # 왼쪽 위 칩: 2026년 귀속(초록 상자) + 미리 준비(금색 글자)
        '<div class="abs" style="left:64px;top:52px;padding:12px 34px 18px;background:linear-gradient(180deg,#2E7D46,#1B5730);border:5px solid #F2C14E;'
        'border-radius:16px;font-family:BH;font-size:72px;line-height:1;color:#fff;box-shadow:0 12px 0 rgba(0,0,0,.45)">2026년 귀속</div>'
        '<div class="abs" style="left:560px;top:64px;font-family:BH;font-size:78px;line-height:1;color:#FFD45A;'
        '-webkit-text-stroke:10px #111;paint-order:stroke fill;filter:drop-shadow(0 8px 0 #000)">미리 준비</div>'
        # 가리키는 개미 (흰 윤곽 스티커)
        '<div class="abs" style="left:-30px;bottom:-40px;width:560px;height:700px">'
        '<img src="assets/mascot/가리킴.png" style="width:100%;height:100%;object-fit:contain;filter:' + STK + '"></div>'
    )
    return bg, body


M.design = design
if __name__ == "__main__":
    shutil.copy(os.path.join(HERE, "thumbs", "3d_layer.png"), os.path.join(M.ROOT, "assets", "3d_layer.png"))
    print(M.render("G", os.path.join(HERE, "thumbs", "thumbnail_G.png")))
