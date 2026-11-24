# -*- coding: utf-8 -*-
"""킹크랩 무게 속임수 — 이번 주(11/23~마지막 수집일) 활킹크랩((활)왕게) kg당 경락가, kg 경매 수량 가중 중앙값 → prices.json
자료: 노량진수산(주) 어종별 경락시세(일별 수집본, StarRate1214/smart-noryangjin data/daily)"""
import datetime as dt, json, os, sys
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/scripts")
import noryangjin_prices as N
DATA = "/home/user/kimhyeoncheol/video_projects/주간시세_리포트/data"
a = dt.date(2026, 11, 23); b = max(dt.date.fromisoformat(f[3:11][:4] + "-" + f[7:9] + "-" + f[9:11]) for f in os.listdir(DATA) if f.startswith("경락_2026"))
rows = N.load(DATA, a, b); g = N.agg_item(rows)[("왕게", "활")]
lw = N.agg_item(N.load(DATA, dt.date(2026, 11, 16), dt.date(2026, 11, 21)))[("왕게", "활")]
days = sorted({r["날짜"] for r in rows if N.item_name(r["어종"]) == ("왕게", "활")})
out = dict(week=f"{a.month}/{a.day}~{b.month}/{b.day}", start=str(a), end=str(b), days=days, med=round(g["med"]), qty=round(g["qty"], 1), lo=g["lo"], hi=g["hi"], last_week=round(lw["med"]))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1); print(out)
