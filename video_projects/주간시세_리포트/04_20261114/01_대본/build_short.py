# -*- coding: utf-8 -*-
"""주간 시세 티저 쇼츠 1편 → short1.json ([음성, {k}, 자막]) — 숫자는 비교.json 값만"""
import json, os, re, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short")
T, DM = G["T"], G["DM"]
SS = [("이번 주 노량진에서 가장 많이 싸진 건, 부시리였습니다.", 1),
      ("킬로그램당 {p:7500}에서 {p:5100}으로, {pc:32} 내렸고, 리포트 네 번 연속 하락이에요.", 2),
      ("이위부터 오위는 선어 광어, 대구, 홍어, 아귀. 겨울 선어가 줄줄이 내렸죠.", 3),
      ("반대로 킹크랩 선어, 줄전갱이, 수꽃게는 올랐습니다.", 4),
      ("도매 경락가 기준이에요. 매주 토요일 노량진 시세, 전체는 관련 영상에서 확인하세요.", 5)]
dm = sorted(DM.items(), key=lambda x: -len(x[0])); rx = re.compile("|".join(re.escape(a) for a, _ in dm)); mp = dict(dm)
out = []
for t, k in SS:
    a = T(t); out.append([a, {"k": k}, rx.sub(lambda m: mp[m.group(0)], a)])
json.dump(dict(title="short1", sections=[dict(id="short1", kind="short", name="short1", sentences=out)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in out: print(x[2])
