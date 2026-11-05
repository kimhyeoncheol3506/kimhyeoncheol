# 20편 프로젝트 생성 -> 렌더 -> 다운로드\어랏 저장 -> 쇼츠 일기장 갱신
import json, os, sys, datetime, subprocess
sys.stdout.reconfigure(encoding="utf-8")
B = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(os.path.expanduser("~"), "Downloads", "어랏")
EDITOR = os.path.dirname(B)   # scripts/ (wadda_edit.py 위치)
sys.path.insert(0, EDITOR)
import wadda_edit  # noqa

S = json.load(open(os.path.join(B, "segments.json"), encoding="utf-8"))
T = json.load(open(os.path.join(B, "titles.json"), encoding="utf-8"))
SRC = json.load(open(os.path.join(B, "sources.json"), encoding="utf-8"))
only = sys.argv[1:]  # 예: 김원훈 1


def chapter(person, idx, k):
    c = S[person][idx]
    title, pop = T[person]["ch"][str(idx)]
    D = round(c["out"] - c["in"], 2)
    pad = c.get("pad", 1.0)
    c.setdefault("file", "clips/%s_%d_%d.mp4" % (c["id"], int(c["in"]), int(c["out"])))
    src = next(s for s in SRC[person] if s["id"] == c["id"])
    cm = src["comments"] or ["ㅋㅋㅋㅋㅋㅋㅋㅋㅋ"]
    subs = [dict(s) for s in c["subs"] if s["t0"] < D - 0.2]
    for s in subs:
        s["t1"] = min(s["t1"], D)
    # 가장 웃음이 몰린 시각 -> 팝
    L = c["laughs"] or [D - 3]
    best = max(L, key=lambda x: sum(1 for y in L if abs(y - x) <= 3))
    pat = max(0.8, min(D - 1.5, best - 0.9))
    pops = [{"at": round(pat, 2), "text": pop, "zoom": 1.22}]
    # 빈 구간에 (빵터짐ㅋㅋ) 상황 자막
    for lt in L:
        if not any(s["t0"] - 0.2 <= lt <= s["t1"] + 0.2 for s in subs) and lt + 1.2 < D:
            subs.append({"t0": round(lt, 2), "t1": round(lt + 1.2, 2), "text": "(빵터짐ㅋㅋㅋ)", "style": "paren"})
            break
    subs.sort(key=lambda s: s["t0"])
    return {"title": title, "src": os.path.join(B, c["file"]), "in": pad, "out": round(pad + D, 2), "x": 0.5, "y": 0.40, "zoom": 1.45,
            "comments": [{"at": 0, "text": cm[k % len(cm)]}, {"at": round(D / 2, 1), "text": cm[(k + 1) % len(cm)]}],
            "subs": subs, "pops": pops,
            "_src": "%s (%s)" % (src.get("channel"), src.get("title", "")[:40]), "_text": c["text"][:80]}


def diary(entry):
    p = os.path.join(OUTDIR, "쇼츠 일기장.txt")
    new = not os.path.exists(p)
    with open(p, "a", encoding="utf-8-sig" if new else "utf-8") as f:
        if new:
            f.write("■ 쇼츠 일기장 (와따마 스타일 개그 짤)\n\n")
        f.write(entry + "\n")


os.makedirs(OUTDIR, exist_ok=True)
for person in T.keys():
    idxs = [int(i) for i in T[person]["ch"].keys()]
    idxs = [i for i in range(len(S[person])) if i in idxs]          # 점수순
    groups = [idxs[v::5] for v in range(5)]
    for v, g in enumerate(groups, 1):
        start = T[person].get("start", 1)          # 이어 만들 때 시작 번호 (예: 6)
        name = "%s %d" % (person, v + start - 1)
        if only and name not in " ".join(only) and person not in only:
            continue
        if not only and os.path.exists(os.path.join(OUTDIR, name + ".mp4")):
            print("[건너뜀] 이미 있음", name); continue
        g = [i for i in g if os.path.exists(os.path.join(B, "clips/%s_%d_%d.mp4" % (S[person][i]["id"], int(S[person][i]["in"]), int(S[person][i]["out"]))))]
        chs = [chapter(person, i, k) for k, i in enumerate(g)]
        proj = {"output": name + ".mp4", "chapters": chs}
        pj = os.path.join(B, "proj_%s_%d.json" % (person, v))
        json.dump(proj, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        out = os.path.join(OUTDIR, name + ".mp4")
        wadda_edit.render(pj, out)
        dur = float(subprocess.run([wadda_edit.FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], capture_output=True, text=True).stdout)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = ["────────────────────────",
                 "일시: " + now,
                 "제목: " + T[person]["videos"][v - 1],
                 "파일: " + name + ".mp4 (%d분 %02d초)" % (dur // 60, dur % 60),
                 "주제: %s 웃음 터진 장면 모음 (게스트·MC 빵터진 순간 위주)" % person,
                 "영상내용:"]
        for k, ch in enumerate(chs, 1):
            lines.append("  %d) %s - %s" % (k, ch["title"], ch["_src"]))
        diary("\n".join(lines) + "\n")
        print("[저장]", out, "%.1fs" % dur, flush=True)
