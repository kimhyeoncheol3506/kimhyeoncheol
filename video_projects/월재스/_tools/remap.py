#!/usr/bin/env python3
"""대본을 고친 뒤: 예전 sentences.json과 새 문장을 'say' 글자로 맞춰 tts/fix/sXXXX.wav 번호를 옮긴다(바뀐 문장만 새로 생성하면 됨).
  python remap.py <작업폴더>   (build.py chunks 를 돌리기 전에 old 복사본을 tts/sentences_old.json 으로 둔다)"""
import json, os, sys
w = sys.argv[1]; t = os.path.join(w, "tts"); fx = os.path.join(t, "fix")
old = json.load(open(os.path.join(t, "sentences_old.json"), encoding="utf-8"))
new = json.load(open(os.path.join(t, "sentences.json"), encoding="utf-8"))
chk = json.load(open(os.path.join(t, "check.json"))) if os.path.exists(os.path.join(t, "check.json")) else {}
pool = {}
for s in old:
    pool.setdefault(s["say"], []).append(s["id"])
tmp = os.path.join(fx, "_old"); os.makedirs(tmp, exist_ok=True)
for f in os.listdir(fx):
    if f.endswith(".wav"):
        os.replace(os.path.join(fx, f), os.path.join(tmp, f))
nchk, miss = {}, 0
for s in new:
    ids = pool.get(s["say"])
    if ids:
        o = ids.pop(0)
        os.replace(os.path.join(tmp, "s%04d.wav" % o), os.path.join(fx, "s%04d.wav" % s["id"]))
        if str(o) in chk:
            nchk[str(s["id"])] = chk[str(o)]
    else:
        miss += 1
json.dump(nchk, open(os.path.join(t, "check.json"), "w", encoding="utf-8"), ensure_ascii=False)
print("옮김 %d, 새로 만들 문장 %d" % (len(new) - miss, miss))
