# -*- coding: utf-8 -*-
"""가락시장 현대화 쇼츠 → short1.json (문장 + 화면 카드)"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
G["SUBFIX"] += [("삼백사십사억 원", "344억 원"), ("십칠 년", "17년"), ("삼십사 점 칠 퍼센트", "34.7%")]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("가락시장을 다시 짓는 데 얼마가 들까요?", "q", dict(big="?억 원", small="가락시장 시설현대화사업", size=170))
add("{eok:12769}. 처음 계획은 {eok:6830}이었어요.", "a", dict(t="vs", kick="총사업비", a=["처음", "6,830억", "#5FB7A6"], b=["지금", "1조 2,769억", "#E4775F"]))
add("완공 목표는 {yr:2018}에서 {yr:2031}으로 밀렸습니다.", "b", dict(t="vs", kick="완공 목표", a=["처음", "2018년", "#5FB7A6"], b=["지금", "2031년", "#E4775F"]))
add("확보된 돈은 아직 삼십사 점 칠 퍼센트예요.", "c", dict(kick="확보된 순재원 비율", big="34.7%", size=220))
add("이천십일년부터 낸 이자만 삼백사십사억 원이 넘습니다.", "d", dict(kick="국고 융자 이자 (2011~2025)", big="344억 원+", size=170))
add("결국 시장을 수도권 외곽으로 옮기자는 주장도 나왔어요.", "e", dict(big="가락시장<br>이전?", size=170))
add("옮기면 한 해 {eok:4154}을 아낀다는 분석이 있어요.", "f", dict(kick="농경연 분석 (의원 제시)", big="연 4,154억 원", size=150))
add("하지만 일본 도요스시장은 이전 결정 뒤 십칠 년이 걸렸습니다.", "g", dict(kick="츠키지 → 도요스", big="17년", size=220))
add("아직 주장 단계라, 정해진 건 없어요.", "h", dict(kick="꼭 알아 두세요", big="이전 = 확정 아님", size=120))
add("여러분은 가락시장, 옮겨야 한다고 보세요?", "ask", dict(t="ask", q="가락시장<br>옮겨야 할까?"))
json.dump(dict(title="short1", hook="가락시장<br>재건축 얼마?", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
