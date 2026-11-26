# -*- coding: utf-8 -*-
"""노량진 일본산 방어 쇼츠 → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
SH, PJ, PK, RX, QA = G["SH"], G["PJ"], G["PK"], G["RX"], G["QA"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("노량진 활방어, 열 킬로그램 중 여섯 킬로그램은 일본산입니다.", "q", dict(kick="노량진 활방어 경매 · 최근 2주", big=f"{SH}%<br>일본산", size=200))
add(f"최근 두 주 경락시세를 모아 보니 일본산 비중이 {{pc:{SH}}}였어요.", "a", dict(kick=f"경매 물량 {QA:,.0f}kg 중", big=f"일본산 {SH}%", size=170))
add(f"킬로그램당 평균 경락가는 일본산 {{e:{PJ}}}.", "b", dict(kick="일본산 kg당", big=f"{PJ:,}원", size=170))
add(f"국산은 {{e:{PK}}}이었어요.", "c", dict(kick="국산 kg당", big=f"{PK:,}원", size=170))
add(f"일본산이 약 {G['dec'](str(RX))} 배 비쌌습니다.", "d", dict(t="vs", kick="kg당 경락가", a=["일본산", f"{PJ:,}원", "#F1D9A0"], b=["국산", f"{PK:,}원", "#5FB7A6"]))
add("방어값은 십 년 새 네 배 넘게 올랐어요.", "e", dict(kick="11월 방어 경락가 (헤럴드경제)", big="4,870원<br>→ 2만 원", size=130))
add("바다가 뜨거워져 국산 어획이 흔들린 자리를 일본산이 메운 거예요.", "f", dict(kick="2016~2018년 일본산 0건", big="올해 60%", size=180))
add("사기 전엔 원산지 표시부터 확인하세요.", "g", dict(t="warn"))
add("여러분은 국산 방어와 일본산 방어, 차이를 느끼시나요?", "ask", dict(t="ask", q="국산 vs 일본산<br>방어, 차이 느끼나요?"))
json.dump(dict(title="short1", hook="방어 61%<br>일본산", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
