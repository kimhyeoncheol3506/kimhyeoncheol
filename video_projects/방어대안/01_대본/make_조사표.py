# -*- coding: utf-8 -*-
"""조사표.md = prices.json(최근 2주·4주 주별) + 원가·인원별 계산(반올림 전) + 조사_수율.md(수율·1인 200g·상차림비 출처)"""
import json, os, runpy
H = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{H}/build_data.py", run_name="short"); P = G["P"]; T, Y = G["T"], G["Y"]
L = ["# 조사표 — 광어 1kg 사면 회는 몇 g? (회 한 접시의 진짜 값)", "", f"## 최근 2주 kg당 경락가 {P['two']['week']} ({len(P['two']['days'])}일) — 노량진수산(주) 어종별 경락시세 일별 수집본, kg 경매 수량 가중 중앙값"]
L += [f"- {k}: {v['med']:,}원 · {v['qty']:,}kg · 범위 {v['lo']:,}~{v['hi']:,}" for k, v in P["two"]["items"].items()]
L += ["", "## 4주 주별 (변동폭 = (최고−최저)/평균, 30% 이상 가격 계산 제외)"] + [f"- {w['week']}: " + " · ".join(f"{k} {v:,}" for k, v in w["items"].items()) for w in P["weeks"]]
L.append("- 변동폭 %: " + ", ".join(f"{k} {v} (반올림 {round(v)}%)" for k, v in P["var4"].items()))
L += ["", "## 계산 (반올림 전)", "- 회 100g당 도매 원가 = kg당 경락가 ÷ 수율 ÷ 10"]
for n in T:
    L.append(f"- {n}: kg당 {T[n]:,} · 수율 {int(Y[n] * 100)}% → 1kg당 회 {int(Y[n] * 1000)}g · 100g당 {round(G['C100'](n)):,}원" + (f" · 수율 {int(G['YH'][n] * 100)}%면 {round(G['C100'](n, G['YH'][n])):,}원" if n in G["YH"] else ""))
    L.append(f"  - 인원별: " + " / ".join(f"{p}명 {G['kgf'](p, n):.2f}kg {round(G['BUD'](n, p)):,}원" for p in (4, 6, 10)))
L.append(f"- 광어−참돔 kg당 차이 {T['광어'] - T['참돔']:,}원")
L.append(f"- 4명 광어 2kg {round(G['SUB4']):,}원 · 광어 1kg+농어 1kg {G['COMBO']:,}원 · 차이 {round(G['SUB4'] - G['COMBO']):,}원")
L.append(f"- 상차림비 4명: 5,000×4 = {G['SET5']:,}원 · 7,000×4 = {G['SET7']:,}원")
L += ["- 기타 수치: 1인 200g · 4명 800g · 1kg짜리 2마리 · 회 300g 400g 500g · 400~500g 300~400g 350~500g 410g · 2kg 3kg 5kg 2.7kg 6.7kg 4kg 1.6kg 1kg · 40~50% 30~40% 35~50% 40% 30% 50% 41% · 11월 2월 12월 1월 · 2주 4주 · 16일 25일 · 258g · 5,000원 7,000원 · 2곳 · 10으로 · 1인당 · 4명 6명 10명", "", "---", open(f"{H}/조사_수율.md", encoding="utf-8").read()]
open(f"{H}/조사표.md", "w", encoding="utf-8").write("\n".join(L)); print("ok")
