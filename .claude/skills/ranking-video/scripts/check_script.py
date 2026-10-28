# -*- coding: utf-8 -*-
"""대본 사전 점검 (ranking-video v2.10.0) — 음성을 만들기 전에 돌린다.

사용법: python3 -I check_script.py <대본데이터.json> [조사표.md]
검사: ① '그'로 시작하는 문장(FAIL) ② 정보 카드 at 문구가 실제 문장 시작과 맞는지(FAIL) ③ 같은 어미가 3문장 이상 이어짐(WARN)
      ④ 삭제 목록 표현·정보 없는 문장 비율(WARN) ⑤ 숫자 밀도(분당 숫자 문장 6개 이상 권장, WARN) ⑥ '내 관점' 한 줄(WARN) ⑦ 조사표가 있으면 check_numbers 실행(FAIL)
FAIL이 있으면 종료 코드 1. (기준은 references/품질개선_기획서.md·내_규칙.md)
"""
import json, os, re, subprocess, sys

D = json.load(open(sys.argv[1], encoding="utf-8")); fail, warn = [], []
dm = sorted(D.get("display_map", []), key=lambda x: -len(x[0])); mp = dict(dm)
rx = re.compile("|".join(re.escape(a) for a, _ in dm)) if dm else None
disp = lambda t: rx.sub(lambda m: mp[m.group(0)], t) if rx else t
S = [(si, ti, x[0]) for si, s in enumerate(D["sections"]) for ti, x in enumerate(s["sentences"])]
chars = sum(len(t) for _, _, t in S); minutes = chars / 8.0 / 60  # 실제 완성본 기준 약 초당 8자(카드·쉼 포함)
for si, ti, t in S:
    if t.lstrip().startswith("그"): fail.append(f"'그'로 시작 {si:02d}_{ti:02d}: {t[:30]}")
for c in D.get("graphics", {}).get("info_cards", []):
    at = c.get("at"); sec = next((s for s in D["sections"] if s["name"] == c["section"]), None)
    if at and sec and not any(x[0].startswith(at) for x in sec["sentences"]): fail.append(f"카드 at 문구가 문장 시작과 안 맞음 [{c['section']}]: '{at}'")
ends = [re.findall(r"(죠|요|니다|거든요|예요|네요)[.?!]?$", t) for _, _, t in S]; run = 1
for i in range(1, len(S)):
    run = run + 1 if ends[i] and ends[i] == ends[i - 1] else 1
    if run == 4 and ends[i]: warn.append(f"같은 어미({ends[i][0]}) 4문장 연속: {S[i][0]:02d}_{S[i][1]:02d} 근처")
BAN = ["자, 이제", "정리해 볼게요", "그럼 ", "넘어가 보겠습니다", "알아보도록 하겠습니다"]
for b in BAN:
    n = sum(b in t for _, _, t in S)
    if n > 1: warn.append(f"군더더기 표현 '{b}' {n}회")
nonfact = sum(1 for _, _, t in S if not re.search(r"\d", disp(t)) and len(t) < 18 and not t.startswith("꿀팁")); ratio = nonfact / max(1, len(S))
if ratio > 0.25: warn.append(f"짧고 숫자 없는 문장 비율 {ratio:.0%} (25% 이하 권장)")
numsent = sum(1 for _, _, t in S if re.search(r"\d", disp(t))); per_min = numsent / max(minutes, 1)
if per_min < 6: warn.append(f"숫자 문장 분당 {per_min:.1f}개 (6개 이상 권장)")
if not any(re.search(r"제 생각|저는 .*생각|제 관점|개인적으로", t) for _, _, t in S): warn.append("'내 관점' 한 줄이 없음(영상마다 1줄 권장, 아웃트로 직전)")
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
    r = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_numbers.py"), sys.argv[1], sys.argv[2]], capture_output=True, text=True)
    if r.returncode != 0: fail.append("조사표에 없는 숫자: " + r.stdout.strip().replace("\n", " / ")[:300])
print(f"대본 {chars}자 · {len(S)}문장 · 약 {minutes:.1f}분 · 숫자 문장 분당 {per_min:.1f}개")
for f in fail: print("FAIL", f)
for w in warn: print("WARN", w)
if not fail and not warn: print("PASS 모든 항목 통과")
sys.exit(1 if fail else 0)
