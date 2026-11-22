"""Frame renderer + resumable chunked video encoding.

Used through the CLI (cli.py): stills, chunks (resumable, time-boxed), join.
"""
import json
import math
import os
import re
import subprocess
import sys
import time

import numpy as np
import skia

from .paint import surface, to_array, from_array, argb, LINEAR
from .scene import Layer, Shot, W, H
from .sets import build_set
from .character import make, draw_character
from .light import MOODS, cast_shadow
from .text import draw_caption
from . import director as dr
from . import props as pr

SEG = 60   # frames per chunk file (2 s at 30 fps)


def ffmpeg_exe():
    exe = os.environ.get('TOON2D_FFMPEG')
    if exe and os.path.exists(exe):
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# ----------------------------------------------------------------------------- hold props
def hold_fn(name):
    if not name:
        return None
    if name.startswith('planet:') or name == 'earth':
        kind = 'earth' if name == 'earth' else name.split(':', 1)[1]
        return lambda cv, t, md: pr.planet_kind(cv, 0, -70, 70, kind, seed=2)
    if name.startswith('sign:'):
        txt = name.split(':', 1)[1]
        return lambda cv, t, md: pr.sign_board(cv, 0, -40, txt, s=0.45, post=False)
    if name.startswith('tag:'):
        txt = name.split(':', 1)[1]
        return lambda cv, t, md: pr.price_tag(cv, 0, -40, txt, s=0.5)
    if name.startswith('newspaper:'):
        hl = name.split(':', 1)[1].replace('|', '\n')
        return lambda cv, t, md: pr.newspaper(cv, 0, -160, s=0.45, headline=hl)
    return None


# ----------------------------------------------------------------------------- scenes
class Runtime:
    def __init__(self, project, plan):
        self.project, self.plan = project, plan
        self.words = plan['words']
        self.cache = os.path.join(project, '.cache')
        self.shots = {}

    def shot(self, i):
        if i in self.shots:
            return self.shots[i]
        sc = self.plan['scenes'][i]
        layers, meta = build_set(sc['set'], sc['mood'], self.cache, **sc.get('set_args', {}))
        groups = {}
        for c in sc['cast']:
            groups.setdefault(c.get('z', 0.97), []).append(c)
        for z, cs in groups.items():
            L = Layer('actors', z)
            for c in cs:
                L.live.append(self._actor_fn(sc, c))
            layers.append(L)
        shot = Shot(layers, sc['mood'], lambda t, sc=sc: dr.cam_from_frame(dr.frame_at(sc, t)),
                    bloom_strength=sc.get('bloom', 0.45))
        self.shots = {k: v for k, v in self.shots.items() if abs(k - i) <= 1}   # keep memory small
        self.shots[i] = shot
        return shot

    def _actor_fn(self, sc, c):
        words = self.words

        def fn(cv, t, mood):
            st = dr.actor_state(c, sc['acts'], words, t)
            if st['type'] == 'dino':                        # small friendly dinosaur (not a round-head character)
                from .prehistoric import draw_dino
                s = st.get('scale', 1.0)
                if st.get('shadow', True):
                    cast_shadow(cv, st['x'], st['y'] + 4 * s, 130 * s, 28 * s, MOODS[mood], a=0.5)
                draw_dino(cv, st['x'], st['y'], s, t + c.get('phase', 0.0), mood, dir=st.get('dir', 1), expr=st.get('expr', 'happy'),
                          col=st.get('torso', '#5ab88a'))
                return
            spec = make(st['type'], pose=st['pose'], expr=st['expr'], face=st.get('face', 0.3), dir=st.get('dir', 1))
            if st.get('talk'):
                spec['talk'] = True
            if st.get('look'):
                spec['look'] = tuple(st['look'])
            hf = hold_fn(st.get('hold'))
            if hf:
                spec['hold_fn'] = hf
                if spec['pose'] == 'stand':
                    spec['pose'] = 'hold'
            for k in ('skin', 'torso', 'accent', 'hat', 'hair'):
                if k in st:
                    spec[k] = st[k]
            s = st.get('scale', 1.0)
            if st.get('shadow', True):
                cast_shadow(cv, st['x'], st['y'] + 4 * s, 150 * s, 34 * s, MOODS[mood], a=0.5)
            draw_character(cv, spec, st['x'], st['y'], s, t + c.get('phase', 0.0), mood)
        return fn

    def scene_index(self, t):
        sc = self.plan['scenes']
        for i in range(len(sc) - 1, -1, -1):
            if t >= sc[i]['t0']:
                return i
        return 0

    def frame(self, f, subframes=None):
        fps = self.plan['fps']
        t = f / fps
        i = self.scene_index(t)
        sc = self.plan['scenes']
        half = dr.XFADE / 2 / fps
        # short cross-dissolve around scene boundaries (both sides rendered without motion blur, so it stays crisp)
        blend_with, a = None, 0.0
        if i + 1 < len(sc) and sc[i + 1]['t0'] - t < half:
            blend_with, a = i + 1, 0.5 - (sc[i + 1]['t0'] - t) / (2 * half)
        elif i > 0 and t - sc[i]['t0'] < half:
            blend_with, a = i - 1, 0.5 - (t - sc[i]['t0']) / (2 * half)
        a = a * a * (3 - 2 * a) if a > 0 else a               # smoothstep: quick through the middle
        surf = self.shot(i).render(t, subframes=1 if blend_with is not None else subframes)
        if blend_with is not None and a > 0.01:
            other = self.shot(blend_with).render(t, subframes=1)
            p = skia.Paint(); p.setAlphaf(min(1.0, a))
            surf.getCanvas().drawImage(other.makeImageSnapshot(), 0, 0, LINEAR, p)
        cap = dr.caption_at(self.plan['captions'], t)
        if cap:
            draw_caption(surf.getCanvas(), [w.lower() if self.plan['story'].get('lowercase', True) else w for w in cap['words']], t - cap['s'], hl=tuple(self.plan['story'].get('highlight', [])), hl_red=tuple(self.plan['story'].get('highlight_red', [])))
        return surf


