# -*- coding: utf-8 -*-
"""그림 변화 간격 검사 (Stickman Video Director 의 '3초 규칙'을 toon2d 에 맞춘 것).
카메라 이동·줌·자막 교체는 '그림 변화'로 치지 않는다. 장면 전환과 인물 연기(acts: pose/expr/hold/x/talk)만 센다.
  1) 첫 3초 안에 눈에 보이는 그림 변화(인물 표정·자세·소품, 또는 장면 전환)가 최소 1번 (0.3~3.0초)
  2) 같은 그림 상태가 3초를 넘기지 않기 (넘는 구간을 시간과 대사로 출력 → 그 단어에 act 추가)
사용: python pace_check.py <프로젝트> [--max 3.0]      (plan.json, words.json 필요. plan 다음, stills 전에 실행)
종료코드 0 = 통과, 1 = 고칠 곳 있음(렌더 전 storyboard 수정 권장. calm 장면은 경고만).
"""
import argparse, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("proj")
ap.add_argument("--max", type=float, default=3.0)
a = ap.parse_args()
P = os.path.abspath(a.proj)
plan = json.load(open(os.path.join(P, "plan.json"), encoding="utf-8"))
words = json.load(open(os.path.join(P, "words.json"), encoding="utf-8"))
dur = float(plan["duration"])
KEYS = ("pose", "expr", "hold", "x", "y", "talk", "dir", "face")

ev = []  # (t, 종류, calm)
for s in plan["scenes"]:
    ev.append((float(s["t0"]), "장면:" + s["id"], s.get("calm", False)))
    for act in s.get("acts", []):
        if any(k in act for k in KEYS):
            w = act.get("w", 0)
            t = float(act.get("t", words[min(w, len(words) - 1)]["s"]))
            what = ",".join("%s=%s" % (k, act[k]) for k in KEYS if k in act)
            ev.append((t, "%s %s" % (act.get("who", "?"), what), s.get("calm", False)))
ev.sort(key=lambda e: e[0])
times = [e[0] for e in ev] + [dur]

bad = 0
first = [e for e in ev if 0.3 <= e[0] <= 3.0]
if first:
    print("OK  첫 3초 그림 변화: %.2fs %s" % (first[0][0], first[0][1]))
else:
    print("FAIL 첫 3초(0.3~3.0s)에 인물 연기/장면 변화가 없음 → 첫 문장 단어에 expr/pose/hold act 추가")
    bad += 1


def text_at(t0, t1):
    return " ".join(w["w"] for w in words if t0 <= w["s"] < t1)


for i in range(len(ev)):
    t0, t1 = ev[i][0], times[i + 1]
    if t1 - t0 > a.max:
        calm = ev[i][2]
        tag = "WARN" if calm else "FAIL"
        if not calm:
            bad += 1
        print("%s %.1f~%.1fs (%.1f초) 그림 그대로 [%s] 대사: %s" % (tag, t0, t1, t1 - t0, ev[i][1], text_at(t0, t1)[:60]))
n = len(ev)
print("그림 변화 %d회 / %.0f초 = 평균 %.1f초마다" % (n, dur, dur / max(1, n)))
print("PACE OK" if not bad else "PACE: %d곳 수정 필요" % bad)
sys.exit(1 if bad else 0)
