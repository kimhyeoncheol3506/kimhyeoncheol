# -*- coding: utf-8 -*-
"""조사표.md = 이번 주 시세·손해 계산표 + 조사_무게속임수.md(출처)"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); P = json.load(open(f"{H}/../00_data/prices.json", encoding="utf-8")); PR = P["med"]
rows = "\n".join(f"| {g:,}g | {round(PR * g / 1000):,}원 |" for g in (100, 120, 300, 800, 950, 1000))
t = (f"# 조사표 — 킹크랩 무게 속임수\n\n## 시세 (노량진수산(주) 어종별 경락시세 일별 수집본)\n- 이번 주 {P['week']} ({len(P['days'])}일) 활킹크랩((활)왕게) kg당 수량 가중 중앙값 {PR:,}원 · 물량 {int(P['qty']):,}kg\n"
     f"- 지난주 11/16~11/21 {P['last_week']:,}원\n\n## 손해 환산 (경락가 × 무게, 천 원 반올림 전)\n| 무게 차이 | 금액 |\n|---|---|\n{rows}\n\n"
     "## 계산 참고\n- 3kg × (1 − 30~35%) = 1.95~2.1kg · 3kg→2kg 감소율 33% · 1.25kg vs 2.2kg 차이 950g · 3.2kg−2.4kg = 800g · 1.9kg−1.2kg = 700g · 132,300원(2.035kg × 65,000원 → 13만 원 넘음, 130,000원 기준) · 과태료 1차 100,000원(10만 원)\n\n"
     + open(f"{H}/조사_무게속임수.md", encoding="utf-8").read())
open(f"{H}/조사표.md", "w", encoding="utf-8").write(t)
