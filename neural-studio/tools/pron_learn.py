"""발음 학습 기록 보기·반영·직접 고치기.

  python tools/pron_learn.py              # 자주 틀린 낱말 표 + 사전 반영(2번 이상, 다른 문장)
  python tools/pron_learn.py --set 장단기 장단끼   # 사람이 정한 발음으로 고정(자동 학습이 덮어쓰지 않음)
  python tools/pron_learn.py --drop 장단기         # 학습 항목 지우기
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from facetube import pron_learn  # noqa: E402
from facetube.pron_dict import LEARNED_PATH  # noqa: E402


def _load():
    try:
        return json.loads(LEARNED_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return {}


def _save(d):
    LEARNED_PATH.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", nargs=2, metavar=("낱말", "발음"))
    ap.add_argument("--drop", metavar="낱말")
    a = ap.parse_args()
    if a.set:
        d = _load()
        d[a.set[0]] = {**d.get(a.set[0], {}), "say": a.set[1], "status": "locked", "locked": True}
        _save(d)
        print(f"고정: {a.set[0]} → {a.set[1]}")
        return
    if a.drop:
        d = _load()
        d.pop(a.drop, None)
        _save(d)
        print(f"지움: {a.drop}")
        return
    stats = pron_learn.collect()
    added, manual = pron_learn.update()
    rows = sorted(stats.items(), key=lambda kv: -kv[1]["count"])
    print(f"틀린 기록 {sum(s['count'] for s in stats.values())}건, 낱말 {len(stats)}개 (rules/pron_watch.jsonl)")
    print("| 낱말 | 횟수 | 문장 수 | 목소리 | 들린 소리 | 사전 |")
    print("|---|---|---|---|---|---|")
    learned = _load()
    for w, s in rows[:40]:
        e = learned.get(w, {})
        state = (f"→ {e['say']}" if e.get("say") else "직접 고쳐야 함") if e else "관찰 중(1문장)"
        print(f"| {w} | {s['count']} | {len(s['sentences'])} | {', '.join(sorted(v for v in s['voices'] if v))} | "
              f"{max(s['heard'], key=s['heard'].get)} | {state} |")
    if added:
        print("\n새로 사전에 넣음:", ", ".join(added))
    if manual:
        print("철자대로 적어도 틀리는 낱말(대본에 '원문{{발음}}' 으로 적거나 --set 으로 고정):", ", ".join(manual))


if __name__ == "__main__":
    main()
