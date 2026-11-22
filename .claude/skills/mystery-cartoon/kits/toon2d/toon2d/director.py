"""Storyboard + word timings -> a timed plan: scenes, camera beats, actor tracks, caption chunks.

The storyboard (written per video) says WHAT is on screen per sentence; the director decides WHEN the camera moves:
- a new framing on (almost) every sentence start, plus automatic beats so framings change every ~0.86 s,
- moves of 19 frames with symmetric ease-in-out, landing on word onsets,
- a slow push between moves (never still), ~2 push-ins per pull-out,
- fewer beats (longer holds) in scenes marked "calm" and in the second half of the video,
- cross-dissolves of 5 frames between scenes (set or mood changes),
- every framing keeps faces whole: beats are corrected at plan time, small leftovers by a smoothed offset track.
"""
import json
import math
import os

from .text import text_width, CAP_SIZE, CAP_MAX_W

FPS = 30
MOVE = 19 / FPS            # move duration (s)
XFADE = 5                  # frames of cross-dissolve between scenes (short: two scenes never mush)
BEAT = 0.86                # target seconds between framings
DRIFT = 0.035              # slow push per second between moves (fraction of frame height)


def ease(u):
    u = max(0.0, min(1.0, u))
    return 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def onset(words, i):
    i = max(0, min(len(words) - 1, i))
    return words[i]['s']


def resolve_frame(fr, cast, default=(540, 960, 1920)):
    """Frame spec -> (cx, cy, h) in subject-plane pixels."""
    if fr is None:
        return default
    if isinstance(fr, (list, tuple)):
        return tuple(float(v) for v in fr)
    if fr == 'wide':
        return (540.0, 960.0, 1920.0)
    if fr == 'two' or fr == 'all':
        xs = [c['x'] for c in cast] or [540]
        ys = [c['y'] - 300 * c.get('scale', 1) for c in cast] or [960]
        sc = max([c.get('scale', 1) for c in cast] or [1])
        w = max(xs) - min(xs) + 700 * sc
        return ((max(xs) + min(xs)) / 2, sum(ys) / len(ys) + 120 * sc, max(1100 * sc, w * 16 / 9))
    for c in cast:
        if c['id'] == fr:
            s = c.get('scale', 1)
            return (float(c['x']), float(c['y'] - 330 * s), 1250.0 * s)
        if fr.startswith(c['id'] + ':'):
            s = c.get('scale', 1)
            kind = fr.split(':', 1)[1]
            if kind == 'face':
                return (float(c['x']), float(c['y'] - 380 * s), 760.0 * s)
            if kind == 'full':
                return (float(c['x']), float(c['y'] - 260 * s), 1800.0 * s)
    raise ValueError('unknown frame %r' % (fr,))


