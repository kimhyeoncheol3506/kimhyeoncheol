#!/usr/bin/env python3
"""규칙 시스템: 피드백 원문(feedback/inbox.jsonl) → 규칙(rules/*.yaml) → 린트(코드 점검과 연결).

  python scripts/rules/rules.py list [--scope shorts]     규칙 목록
  python scripts/rules/rules.py stats                      개수, 린트로 점검되는 것/사람 판단에 의존하는 것
  python scripts/rules/rules.py inbox [--pending]          피드백 원문 목록
  python scripts/rules/rules.py add "<현철님이 한 말 그대로>" [--context ...]   인박스에 쌓기(pending)
  python scripts/rules/rules.py promote FB-0010 --id EDIT-12 --scope all --text "..." [--config a.b] [--code file:symbol] [--manual]
  python scripts/rules/rules.py lint                       규칙·설정·코드가 서로 맞는지 검사(실패하면 종료 코드 1)

린트가 보는 것: id 중복, 필수 항목, enforce.config 가 style.yaml 에 실제 있는지, enforce.code 파일·함수가 실제 있는지,
인박스 원문이 가리키는 규칙이 있는지, 처리 안 된 인박스(pending)가 7일을 넘었는지(경고).
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RULES = os.path.join(ROOT, "rules")
INBOX = os.path.join(ROOT, "feedback", "inbox.jsonl")
SCOPES = {"all", "shorts", "longform", "voice", "external", "process"}


def load_rules():
    out = []
    for f in sorted(glob.glob(os.path.join(RULES, "*.yaml"))):
        for r in yaml.safe_load(open(f, encoding="utf-8")) or []:
            r["_file"] = os.path.basename(f)
            out.append(r)
    return out


def load_inbox():
    if not os.path.exists(INBOX):
        return []
    return [json.loads(l) for l in open(INBOX, encoding="utf-8") if l.strip()]


def dotted(d, path):
    for k in path.split("."):
        if not isinstance(d, dict) or k not in d:
            return False
        d = d[k]
    return True


def lint():
    errs, warns = [], []
    style = yaml.safe_load(open(os.path.join(ROOT, "style.yaml"), encoding="utf-8"))
    rules = load_rules()
    ids = {}
    for r in rules:
        rid = r.get("id", "?")
        if rid in ids:
            errs.append(f"{rid}: id 중복 ({ids[rid]} 와 {r['_file']})")
        ids[rid] = r["_file"]
        for k in ("id", "scope", "text", "why", "date", "enforce"):
            if not r.get(k):
                errs.append(f"{rid}: '{k}' 없음")
        if r.get("scope") not in SCOPES:
            errs.append(f"{rid}: scope '{r.get('scope')}' 는 {sorted(SCOPES)} 중 하나여야 함")
        en = r.get("enforce") or {}
        if en.get("type") not in ("lint", "manual"):
            errs.append(f"{rid}: enforce.type 은 lint 또는 manual")
        if en.get("type") == "lint":
            if not en.get("config") and not en.get("code"):
                errs.append(f"{rid}: lint 규칙인데 config 도 code 도 없음")
            if en.get("config") and not dotted(style, en["config"]):
                errs.append(f"{rid}: style.yaml 에 '{en['config']}' 가 없음")
            if en.get("code"):
                path, _, sym = en["code"].partition(":")
                full = os.path.join(ROOT, path)
                if not os.path.exists(full):
                    errs.append(f"{rid}: 코드 파일 없음 {path}")
                elif sym and sym not in open(full, encoding="utf-8", errors="ignore").read():
                    errs.append(f"{rid}: {path} 안에 '{sym}' 가 없음")
    rid_set = set(ids)
    today = datetime.date.today()
    for fb in load_inbox():
        for rid in fb.get("rules", []):
            if rid not in rid_set:
                errs.append(f"{fb['id']}: 규칙 {rid} 가 rules/ 에 없음")
        if fb.get("status") == "pending":
            age = (today - datetime.date.fromisoformat(fb["date"])).days
            if age > 7:
                warns.append(f"{fb['id']}: 처리 안 된 피드백이 {age}일째 — 규칙으로 바꾸거나 이유를 적어 닫으세요")
    return rules, errs, warns


def cmd_list(a):
    for r in load_rules():
        if a.scope and r["scope"] != a.scope:
            continue
        mark = "린트" if r["enforce"]["type"] == "lint" else "수동"
        print(f"{r['id']:10} [{r['scope']:8}] ({mark}) {r['text'][:90]}")


def cmd_stats(a):
    rules = load_rules()
    lint_n = sum(1 for r in rules if r["enforce"]["type"] == "lint")
    print(f"규칙 {len(rules)}개 = 린트로 점검 {lint_n}개 + 사람/제 판단에 의존(manual) {len(rules) - lint_n}개")
    by = {}
    for r in rules:
        by.setdefault(r["scope"], [0, 0])
        by[r["scope"]][0] += 1
        by[r["scope"]][1] += r["enforce"]["type"] == "lint"
    for s, (n, l) in sorted(by.items()):
        print(f"  {s:9} {n:3}개 (린트 {l})")
    ib = load_inbox()
    print(f"피드백 원문 {len(ib)}건 (처리 대기 {sum(1 for x in ib if x['status'] == 'pending')}건)")
    print("수동 규칙(자동 점검 없음):", ", ".join(r["id"] for r in rules if r["enforce"]["type"] == "manual"))


def cmd_inbox(a):
    for fb in load_inbox():
        if a.pending and fb["status"] != "pending":
            continue
        print(f"{fb['id']} {fb['date']} [{fb['status']}] {fb['text'][:80]}  → {','.join(fb.get('rules', [])) or '-'}")


def next_id(ib):
    n = max([int(x["id"].split("-")[1]) for x in ib] + [0]) + 1
    return f"FB-{n:04d}"


def cmd_add(a):
    ib = load_inbox()
    fb = {"id": next_id(ib), "date": str(datetime.date.today()), "text": a.text, "context": a.context or "", "status": "pending", "rules": []}
    with open(INBOX, "a", encoding="utf-8") as f:
        f.write(json.dumps(fb, ensure_ascii=False) + "\n")
    print("인박스에 쌓음:", fb["id"], "— 다음 영상에도 적용될 말이면 promote 로 규칙으로 바꾸세요")


def cmd_promote(a):
    ib = load_inbox()
    fb = next((x for x in ib if x["id"] == a.fb), None)
    if not fb:
        sys.exit(f"{a.fb} 가 인박스에 없음")
    if any(r["id"] == a.id for r in load_rules()):
        sys.exit(f"{a.id} 는 이미 있는 규칙 id")
    en = {"type": "manual"} if a.manual else {"type": "lint"}
    if a.config:
        en["config"] = a.config
    if a.code:
        en["code"] = a.code
    rule = {"id": a.id, "scope": a.scope, "text": a.text, "why": f"{fb['text']} ({fb['date']})", "date": fb["date"], "enforce": en}
    path = os.path.join(RULES, "feedback.yaml")
    cur = yaml.safe_load(open(path, encoding="utf-8")) if os.path.exists(path) else []
    cur = (cur or []) + [rule]
    with open(path, "w", encoding="utf-8") as f:
        f.write("# 인박스(feedback/inbox.jsonl)에서 규칙으로 바뀐 것\n")
        yaml.safe_dump(cur, f, allow_unicode=True, sort_keys=False, width=1000)
    fb["status"] = "promoted"
    fb["rules"] = sorted(set(fb.get("rules", []) + [a.id]))
    with open(INBOX, "w", encoding="utf-8") as f:
        for x in ib:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print(f"{a.fb} → 규칙 {a.id} (rules/feedback.yaml). 이어서 `lint` 로 검사하세요")


def cmd_lint(a):
    rules, errs, warns = lint()
    for w in warns:
        print("⚠", w)
    for e in errs:
        print("✗", e)
    print(f"규칙 {len(rules)}개 검사: 오류 {len(errs)}, 경고 {len(warns)}")
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("list"); p.add_argument("--scope"); p.set_defaults(f=cmd_list)
    sp.add_parser("stats").set_defaults(f=cmd_stats)
    p = sp.add_parser("inbox"); p.add_argument("--pending", action="store_true"); p.set_defaults(f=cmd_inbox)
    p = sp.add_parser("add"); p.add_argument("text"); p.add_argument("--context"); p.set_defaults(f=cmd_add)
    p = sp.add_parser("promote"); p.add_argument("fb"); p.add_argument("--id", required=True)
    p.add_argument("--scope", required=True); p.add_argument("--text", required=True)
    p.add_argument("--config"); p.add_argument("--code"); p.add_argument("--manual", action="store_true"); p.set_defaults(f=cmd_promote)
    sp.add_parser("lint").set_defaults(f=cmd_lint)
    a = ap.parse_args()
    sys.exit(a.f(a) or 0)


if __name__ == "__main__":
    main()
