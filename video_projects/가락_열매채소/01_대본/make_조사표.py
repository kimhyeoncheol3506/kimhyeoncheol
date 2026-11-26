# -*- coding: utf-8 -*-
"""조사표.md = garak.csv에서 이 편 품목의 올해·작년 등급·상자별 평균(반올림 전) + 계산 + topic.json의 출처 자료"""
import json, os, runpy
H = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{H}/build_data.py", run_name="short"); CFG, INFO, R, st_ = G["CFG"], G["INFO"], G["R"], G["st_"]
L = [f"# 조사표 — {CFG['title']}", "", "## 가락시장 경락가 (KAMIS 도매가격(가락시장 경락가격)) — 올해 2026.11.12~11.26 · 작년 2025.11.12~11.26 일별 평균가의 평균"]
its = {v["kamis"] for v in INFO.values()}
for (y, it, u, g) in sorted(k for k in R if k[1] in its):
    s = st_(y, it, u, g)
    if not s: L.append(f"- {y} | {it} | {u} | {g}: 매일 같은 값 → 제외"); continue
    L.append(f"- {y} | {it} | {u} | {g}: 평균 {s['avg']:,}원 · {s['days']}일 · 최고 {s['hi'][0]} {s['hi'][1]:,} · 최저 {s['lo'][0]} {s['lo'][1]:,}")
L += ["", "## 계산 (반올림 전)"]
for n, v in INFO.items():
    if not v["t"]: continue
    L.append(f"- {n} {v['unit']} 상: 올해 {v['t']['avg']:,} · kg당 {v['t']['avg'] / v['kg']:,.1f} (100원 단위 {int(round(v['t']['avg'] / v['kg'], -2)):,})" + (f" · 작년 {v['l']['avg']:,} · 변화 {(v['t']['avg'] - v['l']['avg']) / v['l']['avg'] * 100:.1f}%" if v["l"] else " · 작년 비교 없음"))
    for g, s in v["grades"].items():
        if s: L.append(f"  - {g}: {s['avg']:,} · kg당 {s['avg'] / v['kg']:,.1f} (100원 단위 {int(round(s['avg'] / v['kg'], -2)):,})" + (f" · 작년 {v['lgrades'][g]['avg']:,} · 변화 {(s['avg'] - v['lgrades'][g]['avg']) / v['lgrades'][g]['avg'] * 100:.1f}%" if v['lgrades'].get(g) else ""))
    for u, s in v["units"].items():
        if s: L.append(f"  - 상자 {u} 상: {s['avg']:,} · kg당 {s['avg'] / G['kgof'](u):,.1f} (100원 단위 {int(round(s['avg'] / G['kgof'](u), -2)):,}) · {s['days']}일")
    if v["grades"].get("특") and v["grades"].get("하"): L.append(f"  - 특÷하 {v['grades']['특']['avg'] / v['grades']['하']['avg']:.2f}")
    t = v["t"]; L.append(f"  - 최고−최저 {t['hi'][1] - t['lo'][1]:,} ÷ 평균 = {(t['hi'][1] - t['lo'][1]) / t['avg'] * 100:.1f}%")
us = G.get("US") or {}
if len(us) >= 2:
    ul = sorted(us, key=G["kgof"]); a, b = ul[0], ul[-1]; pa, pb = us[a]["avg"] / G["kgof"](a), us[b]["avg"] / G["kgof"](b); L.append(f"- 상자 비교 {a} vs {b}: kg당 {pa:,.1f} vs {pb:,.1f} · 차이 {(pa - pb) / pb * 100:.1f}% (반올림 {abs(round((pa - pb) / pb * 100))}%)")
# 반올림·계산값 (자막에 쓰이는 형태)
for n in G["NAMES"]:
    y = G["yoy"](n)
    if y is not None: L.append(f"- {n} 작년 대비 반올림 {y}% ({abs(y)})")
    g = INFO[n]["grades"]; gk = [x for x in ["특", "상", "중", "하"] if g.get(x)]
    if len(gk) >= 2: L.append(f"- {n} {gk[0]}÷{gk[-1]} 반올림 {round(g[gk[0]]['avg'] / g[gk[-1]]['avg'], 1)}배")
    if g.get("상") and g.get("중"): L.append(f"- {n} 상−중 {g['상']['avg'] - g['중']['avg']:,} (100원 단위 {int(round(g['상']['avg'] - g['중']['avg'], -2)):,}) · {(g['상']['avg'] - g['중']['avg']) / g['상']['avg'] * 100:.1f}% (반올림 {round((g['상']['avg'] - g['중']['avg']) / g['상']['avg'] * 100)})")
for n, pc, a1, a2 in (G.get("WK") or []): L.append(f"- 주간 {n}: 지난주 {a1:,.0f} (100원 단위 {int(round(a1, -2)):,}) → 이번 주 {a2:,.0f} ({int(round(a2, -2)):,}) · {pc}% ({abs(pc)})")
for sec in G["SECS"]:
    if sec["id"].startswith("years"):
        for r in sec["vis"]["rows"]: L.append(f"- 연도표 {sec['name']}: {r[0]} {r[2][0][0]} {r[2][1][0]} {r[2][2][0]}")
for sec in G["SECS"]:
    for x in sec["sentences"]:
        if "앞선 해들의 평균" in x[2]: L.append("- 5년 평균 대비: " + x[2])
L += ["- 기타 수치: 2주 · 11월 12일 26일 · 5일 · 1kg · 3가지 5가지 · STEP 1 2 3", "", "## 출처 자료 (topic.json facts)"] + [f"- {x}" for x in CFG.get("sources", [])]
L += ["", "- 원문 표기 대조: " + CFG.get("num_note", "")]
IDX = {l.split()[-1]: l.split()[0] for l in open("/home/user/kimhyeoncheol/video_projects/가락시장_시리즈/00_자료/index.txt", encoding="utf-8") if len(l.split()) >= 2}
for src in CFG.get("sources", []):
    u = src.split()[-1]
    if u in IDX and os.path.exists(f"/home/user/kimhyeoncheol/video_projects/가락시장_시리즈/00_자료/{IDX[u]}.txt"):
        L += ["", f"## 원문 · {src}", open(f"/home/user/kimhyeoncheol/video_projects/가락시장_시리즈/00_자료/{IDX[u]}.txt", encoding="utf-8").read()[:15000]]
open(f"{H}/조사표.md", "w", encoding="utf-8").write("\n".join(L)); print("ok")
