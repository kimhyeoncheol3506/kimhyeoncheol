# -*- coding: utf-8 -*-
"""대본 수정 후 음성 파일 재배치: python3 remap.py <old.json> <new.json> <wav폴더>
같은 TTS 문장은 기존 wav를 새 번호로 옮기고(2단계 이동), 새로 생긴 문장만 비워 둔다 → 음성 대기열이 빈 것만 생성."""
import json, os, sys, shutil
old, new, W = sys.argv[1:4]
key = lambda d: [(f"{i:02d}_{j:02d}", x[0]) for i, s in enumerate(d["sections"]) for j, x in enumerate(s["sentences"])]
O, N = key(json.load(open(old, encoding="utf-8"))), key(json.load(open(new, encoding="utf-8")))
pool = {}
for k, t in O:
    if os.path.exists(f"{W}/{k}.wav"): pool.setdefault(t, []).append(k)
tmp = f"{W}/_remap"; os.makedirs(tmp, exist_ok=True)
for k, t in O:
    if os.path.exists(f"{W}/{k}.wav"): shutil.move(f"{W}/{k}.wav", f"{tmp}/{k}.wav")
moved, missing = 0, []
for k, t in N:
    if pool.get(t):
        src = pool[t].pop(0); shutil.move(f"{tmp}/{src}.wav", f"{W}/{k}.wav"); moved += 1
    else: missing.append(k)
for f in os.listdir(tmp): os.remove(f"{tmp}/{f}")
os.rmdir(tmp); print("옮김", moved, "새로 만들 것", missing)
