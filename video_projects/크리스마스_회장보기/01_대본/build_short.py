# -*- coding: utf-8 -*-
"""크리스마스·연말 회 장보기 티저 쇼츠 → short1.json — 숫자는 build_data와 같은 표"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S, B10, DF = G["S"], G["B10"], G["DIFF10"]; BIG, SMALL = G["BIG"], G["SMALL"]
SS = [S("크리스마스 주에 회를 사면, 십이월 첫 주보다 얼마나 더 낼까요?", k=1),
      S(f"작년 노량진 경락가로 열 명이 {BIG}로만 먹으면, 첫 주 약 {{p:{int(B10[BIG][0])}}}, 크리스마스 주 약 {{p:{int(B10[BIG][1])}}}.", k=2),
      S(f"약 {{p:{int(DF[BIG])}}}을 더 냈어요. {SMALL}는 차이가 약 {{p:{int(DF[SMALL])}}}으로 가장 작았습니다.", k=3),
      S(f"올해 지금 경락가로는, 열 명 농어 오 킬로그램이 약 {{p:{int(G['BUD']('농어', 10, G['T']['농어']))}}}이에요. 광어는 작년보다 비싸요.", k=3),
      S("활어는 미리 사 두는 게 아니라, 언제 사러 갈지가 핵심이에요. 인원별 예산은 관련 영상에서 보세요.", k=4)]
json.dump(dict(title="short1", sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
