"""32편 사이버·3D 썸네일 A~D (공용 도구 tools/thumb_cyber.py 사용). 사용: VAR=A python3 make_thumb_cyber.py out.png"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from tools.thumb_cyber import render

VAR = os.environ.get("VAR", "A")
DATA = dict(left="다우 +3%", right="코스피 −5.28%", chip="−5.28%")
print(render(sys.argv[1], VAR, "같은 선거, 정반대", "코스피 −5%?", mascot="충격", data=DATA))