def plan(story, words, total=None):
    n = len(words)
    end_t = (total if total else words[-1]['e']) + story.get('end_pad', 0.68)
    scenes = story['scenes']
    out_scenes = []
    for si, sc in enumerate(scenes):
        t0 = 0.0 if si == 0 else onset(words, sc['start_word'])
        t1 = end_t if si == len(scenes) - 1 else onset(words, scenes[si + 1]['start_word'])
        cast = sc.get('cast', [])
        keys = sorted(sc.get('keys', []), key=lambda k: k['w'])
        # author keys -> (time, frame)
        kf = []
        for k in keys:
            t = 0.0 if (si == 0 and k['w'] == sc['start_word']) else onset(words, k['w'])
            kf.append([t, resolve_frame(k.get('frame'), cast), k.get('roll', 0.0), True])
        if not kf or kf[0][0] > t0 + 0.05:
            kf.insert(0, [t0, resolve_frame(sc.get('frame', 'two' if cast else 'wide'), cast), 0.0, True])
        # sentence starts inside the scene also get a beat when no author key is near
        ws = [i for i in range(n) if t0 <= words[i]['s'] < t1]
        sent_starts = [i for i in ws if i == 0 or words[i]['sent'] != words[i - 1]['sent']]
        calm = sc.get('calm', False)
        # automatic beats
        auto = []
        pattern = ['in', 'in_side', 'in', 'out', 'in_side_r', 'in', 'in', 'in_side']
        pi = si * 3
        allk = sorted(kf, key=lambda k: k[0])
        bounds = [k[0] for k in allk] + [t1]
        for a, b in zip(bounds[:-1], bounds[1:]):
            frac = a / max(1e-3, end_t)
            beat = BEAT * (1.25 if frac > 0.45 else 1.0) * (1.7 if calm else 1.0)
            t = a + beat
            while t < b - beat * 0.55:
                cands = [words[i]['s'] for i in ws if abs(words[i]['s'] - t) < 0.4 and words[i]['s'] - a > 0.45 and b - words[i]['s'] > 0.4]
                if cands:
                    tt = min(cands, key=lambda s: abs(s - t))
                    auto.append([tt, pattern[pi % len(pattern)], 0.0, False])
                    pi += 1
                    t = tt + beat
                else:
                    t += 0.2
        for i in sent_starts:
            st = words[i]['s']
            if all(abs(st - k[0]) > 0.5 for k in allk + auto) and st - t0 > 0.4:
                auto.append([st, pattern[pi % len(pattern)], 0.0, False])
                pi += 1
        allk = sorted(allk + auto, key=lambda k: k[0])
        # resolve relative beats into absolute frames
        prev = allk[0][1]
        res = []
        tmp = dict(cast=cast, acts=sc.get('acts', []))
        for bi, (t, fr, roll, author) in enumerate(allk):
            if isinstance(fr, str):
                cx, cy, h = prev
                if fr == 'in':
                    fr = (cx, cy - h * 0.03, h * 0.84)
                elif fr == 'out':
                    fr = (cx, cy + h * 0.02, h * 1.14)
                elif fr == 'in_side':
                    fr = (cx - h * 0.06, cy, h * 0.88)
                elif fr == 'in_side_r':
                    fr = (cx + h * 0.06, cy, h * 0.88)
                fr = (fr[0], fr[1], min(2300.0, fr[2]))
            fr = (fr[0], fr[1], max(H_MIN, fr[2]))
            if res and abs(fr[2] - prev[2]) < 1.0 and math.hypot(fr[0] - prev[0], fr[1] - prev[1]) < 20:
                # already at the tightest framing: make the beat a small sideways reframe instead of no move
                side = 1 if len(res) % 2 else -1
                fr = (fr[0] + side * 0.07 * fr[2], fr[1] - 0.02 * fr[2], fr[2])
            t_next = allk[bi + 1][0] if bi + 1 < len(allk) else t1
            fr = beat_safe(tmp, words, tuple(fr), roll, t, t_next)
            fr = inside_set(fr)
            res.append(dict(t=round(t, 3), frame=[round(v, 1) for v in fr], roll=roll, author=author))
            prev = fr
        scd = dict(id=sc.get('id', str(si)), t0=round(t0, 3), t1=round(t1, 3), set=sc['set'], mood=sc['mood'],
                   set_args=sc.get('set_args', {}), cast=cast, acts=sc.get('acts', []), live=sc.get('live', []),
                   beats=res, calm=calm)
        make_safe_track(scd, words, story.get('fps', FPS))
        out_scenes.append(scd)
    return dict(fps=story.get('fps', FPS), duration=round(end_t, 3), scenes=out_scenes, captions=chunk_captions(words, end_t))


# ----------------------------------------------------------------------------- camera evaluation
def frame_at(scene, t):
    """Camera frame (cx, cy, h, roll) at time t: the beat camera plus the face-safety offset track."""
    fr = _beat_frame(scene, t)
    sf = scene.get('safe')
    if not sf:
        return fr
    x = t * sf['fps'] - sf['f0']
    d = sf['d']
    i = int(math.floor(x))
    u = x - i
    a = d[max(0, min(len(d) - 1, i))]
    b = d[max(0, min(len(d) - 1, i + 1))]
    o = [a[k] + (b[k] - a[k]) * u for k in range(3)]
    return (fr[0] + o[0], fr[1] + o[1], fr[2] * o[2], fr[3])


