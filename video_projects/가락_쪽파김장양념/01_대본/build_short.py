# -*- coding: utf-8 -*-
"""가락시장 시리즈 쇼츠 1편 → short1.json (문장 + 화면 카드) — 숫자는 build_data와 같은 표"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S, CFG, M, MI, INFO, NAMES, perkg, yoy, r100, uname, K_, kgof, dec = (G[k] for k in ("S", "CFG", "M", "MI", "INFO", "NAMES", "perkg", "yoy", "r100", "uname", "K_", "kgof", "dec"))
SS, C = [], {}
def add(text, key, card): SS.append(S(text, c=key)); C[key] = card
t = MI["t"]; GR = MI["grades"]; y = yoy(M)
add(CFG["short_q"], "q", dict(big=f"{M} ?원", small="가락시장 경매가", size=150))
add(f"가락시장 경락가로 {M} {K_(MI['unit'])} 상자 상품이 평균 {{e:{t['avg']}}}.", "b", dict(kick=f"{M} {uname(MI['unit'])} 상품 · 최근 2주", big=f"{t['avg']:,}원", small=f"kg당 약 {r100(perkg(M)):,}원"))
if y is not None: add(f"작년 같은 때보다 약 {{pc:{abs(y)}}} {'올랐어요' if y > 0 else '내렸어요'}.", "y", dict(kick="작년 같은 기간 대비", big=f"{y:+d}%", col="#E4775F" if y > 0 else "#5FB7A6", size=200))
if GR.get("특") and GR.get("하"):
    RT = round(GR["특"]["avg"] / GR["하"]["avg"], 1); G["SUBFIX"].append((f"{dec(str(RT))}배", f"{RT:g}배"))
    add(f"같은 상자라도 특품은 {{e:{GR['특']['avg']}}}, 하품은 {{e:{GR['하']['avg']}}}.", "g", dict(t="vs", kick="등급별 상자 값", a=["특품", f"{GR['특']['avg']:,}원", "#F1D9A0"], b=["하품", f"{GR['하']['avg']:,}원", "#5FB7A6"]))
    add(f"약 {dec(str(RT))}배 차이예요.", "r", dict(kick="특품 ÷ 하품", big=f"{RT:g}배", size=220))
if len(NAMES) > 1:
    ch = min(NAMES, key=perkg); de = max(NAMES, key=perkg)
    add(f"킬로그램당으로 보면 {de}는 약 {{e:{r100(perkg(de))}}}, {ch}는 약 {{e:{r100(perkg(ch))}}}.", "c", dict(t="vs", kick="kg당 상품 경락가", a=[de, f"{r100(perkg(de)):,}원", "#E4775F"], b=[ch, f"{r100(perkg(ch)):,}원", "#5FB7A6"]))
add("KAMIS 가락시장 경락가격에서 누구나 무료로 확인할 수 있어요.", "h", dict(kick="직접 확인", big="KAMIS<br>가락시장 경락가격", size=100))
add("새벽 경매 도매가 기준이라, 동네 가게 값과는 달라요.", "warn", dict(t="warn"))
add(CFG["short_ask"], "ask", dict(t="ask", q=CFG["short_ask_card"]))
json.dump(dict(title="short1", hook=CFG["short_hook"], cards=C, sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
