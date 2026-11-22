# -*- coding: utf-8 -*-
"""장면 분위기(plan.json mood)에 맞춰 BGM 을 2~4곡으로 전환해 믹스.
night/day/interior = 긴장(T), sunset/dawn/golden/dream = 슬픔(S). 음성 나올 때 음악이 살짝 내려가고(사이드체인), 쉼에서 올라옴.
사용: python bgm_mix.py <plan.json> <입력mp4(무음악)> <출력mp4> <에피소드번호>
"""
import json, os, subprocess, sys, glob
FF = "ffmpeg"
plan_p, src, out, ep = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
MD = os.environ.get("BGM_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "music")
T = sorted(glob.glob(os.path.join(MD, "T_*.mp3")))
S = sorted(glob.glob(os.path.join(MD, "S_*.mp3"))) + [os.path.join(MD, f) for f in ("My_Dear_One.mp3", "Spinning_And_Swirling.mp3")]
p = json.load(open(plan_p, encoding="utf-8"))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
cat = lambda m: "S" if m in ("sunset", "dawn", "golden", "dream") else "T"
segs = []
for s in p["scenes"]:
    c = cat(s.get("mood", "night"))
    t0 = float(s.get("t0", 0))
    if segs and segs[-1][1] == c:
        continue
    segs.append([t0, c])
# 짧은 구간(18초 미만)은 앞 구간에 흡수
merged = []
for i, (t0, c) in enumerate(segs):
    t1 = segs[i + 1][0] if i + 1 < len(segs) else dur
    if merged and (t1 - t0 < 18 or merged[-1][1] == c):
        continue
    merged.append([t0, c])
# 다시 같은 카테고리 연속 제거
m2 = []
for t0, c in merged:
    if m2 and m2[-1][1] == c:
        continue
    m2.append([t0, c])
m2[0][0] = 0.0
ti, si = ep * 2, ep * 3
args = [FF, "-v", "error", "-y", "-i", src]
fil, labels = [], []
XF = 1.6
for i, (t0, c) in enumerate(m2):
    t1 = m2[i + 1][0] if i + 1 < len(m2) else dur
    if c == "T":
        f = T[ti % len(T)]; ti += 1
    else:
        f = S[si % len(S)]; si += 1
    args += ["-stream_loop", "-1", "-i", f]
    k = i + 1
    L = (t1 - t0) + (XF if i + 1 < len(m2) else 0)
    fo = 3.0 if i + 1 == len(m2) else XF
    fil.append("[%d:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=%.2f,afade=t=out:st=%.3f:d=%.2f,adelay=%d|%d[m%d]" % (k, L, 1.5 if i == 0 else XF, max(0, L - fo), fo, int(t0 * 1000), int(t0 * 1000), i))
    labels.append("[m%d]" % i)
    print("seg %5.1f-%5.1f %s %s" % (t0, t1, c, os.path.basename(f)))
fil.append("%samix=inputs=%d:normalize=0:duration=longest,volume=0.55[mus]" % ("".join(labels), len(labels)))
fil.append("[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v1][v2]")
fil.append("[mus][v1]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=450:makeup=1[duck]")
fil.append("[v2][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
args += ["-filter_complex", ";".join(fil), "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", "%.3f" % dur, out]
subprocess.run(args, check=True)
print("OUT", out)
