# -*- coding: utf-8 -*-
"""자막 없는 프레임 PNG 뽑기 (썸네일 원본용).
사용: python nocap.py <프로젝트폴더> <초,초,...>   (plan 이 끝난 프로젝트)
엔진 경로: 환경변수 TOON2D_DIR (t2d.py 가 있는 폴더). 없으면 이 파일 기준 ../../mystery-cartoon/kits/toon2d
"""
import os, sys
import skia
HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.environ.get("TOON2D_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "mystery-cartoon", "kits", "toon2d"))
sys.path.insert(0, ENG)
from toon2d import render
P = os.path.abspath(sys.argv[1])
rt = render.load(P)
rt.plan['captions'] = []
fps = rt.plan.get('fps', 30)
for t in [float(x) for x in sys.argv[2].split(',')]:
    s = rt.frame(int(t * fps), subframes=1)
    out = os.path.join(P, 'nocap_%05.1f.png' % t)
    s.makeImageSnapshot().save(out, skia.kPNG)
    print(out)
