# -*- coding: utf-8 -*-
"""광어 수율편 — 광어(넙치)·참돔·농어·방어·우럭(활) kg당 경락가(kg 경매 수량 가중 중앙값): 최근 2주(11/16~마지막 날) + 4주 주별 변동폭 → prices.json
자료: 노량진수산(주) 어종별 경락시세(일별 수집본, StarRate1214/smart-noryangjin)"""
import datetime as dt, json, os, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/scripts")
import noryangjin_prices as N
DATA = "/home/user/kimhyeoncheol/video_projects/주간시세_리포트/data"
ITEMS = [("넙치", "활"), ("참돔", "활"), ("농어", "활"), ("우럭", "활"), ("방어", "활")]
last = max(f[3:11] for f in os.listdir(DATA) if f.startswith("경락_2026")); LAST = dt.date(int(last[:4]), int(last[4:6]), int(last[6:]))
D = dt.date.fromisoformat
W = [("11/2~11/7", "2026-11-02", "2026-11-07"), ("11/9~11/14", "2026-11-09", "2026-11-14"), ("11/16~11/21", "2026-11-16", "2026-11-21"), (f"11/23~{LAST.month}/{LAST.day}", "2026-11-23", str(LAST))]
weeks = []
for lab, a, b in W:
    g = N.agg_item(N.load(DATA, D(a), D(b))); weeks.append(dict(week=lab, items={f"{x}({y})": round(g[(x, y)]["med"]) for x, y in ITEMS if (x, y) in g}))
var = {}
for k in [f"{a}({b})" for a, b in ITEMS]:
    v = [w["items"][k] for w in weeks if k in w["items"]]; var[k] = round((max(v) - min(v)) / (sum(v) / len(v)) * 100, 1)
rows = N.load(DATA, D("2026-11-16"), LAST); g = N.agg_item(rows)
two = dict(week=f"11/16~{LAST.month}/{LAST.day}", days=sorted({r["날짜"] for r in rows}),
           items={f"{a}({b})": dict(med=round(g[(a, b)]["med"]), qty=round(g[(a, b)]["qty"], 1), lo=round(g[(a, b)]["lo"]), hi=round(g[(a, b)]["hi"])) for a, b in ITEMS if (a, b) in g})
json.dump(dict(two=two, weeks=weeks, var4=var, last=str(LAST)), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("최근 2주", two["week"], len(two["days"]), "일 |", " · ".join(f"{k} {v['med']:,}({v['qty']:,.0f}kg)" for k, v in two["items"].items()))
for w in weeks: print(w["week"], w["items"])
print("4주 변동폭 %", var)
