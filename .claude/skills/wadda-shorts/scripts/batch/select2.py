# 웃음 마커 밀집 구간 선택 + 중복(같은 방송 재업로드) 제거 + 자막 청크
import json, os, re, subprocess, sys, glob
sys.stdout.reconfigure(encoding="utf-8")
B = os.path.dirname(os.path.abspath(__file__))
SUB = os.path.join(B, "subs"); os.makedirs(SUB, exist_ok=True)
env = dict(os.environ, TEMP=SUB, TMP=SUB)
sys.path.insert(0, B)
from _bins import YTDLP
S = json.load(open(os.path.join(B, "sources.json"), encoding="utf-8"))
LAUGH = re.compile(r"\[(웃음|박수|폭소|웃는 소리|환호|웃음소리)\]")
WIN, NEED = 24.0, int(os.environ.get("NEED", 33))


def words_of(vid):
    p = os.path.join(SUB, vid + ".ko.json3")
    if not os.path.exists(p):
        subprocess.run([YTDLP, "--skip-download", "--write-auto-subs", "--sub-langs", "ko", "--sub-format", "json3",
                        "-o", os.path.join(SUB, vid), "https://www.youtube.com/watch?v=" + vid], env=env, capture_output=True)
    if not os.path.exists(p):
        return [], []
    j = json.load(open(p, encoding="utf-8"))
    W, L = [], []
    for ev in j.get("events", []):
        t0 = ev.get("tStartMs", 0) / 1000
        for s in ev.get("segs", []) or []:
            w = s.get("utf8", "")
            t = t0 + s.get("tOffsetMs", 0) / 1000
            if LAUGH.search(w):
                L.append(t)
            w2 = LAUGH.sub("", w).replace("[음악]", "").replace("[콧방귀]", "").strip()
            if w2:
                W.append((t, w2))
    W.sort()
    return W, sorted(L)


def build_chunks(c, W, L):
    ws = [(t - c["in"], w) for t, w in W if c["in"] <= t < c["out"]]
    chunks, cur, cs, color = [], "", None, "yellow"
    for i, (t, w) in enumerate(ws):
        new_spk = w.startswith(">>")
        w = w.replace(">>", "").strip()
        if not w:
            continue
        gap = t - (ws[i - 1][0] if i else t)
        if cur and (new_spk or len(cur) + len(w) + 1 > 13 or gap > 0.7):
            chunks.append({"t0": round(cs, 2), "t1": round(t, 2), "text": cur, "color": color})
            cur, cs = "", None
        if new_spk:
            color = "green" if color == "yellow" else "yellow"
        if cs is None:
            cs = t
        cur = (cur + " " + w).strip()
    if cur:
        chunks.append({"t0": round(cs, 2), "t1": round(min(c["out"] - c["in"], cs + 1.6), 2), "text": cur, "color": color})
    for ch in chunks:
        ch["t1"] = round(min(ch["t1"], ch["t0"] + 2.6), 2)
    c["subs"] = chunks
    c["laughs"] = [round(x - c["in"], 2) for x in L if c["in"] <= x <= c["out"]]
    c["text"] = " / ".join(x["text"] for x in chunks)


_CONF = {}


def conf_mean(vid, a, b):
    """유튜브 자동자막 단어 신뢰도(acAsrConf) 평균. 신형 자막(구두점 있음)은 값이 없어서 None"""
    if vid not in _CONF:
        p = os.path.join(SUB, vid + ".ko.json3"); out = []
        if os.path.exists(p):
            for ev in json.load(open(p, encoding="utf-8")).get("events", []):
                t0 = ev.get("tStartMs", 0) / 1000
                for sg in ev.get("segs") or []:
                    if "acAsrConf" in sg:
                        out.append((t0 + sg.get("tOffsetMs", 0) / 1000, sg["acAsrConf"]))
        _CONF[vid] = out
    cs = [v for t, v in _CONF[vid] if a <= t < b and v > 0]   # 신형 자막은 0으로 옴 = 점수 없음
    return sum(cs) / len(cs) if cs else None


def caption_ok(text, vid=None, a=0, b=0):
    """자동자막이 깨진 구간(노래·함성 속 엉터리 인식) 걸러내기"""
    toks = [t for t in re.split(r"[\s/]+", text) if t]
    if len(toks) < 20:
        return False
    one = sum(1 for t in toks if len(re.sub(r"[^가-힣]", "", t)) <= 1) / len(toks)
    latin = sum(1 for t in toks if re.search(r"[A-Za-z0-9#*]", t))
    if one >= 0.35 or latin > 2:
        return False
    m = conf_mean(vid, a, b) if vid else None
    return m is None or m >= 208


def bigr(t):
    t = re.sub(r"[^가-힣a-zA-Z0-9]", "", t)
    return set(t[i:i + 2] for i in range(len(t) - 1))


sys.path.insert(0, B)
import registry
USED = registry.load()
# 동시에 진행 중인 다른 배치의 후보도 피한다: EXTRA_USED=다른폴더\segments.json;...
for _ep in filter(None, os.environ.get("EXTRA_USED", "").split(";")):
    for _segs in json.load(open(_ep, encoding="utf-8")).values():
        for _c in _segs:
            USED.append({"id": _c["id"], "a": _c["in"], "b": _c["out"], "bg": sorted(bigr(_c.get("text", "")))})
print('기존 사용 컷', len(USED), '개와 겹치는 구간은 제외')
out = {}
skipped = 0
for person, srcs in S.items():
    cache, cands = {}, []
    for src in srcs:
        cache[src["id"]] = words_of(src["id"])
        W, L = cache[src["id"]]
        if not W:
            continue
        dur = src.get("dur") or W[-1][0]
        for lt in L:
            end = min(dur - 0.5, lt + 2.8)
            st = max(3.0, end - WIN)
            n = sum(1 for x in L if st <= x <= end)
            late = sum(1 for x in L if end - 9 <= x <= end)
            cands.append((n + 0.5 * late, src["id"], st, end))
    cands.sort(reverse=True)
    chosen = []
    for sc, vid, st, en in cands:
        if any(c["id"] == vid and not (en + 6 < c["in"] or st > c["out"] + 6) for c in chosen):
            continue
        if sum(1 for c in chosen if c["id"] == vid) >= 7:
            continue
        c = {"id": vid, "in": round(st, 2), "out": round(en, 2), "score": sc}
        build_chunks(c, *cache[vid])
        if not caption_ok(c["text"], vid, st, en):
            continue
        if registry.clashes(USED, vid, st, en, c["text"]):
            skipped += 1
            continue
        bg = bigr(c["text"])
        if len(bg) < 25:
            continue
        if any(len(bg & x["_bg"]) / max(1, len(bg | x["_bg"])) > 0.17 for x in chosen):
            continue
        c["_bg"] = bg
        chosen.append(c)
        if len(chosen) >= NEED:
            break
    for c in chosen:
        c.pop("_bg", None)
    out[person] = chosen
    for c in chosen:
        USED.append({"id": c["id"], "a": c["in"], "b": c["out"], "bg": sorted(bigr(c["text"]))})
    print(person, len(chosen), {s["id"]: sum(1 for c in chosen if c["id"] == s["id"]) for s in srcs})
print('기존 영상과 겹쳐서 뺀 후보:', skipped)
json.dump(out, open(os.path.join(B, "segments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