def _beat_frame(scene, t):
    """Camera frame (cx, cy, h, roll) at time t inside a scene: eased moves around beats + slow drift."""
    beats = scene['beats']
    f = list(beats[0]['frame']) + [beats[0].get('roll', 0.0)]
    t_last = beats[0]['t']
    for k in range(1, len(beats)):
        b = beats[k]
        ms = b['t'] - MOVE * 0.35          # the move lands just after the word onset
        if t < ms:
            break
        # drift from t_last to ms
        d = max(0.0, ms - t_last)
        f[2] *= (1 - DRIFT) ** d
        target = list(b['frame']) + [b.get('roll', 0.0)]
        u = (t - ms) / MOVE
        if u < 1:
            e = ease(u)
            return tuple(f[i] + (target[i] - f[i]) * e for i in range(4))
        f = target
        t_last = ms + MOVE
    d = max(0.0, t - t_last)
    return (f[0] + d * 6, f[1], f[2] * (1 - DRIFT) ** d, f[3])


def cam_from_frame(fr):
    from .scene import Cam, CX, CY, H
    cx, cy, h, roll = fr
    s = H / h
    return Cam(x=cx - CX, y=cy - CY, z=1 - 1 / s, roll=roll, zoom=1.0)


# ----------------------------------------------------------------------------- faces vs frame edges
FACE_DY, FACE_R = 375.0, 100.0   # head centre above the feet and head radius, in character units
EDGE_M = 24.0                    # a framed face keeps at least this many pixels inside the frame
NECK = 0.55                      # ...and at the bottom edge also 0.55 head radii (a head never sits on the edge)
H_MIN = 800.0                    # tightest framing (frame height in subject px): painted planes stay crisp
ECU_R = 0.40                     # a face wider than 2*0.40 of the frame width is a deliberate extreme close-up


def faces_at(scene, words, t):
    """[(id, u, v, r, z)] head circles in plane coordinates at time t."""
    out = []
    for c in scene['cast']:
        st = actor_state(c, scene.get('acts', []), words, t)
        if st.get('type') == 'dino':                       # head of the small dinosaur
            s = st.get('scale', 1.0)
            out.append((c['id'], st['x'] + st.get('dir', 1) * 110 * s, st['y'] - 245 * s, 85 * s, c.get('z', 0.97)))
            continue
        s = st.get('scale', 1.0) * (0.86 if st.get('type') == 'kid' else 1.0)
        out.append((c['id'], st['x'], st['y'] - FACE_DY * s, FACE_R * s, c.get('z', 0.97)))
    return out


def face_on_screen(fr, face):
    """Screen circle (x, y, r) of a head for camera frame fr = (cx, cy, h, roll)."""
    from .scene import CX, CY, W, H
    cam = cam_from_frame(fr)
    _, u, v, r, z = face
    s = z / max(0.05, z - cam.z) * cam.zoom
    x, y = CX + s * (u - CX - cam.x / z), CY + s * (v - CY - cam.y / z)
    rr = r * s
    if abs(cam.roll) > 0.05:
        a = math.radians(cam.roll)
        k = abs(math.cos(a)) + abs(math.sin(a)) * H / W
        dx, dy = x - CX, y - CY
        x, y = CX + k * (dx * math.cos(a) - dy * math.sin(a)), CY + k * (dx * math.sin(a) + dy * math.cos(a))
        rr *= k
    return x, y, rr


