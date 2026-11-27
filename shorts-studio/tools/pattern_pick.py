"""다음 쇼츠 패턴을 랜덤으로 고른다 (v1.25.0). 최근 3편에 쓴 패턴은 빼고 고른다.

  python tools/pattern_pick.py          # 다음 패턴 1개 (이름·참고 포맷·대본 규칙)
  python tools/pattern_pick.py --n 3    # 오늘치 3개 (서로 다르게)
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from studio.patterns import PATTERNS  # noqa: E402

RULES = {
    "countdown": "items[0]=1위. item 장면 visual.rank 를 5→1 순서로. 마지막 verdict 도장",
    "translator": "items[{who,outer,inner}]. 장면 cap 2개(겉말 / 번역), 두 번째 자막에서 속뜻 공개",
    "spec": "profile{name,line,gender} + stats[{k,v,score}]. item visual.stat, verdict 도장=등급(B+ 등)",
    "balance": "rounds[{a,b,pick}]. 라운드마다 제시 장면(round) + 픽 장면(round,pick,new:false,pick_at_chunk:0)",
    "test": "question + options[{k,text,result}]. question 장면(timer_at_chunk, pause_after 2.6) → item visual.opt",
    "katalk": "rounds[{name,ng[],ok[]}]. item visual.round + side ng/ok, 말풍선은 장면 길이에 맞춰 자동 등장",
    "essay": "여의도여자 CALM 톤, 속도 1.0, 자막 2줄이 화면 중앙 본문. 도장·효과 없음",
    "steps": "steps[{name,sub}] 3~5개. item visual.step, verdict 도장",
    "checklist": "checks[] 4~6개. item visual.check, verdict '3개 이상이면' 도장",
    "ox": "cases[{text,ox,label?}]. item visual.case, 두 번째 자막에서 O/X 공개",
}


def recent(k=3):
    h = json.loads((ROOT / "state" / "history.json").read_text(encoding="utf-8"))
    out = []
    for x in reversed(h):
        p = ROOT / "projects" / x["project"] / "script.json"
        if p.exists():
            s = json.loads(p.read_text(encoding="utf-8"))
            if s.get("concept") == "pattern":
                out.append(s.get("pattern"))
        if len(out) >= k:
            break
    return out


def pick(n=1):
    avoid = set(recent())
    pool = [k for k in PATTERNS if k not in avoid] or list(PATTERNS)
    random.SystemRandom().shuffle(pool)
    return pool[:n]


if __name__ == "__main__":
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 1
    for k in pick(n):
        print(json.dumps({"pattern": k, "label": PATTERNS[k]["label"], "rule": RULES[k]}, ensure_ascii=False))
