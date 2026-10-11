"""트리거 감시: 두 계정의 최신 게시물을 조회 → 조건 충족 + 미제작이면 제작 대기열에 올린다.

  빙글빙글블라인드(@bingbingblind) 조회수 ≥ 3000 → 쇼츠
  Secret BB(@BBstyle0508)          조회수 ≥ 5000 → 롱폼

X는 로그인 없이 조회가 막혀 있어서, 게시물 데이터는 '가져오기(fetcher)'를 끼워 넣는 구조다.
  - fetch_from_file : 사람이/브라우저 자동화가 저장한 JSON 파일을 읽는다 (지금 바로 동작)
  - fetch_from_x_api: X API 키(X_BEARER_TOKEN)가 있으면 공식 API로 조회
사용: python monitor/watch.py --posts posts.json   또는   X_BEARER_TOKEN=... python monitor/watch.py
출력: monitor/queue.json (제작할 소재 목록), monitor/state.json (이미 처리한 게시물 id)
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES = [
    {"handle": "bingbingblind", "min_views": 3000, "format": "short"},
    {"handle": "BBstyle0508", "min_views": 5000, "format": "long"},
]


def fetch_from_file(path):
    """[{"handle","id","text","views","media":[url..],"created_at"}]"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fetch_from_x_api(token, handle, limit=20):
    def get(url):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    uid = get(f"https://api.x.com/2/users/by/username/{handle}")["data"]["id"]
    q = urllib.parse.urlencode({"max_results": limit, "tweet.fields": "public_metrics,created_at",
                                "expansions": "attachments.media_keys", "media.fields": "url"})
    d = get(f"https://api.x.com/2/users/{uid}/tweets?{q}")
    media = {m["media_key"]: m.get("url") for m in d.get("includes", {}).get("media", [])}
    out = []
    for t in d.get("data", []):
        keys = t.get("attachments", {}).get("media_keys", [])
        out.append({"handle": handle, "id": t["id"], "text": t["text"], "created_at": t.get("created_at"),
                    "views": t.get("public_metrics", {}).get("impression_count", 0),
                    "media": [media[k] for k in keys if media.get(k)]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", help="게시물 JSON 파일 (fetch_from_file)")
    a = ap.parse_args()
    state_f, queue_f = HERE / "state.json", HERE / "queue.json"
    state = json.loads(state_f.read_text()) if state_f.exists() else {"done": []}
    queue = json.loads(queue_f.read_text(encoding="utf-8")) if queue_f.exists() else []
    if a.posts:
        posts = fetch_from_file(a.posts)
    elif os.environ.get("X_BEARER_TOKEN"):
        posts = [p for r in RULES for p in fetch_from_x_api(os.environ["X_BEARER_TOKEN"], r["handle"])]
    else:
        raise SystemExit("게시물 소스가 없습니다: --posts 파일 또는 X_BEARER_TOKEN 필요")
    added = 0
    for p in posts:
        rule = next((r for r in RULES if r["handle"].lower() == p["handle"].lower()), None)
        if not rule or p["id"] in state["done"] or p.get("views", 0) < rule["min_views"]:
            continue
        queue.append({**p, "format": rule["format"]})
        state["done"].append(p["id"])
        added += 1
    queue_f.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    state_f.write_text(json.dumps(state, indent=2))
    print(f"새 소재 {added}건 → {queue_f}")


if __name__ == "__main__":
    main()
