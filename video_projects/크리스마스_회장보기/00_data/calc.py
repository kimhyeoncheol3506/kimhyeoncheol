# -*- coding: utf-8 -*-
"""크리스마스·연말 회 장보기 — 광어·참돔·농어(활) kg당 경락가(kg 경매 수량 가중 중앙값) 주별 → prices.json
올해: 최근 4주(변동폭 규칙) + 최근 2주(11/16~11/28). 작년: 2025년 11월 마지막 주 + 12월 주별(월~토, 일별 수집본 전체 날짜).
자료: 노량진수산(주) 어종별 경락시세(일별 수집본)"""
import datetime as dt, json, os, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/scripts")
import noryangjin_prices as N
DATA = "/home/user/kimhyeoncheol/video_projects/주간시세_리포트/data"
ITEMS = [("넙치", "활"), ("참돔", "활"), ("농어", "활"), ("우럭", "활"), ("방어", "활")]
last = max(f[3:11] for f in os.listdir(DATA) if f.startswith("경락_2026")); LAST = dt.date(int(last[:4]), int(last[4:6]), int(last[6:]))
W = [("11/2~11/7", "2026-11-02", "2026-11-07"), ("11/9~11/14", "2026-11-09", "2026-11-14"), ("11/16~11/21", "2026-11-16", "2026-11-21"), (f"11/23~{LAST.month}/{LAST.day}", "2026-11-23", str(LAST)),
     ("작년 11/24~11/29", "2025-11-24", "2025-11-29"), ("작년 12/1~12/6", "2025-12-01", "2025-12-06"), ("작년 12/8~12/13", "2025-12-08", "2025-12-13"), ("작년 12/15~12/20", "2025-12-15", "2025-12-20"),
     ("작년 12/22~12/27", "2025-12-22", "2025-12-27"), ("작년 12/29~12/31", "2025-12-29", "2025-12-31")]
D = dt.date.fromisoformat; out = []
for lab, a, b in W:
    rows = N.load(DATA, D(a), D(b)); g = N.agg_item(rows); w = dict(week=lab, start=a, end=b, days=sorted({r["날짜"] for r in rows}), items={})
    for k in ITEMS:
        if k in g: w["items"][f"{k[0]}({k[1]})"] = dict(med=round(g[k]["med"]), qty=round(g[k]["qty"], 1), days=g[k]["days"])
    out.append(w)
var = {}
for k in [f"{a}({b})" for a, b in ITEMS]:
    v = [w["items"][k]["med"] for w in out[:4] if k in w["items"]]; var[k] = round((max(v) - min(v)) / (sum(v) / len(v)) * 100, 1)
rows = N.load(DATA, D("2026-11-16"), LAST); g = N.agg_item(rows)
two = dict(week=f"11/16~{LAST.month}/{LAST.day}", days=sorted({r["날짜"] for r in rows}), items={f"{a}({b})": dict(med=round(g[(a, b)]["med"]), qty=round(g[(a, b)]["qty"], 1)) for a, b in ITEMS if (a, b) in g})
print("최근 2주", two["week"], len(two["days"]), "일 |", " · ".join(f"{k} {v['med']:,}" for k, v in two["items"].items()))
daily = []
for d in range(22, 28):
    day = dt.date(2025, 12, d); g = N.agg_item(N.load(DATA, day, day))
    daily.append(dict(date=str(day), dow="월화수목금토"[day.weekday()], items={f"{a}({b})": dict(med=round(g[(a, b)]["med"]), qty=round(g[(a, b)]["qty"])) for a, b in ITEMS[:3] if (a, b) in g}))
json.dump(dict(weeks=out, two=two, daily=daily, var4=var, last=str(LAST)), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for w in out: print(w["week"], len(w["days"]), "일 |", " · ".join(f"{k} {v['med']:,}({v['qty']:,.0f})" for k, v in w["items"].items()))
print("4주 변동폭 %", var)
