# -*- coding: utf-8 -*-
"""티저 쇼츠 2편 대본 → short1.json, short2.json (build_data.py의 숫자 표기·자막 규칙 그대로)"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
S = runpy.run_path(f"{HERE}/build_data.py", run_name="shorts")["S"]
SH = {
 "short1": [S("노량진에서 광어 일 킬로그램, 한 사람은 {p:27310}, 한 사람은 {p:4330}을 냈습니다.", k=1),
            S("둘 다 같은 {mi:4} 광어인데, 차이는 {x:6.3}입니다.", k=2),
            S("하나는 활어, 하나는 선어였어요. 노량진수산 도매 경락가 기준이에요.", k=3),
            S("선어는 나쁜 물건이 아니라, 등급과 용도가 다른 물건입니다. 회는 활어, 구이나 탕은 선어가 가성비죠.", k=4),
            S("가게 판매가와는 다른 도매가 기준이에요. 값을 가르는 세 가지 기준, 관련 영상에서 확인하세요.", k=5)],
 "short2": [S("제주 광어가 비쌀까요, 완도 광어가 비쌀까요?", k=1),
            S("노량진 도매 경락가로 {mi:4} 광어를 비교하면, 제주산 {p:27860}, 완도산 {p:27950}입니다.", k=2),
            S("차이는 킬로그램당 {e:90}, 사실상 같은 값이었어요.", k=3),
            S("반면 안흥산은 {p:14080}으로, 제주산과 거의 두 배 차이가 났습니다. 원인은 이 데이터만으로는 알 수 없어요.", k=4),
            S("구월부터 십일월 초까지의 도매가 기준이에요. 전체 분석은 관련 영상에서 확인하세요.", k=5)]}
for n, ss in SH.items():
    json.dump(dict(title=n, sections=[dict(id=n, kind="short", name=n, sentences=ss)]), open(f"{HERE}/{n}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(n, sum(len(x[0].replace(" ", "")) for x in ss), "자", [x[2] for x in ss])
