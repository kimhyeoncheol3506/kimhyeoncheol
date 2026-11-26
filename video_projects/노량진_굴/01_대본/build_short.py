# -*- coding: utf-8 -*-
"""노량진 굴 쇼츠 → short1.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
WLOW, WL, UP, RG, MIX = G["WLOW"], G["WL"], G["UP"], G["RG"], G["MIX"]
SS, C = [], {}
def add(t, k, c): SS.append(S(t, c=k)); C[k] = c
add("굴값이 한 달 새 크게 올랐습니다.", "q", dict(kick="노량진 깐굴 한 상자 · 주별 평균", big=f"{UP}%↑", size=230))
add(f"시월 말 한 상자 {{e:{WLOW[1]}}}이던 깐굴이.", "a", dict(kick="10/26~11/1", big=f"{WLOW[1]:,}원", size=180))
add(f"이번 주엔 {{e:{WL[1]}}}이 됐어요.", "b", dict(kick="11/23~25", big=f"{WL[1]:,}원", size=180))
add(f"산지별로 보면 통영산 {{e:{RG['통영'][0]}}}, 남해산 {{e:{RG['남해'][0]}}}.", "c", dict(t="vs", kick="산지별 상자당 (11/12~25)", a=["통영", f"{RG['통영'][0]:,}원", "#5FB7A6"], b=["남해", f"{RG['남해'][0]:,}원", "#F1D9A0"]))
add(f"같은 산지끼리는 이번 달 들어 약 {{pc:{MIX['삼천포'][2]}}}에서 {{pc:{MIX['통영'][2]}}} 올랐어요.", "d", dict(kick="산지별 상승폭 (11/2~8 → 11/23~25)", big=f"{MIX['삼천포'][2]}~{MIX['통영'][2]}%", size=170))
add("생굴이 걱정되면 삼배체굴을 고르거나 익혀 드세요.", "e", dict(kick="입질의추억 김지민 당부", big="노로바이러스<br>주의", size=140))
add("노량진 도매 경락가라 가게 값과는 달라요.", "g", dict(t="warn"))
add("여러분은 굴, 생으로 드세요 익혀 드세요?", "ask", dict(t="ask", q="굴, 생으로?<br>익혀서?"))
json.dump(dict(title="short1", hook=f"굴값<br>{UP}%↑", cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
