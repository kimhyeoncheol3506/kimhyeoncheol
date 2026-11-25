# -*- coding: utf-8 -*-
"""김장배추 쇼츠 1편 → short1.json — 숫자는 build_data와 같은 표. sig c=카드 이름"""
import json, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(f"{HERE}/build_data.py", run_name="short"); S, B26, B25, BM26, H10, W10, AT20 = (G[k] for k in ("S", "B26", "B25", "BM26", "H10", "W10", "AT20"))
SS = [S("배추 한 포기, 가락시장 경매가로 얼마일까요?", c="q"),
      S(f"중품은 약 {{e:{int(round(BM26, -2))}}}, 상품도 약 {{e:{int(round(B26, -2))}}}.", c="b"),
      S(f"작년 상품은 약 {{e:{int(round(B25, -2))}}}. 거의 반값이에요.", c="ly"),
      S("하지만 김장비는 배추에서 갈리지 않아요.", c="but"),
      S(f"열 포기 김장에 고춧가루만 약 {{p:{int(H10['고춧가루'])}}}.", c="chili"),
      S(f"배추 열 포기 값, 약 {{p:{int(H10['배추'])}}}보다 비쌉니다.", c="vs"),
      S("새우젓은 사십 점 이 퍼센트, 깐마늘은 이십일 점 육 퍼센트 올랐어요.", c="up"),
      S(f"열 포기 김장 재료비는 약 {{p:{int(AT20 / 2)}}}입니다.", c="total"),
      S("도매가와 aT 조사 기준이라, 동네 가게 값과는 달라요.", c="warn"),
      S("여러분은 올해 김장, 몇 포기 하세요?", c="ask")]
json.dump(dict(title="short1", hook="배추 한 포기<br>1000원대?", sections=[dict(id="short1", kind="short", name="short1", sentences=SS)]), open(f"{HERE}/short1.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for x in SS: print(x[2])
