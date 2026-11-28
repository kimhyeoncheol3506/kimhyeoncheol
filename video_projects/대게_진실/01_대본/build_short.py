# -*- coding: utf-8 -*-
"""대게 쇼츠 '1kg 찌면 살은 몇 g?' (패턴 1 숫자 충격 1개) → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
LV, SV, M30, M20 = G["LV"], G["SV"], G["M30"], G["M20"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("찐 대게 일 킬로그램, 살은 몇 그램일까요?", "q", dict(kick="대게 1kg", big="살은<br>몇 g?", size=200))
add("찌면 피와 수분이 빠져서, 살아 있는 상태가 좋은 갑각류도 이십에서 이십오 퍼센트가 준다고 해요.", "a", dict(kick="찌면 줄어드는 무게 (전문가 설명)", big="20~25%↓", size=190))
add("일 킬로그램이 칠백오십에서 팔백 그램이 되는 거죠.", "b", dict(kick="1kg 찌면", big="750~800g", size=180))
add("살만 따지면 전체 무게의 이십에서 삼십 퍼센트라는 설명이 흔해요.", "c", dict(kick="대게 살 비율 (흔히 인용)", big="20~30%", size=200))
add("그러니까 일 킬로그램을 사도 살은 이백에서 삼백 그램 정도예요.".replace("그러니까 ", "결국 "), "d", dict(kick="1kg 사면 살은", big="200~300g", size=190))
add(f"노량진 활대게 경락가 {{e:{LV['this']['p']}}}으로 치면, 살 무게 백 그램에 {{e:{M30}}}에서 {{e:{M20}}}꼴이에요.", "e", dict(kick="살 100g당 · 경락가 기준", big=f"{M30:,}~<br>{M20:,}원", size=150))
add("공식 실측값은 아니니 범위로만 보시고, 살 때는 찌기 전 무게를 꼭 확인하세요.", "g", dict(t="warn"))
add("여러분은 대게 살 때 활대게 사세요, 쪄 놓은 대게 사세요?", "ask", dict(t="ask", q="활대게?<br>쪄 놓은 대게?"))
json.dump(dict(title="short1", hook="대게 1kg<br>살은 몇 g?", market_label="노량진", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]),
          open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
