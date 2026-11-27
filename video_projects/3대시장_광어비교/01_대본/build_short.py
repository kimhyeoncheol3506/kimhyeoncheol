# -*- coding: utf-8 -*-
"""3대시장 광어 쇼츠 3편 → short1~3.json"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__)); G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S = G["S"]
P, PJ, PC, GAP, RX, C40, C50 = G["P"], G["PJ"], G["PC"], G["GAP"], G["RX"], G["C40"], G["C50"]
def make(name, hook, items):
    SS, C = [], {}
    for t, k, c in items: SS.append(S(t, c=k)); C[k] = c
    json.dump(dict(title=name, hook=hook, cards=C, sections=[dict(id=name, kind="short", name=name, sentences=SS)]), open(f"{HERE}/{name}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("==", name); [print(x[2]) for x in SS]
make("short1", f"광어 1kg<br>{RX:g}배 차이", [
  (f"같은 광어 일 킬로그램, 산지 따라 최대 {{e:{GAP}}} 차이 납니다.", "q", dict(kick="노량진 활광어 kg당 경락가", big=f"{GAP:,}원<br>차이", size=170)),
  (f"제주산은 킬로그램당 {{e:{PJ}}}.", "a", dict(kick="제주산 · 최근 2주", big=f"{PJ:,}원", size=190)),
  (f"전체 평균은 킬로그램당 {{e:{P}}}이었는데요.", "b0", dict(kick="노량진 활광어 평균 · 최근 2주", big=f"{P:,}원", size=190)),
  (f"중국산은 {{e:{PC}}}이었어요.", "b", dict(kick="중국산 · 최근 2주", big=f"{PC:,}원", size=190)),
  (f"약 {{x:{RX}}}. 노량진 새벽 경매 경락가예요.", "c", dict(t="vs", kick="kg당 경락가", a=["제주산", f"{PJ:,}원", "#F1D9A0"], b=["중국산", f"{PC:,}원", "#5FB7A6"])),
  ("가락시장 활광어 경락가는 공개 자료에서 찾지 못했어요.", "d", dict(kick="가락시장 · 소래포구", big="공개 시세<br>확인 못 함", size=130)),
  ("소래포구도 공개 경매 시세는 없어서, 가게마다 값이 달라요.", "d2", dict(kick="소래포구", big="가게마다<br>다른 값", size=150)),
  ("그래서 원산지 표시가 제일 중요합니다.".replace("그래서 ", "따라서 "), "e", dict(kick="살 때 확인", big="원산지 표시", size=170)),
  ("여러분은 광어 살 때 원산지 확인하시나요?", "ask", dict(t="ask", q="광어 원산지<br>확인하시나요?"))])
make("short2", "소래포구<br>확인할 3가지", [
  ("소래포구 가기 전에 이 세 가지만 확인하세요.", "q", dict(kick="소래포구에서 꼭", big="3가지", size=240)),
  ("첫째, 원산지 표시. 광어는 산지 따라 세 배 넘게 차이 나요.", "a", dict(kick="① 원산지", big="국산 · 중국산", size=150)),
  ("둘째, 저울이 영점인지, 기울지 않았는지 보세요.", "b", dict(kick="② 저울", big="영점 · 수평", size=170)),
  ("셋째, 회 뜨기 전 살아 있을 때 무게를 확인하세요.", "c", dict(kick="③ 손질 전 무게", big="생물 무게 먼저", size=150)),
  ("이천이십사년 저울 점검에선 이백구십여 곳 중 아홉 곳이 불합격이었어요.", "d", dict(kick="2024년 3월 (서울신문)", big="290여 곳 중<br>9곳 불합격", size=130)),
  ("올해 십일월 이십사일엔 남동구가 민관 합동점검을 했고, 성수기엔 매달 점검한대요.", "d2", dict(kick="인천 남동구 · 11/24", big="성수기<br>매달 점검", size=160)),
  ("이만 원 이상 사면 주차 두 시간 무료, 주차증 꼭 챙기세요.", "e", dict(kick="소래포구종합어시장 안내", big="2만 원↑<br>2시간 무료", size=140)),
  ("여러분은 소래포구에서 어떤 걸 확인하세요?", "ask", dict(t="ask", q="소래포구<br>뭘 확인하세요?"))])
make("short3", "회 100g<br>원가 얼마?", [
  ("광어 일 킬로그램 사서 회 뜨면, 몇 그램 나올까요?", "q", dict(kick="광어 1kg → 회", big="400~500g", size=160)),
  ("수율 사십에서 오십 퍼센트, 회는 사백에서 오백 그램이에요.", "a", dict(kick="광어 수율", big="40~50%", size=220)),
  (f"노량진 경락가 킬로그램당 {{e:{P}}}으로 계산하면.", "b", dict(kick="노량진 활광어 · 최근 2주", big=f"kg {P:,}원", size=170)),
  (f"회 백 그램 원가는 {{e:{C50}}}에서 {{e:{C40}}}입니다.", "c", dict(kick="회 100g당 도매 원가", big=f"{C50:,}~<br>{C40:,}원", size=150)),
  (f"제주산이면 백 그램에 {{e:{G['CJ40']}}}, 중국산이면 {{e:{G['CC40']}}}이에요.", "c2", dict(t="vs", kick="회 100g 원가 (수율 40%)", a=["제주산", f"{G['CJ40']:,}원", "#F1D9A0"], b=["중국산", f"{G['CC40']:,}원", "#5FB7A6"])),
  ("여기에 상차림비가 붙어요. 후기 기준 한 사람에 삼천 원에서 오천 원.", "d", dict(kick="상차림비 (후기 기준)", big="1인<br>3천~5천 원", size=150)),
  ("원가를 알고 가면 값이 적당한지 바로 보여요.", "g", dict(t="warn")),
  ("여러분은 광어 회 백 그램, 얼마면 적당하다고 보세요?", "ask", dict(t="ask", q="회 100g<br>얼마면 적당?"))])
