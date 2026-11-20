#!/usr/bin/env python3
"""summarize.py <analysis_dir> -> FORENSICS-AUTO.md (numbers only; mark everything MEASURED)."""
import json, sys, os, re
d = sys.argv[1]; L = lambda n: json.load(open(os.path.join(d, n))) if os.path.exists(os.path.join(d, n)) else None
o = ['# FORENSICS-AUTO (MEASURED)']
pr = L('probe.json')
if pr:
    vs = [s for s in pr['streams'] if s['codec_type'] == 'video']; au = [s for s in pr['streams'] if s['codec_type'] == 'audio']
    if vs: o.append(f"- video: {vs[0]['width']}x{vs[0]['height']} @ {vs[0].get('r_frame_rate')} codec {vs[0]['codec_name']}, duration {float(pr['format']['duration']):.1f}s")
    o.append(f"- audio: {'yes ' + au[0]['codec_name'] if au else 'none'}")
ln = os.path.join(d, 'loudnorm.txt')
if os.path.exists(ln):
    m = re.search(r'"input_i"\s*:\s*"([-\d.]+)"', open(ln).read()); o.append(f"- integrated loudness: {m.group(1)} LUFS" if m else '')
sc = L('scenes.json')
if sc: o.append(f"- shots: {sc['n_shots']} (avg {sc['avg']}s, median {sc['median']}s, min {sc['min']}s, max {sc['max']}s) -> {'continuous/few cuts' if sc['n_shots'] < sc['duration']/12 else 'cut-driven'}")
pa = L('palette.json')
if pa: o.append('- palette: ' + ', '.join(f"{c['hex']} ({int(c['share']*100)}%)" for c in pa['palette'][:6]) + f"; saturation {pa['mean_saturation']}, brightness {pa['mean_brightness']}, bg guess {pa['corner_color_guess']}, extreme contrast {pa['contrast_ratio_extremes']}:1")
mo = L('motion.json')
if mo: o.append(f"- motion: mean energy {mo['mean_energy']}, static ratio {mo['static_ratio']}, median pan/step x={mo['median_abs_pan_x_per_step']} y={mo['median_abs_pan_y_per_step']}, shake std x={mo['shake_std_x']} y={mo['shake_std_y']}, energy peaks (beats) {len(mo['energy_peaks_s'])}")
au = L('audio_onsets.json')
if au and 'summary' in au: s = au['summary']; o.append(f"- audio onsets: {s['onsets']} ({s['per_minute']}/min) classes {s['class_counts']}, mean RMS {s['rms_db_mean']} dB (includes speech)")
o.append('\nNext: view sheets/ (LOOK at them), then write FORENSICS.md judgments (MEASURED vs ESTIMATED) and STYLE-SPEC.md.')
open(os.path.join(d, 'FORENSICS-AUTO.md'), 'w').write('\n'.join(x for x in o if x)); print('\n'.join(x for x in o if x))
