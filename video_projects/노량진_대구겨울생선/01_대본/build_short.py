# -*- coding: utf-8 -*-
"""노량진 대구 쇼츠 → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
CD, WL, AG = G["CD"], G["WLAST"], G["AG"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("대구 한 마리 삼만 원. 일주일 새 오천 원 올랐대요.", "q", dict(kick="소매 대구 대자 1마리 (한국물가정보)", big="3만 원", size=220))
add(f"그런데 노량진 새벽 경매에선 킬로그램당 평균 {{e:{CD['p']}}}이었어요.".replace("그런데", "하지만"), "a", dict(kick="노량진 선어 대구 · 최근 2주", big=f"kg {CD['p']:,}원", size=170))
add(f"이번 주는 {{e:{WL[1]}}}으로 오히려 내려왔습니다.", "b", dict(kick="이번 주(11/23~25)", big=f"{WL[1]:,}원", size=190))
add("소매는 한 마리 값, 경락가는 킬로그램당 도매가라 단위가 달라요.", "c", dict(t="vs", kick="단위가 다르다", a=["소매", "1마리", "#FF5A3C"], b=["경락가", "kg당", "#5FB7A6"]))
add("수온이 높아 찬물 생선 어획이 줄었다는 분석도 있어요.", "d", dict(kick="한국물가정보 분석", big="수온↑<br>냉수성 어종↓", size=120))
add(f"아귀는 킬로그램당 {{e:{AG['p']}}}이었습니다.", "e", dict(kick="노량진 선어 아귀", big=f"kg {AG['p']:,}원", size=170))
add("살 때는 무게를 물어보고 킬로그램당으로 비교하세요.", "g", dict(t="warn"))
add("여러분은 대구탕, 아귀찜, 물메기탕 중 뭐가 좋으세요?", "ask", dict(t="ask", q="대구탕·아귀찜<br>물메기탕?"))
json.dump(dict(title="short1", hook="대구 3만 원?<br>도매는", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
