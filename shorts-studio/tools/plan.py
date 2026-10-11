"""오늘 만들 것 정하기: 쇼츠 컨셉 홀짝 교대(A 사연판정소 ↔ B 카톡판독소) + 주제 은행에서 다음 주제.

  python tools/plan.py            # 다음 쇼츠 컨셉, 다음 B 주제, 다음 롱폼 주제 출력
  python tools/plan.py --done <프로젝트폴더>   # 제작 완료 기록 (make.py가 자동 호출)
하루 목표: 쇼츠 2(A 1 + B 1, 스샷 없으면 B 2) + 롱폼 1
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIST = ROOT / "state" / "history.json"
TOPICS = ROOT / "state" / "topics.json"


def load(p, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def record(project: Path):
    s = json.loads((project / "script.json").read_text(encoding="utf-8"))
    h = load(HIST, [])
    h = [x for x in h if x["project"] != project.name]
    h.append({"date": date.today().isoformat(), "project": project.name, "format": s["format"],
              "concept": s.get("concept", "card" if s["format"] == "short" else "map"),
              "title": s.get("upload", {}).get("title", s.get("title")), "topic_id": s.get("topic_id")})
    HIST.write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")
    t = load(TOPICS, {})
    for group in ("kakao", "long"):
        for x in t.get(group, []):
            if x["id"] == s.get("topic_id"):
                x["used"] = True
    TOPICS.write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding="utf-8")


def plan():
    h = load(HIST, [])
    t = load(TOPICS, {})
    shorts = [x for x in h if x["format"] == "short"]
    last = shorts[-1]["concept"] if shorts else "kakao"
    nxt = "kakao" if last == "card" else "card"
    k = next((x for x in t.get("kakao", []) if not x.get("used")), None)
    l = next((x for x in t.get("long", []) if not x.get("used")), None)
    print(json.dumps({"next_short_concept": nxt,
                      "rule": "card(A)는 블라인드 스샷이 있을 때. 스샷이 없으면 kakao(B)로 대체",
                      "next_kakao_topic": k, "next_long_topic": l,
                      "made_today": [x["project"] for x in h if x["date"] == date.today().isoformat()]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--done":
        record(Path(sys.argv[2]))
    else:
        plan()
