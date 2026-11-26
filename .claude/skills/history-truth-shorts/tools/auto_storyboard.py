# -*- coding: utf-8 -*-
"""롱폼용 반자동 storyboard 생성기.
에피소드마다 spec.py(짧은 장면 목록)만 쓰면 카메라 키·연기·3초 규칙 보충을 자동으로 채운다.
사용: python auto_storyboard.py <프로젝트>      (프로젝트에 words.json, script.txt, spec.py 필요)

spec.py 형식:
SEG = [
  # (시작 줄번호, set, mood, [배우...], {줄번호: "팻말"}, 옵션dict)
  (0, "office", "night", [P("rhee","boss",torso="#2b2f3a")], {1: "대마도 반환"}),
  ...
]
END_PAD = 2.5
배우 P(id, type, **덮어쓰기). x 위치는 인원수에 맞춰 자동(1명 460~540, 2명, 3명). 팻말은 첫 배우가 든다(옵션 holder="id").
"""
import itertools, json, os, sys, runpy

P_ = os.path.abspath(sys.argv[1])
W = json.load(open(os.path.join(P_, "words.json"), encoding="utf-8"))
lines = [l for l in open(os.path.join(P_, "script.txt"), encoding="utf-8").read().splitlines() if l.strip()]
first_w = {}
for i, w in enumerate(W):
    first_w.setdefault(w["sent"], i)
T = lambda w: W[min(w, len(W) - 1)]["s"]


def P(id_, type_, **k):
    d = {"id": id_, "type": type_}
    d.update(k); return d


spec = runpy.run_path(os.path.join(P_, "spec.py"), init_globals={"P": P})
SEG = spec["SEG"]
INDOOR_NARROW = {"study_room"}
GROUND = {"palace_hall": 1600, "study_room": 1700, "gate_court": 1760, "office": 1700, "village_road": 1760,
          "river_camp": 1760, "mountain_pass": 1740, "fortress_wall": 1690, "sea_battle": 1750}


def place(cast, set_):
    n = len(cast)
    if set_ in INDOOR_NARROW:
        xs = {1: [460], 2: [300, 640], 3: [220, 460, 700]}[min(n, 3)]
    elif set_ == "village_road":
        xs = {1: [480], 2: [340, 640], 3: [300, 480, 660]}[min(n, 3)]
    else:
        xs = {1: [540], 2: [360, 720], 3: [240, 540, 840]}[min(n, 3)]
    y = GROUND.get(set_, 1720)
    out = []
    for i, c in enumerate(cast[:3]):
        d = {"z": 1.0, "scale": 1.0, "pose": "stand", "expr": "neutral"}
        d.update(c)
        d.setdefault("x", xs[i]); d.setdefault("y", y)
        if n == 1:
            d.setdefault("face", 0.2); d.setdefault("dir", 1)
        else:
            left = d["x"] < 540
            d.setdefault("face", 0.35 if left else -0.35); d.setdefault("dir", 1 if left else -1)
        if d["type"] == "jking" and set_ == "palace_hall" and n > 1 and i == 0:
            d["y"] = 1560
        out.append(d)
    return out


def SG(c):
    return [c["x"] + 110, c["y"] - 420, 950]


EXPR = ["angry", "shocked", "sad", "sly", "deadpan", "happy", "neutral", "smug", "scared"]
POSE = ["point", "stand", "think", "arms_crossed", "shrug", "cheer"]
scenes = []
for si, seg in enumerate(SEG):
    line0, set_, mood, cast, signs = seg[:5]
    opt = seg[5] if len(seg) > 5 else {}
    line1 = SEG[si + 1][0] if si + 1 < len(SEG) else len(lines)
    cast = place(cast, set_)
    w0 = first_w[line0]
    w_end = first_w[line1] if line1 < len(lines) else len(W)
    holder = next((c for c in cast if c["id"] == opt.get("holder")), cast[0])
    keys, acts = [], []
    fcyc = itertools.cycle(["all"] + [c["id"] for c in cast] + [cast[0]["id"] + ":full"]) if len(cast) > 1 else itertools.cycle([cast[0]["id"], cast[0]["id"] + ":full", [cast[0]["x"], cast[0]["y"] - 380, 1100]])
    ecyc = itertools.cycle(EXPR[si % 3:] + EXPR[:si % 3])
    pcyc = itertools.cycle(POSE)
    spk = itertools.cycle(cast)
    keys.append({"w": w0, "frame": opt.get("open", [540, 1150, 1500] if len(cast) > 1 else cast[0]["id"])})
    for ln in range(line0, line1):
        w = first_w[ln]
        if ln in signs:
            keys.append({"w": w, "frame": SG(holder)})
            acts.append({"w": w, "who": holder["id"], "pose": "hold", "hold": "sign:" + signs[ln], "dir": 1, "expr": next(ecyc)})
            continue
        if ln != line0 or len(cast) == 1:
            keys.append({"w": w, "frame": next(fcyc)})
        c = next(spk)
        a = {"w": w, "who": c["id"], "expr": next(ecyc), "pose": next(pcyc)}
        if '"' in lines[ln] or "다." in lines[ln][-3:] and len(cast) > 1:
            a["talk"] = True
        acts.append(a)
    # 3초 규칙 보충
    t_end = T(w_end) if w_end < len(W) else W[-1]["e"] + spec.get("END_PAD", 2.5)
    holders = {a["who"] for a in acts if "hold" in a}
    for _ in range(60):
        ts = sorted({T(w0)} | {T(a["w"]) for a in acts}) + [t_end]
        g = max(zip(ts, ts[1:]), key=lambda p: p[1] - p[0])
        if g[1] - g[0] <= 2.7:
            break
        mid = (g[0] + g[1]) / 2
        cands = [k for k in range(w0, w_end) if g[0] + 0.4 < T(k) < g[1] - 0.2]
        if not cands:
            break
        w = min(cands, key=lambda k: abs(T(k) - mid))
        free = [c for c in cast if c["id"] not in holders] or cast
        c = free[_ % len(free)]
        a = {"w": w, "who": c["id"], "expr": next(ecyc)}
        if c["id"] not in holders:
            a["pose"] = next(pcyc)
        acts.append(a)
    # 같은 단어 중복 key 제거
    seen, k2 = set(), []
    for k in keys:
        if k["w"] not in seen:
            k2.append(k); seen.add(k["w"])
    sc = {"id": "s%02d" % si, "start_word": w0, "set": set_, "mood": mood, "cast": cast, "keys": k2, "acts": sorted(acts, key=lambda a: a["w"])}
    if opt.get("calm"):
        sc["calm"] = True
    scenes.append(sc)

sb = {"title": spec.get("TITLE", ""), "fps": 30, "end_pad": spec.get("END_PAD", 2.5), "lowercase": False, "scenes": scenes}
json.dump(sb, open(os.path.join(P_, "storyboard.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# chapters.json(line) → chapters_w.json(w)
cp = os.path.join(P_, "chapters.json")
if os.path.exists(cp):
    ch = json.load(open(cp, encoding="utf-8"))
    for c in ch:
        if "line" in c:
            c["w"] = first_w[c["line"]]
    json.dump(ch, open(os.path.join(P_, "chapters_w.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(scenes), "scenes")
