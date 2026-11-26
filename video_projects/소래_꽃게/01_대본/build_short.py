# -*- coding: utf-8 -*-
"""소래포구 꽃게 쇼츠 → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
WA, PA, PS = G["WA"], G["PA"], G["PS"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("소래포구 가기 전에 보세요. 암꽃게 값이 두 배가 됐어요.", "q", dict(kick="노량진 활 암꽃게 kg당", big="2배↑", size=240))
add(f"시월 첫 주 킬로그램당 {{e:{WA[0][1]}}}.", "a", dict(kick="10월 첫 주", big=f"{WA[0][1]:,}원", size=180))
add(f"십일월 셋째 주엔 {{e:{WA[6][1]}}}입니다.", "b", dict(kick="11월 셋째 주", big=f"{WA[6][1]:,}원", size=180))
add(f"최근 두 주 수꽃게는 {{e:{PS}}}으로 그대로였어요.", "c", dict(t="vs", kick="최근 2주 kg당", a=["암꽃게", f"{PA:,}원", "#F1D9A0"], b=["수꽃게", f"{PS:,}원", "#5FB7A6"]))
add("십일월 암꽃게는 살과 장이 오른다는데, 그만큼 찾는 사람도 많아요.", "d", dict(kick="입질의추억 김지민", big="11월엔<br>암꽃게", size=170))
add("꽃게는 물을 빼고, 영점 맞춘 저울로 재 달라고 하세요.", "e", dict(kick="살 때 확인", big="물 빼고 재기", size=160))
add("노량진 도매 경락가라 소래포구 가게 값과는 달라요.", "g", dict(t="warn"))
add("여러분은 암꽃게파세요, 수꽃게파세요?", "ask", dict(t="ask", q="암꽃게? 수꽃게?"))
json.dump(dict(title="short1", hook="암꽃게<br>2배↑", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
