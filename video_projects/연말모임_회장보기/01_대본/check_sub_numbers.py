# -*- coding: utf-8 -*-
"""자막 숫자 ↔ 조사표 대조. '2만 7천 원' 같은 반올림 금액은 조사표 원값 중 ±500원 안에 있는 값이 있어야 통과.
사용: python3 check_sub_numbers.py 대본데이터.json [short1.json ...]"""
import json, re, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(f"{HERE}/조사표.md", encoding="utf-8").read()
nums = {m.replace(",", "") for m in re.findall(r"\d[\d,]*(?:\.\d+)?", src)}
prices = sorted({int(m.replace(",", "")) for m in re.findall(r"\d{1,3},\d{3}", src)})
bad = 0; cnt = 0
for f in sys.argv[1:]:
    D = json.load(open(f if os.path.isabs(f) else f"{HERE}/{f}", encoding="utf-8"))
    for si, s in enumerate(D["sections"]):
        for i, x in enumerate(s["sentences"]):
            t = x[2]
            for m in re.finditer(r"(\d+)만(?: (\d)천)? 원|(?<![\d만] )(?<!\d)(\d)천 원", t):
                v = int(m.group(1) or 0) * 10000 + int(m.group(2) or m.group(3) or 0) * 1000; cnt += 1
                near = [p for p in prices if abs(p - v) <= 500]
                if not near and not re.search(re.escape(m.group(0)) + "을 조금|에 조금", t) and v not in (10000,):
                    bad += 1; print(f"[{f} {si:02d}_{i:02d}] 반올림 금액 {m.group(0)} → 조사표에 ±500 값 없음 | {t}")
            t2 = re.sub(r"\d+만(?: \d천)? 원|\d천 원", "", t)
            for n in re.findall(r"\d[\d,]*(?:\.\d+)?", t2):
                n = n.replace(",", ""); cnt += 1
                if n not in nums: bad += 1; print(f"[{f} {si:02d}_{i:02d}] {n} 조사표에 없음 | {t}")
print(f"대조 {cnt}개 · 불일치 {bad}개")
sys.exit(1 if bad else 0)