def face_cut(x, y, r, tol=0.0):
    """None if the head is fully inside, fully outside, or an extreme close-up; else the needed screen shift
    (dx, dy) that brings it fully in or fully out, whichever is smaller."""
    from .scene import W, H
    if r > ECU_R * W:
        return None
    if x + r < 0 or x - r > W or y + r < 0 or y - r > H:
        return None
    m = EDGE_M - tol
    if x - r >= m and x + r <= W - m and y - r >= m and y + r <= H - m - NECK * r:
        return None

    def axis(c, lo, hi):
        if c - r < lo + EDGE_M:
            inn, out = (lo + EDGE_M) - (c - r), lo - (c + r) - 4
        elif c + r > hi - EDGE_M:
            inn, out = (hi - EDGE_M) - (c + r), hi - (c - r) + 4
        else:
            return 0.0
        return inn if abs(inn) <= abs(out) * 1.6 else out      # prefer keeping the face in frame
    return axis(x, 0, W), axis(y, 0, H)


def _solve_axis(circles, lo, hi, neck=0.0):
    """Smallest shift d so every circle (c, r, keep) ends fully inside [lo+M, hi-M] (keep) or fully outside."""
    lo_d, hi_d = -1e9, 1e9
    outs = []
    for c, r, keep in circles:
        if keep:
            lo_d, hi_d = max(lo_d, lo + EDGE_M - (c - r)), min(hi_d, hi - EDGE_M - neck * r - (c + r))
        else:
            outs.append((c, r))
    if lo_d > hi_d:
        return None
    d = min(max(0.0, lo_d), hi_d)
    for c, r in outs:                                   # partly visible but mostly out: push it out
        if lo - 4 < c + r + d and c - r + d < hi + 4:
            left, right = (lo - 4) - (c + r), (hi + 4) - (c - r)
            d2 = left if abs(left - d) < abs(right - d) else right
            if lo_d <= d2 <= hi_d:
                d = d2
            else:
                return None
    return d


def safe_frame(fr, faces):
    """Return (dx, dy, hk): subject-plane pan and zoom-out factor that keep framed faces whole."""
    from .scene import W, H
    cx, cy, h, roll = fr
    dx = dy = 0.0
    hk = 1.0
    for _ in range(8):
        f2 = (cx + dx, cy + dy, h * hk, roll)
        circ = [face_on_screen(f2, fc) for fc in faces]
        xs, ys = [], []
        for x, y, r in circ:
            if r > ECU_R * W or x + r < 0 or x - r > W or y + r < 0 or y - r > H:
                continue
            # keep the face when at least ~45% of it is already inside on both axes
            vis_x = (min(x + r, W) - max(x - r, 0)) / (2 * r)
            vis_y = (min(y + r, H) - max(y - r, 0)) / (2 * r)
            keep = vis_x > 0.45 and vis_y > 0.45
            xs.append((x, r, keep)); ys.append((y, r, keep))
        sx, sy = _solve_axis(xs, 0, W), _solve_axis(ys, 0, H, NECK)
        if sx is None or sy is None:
            hk *= 1.08                                       # no pan works: widen a little and try again
            continue
        if abs(sx) < 0.5 and abs(sy) < 0.5:
            break
        s = H / (h * hk)
        dx -= sx / s
        dy -= sy / s
    return dx, dy, hk


def inside_set(fr):
    """Keep a framing inside the painted planes (the 1080x1920 frame plus 90 % of the bake margins)."""
    from .scene import W, H, MX, MY
    cx, cy, h = fr
    h = min(h, H + 1.8 * MY)
    w = h * W / H
    cy = max(-0.9 * MY + h / 2, min(H + 0.9 * MY - h / 2, cy))
    cx = max(-0.9 * MX + w / 2, min(W + 0.9 * MX - w / 2, cx))
    return (cx, cy, h)


def beat_safe(scene, words, fr, roll, ta, tb, samples=7):
    """Static framing correction for one beat: pan (or widen) so no face is cut while this framing holds."""
    if not scene['cast']:
        return fr
    ts = [ta + (tb - ta) * j / (samples - 1) for j in range(samples)]
    faces = [fc for tt in ts for fc in faces_at(scene, words, tt)]
    f4 = (fr[0], fr[1], fr[2], roll)
    if not any(face_cut(*face_on_screen(f4, fc)) for fc in faces):
        return fr
    dx, dy, hk = safe_frame(f4, faces)
    return (fr[0] + dx, fr[1] + dy, max(H_MIN, min(2600.0, fr[2] * hk)))


