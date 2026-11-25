# -*- coding: utf-8 -*-
"""김장배추 — 가락시장 경락가(KAMIS '도매가격(가락시장 경락가격)' 화면) 2026 vs 2025, 11/12~11/25 일별 평균가의 평균 → prices.json"""
import csv, json, os, collections
H = os.path.dirname(os.path.abspath(__file__))
R = list(csv.DictReader(open(f"{H}/garak_kamis.csv", encoding="utf-8")))
g = collections.defaultdict(list)
for r in R: g[(r["date"][:4], r["item"], r["unit"], r["grade"])].append((r["date"], int(r["avg"].replace(",", ""))))
out = {}
for (y, it, u, gr), v in g.items():
    v = sorted(set(v)); w1 = [p for d, p in v if d[5:] >= "11.19"]
    out[f"{y}|{it}|{u}|{gr}"] = dict(avg=round(sum(p for _, p in v) / len(v)), days=len(v), last=v[-1][1], last_date=v[-1][0], lo=min(p for _, p in v), hi=max(p for _, p in v),
                                     wk=round(sum(w1) / len(w1)) if w1 else None, daily=v)
json.dump(out, open(f"{H}/prices.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in sorted(out):
    if "|상" in k or "절임" in k: o = out[k]; print(k, o["avg"], f"({o['days']}일, {o['lo']}~{o['hi']}, 최근주 {o['wk']}, 마지막 {o['last_date']} {o['last']})")
