#!/usr/bin/env python3
"""usage: prep_voice.py <voiceover.(mp3|wav)> <script.txt> [workdir=02-videos/current]
1) trims silent pauses (fast pacing)  2) forced-aligns the script to the audio  3) writes engine/public/{words.json,script.json,voice.wav}
Numbers/symbols/names must be spelled as spoken in <workdir>/script_spoken.txt? NO: put overrides in <workdir>/spoken.json next to script.txt
  e.g. {"1.7":"one point seven","Nvidia":"in video"}; the tool prints UNKNOWN WORDS if the aligner needs them."""
import sys, os, re, json, shutil, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
voice, script = sys.argv[1], sys.argv[2]; work = sys.argv[3] if len(sys.argv) > 3 else os.path.join(root, "02-videos", "current")
os.makedirs(work, exist_ok=True); sp = os.path.join(work, "script.txt")
if os.path.abspath(script) != os.path.abspath(sp): shutil.copy(script, sp)
v = os.path.join(root, "tools", "voice")
subprocess.run([sys.executable, os.path.join(v, "trim.py"), voice, os.path.join(work, "out")], check=True)
wav = os.path.join(work, "out", "voiceover-trimmed.wav")
r = subprocess.run([sys.executable, "-I", os.path.join(v, "align.py"), wav, sp, os.path.join(work, "words.json")])
if r.returncode: sys.exit("ALIGN FAILED: add spoken overrides to " + os.path.join(work, "spoken.json") + " and rerun")
words = json.load(open(os.path.join(work, "words.json"))); toks = open(sp).read().split()
if len(toks) != len(words): print(f"WARNING: script tokens {len(toks)} != aligned words {len(words)}; fix script spacing/hyphens so captions match"); 
pub = os.path.join(root, "engine", "public"); os.makedirs(pub, exist_ok=True)
shutil.copy(os.path.join(work, "words.json"), os.path.join(pub, "words.json")); json.dump(toks, open(os.path.join(pub, "script.json"), "w")); shutil.copy(wav, os.path.join(pub, "voice.wav"))
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",wav]))
print(f"OK words={len(words)} duration={dur:.2f}s frames={int(dur*30)+3} -> set durationInFrames in engine/src/Root.tsx")