def make_safe_track(scene, words, fps=FPS, smooth=4, max_step=10.0, max_off=0.16):
    """Per-frame safety offsets for the scene camera, lightly smoothed; stored in scene['safe']."""
    scene.pop('safe', None)
    if not scene['cast']:
        return
    f0, f1 = int(math.floor(scene['t0'] * fps)), int(math.ceil(scene['t1'] * fps)) + 1
    raw = []
    for f in range(f0, f1):
        t = f / fps
        raw.append(safe_frame(frame_at(scene, t), faces_at(scene, words, t)))
    if not any(abs(a) > 0.5 or abs(b) > 0.5 or abs(c - 1) > 1e-3 for a, b, c in raw):
        return
    # smooth with a small window, but never smooth a needed offset below what one neighbour needs
    n = len(raw)
    out = []
    for i in range(n):
        acc = [0.0, 0.0, 0.0]
        wsum = 0.0
        for j in range(max(0, i - smooth), min(n, i + smooth + 1)):
            w = 1.0 - abs(j - i) / (smooth + 1)
            for k in range(3):
                acc[k] += raw[j][k] * w
            wsum += w
        sm = [v / wsum for v in acc]
        for k in range(2):                                   # keep at least the frame's own need
            if abs(raw[i][k]) > abs(sm[k]) and raw[i][k] * sm[k] >= 0:
                sm[k] = raw[i][k]
        sm[2] = max(sm[2], raw[i][2])
        out.append(sm)
    # cap the size of the correction and how fast it may change (no visible camera jumps)
    h_ref = scene['beats'][0]['frame'][2]
    lim = max_off * h_ref
    prev = [0.0, 0.0, 1.0]
    for i in range(n):
        o = out[i]
        for k in range(2):
            v = max(-lim, min(lim, o[k]))
            o[k] = max(prev[k] - max_step, min(prev[k] + max_step, v))
        o[2] = max(prev[2] - 0.006, min(prev[2] + 0.006, min(o[2], 1.15)))
        prev = o
    for i in range(n - 2, -1, -1):                          # and the same limit backwards (ease into it)
        for k in range(2):
            out[i][k] = max(out[i + 1][k] - max_step, min(out[i + 1][k] + max_step, out[i][k])) if abs(out[i][k]) < abs(out[i + 1][k]) else out[i][k]
    out = [[round(o[0], 1), round(o[1], 1), round(o[2], 4)] for o in out]
    scene['safe'] = dict(f0=f0, fps=fps, d=out)


def face_report(plan, min_frames=8, settle=20.0, tol=4.0):
    """[(t0, t1, actor id)] spans where a framed face is sliced by a frame edge for >= min_frames frames.
    A face counts as framed when it moves less than `settle` px per frame on screen; a face swept past an edge
    during a fast camera move is motion, not a framing."""
    fps = plan['fps']
    words = plan['words']
    out = []
    for sc in plan['scenes']:
        runs = {}
        f0, f1 = int(math.ceil(sc['t0'] * fps)), int(sc['t1'] * fps)
        for f in range(f0, f1):
            t = f / fps
            fr, fr2 = frame_at(sc, t), frame_at(sc, t + 1.0 / fps)
            bad = set()
            for fc, fc2 in zip(faces_at(sc, words, t), faces_at(sc, words, t + 1.0 / fps)):
                x, y, r = face_on_screen(fr, fc)
                x2, y2, _ = face_on_screen(fr2, fc2)
                if face_cut(x, y, r, tol) and math.hypot(x2 - x, y2 - y) < settle:
                    bad.add(fc[0])
            for who in list(runs):
                if who not in bad:
                    s0, s1 = runs.pop(who)
                    if s1 - s0 + 1 >= min_frames:
                        out.append((s0 / fps, (s1 + 1) / fps, who))
            for who in bad:
                runs[who] = (runs[who][0], f) if who in runs else (f, f)
        for who, (s0, s1) in runs.items():
            if s1 - s0 + 1 >= min_frames:
                out.append((s0 / fps, (s1 + 1) / fps, who))
    return sorted(out)


