# -*- coding: utf-8 -*-
"""새 영상 패턴 뽑기: 10개 중 랜덤 1개(직전 2편 패턴 제외) → <프로젝트>/00_data/pattern.json + <프로젝트>/pattern.txt, history.json에 기록
사용: python3 pick_pattern.py <프로젝트폴더> [--only 1,3] [--seed N]
  - 이미 pattern.json이 있으면 다시 뽑지 않고 그대로 쓴다(재렌더해도 패턴 고정).
  - 롱폼_만들기.sh 가 pattern.txt 를 upload_ready/<편>/ 으로 복사한다."""
import json, os, random, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); H = f"{HERE}/history.json"
TH = json.load(open(f"{HERE}/themes.json", encoding="utf-8"))
P = os.path.abspath(sys.argv[1]); a = sys.argv[2:]
only = [int(x) for x in a[a.index("--only") + 1].split(",")] if "--only" in a else list(range(1, 11))
if "--seed" in a: random.seed(int(a[a.index("--seed") + 1]))
pj = f"{P}/00_data/pattern.json"
if os.path.exists(pj):
    d = json.load(open(pj, encoding="utf-8")); print(f"이미 정함: 패턴 {d['num']} {d['name']}"); sys.exit(0)
hist = json.load(open(H, encoding="utf-8")) if os.path.exists(H) else []
recent = [h["num"] for h in hist[-2:]]
cand = [n for n in only if n not in recent] or [n for n in range(1, 11) if n not in recent]
n = random.choice(cand); name = TH[str(n)]["name"]
os.makedirs(f"{P}/00_data", exist_ok=True)
d = dict(num=n, name=name, date=datetime.date.today().isoformat(), candidates=cand, excluded_recent=recent)
json.dump(d, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(f"{P}/pattern.txt", "w", encoding="utf-8").write(f"{n}\n{name}\n")
hist.append(dict(num=n, name=name, project=os.path.basename(P), date=d["date"]))
json.dump(hist, open(H, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"패턴 {n} {name} (후보 {cand}, 직전 제외 {recent})")
