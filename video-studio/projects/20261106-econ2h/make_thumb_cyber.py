"""33편 경제 지식 2시간 완전정리 — 사이버·3D 썸네일 A~D (tools/thumb_cyber.py). 사용: VAR=A python3 make_thumb_cyber.py out.png"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from tools.thumb_cyber import render

VAR = os.environ.get("VAR", "A")
TXT = {"A": ("월급쟁이 필수", "경제 2시간"), "B": ("틀어놓고 듣는", "경제 2시간"),
       "C": ("돈의 원리 8가지", "경제 2시간"), "D": ("이것도 모르고 투자?", "경제 2시간")}[VAR]
DATA = dict(left="돈의 양 ↑", right="내 돈의 힘 ↓", left_bars=[80, 110, 140, 180, 220, 270, 330, 400], right_bars=[380, 350, 320, 290, 250, 210, 170, 130],
            chip="2H", line="M80,520 L380,470 L700,430 L1000,360 L1300,300 L1600,220 L1860,140", line_color="#ffd23f")
print(render(sys.argv[1], VAR, TXT[0], TXT[1], mascot={"A": "놀람", "B": "놀람", "C": "걱정", "D": "충격"}[VAR], data=DATA))
