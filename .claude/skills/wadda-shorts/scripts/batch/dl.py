import json, os, subprocess, sys, glob
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding="utf-8")
B = os.path.dirname(os.path.abspath(__file__))
CL = os.path.join(B, "clips"); os.makedirs(CL, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bins import YTDLP, FFD
env = dict(os.environ, TEMP=CL, TMP=CL)
S = json.load(open(os.path.join(B, "segments.json"), encoding="utf-8"))
jobs = []
for person, segs in S.items():
    for c in segs:
        name = "%s_%d_%d" % (c["id"], int(c["in"]), int(c["out"]))
        c["file"] = "clips/" + name + ".mp4"
        a, b = max(0, c["in"] - 1.0), c["out"] + 1.0
        c["pad"] = round(c["in"] - a, 2)
        jobs.append((name, c["id"], a, b))
json.dump(S, open(os.path.join(B, "segments.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def fmt(t):
    return "%d:%02d:%05.2f" % (int(t // 3600), int(t % 3600 // 60), t % 60)


def run(j):
    name, vid, a, b = j
    out = os.path.join(CL, name + ".mp4")
    if os.path.exists(out) and os.path.getsize(out) > 50000:
        return name, "skip"
    r = subprocess.run([YTDLP, "--ffmpeg-location", FFD, "-f", "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
                        "--download-sections", "*%s-%s" % (fmt(a), fmt(b)), "--force-keyframes-at-cuts", "--merge-output-format", "mp4",
                        "-o", out, "https://www.youtube.com/watch?v=" + vid], env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = os.path.exists(out)
    return name, "ok" if ok else ("FAIL " + (r.stderr or "")[-200:])


with ThreadPoolExecutor(4) as ex:
    for i, (n, st) in enumerate(ex.map(run, jobs), 1):
        print(i, len(jobs), n, st, flush=True)
