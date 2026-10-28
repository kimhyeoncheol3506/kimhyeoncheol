#!/usr/bin/env python3
"""발행 원장: 영상의 렌더·업로드·예약·공개·삭제를 이벤트로 한 줄씩 기록한다(append-only, content/history/published.jsonl).

업로드는 현철님이 YouTube Studio 에서 하므로, 하신 뒤 "올렸어요/예약했어요/공개했어요/지웠어요"라고 알려 주시면 제가 기록한다.

  python tools/ledger.py add --video demo_short_coffee --event uploaded --url https://youtu.be/XXXX --visibility private --note "첫 업로드"
  python tools/ledger.py add --video demo_short_coffee --event scheduled --at 2026-10-30T18:00+09:00
  python tools/ledger.py add --video demo_short_coffee --event published
  python tools/ledger.py list [--video SLUG]
  python tools/ledger.py summary          영상별 현재 상태
  python tools/ledger.py check            기록이 앞뒤가 맞는지 검사(실패하면 종료 코드 1)
이벤트: rendered(만들었음) → uploaded(올렸음) → scheduled(예약) → published(공개) → deleted(삭제). 지운 영상을 다시 올리면 uploaded 부터 다시.
"""
import argparse
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "content", "history", "published.jsonl")
EVENTS = ["rendered", "uploaded", "scheduled", "published", "deleted"]
VIS = ["private", "unlisted", "public"]


def load(path):
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def state_of(events):
    """한 영상의 이벤트 목록 -> 현재 상태"""
    st = "none"
    for e in events:
        ev = e["event"]
        if ev == "rendered":
            st = "rendered" if st in ("none", "deleted") else st
        elif ev == "uploaded":
            st = "uploaded"
        elif ev == "scheduled":
            st = "scheduled"
        elif ev == "published":
            st = "published"
        elif ev == "deleted":
            st = "deleted"
    return st


def check(rows):
    errs = []
    last_ts = ""
    by = {}
    ids = set()
    for r in rows:
        if r["id"] in ids:
            errs.append(f"{r['id']}: id 중복")
        ids.add(r["id"])
        if r["event"] not in EVENTS:
            errs.append(f"{r['id']}: 알 수 없는 이벤트 {r['event']}")
        if r["ts"] < last_ts:
            errs.append(f"{r['id']}: 시각이 앞 기록보다 이전")
        last_ts = r["ts"]
        if r["event"] == "scheduled" and not r.get("at"):
            errs.append(f"{r['id']}: scheduled 인데 at(예약 시각)이 없음")
        if r.get("visibility") and r["visibility"] not in VIS:
            errs.append(f"{r['id']}: visibility 는 {VIS}")
        cur = state_of(by.get(r["video"], []))
        need = {"scheduled": ("uploaded", "scheduled"), "published": ("uploaded", "scheduled", "published"), "deleted": ("uploaded", "scheduled", "published")}
        if r["event"] in need and cur not in need[r["event"]]:
            errs.append(f"{r['id']}: {r['video']} 은(는) '{cur}' 상태인데 {r['event']} 를 기록함 (앞 단계 기록이 빠졌나요?)")
        by.setdefault(r["video"], []).append(r)
    return errs, by


def cmd_add(a):
    rows = load(a.ledger)
    n = max([int(r["id"].split("-")[1]) for r in rows] + [0]) + 1
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
    r = {"id": f"E-{n:04d}", "ts": now, "event": a.event, "video": a.video}
    for k in ("title", "url", "at", "visibility", "by", "note"):
        v = getattr(a, k)
        if v:
            r[k] = v
    errs, _ = check(rows + [r])
    if errs and not a.force:
        print("✗ 기록하지 않음:\n  " + "\n  ".join(errs[-2:]), file=sys.stderr)
        sys.exit(1)
    os.makedirs(os.path.dirname(a.ledger), exist_ok=True)
    with open(a.ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("기록:", r["id"], r["event"], r["video"])


def cmd_list(a):
    for r in load(a.ledger):
        if a.video and r["video"] != a.video:
            continue
        extra = " ".join(f"{k}={r[k]}" for k in ("url", "at", "visibility", "note") if r.get(k))
        print(f"{r['id']} {r['ts'][:16]} {r['event']:9} {r['video']}  {extra}")


def cmd_summary(a):
    rows = load(a.ledger)
    _, by = check(rows)
    print(f"이벤트 {len(rows)}건, 영상 {len(by)}개")
    for v, ev in by.items():
        print(f"  {v:28} {state_of(ev):10} (마지막 {ev[-1]['event']} {ev[-1]['ts'][:10]})")


def cmd_check(a):
    errs, _ = check(load(a.ledger))
    for e in errs:
        print("✗", e)
    print(f"기록 {len(load(a.ledger))}건 검사: 오류 {len(errs)}")
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", default=DEFAULT)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("add"); p.add_argument("--video", required=True); p.add_argument("--event", required=True, choices=EVENTS)
    for k in ("title", "url", "at", "visibility", "note"):
        p.add_argument(f"--{k}")
    p.add_argument("--by", default="user"); p.add_argument("--force", action="store_true"); p.set_defaults(f=cmd_add)
    p = sp.add_parser("list"); p.add_argument("--video"); p.set_defaults(f=cmd_list)
    sp.add_parser("summary").set_defaults(f=cmd_summary)
    sp.add_parser("check").set_defaults(f=cmd_check)
    a = ap.parse_args()
    sys.exit(a.f(a) or 0)


if __name__ == "__main__":
    main()