def _plan_hash(project):
    import hashlib
    return hashlib.sha256(open(os.path.join(project, 'plan.json'), 'rb').read()).hexdigest()[:16]


def _sync_plan(project):
    """Chunks are rendered from one plan.json; if the plan changed since, the old chunks are removed."""
    d = os.path.join(project, 'chunks')
    os.makedirs(d, exist_ok=True)
    tag = os.path.join(d, 'plan.sha')
    h = _plan_hash(project)
    old = open(tag).read().strip() if os.path.exists(tag) else None
    segs = [x for x in os.listdir(d) if re.fullmatch(r'seg_\d{5}\.mp4', x)]
    if old != h and (segs or old):
        for x in segs:
            os.remove(os.path.join(d, x))
        if segs:
            print('plan.json changed since the last render: %d old segment(s) removed' % len(segs))
    with open(tag, 'w') as f:
        f.write(h)


def load(project):
    plan = json.load(open(os.path.join(project, 'plan.json'), encoding='utf-8'))
    return Runtime(project, plan)


def n_frames(plan):
    return int(math.ceil(plan['duration'] * plan['fps']))


# ----------------------------------------------------------------------------- stills
def stills(project, times, outdir=None):
    rt = load(project)
    outdir = outdir or os.path.join(project, 'stills')
    os.makedirs(outdir, exist_ok=True)
    paths = []
    times = [t for t in times if math.isfinite(t) and 0 <= t <= rt.plan['duration']]
    for t in times:
        f = int(round(t * rt.plan['fps']))
        s = rt.frame(f, subframes=1)
        p = os.path.join(outdir, 'still_%06.2fs.png' % t)
        s.makeImageSnapshot().save(p, skia.kPNG)
        paths.append(p)
    return paths


