# -*- coding: utf-8 -*-
"""주간 시세 티저 쇼츠 1편 → short1.json ([음성, {k}, 자막]) — 숫자는 비교.json 값만"""
import json, os, re, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short")
T, DM = G["T"], G["DM"]
SS = [("이번 주 노량진에서 가장 많이 싸진 건, 활우럭이었습니다.", 1),
      ("킬로그램당 {p:28800}에서 {p:18700}으로, {pc:35} 내렸어요.", 2),
      ("이위부터 오위는 선어 대게, 방어, 도다리, 선어 광어. 겨울 횟감이 줄줄이 내렸죠.", 3),
      ("반대로 네 번 연속 싸졌던 부시리는 {pc:70} 올랐고, 삼치와 킹크랩도 올랐습니다.", 4),
      ("도매 경락가 기준이에요. 매주 토요일 노량진 시세, 전체는 관련 영상에서 확인하세요.", 5)]
dm = sorted(DM.items(), key=lambda x: -len(x[0])); rx = re.compile("|".join(re.escape(a) for a, _ in dm)); mp = dict(dm)
out = []
for t, k in SS:
    a = T(t); out.append([a, {"k": k}, rx.sub(lambda m: mp[m.group(0)], a)])
json.dump(dict(title="short1", sections=[dict(id="short1", kind="short", name="short1", sentences=out)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in out: print(x[2])
