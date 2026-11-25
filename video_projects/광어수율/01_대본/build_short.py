# -*- coding: utf-8 -*-
"""광어 수율 쇼츠 3편(A/B용, 같은 데이터·다른 훅) → short1.json·short2.json·short3.json — 숫자는 build_data와 같은 표
sig: c=카드 이름, fx={애니메이션 단계: 문장 안 비율}"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S, T, C100, SUB4 = G["S"], G["T"], G["C100"], G["SUB4"]
SH = {
 "short1": dict(hook="광어 1kg<br>= 회 400g?", s=[
  S("광어 일 킬로그램 사면, 회는 몇 그램일까요?", c="fish", fx={"show": 0.0}),
  S("머리 떼고,", fx={"head": 0.0}),
  S("뼈와 지느러미 빼고,", fx={"bone": 0.0}),
  S("껍질과 내장까지 걷어 내면,", fx={"skin": 0.0}),
  S("남는 회는 약 {g:400}.", fx={"plate": 0.0}),
  S("자료마다 사십에서 오십 퍼센트, 그 낮은 쪽이에요.", c="range"),
  S(f"노량진 도매 경락가로 광어는 킬로그램당 {{e:{T['광어']}}}.", c="price"),
  S(f"회 {{g:400}}에 {{e:{T['광어']}}}이니,", c="div"),
  S(f"회 백 그램당 도매 원가는 약 {{p:{int(C100('광어'))}}}.", c="c100"),
  S("가게 값이 아니라, 새벽 경매 도매가예요.", c="warn"),
  S("횟집 회 한 접시, 여러분은 얼마가 맞다고 보세요?", c="ask")]),
 "short2": dict(hook="회 한 접시<br>= 광어 몇 마리?", s=[
  S("네 명이 먹을 회 한 상, 광어 몇 마리면 될까요?", c="q4"),
  S("한 사람이 먹는 회는 보통 {g:200}.", c="p200"),
  S("네 명이면 회 {g:800}이에요.", c="p800"),
  S("광어 일 킬로그램을 사면,", c="fish", fx={"show": 0.0}),
  S("머리, 뼈, 껍질, 내장이 빠지고,", fx={"head": 0.0, "bone": 0.3, "skin": 0.6}),
  S("회는 약 {g:400}만 남아요.", fx={"plate": 0.0}),
  S("결국 광어 {k:2}, 일 킬로그램짜리라면 두 마리입니다.", c="two"),
  S(f"노량진 도매 경락가로 약 {{p:{int(SUB4)}}}.", c="won"),
  S("큰 광어일수록 회가 더 나오는 편이라, 마리 수는 줄 수 있어요.", c="big"),
  S("여러분 모임엔 광어 몇 마리 잡으세요?", c="ask")]),
 "short3": dict(hook="참돔 1kg<br>= 회 300g", s=[
  S("참돔은 일 킬로그램 사면, 회가 약 {g:300}입니다.", c="fish", fx={"show": 0.0, "head": 0.25, "bone": 0.42, "skin": 0.58, "plate": 0.75}),
  S("광어는 {g:400}인데, 참돔은 왜 적을까요?", c="vsg"),
  S("자료마다 수율이 삼십에서 사십 퍼센트로, 광어보다 낮아요.", c="range"),
  S("대신 값은 참돔이 쌉니다.", c="cheap"),
  S(f"킬로그램당 참돔 {{e:{T['참돔']}}}, 광어 {{e:{T['광어']}}}.", c="vsp"),
  S("회 백 그램으로 바꾸면요?", c="q"),
  S(f"참돔 약 {{p:{int(C100('참돔'))}}}, 광어도 약 {{p:{int(C100('광어'))}}}.", c="vsc"),
  S("킬로그램 값은 달라도, 회 값은 거의 같습니다.", c="same"),
  S("노량진 도매 경락가 기준이라, 가게 값과는 달라요.", c="warn"),
  S("횟집에서 한 접시 고른다면, 광어와 참돔 중 뭘 고르시겠어요?", c="ask")])}
for nm, v in SH.items():
    json.dump(dict(title=nm, hook=v["hook"], sections=[dict(id=nm, kind="short", name=nm, sentences=v["s"])]), open(f"{HERE}/{nm}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(nm, "|", " / ".join(x[2] for x in v["s"]))
