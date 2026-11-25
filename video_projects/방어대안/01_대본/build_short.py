# -*- coding: utf-8 -*-
"""방어 대안 쇼츠 1편 → short1.json — 숫자는 build_data와 같은 표. sig c=카드 이름"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S, T, G10, HI, B1, DROP = G["S"], G["T"], G["G10"], G["HI"], G["B1"], G["DROP"]
G["SUBFIX"].append(("네 배", "4배"))
SS = [S("만 원어치 회, 방어는 몇 그램일까요?", c="q"),
      S(f"노량진 도매 경락가로 방어는 약 {{g:{G10('방어')}}}.", c="b"),
      S(f"부시리는 약 {{g:{G10('부시리')}}}. 네 배 가까이 됩니다.", c="vs"),
      S(f"방어 경락가도 이번 주 킬로그램당 {{e:{B1}}}, 삼 주 전보다 약 {{pc:{DROP}}} 내렸어요.", c="drop"),
      S(f"부시리는 {{e:{T['부시리']}}}이지만, 주마다 값이 크게 바뀝니다.", c="range"),
      S(f"값이 높았던 주로 잡아도, 부시리 회는 약 {{g:{G10('부시리', HI['부시리'])}}}이에요.", c="hi"),
      S(f"광어는 오히려 약 {{g:{G10('광어')}}}. 방어보다 적어요.", c="gw"),
      S("방어와 부시리는 위턱 끝을 보세요. 방어는 각지고, 부시리는 둥급니다.", c="tell"),
      S("새벽 경매 도매가 기준이라, 가게 값과는 달라요.", c="warn"),
      S("여러분은 올겨울 방어파세요, 부시리파세요?", c="ask")]
json.dump(dict(title="short1", hook="1만 원어치 회<br>방어 vs 부시리", sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