# ----------------------------------------------------------------------------- chunks
def _encode_segment(args):
    project, seg, fstart, fend, threads = args
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    rt = load(project)
    d = os.path.join(project, 'chunks')
    out = os.path.join(d, 'seg_%05d.mp4' % seg)
    tmp = out + '.part.mp4'
    fps = rt.plan['fps']
    cmd = [ffmpeg_exe(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '%dx%d' % (W, H), '-r', str(fps),
           '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
           '-threads', str(threads), '-x264-params', 'keyint=%d' % SEG, tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(fstart, fend):
        s = rt.frame(f)
        info = skia.ImageInfo.Make(W, H, skia.kRGBA_8888_ColorType, skia.kPremul_AlphaType)
        buf = bytearray(W * H * 4)
        s.readPixels(info, buf, W * 4, 0, 0)
        proc.stdin.write(buf)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('ffmpeg failed on segment %d' % seg)
    os.replace(tmp, out)
    return seg, fend - fstart, time.time() - t0


def chunks(project, budget=200.0, workers=2, start=None, end=None):
    """Render missing segments until the time budget is used; re-run to continue. Returns (done, total)."""
    import multiprocessing as mp
    t_budget = time.time()                       # the set bake counts against the budget (phone time limits)
    workers = max(1, min(int(workers), os.cpu_count() or 1))
    start = 0.0 if start is None else start
    if not (math.isfinite(start) and start >= 0 and (end is None or (math.isfinite(end) and end > start))):
        raise SystemExit('--start/--end must be finite seconds >= 0 with end > start')
    _sync_plan(project)
    rt = load(project)
    nf = n_frames(rt.plan)
    fps = rt.plan['fps']
    f0 = int(start * fps)
    f1 = min(nf, int(math.ceil(end * fps)) if end else nf)
    d = os.path.join(project, 'chunks')
    os.makedirs(d, exist_ok=True)
    segs = []
    for k, fs in enumerate(range(f0, f1, SEG)):
        seg = fs // SEG
        if not os.path.exists(os.path.join(d, 'seg_%05d.mp4' % seg)):
            segs.append((project, seg, fs, min(fs + SEG, f1), 1))
    total = len(range(f0, f1, SEG))
    # bake every set in this process first so workers only read the cache
    for i in range(len(rt.plan['scenes'])):
        rt.shot(i)
    if segs and time.time() - t_budget > budget * 0.6:
        print('set bake done (%.0f s, cached for the next run). segments: %d/%d present. run again to continue'
              % (time.time() - t_budget, total - len(segs), total))
        return total - len(segs), total
    t_start = time.time()
    done_now, frames_now = 0, 0
    if not segs:
        print('all %d segments present. DONE' % total)
        return total, total
    est = None
    with mp.get_context('spawn').Pool(workers) as pool:
        pending = []
        it = iter(segs)
        def submit():
            try:
                a = next(it)
            except StopIteration:
                return False
            pending.append(pool.apply_async(_encode_segment, (a,)))
            return True
        for _ in range(workers):
            submit()
        while pending:
            r = pending.pop(0).get()
            done_now += 1
            frames_now += r[1]
            el = time.time() - t_start
            per_frame = el / frames_now * 1.0
            print('segment %d done (%d frames, %.1fs) | %.3f s/frame wall' % (r[0], r[1], r[2], per_frame), flush=True)
            # only start another segment if it will finish inside the budget
            seg_time = r[2]
            if time.time() - t_budget + seg_time * 1.15 < budget:
                submit()
    have = len([x for x in os.listdir(d) if re.fullmatch(r'seg_\d{5}\.mp4', x)])
    print('segments: %d/%d present. %s' % (have, total, 'DONE' if have >= total else 'run again to continue'))
    return have, total


def join(project, out_name='final.mp4', end=None):
    from . import audio
    rt = load(project)
    d = os.path.join(project, 'chunks')
    nf = n_frames(rt.plan)
    dur = rt.plan['duration']
    if end:
        nf = min(nf, int(math.ceil(end * rt.plan['fps'])))
        dur = min(dur, end)
    tag = os.path.join(d, 'plan.sha')
    if not os.path.exists(tag) or open(tag).read().strip() != _plan_hash(project):
        raise SystemExit('plan.json changed since the last render: run render again until DONE, then join')
    segs = sorted(x for x in os.listdir(d) if re.fullmatch(r'seg_\d{5}\.mp4', x))
    need = int(math.ceil(nf / SEG))
    if len(segs) < need:
        raise SystemExit('missing segments: %d/%d (run chunks again)' % (len(segs), need))
    lst = os.path.join(d, 'list.txt')
    with open(lst, 'w', encoding='utf-8') as f:
        for s in segs[:need]:
            f.write("file '%s'\n" % s)
    video = os.path.join(project, '_video.mp4')
    subprocess.run([ffmpeg_exe(), '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', video], check=True)
    mix = audio.build_mix(project, dur)
    out = os.path.join(project, out_name)
    subprocess.run([ffmpeg_exe(), '-v', 'error', '-y', '-i', video, '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-t', '%.3f' % dur, '-map_metadata', '-1', '-fflags', '+bitexact',
                    '-movflags', '+faststart', out], check=True)
    os.remove(video)
    return out
