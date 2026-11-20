# -*- coding: utf-8 -*-
import json, os, shutil, subprocess
R = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(R, "..", "samples", "B_voynich")
P = os.path.join(R, "engine", "public")
w = json.load(open(os.path.join(S, "timings.json"), encoding="utf-8"))
json.dump([x["word"] for x in w], open(os.path.join(P, "script.json"), "w", encoding="utf-8"), ensure_ascii=False)
json.dump([{"word": x["word"].rstrip(".,!?"), "start": x["start"], "end": x["end"]} for x in w], open(os.path.join(P, "words.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
shutil.copy(os.path.join(S, "voice.wav"), os.path.join(P, "voice.wav"))
shutil.copy(os.path.join(R, "..", "toon2d_ko", "toon2d", "fonts", "Pretendard-ExtraBold.otf"), os.path.join(P, "Pretendard-ExtraBold.otf"))
os.makedirs(os.path.join(R, "sfx"), exist_ok=True)
subprocess.run(["python", os.path.join(R, "tools", "voice", "make_sfx.py"), os.path.join(R, "sfx")], check=False)
ev = [{"t": 4.75, "sfx": "stamp", "db": -2}, {"t": 5.85, "sfx": "whoosh", "db": -4},
      {"t": 10.25, "sfx": "whoosh", "db": -4}, {"t": 13.12, "sfx": "impact", "db": 0}]
json.dump(ev, open(os.path.join(R, "sfx_b.json"), "w"))
subprocess.run(["python", os.path.join(R, "tools", "mix_sfx.py"), os.path.join(P, "voice.wav"), os.path.join(R, "sfx_b.json"), os.path.join(P, "mix.wav"), os.path.join(R, "sfx")], check=True)
print(os.listdir(os.path.join(R, "sfx")))
