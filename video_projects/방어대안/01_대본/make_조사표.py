# -*- coding: utf-8 -*-
"""조사표.md = prices.json(최근 2주·4주 주별·작년) + 계산(반올림 전) + 조사_방어대안.md(보도·구별법·수율) + 조사_수율.md"""
import json, os, runpy
H = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{H}/build_data.py", run_name="short"); P = G["P"]
L = ["# 조사표 — 방어 대안 5가지", "", f"## 최근 2주 kg당 경락가 {P['two']['week']} ({len(P['two']['days'])}일) — 노량진수산(주) 어종별 경락시세 일별 수집본, kg 경매 수량 가중 중앙값"]
L += [f"- {k}: {v['med']:,}원 · {v['qty']:,}kg · {v['days']}일 · 범위 {v['lo']:,}~{v['hi']:,}" for k, v in P["two"]["items"].items()]
L += ["", "## 4주 주별"] + [f"- {w['week']}: " + " · ".join(f"{k} {v['med']:,}" for k, v in w["items"].items()) for w in P["weeks"]]
L.append("- 변동폭 %: " + ", ".join(f"{k} {v} (반올림 {round(v)}%)" for k, v in P["var4"].items()))
L += ["", f"## 작년 {P['lastyear']['week']}"] + [f"- {k}: {v['med']:,}원" for k, v in P["lastyear"]["items"].items()]
L += ["", "## 계산 (반올림 전)", f"- 방어 11/9~11/14 {G['B0']:,} → 이번 주 {G['B1']:,}: {(G['B0'] - G['B1']) / G['B0'] * 100:.1f}% (반올림 {G['DROP']}%) · 작년 11/24~11/29 {G['LYB']:,} 대비 {(G['LYB'] - G['B1']) / G['LYB'] * 100:.1f}% (반올림 {G['VSLY']}%)"]
for n in G["Y"]:
    L.append(f"- {n}: kg당 {G['T'][n]:,} · 수율 {int(G['Y'][n] * 100)}% → 회 100g {G['C100'](n):,.0f}원 · 1만 원어치 회 {10000 / G['C100'](n) * 100:.0f}g (10g 단위 {G['G10'](n)}g)"
             + f" · 4주 최고 {G['HI'][n]:,}원이면 100g {G['C100'](n, G['HI'][n]):,.0f}원 · {G['G10'](n, G['HI'][n])}g")
L += ["- 4주 범위: " + " · ".join(f"{n} {G['LO'][n]:,}~{G['HI'][n]:,}" for n in G["LO"]), "- 잿방어(활) 최근 2주 52.6kg → 반올림 53kg",
      "- 보도 숫자(원문 표기 2만1685원·1만7517원·2만72원): 21,685 17,517 20,072", "- 기타 수치: 3~6kg 6~8kg 8kg 이상 · 34~38% 41~54% 40% 30% 34% 41% · 11월 3~10일 1~24일 · 2016년 · 10월 2월 11월 12월 1월 · 2주 3주 4주 · 16일 25일 · 1만 원 · 1천 원 2천 원 · 15%", "", "---",
      open(f"{H}/조사_방어대안.md", encoding="utf-8").read(), "", "---", open(f"{H}/조사_수율.md", encoding="utf-8").read()]
open(f"{H}/조사표.md", "w", encoding="utf-8").write("\n".join(L)); print("ok")