# ----------------------------------------------------------------------------- actors
def actor_state(cast_entry, acts, words, t):
    st = dict(cast_entry)
    st.setdefault('pose', 'stand'); st.setdefault('expr', 'neutral')
    mine = sorted([a for a in acts if a.get('who') == cast_entry['id']], key=lambda a: a['w'])
    x0, y0 = st['x'], st['y']
    for a in mine:
        ta = onset(words, a['w']) + a.get('delay', 0.0)
        if t < ta:
            break
        for k in ('pose', 'expr', 'face', 'dir', 'talk', 'hold', 'look'):
            if k in a:
                st[k] = a[k]
        if 'x' in a or 'y' in a:
            nx, ny = a.get('x', x0), a.get('y', y0)
            dur = a.get('dur', 0.8)
            u = (t - ta) / dur
            if u < 1:
                e = ease(u)
                st['x'], st['y'] = x0 + (nx - x0) * e, y0 + (ny - y0) * e
                if 'pose' not in a and math.hypot(nx - x0, ny - y0) > 30:
                    st['pose'] = 'walk' if dur > 0.5 else 'run'
                    st['dir'] = 1 if nx >= x0 else -1
            else:
                st['x'], st['y'] = nx, ny
            x0, y0 = nx, ny
    return st


# ----------------------------------------------------------------------------- captions
SMALL = {'a', 'an', 'the', 'of', 'to', 'in', 'on', 'at', 'and', 'or', 'but', 'is', 'it', 'for', 'with', 'by', 'so',
         'as', 'if', 'he', 'she', 'we', 'you', 'i', 'my', 'his', 'her', 'was', 'up', 'no', 'not', 'one', 'be'}


def chunk_captions(words, end_t):
    """1-2 words per caption, switched on word onsets."""
    out = []
    i = 0
    n = len(words)
    while i < n:
        w = words[i]
        group = [i]
        if i + 1 < n:
            a, b = w['w'], words[i + 1]['w']
            ends_clause = a[-1:] in ',.!?;:' or a.endswith('...')
            na = a.strip('",.!?;:').lower()
            fits = text_width((a + ' ' + b).lower(), CAP_SIZE) <= CAP_MAX_W
            quick = words[i + 1]['s'] - w['s'] < 0.42
            if not ends_clause and fits and (na in SMALL or quick) and words[i + 1]['sent'] == w['sent']:
                group.append(i + 1)
        txt = [words[k]['w'] for k in group]
        out.append(dict(s=words[group[0]]['s'], words=txt))
        i = group[-1] + 1
    for k in range(len(out)):
        nxt = out[k + 1]['s'] if k + 1 < len(out) else end_t
        out[k]['e'] = round(nxt, 3)
    return out


def caption_at(caps, t):
    for c in caps:
        if c['s'] <= t < c['e']:
            return c
    return None


def _no_nan(c):
    raise ValueError('NaN/Infinity are not allowed')


