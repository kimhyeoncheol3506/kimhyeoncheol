#!/usr/bin/env python3
"""usage: mix_sfx.py voice.wav events.json out.wav [sfxdir=sfx]
events.json = [{"t":1.16,"sfx":"impact","db":-6}, ...]  (db = extra attenuation; SFX files peak at -3 dBFS)
Rules baked in: SFX are SPARSE and QUIET. Default offset -14 dB under the voice, plus sidechain ducking while the voice speaks,
so SFX never fight the voiceover. Output length = voice length."""
import sys, json, subprocess
voice, ev, out = sys.argv[1:4]; sfxdir = sys.argv[4] if len(sys.argv) > 4 else "sfx"
events = json.load(open(ev))
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",voice]))
ins = ["-i", voice]; fl = []; lab = []
for i, e in enumerate(events, 1):
    ins += ["-i", f"{sfxdir}/{e['sfx']}.wav"]
    ms = int(e["t"] * 1000)
    fl.append(f"[{i}:a]volume={e.get('db',-4)-14}dB,adelay={ms}|{ms}[s{i}]"); lab.append(f"[s{i}]")
fl.append("[0:a]asplit=2[v][vk]")
if lab:
    fl.append("".join(lab) + f"amix=inputs={len(lab)}:normalize=0,apad=whole_dur={dur}[sx]")
    fl.append("[sx][vk]sidechaincompress=threshold=0.02:ratio=8:attack=5:release=250[sd]")
    fl.append("[v][sd]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
else:
    fl.append("[v]anull[a]")
subprocess.run(["ffmpeg","-y","-v","error",*ins,"-filter_complex",";".join(fl),"-map","[a]","-t",str(dur),"-ar","48000",out], check=True)
print("mixed", out, round(dur,2), "s,", len(events), "sfx events")
