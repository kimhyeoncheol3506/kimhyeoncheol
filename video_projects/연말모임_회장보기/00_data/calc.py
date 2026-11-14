# -*- coding: utf-8 -*-
"""연말 모임 회 장보기 — 노량진 경락시세에서 횟감 kg당 도매가(수량 가중 중앙값) 주별 계산 → prices.json
최근 4주(10/19~11/14, 월~토) + 작년 12월 주별 표본(월·화 이틀씩). 방어는 전체(활) + 규격 '1미'(대방어) 따로."""
import datetime as dt, json, sys
from collections import defaultdict
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/scripts")
import noryangjin_prices as N
DATA = "/home/user/kimhyeoncheol/video_projects/주간시세_리포트/data"
ITEMS = [("넙치", "활"), ("참돔", "활"), ("방어", "활"), ("우럭", "활"), ("농어", "활"), ("연어", "선"), ("연어", "활")]
WEEKS = [("10/19~10/24", "2026-10-19", "2026-10-24"), ("10/26~10/31", "2026-10-26", "2026-10-31"), ("11/2~11/7", "2026-11-02", "2026-11-07"), ("11/9~11/14", "2026-11-09", "2026-11-14"),
         ("작년 12/1~12/2", "2025-12-01", "2025-12-02"), ("작년 12/8~12/9", "2025-12-08", "2025-12-09"), ("작년 12/15~12/16", "2025-12-15", "2025-12-16"),
         ("작년 12/22~12/23", "2025-12-22", "2025-12-23"), ("작년 12/29~12/30", "2025-12-29", "2025-12-30")]
D = lambda s: dt.date.fromisoformat(s)


def mi1(rows):  # 방어 규격 1미, kg 경매
    pq = [(N.num(r["평균가"]), N.num(r["수량"])) for r in rows if N.item_name(r["어종"]) == ("방어", "활") and r["규격"].strip() == "1미" and r["포장"].strip().lower() == "kg" and N.num(r["수량"]) > 0 and N.num(r["평균가"]) > 0]
    return dict(med=N.wmedian(pq), qty=sum(q for _, q in pq), n=len(pq)) if pq else None


out = []
for lab, a, b in WEEKS:
    rows = N.load(DATA, D(a), D(b)); days = sorted({r["날짜"] for r in rows}); g = N.agg_item(rows); w = dict(week=lab, days=days, items={})
    for k in ITEMS:
        if k in g: w["items"][f"{k[0]}({k[1]})"] = dict(med=round(g[k]["med"]), qty=round(g[k]["qty"], 1), days=g[k]["days"], lo=g[k]["lo"], hi=g[k]["hi"])
    m = mi1(rows)
    if m: w["items"]["대방어(방어 1미)"] = dict(med=round(m["med"]), qty=round(m["qty"], 1))
    out.append(w)
json.dump(out, open(__file__.replace("calc.py", "prices.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for w in out:
    print(w["week"], len(w["days"]), "일 |", " · ".join(f"{k} {v['med']:,}({v['qty']:,.0f}kg)" for k, v in w["items"].items()))