def _fin(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def validate(story, words):
    """Reject storyboards/word lists that would hang or crash later; one clear message per problem."""
    from .sets import _registry
    from .light import MOODS
    from .character import ARCHETYPES
    reg, err = _registry(), []
    if not isinstance(words, list) or not words:
        raise SystemExit('words.json is empty: run `words` (or `silent`) first')
    n = len(words)
    for i, w in enumerate(words):
        if not (isinstance(w, dict) and _fin(w.get('s'), 0, 3600) and _fin(w.get('e'), 0, 3600) and w['s'] <= w['e']):
            err.append('words.json word %d has bad times' % i)
            break
    if not isinstance(story, dict):
        raise SystemExit('storyboard.json must be a JSON object')
    if story.get('fps', FPS) not in (24, 25, 30, 50, 60):
        err.append('fps must be 24, 25, 30, 50 or 60')
    if not _fin(story.get('end_pad', 0.68), 0, 10):
        err.append('end_pad must be 0-10 s')
    scenes = story.get('scenes')
    if not isinstance(scenes, list) or not scenes:
        err.append('storyboard needs a non-empty "scenes" list')
        scenes = []
    wi = lambda v: isinstance(v, int) and not isinstance(v, bool) and 0 <= v < n
    for si, sc in enumerate(scenes):
        tag = 'scene %d' % si
        if not isinstance(sc, dict):
            err.append('%s must be an object' % tag)
            continue
        if sc.get('set') not in reg:
            err.append('%s: unknown set %r (one of %s)' % (tag, sc.get('set'), ', '.join(sorted(reg))))
        if sc.get('mood') not in MOODS:
            err.append('%s: unknown mood %r (one of %s)' % (tag, sc.get('mood'), ', '.join(sorted(MOODS))))
        if not _fin(sc.get('bloom', 0.45), 0, 2):
            err.append('%s: bloom must be 0-2' % tag)
        if not isinstance(sc.get('set_args', {}), dict):
            err.append('%s: set_args must be an object' % tag)
        if not wi(sc.get('start_word', 0)):
            err.append('%s: start_word must be a word index 0-%d' % (tag, n - 1))
        for k in sc.get('keys', []) or []:
            fr = k.get('frame') if isinstance(k, dict) else None
            if not isinstance(k, dict) or not wi(k.get('w')):
                err.append('%s: key %r: "w" must be a word index 0-%d' % (tag, k, n - 1))
            elif isinstance(fr, list) and not (len(fr) == 3 and all(_fin(v, -1e4, 1e4) for v in fr) and fr[2] > 0):
                err.append('%s: frame %r must be [cx, cy, height > 0]' % (tag, fr))
            elif not _fin(k.get('roll', 0), -45, 45):
                err.append('%s: roll must be -45..45' % tag)
        for c in sc.get('cast', []) or []:
            if not isinstance(c, dict):
                err.append('%s: cast entries must be objects' % tag)
                continue
            if c.get('type') not in ARCHETYPES and c.get('type') != 'dino':
                err.append('%s: unknown type %r' % (tag, c.get('type')))
            if not (_fin(c.get('x', 0), -1e4, 1e4) and _fin(c.get('y', 0), -1e4, 1e4)):
                err.append('%s: %s x/y must be numbers' % (tag, c.get('id')))
            if not (_fin(c.get('scale', 1), 0.05, 5) and _fin(c.get('z', 1), 0.2, 10)):
                err.append('%s: %s needs scale 0.05-5 and z 0.2-10' % (tag, c.get('id')))
        for a in sc.get('acts', []) or []:
            if not isinstance(a, dict) or not wi(a.get('w')):
                err.append('%s: act %r: "w" must be a word index 0-%d' % (tag, a, n - 1))
            elif any(isinstance(v, (int, float)) and not isinstance(v, bool) and not _fin(v, -1e4, 1e4)
                     for v in a.values()) or not _fin(a.get('dur', 0.8), 0.05, 10):
                err.append('%s: act %r has a number out of range (dur must be 0.05-10 s)' % (tag, a))
    if err:
        raise SystemExit('storyboard problems:\n  ' + '\n  '.join(err[:25]))


def build(project):
    try:
        story = json.load(open(os.path.join(project, 'storyboard.json'), encoding='utf-8-sig'), parse_constant=_no_nan)
        words = json.load(open(os.path.join(project, 'words.json'), encoding='utf-8-sig'), parse_constant=_no_nan)
    except (OSError, ValueError, RecursionError) as e:
        raise SystemExit('cannot read storyboard.json / words.json: %s' % e)
    validate(story, words)
    p = plan(story, words)
    p['words'] = words
    p['story'] = {k: v for k, v in story.items() if k != 'scenes'}
    with open(os.path.join(project, 'plan.json'), 'w', encoding='utf-8') as f:
        json.dump(p, f, indent=1)
    return p
