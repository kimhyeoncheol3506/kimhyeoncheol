# -*- coding: utf-8 -*-
"""킹크랩 무게 속임수 티저 쇼츠 → short1.json ([음성, {k}, 자막]) — 숫자는 build_data와 같은 시세·출처"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S, L = G["S"], G["L"]
SS = [S("킹크랩 삼 킬로그램 샀는데, 집에서 재 보니 이 킬로그램. 속은 걸까요?", k=1),
      S("찌면 원래 삼십에서 삼십오 퍼센트가 줄어서, 자연 감량일 수도 있어요.", k=2),
      S(f"문제는 찌기 전입니다. 바구니 삼백 그램만 안 빼도, 이번 주 도매가로 약 {{p:{L(300)}}}이에요.", k=3),
      S("저울 영 점, 물 빼기, 중량 창 확인. 무게 속임수 다섯 가지는 관련 영상에서 보세요.", k=4)]
json.dump(dict(title="short1", sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
