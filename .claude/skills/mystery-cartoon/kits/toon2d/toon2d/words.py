"""Word timings for the captions and the camera director -> PROJECT/words.json

python t2d.py words PROJECT [--from FILE] [--model small.en] [--offline] [--force]

Order (never dead-ends):
  1. words.json already there        -> kept as it is (use --force to redo it)
  2. --from FILE, or a timings.json / timings.csv in the project
                                     -> imported: ElevenLabs "with timestamps" JSON (character alignment)
                                        or a plain CSV/JSON of word,start,end (seconds)
  3. faster-whisper (model in PROJECT/.models or $TOON2D_MODELS; downloads once if the network allows)
  4. if whisper can't load or download -> built-in aligner, no download: speech/silence detection on voice.wav,
                                        the script's words spread by syllables inside each speech run,
                                        sentence ends snapped to pauses. Prints a warning; captions may be a
                                        little less exact.
Output: [{"w": "Earth?", "s": 3.21, "e": 3.55, "sent": 2}, ...]. The script's spelling and punctuation always win;
timings from any source only supply the times.
"""
import csv
import difflib
import json
import math
import os
import re
import sys


def norm(w):
    return re.sub(r"[^a-z0-9'\uac00-\ud7a3]", '', w.lower().replace('’', "'"))


SENT_END = re.compile(r'[.!?]["”’)]*$|\.\.\.$|…$')
CLAUSE_END = re.compile(r'[,;:—–-]["”’)]*$')


def script_words(text):
    out = []
    sent = 0
    for line in text.replace('\r', '').split('\n'):
        for tok in line.split():
            out.append(dict(w=tok, sent=sent))
            if SENT_END.search(tok):
                sent += 1
    return out


