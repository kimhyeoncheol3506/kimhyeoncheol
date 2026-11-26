# -*- coding: utf-8 -*-
"""가락시장 경매 시간 쇼츠 → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("무 오백육십육 톤이 이십 분 만에 다 팔렸습니다.", "q", dict(kick="가락시장 채소 경매 (서울신문 르포)", big="566톤 · 20분", size=150))
add("한 건에 사에서 오 초. 가락시장 경매예요.", "a", dict(kick="한 건 낙찰까지", big="4~5초", size=220))
add("채소 경매는 저녁 여섯 시 반부터 시작해요.", "b", dict(kick="채소", big="저녁 6시 반~", size=160))
add("배추와 양파는 밤 열한 시.", "c", dict(kick="배추 · 양파", big="밤 11시", size=200))
add("포도, 감귤, 딸기 같은 과일은 새벽 두 시.", "d", dict(kick="포도·감귤·딸기 등", big="새벽 2시", size=200))
add("사과와 배는 아침 여덟 시예요.", "e", dict(kick="사과 · 배", big="아침 8시", size=200))
add("활어는 새벽 세 시 반에 시작합니다.", "f", dict(kick="수산 · 활어", big="새벽 3시 반", size=170))
add("토요일 저녁부터 일요일 새벽까지는 경매가 없어요.", "g", dict(kick="주말", big="토 저녁~일 새벽<br>경매 없음", size=110))
add("서울시농수산식품공사 안내 기준이고, 시간은 바뀔 수 있어요.", "h", dict(kick="꼭 알아 두세요", big="공식 안내 확인", size=140))
add("여러분은 가락시장 경매, 직접 보신 적 있나요?", "ask", dict(t="ask", q="가락시장 경매<br>보신 적 있나요?"))
json.dump(dict(title="short1", hook="가락시장<br>경매 시간표", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
