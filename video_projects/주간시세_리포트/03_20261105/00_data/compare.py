# -*- coding: utf-8 -*-
"""이번 주(월~목) vs 지난주 같은 요일 비교 — noryangjin_prices.agg_item(kg 경매, 품목+상태, 수량 가중 중앙값) 재사용"""
import datetime as dt, json, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/scripts")
import noryangjin_prices as N
DATA = "/home/user/kimhyeoncheol/video_projects/주간시세_리포트/data"
A0, A1 = dt.date.fromisoformat(sys.argv[1]), dt.date.fromisoformat(sys.argv[2])
B0, B1 = A0 - dt.timedelta(days=7), A1 - dt.timedelta(days=7)
this, last = N.agg_item(N.load(DATA, A0, A1)), N.agg_item(N.load(DATA, B0, B1))
ndays = len({r["날짜"] for r in N.load(DATA, A0, A1)})
MINQ, MIND = 60, 2
res = []
for k, a in this.items():
    b = last.get(k)
    if not b or a["qty"] < MINQ or b["qty"] < MINQ / 2 or a["days"] < MIND or b["days"] < MIND: continue
    res.append(dict(품목=k[0], 상태=k[1], 이번=round(a["med"]), 지난=round(b["med"]), 변동=round((a["med"] / b["med"] - 1) * 100, 1), 이번물량=round(a["qty"]), 지난물량=round(b["qty"]),
                    거래일=a["days"], 범위=f"{a['lo']:,.0f}~{a['hi']:,.0f}", 산지="/".join(a["origins"][:5])))
res.sort(key=lambda r: r["변동"])
tq, lq = sum(v["qty"] for v in this.values()), sum(v["qty"] for v in last.values())
json.dump(dict(this=[str(A0), str(A1)], last=[str(B0), str(B1)], days=ndays, total_this=round(tq), total_last=round(lq), rows=res), open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"이번 {A0}~{A1}({ndays}일) vs {B0}~{B1} · 비교 {len(res)}품목 · 내림 {sum(r['변동'] < 0 for r in res)} 오름 {sum(r['변동'] > 0 for r in res)} · 물량 {tq:,.0f} vs {lq:,.0f}")
for r in res[:14]: print(f"  ↓ {r['품목']}({r['상태']}) {r['지난']:,}→{r['이번']:,} {r['변동']:+.1f}% {r['이번물량']:,}kg {r['거래일']}일 [{r['범위']}] {r['산지']}")
for r in res[-7:][::-1]: print(f"  ↑ {r['품목']}({r['상태']}) {r['지난']:,}→{r['이번']:,} {r['변동']:+.1f}% {r['이번물량']:,}kg {r['거래일']}일 [{r['범위']}] {r['산지']}")