def ffmpeg_exe():
    exe = os.environ.get('TOON2D_FFMPEG')
    if exe and os.path.exists(exe):
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_16k(path):
    """Decode any audio file to mono 16 kHz float32 with ffmpeg (no PyAV needed)."""
    import subprocess
    import numpy as np
    raw = subprocess.run([ffmpeg_exe(), '-v', 'error', '-i', path, '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'],
                         stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


# ---------------------------------------------------------------- 3. whisper

def transcribe(wav, model_name='small.en', cache=None, threads=0):
    from faster_whisper import WhisperModel
    m = WhisperModel(model_name, device='cpu', compute_type='int8', cpu_threads=threads, download_root=cache)
    segs, _ = m.transcribe(load_16k(wav), word_timestamps=True, vad_filter=False, beam_size=5, language='en')
    words = []
    for s in segs:
        for w in s.words:
            words.append(dict(w=w.word.strip(), s=float(w.start), e=float(w.end)))
    return words


def align(script, heard, total=None):
    """Map heard times onto script words with difflib on normalised tokens; interpolate gaps."""
    a = [norm(x['w']) for x in script]
    b = [norm(x['w']) for x in heard]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    times = [None] * len(script)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            times[blk.a + k] = (h['s'], h['e'])
    n = len(script)
    end_t = total if total else (heard[-1]['e'] if heard else n * 0.27)
    i = 0
    while i < n:
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < n and times[j] is None:
            j += 1
        t0 = times[i - 1][1] if i > 0 else 0.0
        t1 = times[j][0] if j < n else end_t
        lens = [max(1, len(norm(script[k]['w']))) for k in range(i, j)]
        tot = sum(lens)
        acc = t0
        for k, L in zip(range(i, j), lens):
            d = (t1 - t0) * L / tot
            times[k] = (acc, acc + d)
            acc += d
        i = j
    out = []
    for sw, (s, e) in zip(script, times):
        out.append(dict(w=sw['w'], s=round(s, 3), e=round(e, 3), sent=sw['sent']))
    return _monotonic(out)


def _monotonic(out):
    for k in range(1, len(out)):
        if out[k]['s'] < out[k - 1]['s'] + 0.04:
            out[k]['s'] = round(out[k - 1]['s'] + 0.04, 3)
        if out[k]['e'] < out[k]['s'] + 0.04:
            out[k]['e'] = round(out[k]['s'] + 0.04, 3)
    return out


# ---------------------------------------------------------------- 2. imported timings

def _num(v):
    v = float(v)
    return v


def read_timings(path):
    """Return heard words [{w, s, e}] from an ElevenLabs timestamps JSON or a word,start,end CSV/JSON."""
    ext = os.path.splitext(path)[1].lower()
    if ext in ('.csv', '.tsv', '.txt'):
        rows = []
        with open(path, encoding='utf-8-sig', newline='') as f:
            sample = f.read(2048)
            f.seek(0)
            delim = '\t' if '\t' in sample else (';' if sample.count(';') > sample.count(',') else ',')
            for r in csv.reader(f, delimiter=delim):
                if len(r) < 3:
                    continue
                try:
                    rows.append(dict(w=r[0].strip(), s=_num(r[1]), e=_num(r[2])))
                except ValueError:
                    continue                                   # header line
        return _ms_to_s(rows)
    data = json.load(open(path, encoding='utf-8-sig'))
    al = None
    if isinstance(data, dict):
        for key in ('alignment', 'normalized_alignment'):
            if isinstance(data.get(key), dict) and data[key].get('characters'):
                al = data[key]
                break
        if al is None and data.get('characters'):
            al = data
        if al is None:
            for key in ('words', 'segments', 'items'):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
    if al is not None:                                         # ElevenLabs character alignment -> words
        ch = al['characters']
        st = al.get('character_start_times_seconds') or al.get('character_start_times')
        en = al.get('character_end_times_seconds') or al.get('character_end_times')
        words, cur = [], None
        for c, s, e in zip(ch, st, en):
            if c.isspace():
                if cur:
                    words.append(cur)
                cur = None
                continue
            if cur is None:
                cur = dict(w=c, s=float(s), e=float(e))
            else:
                cur['w'] += c
                cur['e'] = float(e)
        if cur:
            words.append(cur)
        return [w for w in words if norm(w['w'])]
    rows = []
    for it in data:
        if isinstance(it, (list, tuple)) and len(it) >= 3:
            rows.append(dict(w=str(it[0]), s=_num(it[1]), e=_num(it[2])))
        elif isinstance(it, dict):
            w = it.get('word', it.get('w', it.get('text')))
            s = it.get('start', it.get('s', it.get('start_time')))
            e = it.get('end', it.get('e', it.get('end_time')))
            if w is not None and s is not None and e is not None:
                rows.append(dict(w=str(w).strip(), s=_num(s), e=_num(e)))
    return _ms_to_s(rows)


def _ms_to_s(rows):
    rows = [r for r in rows if isinstance(r.get('s'), (int, float)) and isinstance(r.get('e'), (int, float))
            and math.isfinite(r['s']) and math.isfinite(r['e']) and r['e'] >= 0]
    ends = sorted(r['e'] for r in rows)
    if ends and ends[len(ends) // 2] > 1000:                 # most times look like milliseconds
        for r in rows:
            r['s'] /= 1000.0
            r['e'] /= 1000.0
    return rows


# ---------------------------------------------------------------- 4. built-in aligner (no download)

def syllables(word):
    w = norm(word)
    if not w:
        return 0.5
    if w.isdigit():
        return 1.6 * len(w)
    w = w.replace("'", '')
    groups = re.findall(r'[aeiouy]+', w)
    n = len(groups)
    if w.endswith('e') and not w.endswith(('le', 'ee', 'ye')) and n > 1:
        n -= 1
    if re.search(r'(ed)$', w) and not re.search(r'[td]ed$', w) and n > 1:
        n -= 1
    n = max(1, n)
    cons = len(re.sub(r'[aeiouy]', '', w))
    return n + 0.08 * cons                                   # consonant clusters take time too


def speech_runs(x, sr=16000, hop=0.01):
    """Return (runs [(t0, t1)], gaps [(t0, t1)]) from a mono signal by adaptive energy + hysteresis."""
    import numpy as np
    n = int(sr * hop)
    m = len(x) // n
    if m == 0:
        return [], []
    fr = x[:m * n].reshape(m, n)
    db = 10 * np.log10(np.mean(fr * fr, axis=1) + 1e-10)
    k = 5
    db = np.convolve(db, np.ones(k) / k, mode='same')
    lo, hi = np.percentile(db, 8), np.percentile(db, 95)
    # speech is within ~24 dB of the loud parts; on a noisy recording stay well above the noise floor
    on = max(hi - 24.0, lo + 0.5 * (hi - lo))
    off = max(hi - 30.0, lo + 0.4 * (hi - lo))
    speech = np.zeros(m, bool)
    state = False
    for i in range(m):
        state = db[i] > (off if state else on)
        speech[i] = state
    runs = []
    i = 0
    while i < m:
        if speech[i]:
            j = i
            while j < m and speech[j]:
                j += 1
            runs.append([i * hop, j * hop])
            i = j
        else:
            i += 1
    merged = []                                              # stop consonants make short dips: merge them
    for r in runs:
        if merged and r[0] - merged[-1][1] < 0.09:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    runs = [r for r in merged if r[1] - r[0] >= 0.05]
    gaps = [(runs[i][1], runs[i + 1][0]) for i in range(len(runs) - 1)]
    return [tuple(r) for r in runs], gaps


def offline_align(script, wav):
    x = load_16k(wav)
    total = len(x) / 16000.0
    runs, gaps = speech_runs(x)
    if not runs:
        runs, gaps = [(0.0, total)], []
    # speech-time axis: only the voiced parts, laid end to end
    acc, cum = 0.0, []
    for r in runs:
        cum.append(acc)
        acc += r[1] - r[0]
    T = acc

    def to_real(p):
        p = min(max(p, 0.0), T)
        for r, c in zip(runs, cum):
            if p <= c + (r[1] - r[0]) + 1e-9:
                return r[0] + (p - c)
        return runs[-1][1]

    n = len(script)
    FINAL = 1.5
    syl = []
    for i, w in enumerate(script):
        s = syllables(w['w'])
        if i == n - 1 or script[i + 1]['sent'] != w['sent'] or CLAUSE_END.search(w['w']):
            s += FINAL                                        # speakers stretch the last word before a pause
        syl.append(s)
    # expected speech-time position of every word boundary by syllables
    S = sum(syl)
    pos = [0.0]
    for s in syl:
        pos.append(pos[-1] + T * s / S)
    # boundaries that should sit on a pause: sentence ends (strong) and commas (weak)
    bounds = []                                               # (word index after which the pause comes, weight)
    for i in range(n - 1):
        if script[i + 1]['sent'] != script[i]['sent']:
            bounds.append((i, 'sent'))
        elif CLAUSE_END.search(script[i]['w']):
            bounds.append((i, 'clause'))
    gap_pos = [cum[g + 1] for g in range(len(gaps))]           # speech-time position of each gap
    gap_len = [g[1] - g[0] for g in gaps]
    # snap: dynamic programming over sentence boundaries -> gaps (monotonic), cost = distance - pause bonus
    snapped = {}
    sents = [b for b in bounds if b[1] == 'sent']
    if sents and gaps:
        # each sentence end takes one pause (in order) or none; cost = distance from where the syllables put it,
        # minus a bonus for long pauses; a sentence end left without a pause costs SKIP.
        # A long pause that no sentence end takes also costs a little (a speaker rarely pauses mid-sentence).
        SKIP = 1.2
        G = len(gaps)

        def c(bi, gi):
            d = abs(gap_pos[gi] - pos[sents[bi][0] + 1])
            return d - 0.8 * min(gap_len[gi], 0.7)

        # state: index of the last gap used (-1 = none yet) -> (cost, assignment tuple)
        states = {-1: (0.0, ())}
        for bi in range(len(sents)):
            nxt = {}
            for last, (cst, asg) in states.items():
                cand = [(cst + SKIP, last, asg + (None,))]
                for g in range(last + 1, G):
                    unused = sum(min(gap_len[k], 0.5) for k in range(last + 1, g)) * 0.5
                    cand.append((cst + c(bi, g) + unused, g, asg + (g,)))
                for cc, key, a in cand:
                    if key not in nxt or cc < nxt[key][0]:
                        nxt[key] = (cc, a)
            states = nxt
        best = min(states.values(), key=lambda v: v[0])
        for (i, _), g in zip(sents, best[1]):
            if g is not None:
                snapped[i] = g
    # commas: snap to an unused gap inside the sentence if one is close enough
    used = set(snapped.values())
    for i, kind in bounds:
        if kind != 'clause' or not gaps:
            continue
        g = min(range(len(gaps)), key=lambda k: abs(gap_pos[k] - pos[i + 1]))
        if g not in used and abs(gap_pos[g] - pos[i + 1]) < 0.35 and gap_len[g] >= 0.08:
            lo = max([gg for ii, gg in snapped.items() if ii < i] + [-1])
            hi = min([gg for ii, gg in snapped.items() if ii > i] + [len(gaps)])
            if lo < g < hi:
                snapped[i] = g
                used.add(g)
    # piecewise: anchor positions at snapped boundaries, spread syllables between anchors
    anchors = [(0, 0.0)] + sorted((i + 1, gap_pos[g]) for i, g in snapped.items()) + [(n, T)]
    wpos = [0.0] * (n + 1)
    for (i0, p0), (i1, p1) in zip(anchors, anchors[1:]):
        tot = sum(syl[i0:i1]) or 1.0
        a = p0
        for k in range(i0, i1):
            wpos[k] = a
            a += (p1 - p0) * syl[k] / tot
        wpos[i1] = p1
    out = []
    for k, sw in enumerate(script):
        s = to_real(wpos[k])
        if k in [i + 1 for i in snapped]:                      # a word after a pause starts at the next run
            s = to_real(wpos[k] + 1e-6)
        e = to_real(wpos[k + 1] - 1e-6)
        out.append(dict(w=sw['w'], s=round(s, 3), e=round(max(e, s + 0.05), 3), sent=sw['sent']))
    return _monotonic(out), dict(runs=len(runs), pauses=len(gaps), snapped=len(snapped), speech=round(T, 2))


# ---------------------------------------------------------------- driver

def wav_duration(path):
    import wave
    try:
        with wave.open(path) as f:
            return f.getnframes() / float(f.getframerate())
    except Exception:
        return None


def _write(proj, words, how):
    p = os.path.join(proj, 'words.json')
    tmp = p + '.part'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(words, f, indent=1)
    os.replace(tmp, p)
    print('words: %d from %s -> %s' % (len(words), how, p))


def main(argv):
    proj = argv[0]
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d
    model = opt('--model', 'small.en')
    out = os.path.join(proj, 'words.json')
    wav = os.path.join(proj, 'voice.wav')
    if os.path.exists(out) and '--force' not in argv:
        print('words.json already exists -> kept as it is (%s). Use --force to make it again.' % out)
        return 0
    if not os.path.exists(wav):
        print('ERROR: no voice.wav in %s (put your voice-over there first)' % proj)
        return 2
    text = open(os.path.join(proj, 'script.txt'), encoding='utf-8-sig').read()
    script = script_words(text)
    total = wav_duration(wav)
    src = opt('--from')
    if src:
        found = [p for p in (os.path.join(proj, src), src) if os.path.isfile(p)]   # absolute, project folder, current folder
        if not found:
            print('ERROR: --from %s not found (looked in %s and in the current folder)' % (src, proj))
            return 2
        src = found[0]
    if not src:
        for name in ('timings.json', 'timings.csv', 'timestamps.json', 'alignment.json'):
            if os.path.exists(os.path.join(proj, name)):
                src = os.path.join(proj, name)
                break
    if src:
        try:
            heard = [r for r in read_timings(src) if isinstance(r.get('w'), str) and isinstance(r.get('s'), (int, float))
                     and isinstance(r.get('e'), (int, float)) and math.isfinite(r['s']) and math.isfinite(r['e'])
                     and 0.0 <= r['s'] <= r['e'] <= (total or 3600.0) + 5.0]
        except (ValueError, TypeError, KeyError, AttributeError, IndexError, UnicodeDecodeError, RecursionError) as e:
            print('ERROR: cannot read word timings from %s (%s)' % (os.path.basename(src), type(e).__name__))
            return 2
        if not heard:
            print('ERROR: no word timings found in %s' % src)
            return 2
        span = max(r['e'] for r in heard) - min(r['s'] for r in heard)
        if total and span < 0.5 * total:
            print('WARNING: the timings in %s cover %.1f s of a %.1f s voice.wav: check that the file belongs to this '
                  'voice (seconds vs milliseconds?)' % (os.path.basename(src), span, total))
        words = align(script, heard, total)
        _write(proj, words, 'imported timings (%s, %d words)' % (os.path.basename(src), len(heard)))
        return 0
    if '--offline' not in argv:
        cache = os.environ.get('TOON2D_MODELS') or os.path.join(proj, '.models')
        try:
            heard = transcribe(wav, model, cache)
            words = align(script, heard, total)
            _write(proj, words, 'whisper %s (heard %d)' % (model, len(heard)))
            return 0
        except Exception as e:                                # no network / blocked model host / import problem
            print('whisper unavailable (%s: %s)' % (type(e).__name__, str(e).split('\n')[0][:160]))
    words, info = offline_align(script, wav)
    print('WARNING: used the built-in aligner (no model download). Captions may be a little less exact.')
    print('         speech runs %(runs)d, pauses %(pauses)d, sentence/clause ends snapped %(snapped)d, '
          'speech %(speech).1f s' % info)
    print('         For exact timings: bring timings.json/csv (--from), or copy a .models folder (see SKILL.md).')
    _write(proj, words, 'built-in aligner')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
