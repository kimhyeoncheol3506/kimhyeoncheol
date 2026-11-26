# -*- coding: utf-8 -*-
"""소래포구 합동점검 쇼츠 → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("바가지 오명 소래포구, 이번엔 달라질까요?", "q", dict(kick="인천 남동구 · 11월 24일 발표", big="민관<br>합동점검", size=170))
add("원산지, 위생, 저울, 호객행위, 광장 불법 점용까지 다섯 가지를 점검했어요.", "a", dict(kick="점검 항목", big="5가지", size=230))
add("손님 많은 사월에서 오월, 구월에서 십일월엔 매달 점검합니다.", "b", dict(kick="성수기", big="매달 점검", size=190))
add("고의 부당 상행위는 행정처분에 상인회 자체 징계까지.", "c", dict(t="vs", kick="적발되면", a=["가벼운 위반", "현장 시정", "#5FB7A6"], b=["고의 위반", "처분+징계", "#FF5A3C"]))
add("이천이십사년엔 점포 이백구십여 곳 중 아홉 곳 저울이 불합격이었어요.", "d", dict(kick="2024년 3월 저울 점검 (서울신문)", big="290여 곳 중<br>9곳 불합격", size=130))
add("저울이 영점인지, 쟁반이 봉에 닿지 않았는지 꼭 보세요.", "e", dict(kick="손님이 확인할 것", big="영점 · 수평<br>봉 닿음", size=130))
add("여러분은 소래포구, 좋았던 경험 있으신가요?", "ask", dict(t="ask", q="소래포구<br>가 보셨나요?"))
json.dump(dict(title="short1", hook="소래포구<br>합동점검", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
