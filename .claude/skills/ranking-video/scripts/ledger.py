# -*- coding: utf-8 -*-
"""발행 원장 (ranking-video v2.10.0) — 제작·업로드·예약·공개·삭제를 이벤트로 한 줄씩 남긴다.

파일: video_projects/발행_원장.jsonl (한 줄 = 이벤트 하나, 지우지 않고 덧붙이기만 한다)
사용법:
  python3 -I ledger.py add <프로젝트 폴더> <이벤트: 제작완료|업로드|예약|공개|삭제|메모> [--title 제목] [--url 링크] [--note 메모]
  python3 -I ledger.py list [--project 폴더 이름 일부]
제작완료 이벤트는 프로젝트의 08_완성영상/타임라인.json에서 길이를 읽어 자동 기록한다.
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEDGER = os.path.join(ROOT, "video_projects", "발행_원장.jsonl")

def arg(name, d=""):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else d

def add(proj, event, **kw):
    rec = dict(ts=dt.datetime.now().astimezone().isoformat(timespec="seconds"), project=os.path.relpath(os.path.abspath(proj), os.path.join(ROOT, "video_projects")), event=event)
    tl = os.path.join(proj, "08_완성영상", "타임라인.json")
    if event == "제작완료" and os.path.exists(tl): rec["length_sec"] = round(json.load(open(tl))["total_seconds"])
    rec.update({k: v for k, v in kw.items() if v})
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True); open(LEDGER, "a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n"); return rec

if __name__ == "__main__":
    if sys.argv[1] == "add": print(add(sys.argv[2], sys.argv[3], title=arg("--title"), url=arg("--url"), note=arg("--note")))
    else:
        f = arg("--project")
        for l in open(LEDGER, encoding="utf-8") if os.path.exists(LEDGER) else []:
            r = json.loads(l)
            if f in r["project"]: print(r["ts"][:16], r["event"], r["project"], r.get("length_sec", ""), r.get("title", ""), r.get("note", ""))
