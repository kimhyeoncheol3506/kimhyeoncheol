#!/usr/bin/env python3
"""Trim only short silent pauses. usage: trim.py in.mp3 outdir
 - pauses < 0.20s are untouched
 - longer pauses are shortened to 0.10 + 0.30*(pause-0.10) (natural rhythm kept)
 - leading/trailing silence trimmed to 0.05s
Writes: voiceover-trimmed.wav (48k mono, used by the video), voiceover-trimmed.mp3 (for CapCut), cuts.json"""
import subprocess, re, json, sys, os
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]))
log = subprocess.run(['ffmpeg','-hide_banner','-i',src,'-af','silencedetect=noise=-38dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]
en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
if len(en)<len(st): en.append(dur)
keep=[]; cuts=[]; cur=0.0
for s,e in zip(st,en):
    p=e-s
    if s<0.05: # leading
        keep_len=0.05
    elif e>=dur-0.01: # trailing
        keep_len=0.05
    elif p<0.20: continue
    else: keep_len=0.10+0.30*(p-0.10)
    if p-keep_len<0.02: continue
    a=s+keep_len/2; b=e-keep_len/2
    keep.append((cur,a)); cur=b
    cuts.append({'orig_pause_start':round(s,3),'orig_pause_len':round(p,3),'new_pause_len':round(keep_len,3),'removed':round(p-keep_len,3)})
keep.append((cur,dur))
fc=''; n=0
for i,(a,b) in enumerate(keep):
    fc+=f"[0:a]atrim={a:.4f}:{b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.004,afade=t=out:st={max(0,b-a-0.004):.4f}:d=0.004[a{i}];"
fc+=''.join(f'[a{i}]' for i in range(len(keep)))+f'concat=n={len(keep)}:v=0:a=1[o]'
subprocess.run(['ffmpeg','-y','-v','error','-i',src,'-filter_complex',fc,'-map','[o]','-ar','48000','-ac','1',f'{out}/voiceover-trimmed.wav'],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',f'{out}/voiceover-trimmed.wav','-b:a','256k',f'{out}/voiceover-trimmed.mp3'],check=True)
nd=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{out}/voiceover-trimmed.wav']))
json.dump({'original_duration':round(dur,3),'trimmed_duration':round(nd,3),'removed_total':round(dur-nd,3),'cuts':cuts},open(f'{out}/cuts.json','w'),indent=1)
print(f'original {dur:.3f}s -> trimmed {nd:.3f}s (removed {dur-nd:.3f}s in {len(cuts)} cuts)')
for c in cuts: print(c)
