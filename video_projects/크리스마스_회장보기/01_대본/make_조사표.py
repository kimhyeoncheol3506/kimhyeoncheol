# -*- coding: utf-8 -*-
"""조사표.md = prices.json 주별·일별 표 + 인원별 예산 계산(반올림 전) + 지난 편 조사표(1인 200g·수율 출처)"""
import json, os, runpy
H = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{H}/build_data.py", run_name="short"); P = G["P"]
L = ["# 조사표 — 크리스마스·연말 회 장보기", "", "## 주별 kg당 경락가 (노량진수산(주) 어종별 경락시세 일별 수집본, kg 경매 수량 가중 중앙값)", "| 주 | 일수 | 광어 | 참돔 | 농어 | 방어 |", "|---|---|---|---|---|---|"]
for w in P["weeks"] + [P["two"]]:
    it = w["items"]; L.append(f"| {w['week']} | {len(w['days'])} | " + " | ".join(f"{it[k]['med']:,}" if k in it else "-" for k in ("넙치(활)", "참돔(활)", "농어(활)", "방어(활)")) + " |")
L += ["", f"최근 4주 변동폭(%): {P['var4']} (반올림 {', '.join(f'{k} {round(v)}%' for k, v in P['var4'].items())}) → 30% 이상 제외", "", "## 작년 크리스마스 주 일별 광어"] + [f"- {d['date']}({d['dow']}) {d['items']['넙치(활)']['med']:,}원 · {d['items']['넙치(활)']['qty']:,}kg" for d in P["daily"]]
L += ["", "## 인원별 예산 (반올림 전) = 인원 × 0.2 ÷ 수율 × kg당 가격"]
for n in G["T"]:
    for p in (4, 6, 10):
        L.append(f"- {n} {p}명 {G['kgf'](p, G['Y'][n]):.2f}kg: 작년 첫 주 {round(G['BUD'](n, p, G['A'][n])):,} · 크리스마스 주 {round(G['BUD'](n, p, G['X'][n])):,} · 차이 {round(G['BUD'](n, p, G['X'][n]) - G['BUD'](n, p, G['A'][n])):,} · 올해 지금 {round(G['BUD'](n, p, G['T'][n])):,}")
for nm, c in (("10명 광어 2.5+농어 2.5", G["C10"]), ("6명 농어 2+광어 1", G["C6"])):
    L.append(f"- 조합 {nm}: 작년 첫 주 {round(G['COMBO'](G['A'], c)):,} · 크리스마스 주 {round(G['COMBO'](G['X'], c)):,} · 올해 지금 {round(G['COMBO'](G['T'], c)):,}")
L.append(f"- 올해 광어 10명 − 작년 크리스마스 주 광어 10명: {round(G['BUD']('광어', 10, G['T']['광어']) - G['B10']['광어'][1]):,}")
L.append("- 변화율(%): " + ", ".join(f"{n} 첫 주→크리스마스 주 {G['pct'](G['A'][n], G['X'][n])} · 첫 주→올해 {G['pct'](G['A'][n], G['T'][n])}" for n in G["T"]))
L += ["- 기타 수치: 1인 200g · 수율 광어 40% 참돔 30% 농어 40% · 5kg 6.7kg 2.5kg 2kg 1kg · 30% · 2주 4주 · 16일 22일 25일 27일", "", "---", open(f"{H}/조사_연말1편.md", encoding="utf-8").read()]
open(f"{H}/조사표.md", "w", encoding="utf-8").write("\n".join(L)); print("ok")
