# -*- coding: utf-8 -*-
"""방어 대안 5가지 — 대방어(방어 활 '1미') vs 부시리·참돔·광어(넙치)·농어(활)·삼치(선) kg당 경락가(kg 경매 수량 가중 중앙값)
최근 2주(11/16~마지막 날) + 4주 주별 변동폭 + 작년 같은 시기. 자료: 노량진수산(주) 어종별 경락시세 일별 수집본"""
import datetime as dt, json, os, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/scripts")
import noryangjin_prices as N
DATA = "/home/user/kimhyeoncheol/video_projects/주간시세_리포트/data"; D = dt.date.fromisoformat
ITEMS = [("방어", "활"), ("부시리", "활"), ("참돔", "활"), ("넙치", "활"), ("농어", "활"), ("삼치", "선"), ("잿방어", "활"), ("흑점줄전갱이", "활"), ("참숭어", "활")]
last = max(f[3:11] for f in os.listdir(DATA) if f.startswith("경락_2026")); LAST = dt.date(int(last[:4]), int(last[4:6]), int(last[6:]))
def agg(a, b):
    rows = N.load(DATA, D(a) if isinstance(a, str) else a, D(b) if isinstance(b, str) else b); g = N.agg_item(rows)
    big = N.agg_item([r for r in rows if N.item_name(r["어종"]) == ("방어", "활") and r["규격"].strip() == "1미"])
    out = {f"{x}({y})": dict(med=round(v["med"]), qty=round(v["qty"], 1), lo=round(v["lo"]), hi=round(v["hi"]), days=v["days"]) for (x, y), v in g.items() if (x, y) in ITEMS}
    if ("방어", "활") in big: v = big[("방어", "활")]; out["대방어(1미)"] = dict(med=round(v["med"]), qty=round(v["qty"], 1), lo=round(v["lo"]), hi=round(v["hi"]), days=v["days"])
    return out, sorted({r["날짜"] for r in rows})
W = [("11/2~11/7", "2026-11-02", "2026-11-07"), ("11/9~11/14", "2026-11-09", "2026-11-14"), ("11/16~11/21", "2026-11-16", "2026-11-21"), (f"11/23~{LAST.month}/{LAST.day}", "2026-11-23", str(LAST))]
weeks = [dict(week=l, items=agg(a, b)[0]) for l, a, b in W]
var = {}
for k in weeks[-1]["items"]:
    v = [w["items"][k]["med"] for w in weeks if k in w["items"]]
    if len(v) >= 3: var[k] = round((max(v) - min(v)) / (sum(v) / len(v)) * 100, 1)
two, days = agg("2026-11-16", LAST); ly, ldays = agg("2025-11-17", "2025-11-29")
json.dump(dict(two=dict(week=f"11/16~{LAST.month}/{LAST.day}", days=days, items=two), weeks=weeks, var4=var, lastyear=dict(week="작년 11/17~11/29", days=ldays, items=ly), last=str(LAST)),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("최근 2주", len(days), "일")
for k, v in sorted(two.items(), key=lambda x: -x[1]["med"]): print(f"  {k}: {v['med']:,} ({v['qty']:,}kg, {v['days']}일, {v['lo']:,}~{v['hi']:,}) 변동 {var.get(k)}% · 작년 {ly.get(k, {}).get('med', '-')}")
for w in weeks: print(w["week"], {k: v["med"] for k, v in w["items"].items()})
