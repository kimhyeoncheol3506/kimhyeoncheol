# -*- coding: utf-8 -*-
"""대본 숫자 점검 (ranking-video v2.7.1): 자막에 나올 숫자가 조사표에 있는지 확인한다.

사용법: python3 -I check_numbers.py <대본데이터.json> <조사표.md>
대본의 display_map을 적용한 자막 문장에서 숫자를 뽑아 조사표 본문의 숫자와 비교한다.
조사표에 없는 숫자는 '출처 확인 필요'로 출력한다(종료 코드 1). 원칙: 출처에 없는 숫자는 쓰지 않는다.
"""
import json, re, sys

def nums(t): return {m.replace(",", "") for m in re.findall(r"\d[\d,]*(?:\.\d+)?", t)}

D = json.load(open(sys.argv[1], encoding="utf-8")); src = open(sys.argv[2], encoding="utf-8").read(); ok = nums(src)
dm = sorted(D.get("display_map", []), key=lambda x: -len(x[0]))
rx = re.compile("|".join(re.escape(a) for a, _ in dm)) if dm else None; mp = dict(dm)
bad = []
for s in D["sections"]:
    for i, x in enumerate(s["sentences"]):
        t = rx.sub(lambda m: mp[m.group(0)], x[0]) if rx else x[0]
        for n in nums(t):
            if n not in ok and not n.startswith("0"): bad.append((s["name"], i, n, t))
for c in D.get("graphics", {}).get("info_cards", []):
    for n in nums(" ".join(str(v) for k, v in c.items() if k in ("big", "caption", "tag", "title", "items") and isinstance(v, (str, list)) for v in ([v] if isinstance(v, str) else v))):
        if n not in ok and not n.startswith("0"): bad.append((c["section"], "card", n, c.get("big", c.get("title"))))
if bad:
    print("조사표에 없는 숫자:")
    for sec, i, n, t in bad: print(f"  [{sec} #{i}] {n}  ← {t}")
    sys.exit(1)
print("숫자 점검 통과 (모든 숫자가 조사표에 있음)")
