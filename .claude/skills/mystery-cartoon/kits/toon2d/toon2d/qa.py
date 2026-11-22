"""Checks for a project: plan pacing, captions, still tone, final video format and loudness."""
import glob
import json
import os
import re
import subprocess

import numpy as np

from .words import ffmpeg_exe
from . import checks
from .text import text_width, CAP_SIZE, CAP_MAX_W


def _probe(path):
    r = subprocess.run([ffmpeg_exe(), '-hide_banner', '-i', path], stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
    s = r.stderr
    m = re.search(r'(\d{3,4})x(\d{3,4})', s)
    fps = re.search(r'([\d.]+) fps', s)
    d = re.search(r'Duration: (\d+):(\d+):([\d.]+)', s)
    dur = int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else 0
    return (int(m.group(1)), int(m.group(2))) if m else None, float(fps.group(1)) if fps else None, dur


def run(project):
    fails, warns = [], []
    ok = lambda c, msg, hard=True: None if c else (fails if hard else warns).append(msg)
    p = json.load(open(os.path.join(project, 'plan.json'), encoding='utf-8'))
    words = p['words']
    dur = p['duration']
    nb = sum(len(s['beats']) for s in p['scenes'])
    bpm = nb / dur * 60
    print('duration %.2f s | %d scenes | %.1f framing beats/min | %d captions' % (dur, len(p['scenes']), bpm, len(p['captions'])))
    ok(30 <= dur <= 70, 'duration %.1f s outside 30-70 s' % dur, hard=False)
    ok(40 <= bpm <= 70, 'framing beats %.1f/min outside 40-70' % bpm, hard=False)
    ok(words[0]['s'] <= 0.15, 'voice starts at %.2f s (should be ~0)' % words[0]['s'], hard=False)
    ok(dur - words[-1]['e'] <= 1.2, 'tail after last word %.2f s (keep <= ~0.7)' % (dur - words[-1]['e']), hard=False)
    for c in p['captions']:
        ok(len(c['words']) <= 2, 'caption with %d words: %s' % (len(c['words']), c['words']))
        for ln in (' '.join(c['words']),):
            if text_width(ln.lower(), CAP_SIZE) > CAP_MAX_W and len(c['words']) == 1:
                warns.append('caption wider than safe zone: %s' % ln)
    # push-in vs pull-out share from the plan
    ins = outs = 0
    for s in p['scenes']:
        for a, b in zip(s['beats'][:-1], s['beats'][1:]):
            if b['frame'][2] < a['frame'][2] * 0.98:
                ins += 1
            elif b['frame'][2] > a['frame'][2] * 1.02:
                outs += 1
    print('moves: %d push-in, %d pull-out' % (ins, outs))
    ok(ins >= outs, 'more pull-outs than push-ins', hard=False)
    # faces sliced by a frame edge (checked on every frame of the plan; brief passes during a move are ignored)
    from .director import face_report
    cuts = face_report(p)
    print('faces cut by a frame edge: %d span(s)' % len(cuts))
    for a, b, who in cuts:
        fails.append('face of "%s" cut by the frame edge at %.2f-%.2f s' % (who, a, b))
    stills = sorted(glob.glob(os.path.join(project, 'stills', '*.png')))
    if stills:
        from PIL import Image
        offs = 0
        for s in stills:
            m = checks.measure(np.asarray(Image.open(s).convert('RGB')))
            txt, bad = checks.report(m)
            offs += bad
        print('stills: %d checked, %d metric(s) outside the style ranges (info only, moods differ on purpose)' % (len(stills), offs))
    final = os.path.join(project, 'final.mp4')
    if os.path.exists(final):
        size, fps, vdur = _probe(final)
        print('final.mp4: %s @ %s fps, %.2f s' % (size, fps, vdur))
        ok(size == (1080, 1920), 'resolution %s (need 1080x1920)' % (size,))
        ok(fps and abs(fps - 30) < 0.01, 'fps %s (need 30)' % fps)
        from .audio import measure_lufs, is_silent
        if is_silent(final):
            print('loudness: silent track, loudness not applicable')
        else:
            lufs, tp = measure_lufs(final)
            print('loudness: %.1f LUFS, true peak %.1f dBTP' % (lufs, tp))
            ok(abs(lufs + 14) <= 1.0, 'loudness %.1f LUFS (target -14)' % lufs)
            ok(tp <= -0.9, 'true peak %.1f dBTP (max -1)' % tp)
    else:
        warns.append('final.mp4 not rendered yet')
    for w in warns:
        print('WARN', w)
    for f in fails:
        print('FAIL', f)
    print('CHECK %s' % ('FAILED' if fails else ('PASSED' if os.path.exists(final) else 'PASSED (plan only: final.mp4 not rendered yet)')))
    return 1 if fails else 0
