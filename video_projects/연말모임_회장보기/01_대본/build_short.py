# -*- coding: utf-8 -*-
"""연말 모임 회 장보기 티저 쇼츠 → short1.json ([음성, {k}, 자막]) — 숫자는 build_data와 같은 표·출처"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
S = runpy.run_path(f"{HERE}/build_data.py", run_name="short")["S"]
SS = [S("연말 모임 열 명, 회 몇 킬로그램 사야 할까요?", k=1),
      S("한 사람 회 {g:200}, 광어 수율을 사십 퍼센트로 잡으면, 활광어 {k:5}입니다.", k=2),
      S("이번 주 노량진 도매 경락가로 약 {p:148000}이에요.", k=3),
      S("같은 열 명이라도 농어로 하면 약 {p:85000}. 생선 조합이 예산을 가릅니다.", k=4),
      S("가게 판매가와는 다른 도매가 기준이에요. 인원별 표는 관련 영상에서 확인하세요.", k=5)]
json.dump(dict(title="short1", sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
