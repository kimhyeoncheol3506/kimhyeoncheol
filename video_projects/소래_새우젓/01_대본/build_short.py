# -*- coding: utf-8 -*-
"""소래포구 새우젓 쇼츠 → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("올해 김장, 배추는 싸졌는데 새우젓은 사십이 점 일 퍼센트 올랐어요.", "q", dict(kick="aT 김장재료 조사 · 11/16", big="새우젓<br>42.1%↑", size=170))
add("새우젓 팔백 그램에 {e:15174}입니다.", "a", dict(kick="새우젓 800g", big="15,174원", size=190))
add("배추 스무 포기는 이십칠 점 칠 퍼센트 내렸는데요.", "b", dict(t="vs", kick="1년 전보다", a=["배추 20포기", "27.7%↓", "#5FB7A6"], b=["새우젓 800g", "42.1%↑", "#FF5A3C"]))
add("김장용 추젓은 일 킬로그램 이만 원, 육젓은 칠만 원.", "c", dict(kick="한국물가정보 · 1kg", big="추젓 2만<br>육젓 7만", size=150))
add("인천 젓새우 어획량이 일 년 새 오십오 점 삼 퍼센트 줄었대요.", "d", dict(kick="인천 젓새우 어획 (뉴스1)", big="55.3%↓", size=220))
add("정부 수산대전에서 새우젓을 최대 오십 퍼센트 할인하니 챙기세요.", "e", dict(kick="김장철 특별전", big="최대 50%<br>할인", size=170))
add("여러분은 김장에 추젓 쓰세요, 육젓 쓰세요?", "ask", dict(t="ask", q="추젓? 육젓?"))
json.dump(dict(title="short1", hook="새우젓<br>42%↑", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
