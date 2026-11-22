# 이미 만든 영상에 쓴 컷 기록부 (scripts/used_cuts.json)
#   - select2.py가 이 기록과 겹치는 구간(같은 원본의 시간 겹침, 또는 다른 업로드라도 대사가 비슷한 구간)을 후보에서 뺀다.
#   - batch.py가 영상을 하나 만들 때마다 쓴 컷을 추가한다.
#   python registry.py add-projects <proj_*.json ...>   기존 프로젝트에서 기록 채우기
#   python registry.py stats
import json, os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8")
REG = os.environ.get("WADDA_REGISTRY") or os.path.join(os.path.expanduser("~"), "Downloads", "어랏", "used_cuts.json")
MARGIN = 3.0       # 이 초 이내로 붙어 있어도 겹친 것으로 본다
SIM = 0.17         # 대사 2글자 조각 유사도가 이 이상이면 같은 장면으로 본다


def load():
    return json.load(open(REG, encoding="utf-8")) if os.path.exists(REG) else []


def save(R):
    json.dump(R, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=0)


def bigr(t):
    t = re.sub(r"[^가-힣a-zA-Z0-9]", "", t or "")
    return set(t[i:i + 2] for i in range(len(t) - 1))


def clashes(R, vid, a, b, text=""):
    """기록과 겹치면 그 기록을, 아니면 None"""
    bg = bigr(text)
    for r in R:
        if r["id"] == vid and not (b + MARGIN < r["a"] or a > r["b"] + MARGIN):
            return r
        if len(bg) >= 25 and r.get("bg"):
            rb = set(r["bg"])
            if len(bg & rb) / max(1, len(bg | rb)) > SIM:
                return r
    return None


def add(R, vid, a, b, text, video, title):
    R.append({"id": vid, "a": round(a, 2), "b": round(b, 2), "video": video, "title": title, "bg": sorted(bigr(text))})


if __name__ == "__main__":
    R = load()
    if sys.argv[1:2] == ["add-projects"]:
        for p in sys.argv[2:]:
            P = json.load(open(p, encoding="utf-8"))
            video = os.path.splitext(P.get("output", os.path.basename(p)))[0]
            for ch in P["chapters"]:
                base = os.path.splitext(os.path.basename(ch["src"]))[0]
                m = re.match(r"(.+)_(\d+)_(\d+)$", base)
                if not m:
                    continue
                vid, a0 = m.group(1), float(m.group(2))
                pad = ch.get("in", 1.0)
                a = a0 + 0.0
                b = a0 + (ch["out"] - pad)
                text = " ".join(s.get("text", "") for s in ch.get("subs", [])) or ch.get("_text", "")
                if not clashes([r for r in R if r.get("video") == video and r["id"] == vid and abs(r["a"] - a) < 0.5], vid, a, b):
                    add(R, vid, a, b, text, video, ch.get("title", ""))
        save(R)
    print("기록된 컷:", len(R), "개 /", len({r['video'] for r in R}), "개 영상")
