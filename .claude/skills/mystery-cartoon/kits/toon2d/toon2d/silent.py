"""No-voice mode: a captions-only Short.

python t2d.py silent PROJECT [--script script.txt] [--rate 2.3] [--pause 0.35] [--duration 15.0]

Writes PROJECT/voice.wav (digital silence), PROJECT/timings.json (every script word at a reading pace: about
--rate words per second, --pause seconds after each sentence, a short breath after commas), then runs
`words --from timings.json --force` so words.json is ready for the storyboard.
Video length = last word end + the storyboard's end_pad; the command prints the end_pad that gives --duration.
"""
import json
import math
import os
import re
import shutil
import wave

from .words import script_words, syllables, SENT_END, CLAUSE_END

SR = 48000
MAX_DUR = 600.0                                   # Shorts are 30-70 s; 10 min is a generous ceiling


def _resolve(path, proj):
    for p in (path, os.path.join(proj, path)):
        if p and os.path.exists(p):
            return p
    return None


def reading_times(words, rate=2.3, pause=0.35, comma=0.15, start=0.05):
    """[(start, end)] for script words: total speaking time = n / rate, split by syllable weight, plus pauses."""
    n = len(words)
    wt = [0.6 + syllables(w['w']) for w in words]            # every word costs a beat, long words a bit more
    speak = n / rate
    k = speak / sum(wt)
    out, t = [], start
    for i, (w, x) in enumerate(zip(words, wt)):
        d = x * k
        out.append((round(t, 3), round(t + d * 0.9, 3)))      # 10 % gap so captions switch cleanly
        t += d
        if i < n - 1:
            if SENT_END.search(w['w']):
                t += pause
            elif CLAUSE_END.search(w['w']):
                t += comma
    return out


def main(argv):
    proj = argv[0]
    def opt(k, d=None):
        if k not in argv:
            return d
        if argv.index(k) + 1 >= len(argv):
            raise SystemExit('%s needs a value' % k)
        return argv[argv.index(k) + 1]
    os.makedirs(proj, exist_ok=True)
    src = opt('--script', 'script.txt')
    sp = _resolve(src, proj)
    if not sp:
        print('ERROR: script not found: %s (looked in the current folder and in %s)' % (src, proj))
        return 2
    dst = os.path.join(proj, 'script.txt')
    if os.path.abspath(sp) != os.path.abspath(dst):
        shutil.copyfile(sp, dst)
    try:
        words = script_words(open(dst, encoding='utf-8-sig').read())
    except UnicodeDecodeError:
        print('ERROR: script.txt is not UTF-8 text: save it as UTF-8 and run again')
        return 2
    if not words:
        print('ERROR: the script is empty')
        return 2
    try:
        rate, pause = float(opt('--rate', 2.3)), float(opt('--pause', 0.35))
        want = float(opt('--duration', 0) or 0)
    except ValueError:
        print('ERROR: --rate, --pause and --duration must be numbers')
        return 2
    if not (0.5 <= rate <= 6 and 0 <= pause <= 3 and (want == 0 or 1 <= want <= MAX_DUR)):
        print('ERROR: use --rate 0.5-6, --pause 0-3, --duration 1-%d' % MAX_DUR)
        return 2
    times = reading_times(words, rate, pause)
    last = times[-1][1]
    TAIL = 0.6                                                   # the last caption stays up this long
    if want and last > want - TAIL:
        # keep the sentence pauses, read the words a little faster so the script fits the requested length
        n_pause = sum(1 for w in words[:-1] if SENT_END.search(w['w']))
        n_comma = sum(1 for w in words[:-1] if CLAUSE_END.search(w['w']) and not SENT_END.search(w['w']))
        speak = want - TAIL - 0.05 - n_pause * pause - n_comma * 0.15
        if speak < len(words) / 4.0:
            print('ERROR: %d words cannot be read in %.1f s (would need over 4 words/s). Shorten the script or raise --duration.'
                  % (len(words), want))
            return 2
        new_rate = len(words) / speak
        print('NOTE: at %.1f words/s the script needs %.2f s; reading at %.2f words/s to fit %.1f s' % (rate, last + TAIL, new_rate, want))
        times = reading_times(words, new_rate, pause)
        last = times[-1][1]
    dur = want or round(last + 0.7, 2)
    if not math.isfinite(dur) or dur > MAX_DUR:
        print('ERROR: the script reads for %.0f s; the limit is %d s. Shorten script.txt.' % (last, MAX_DUR))
        return 2
    vp = os.path.join(proj, 'voice.wav')
    tmp = vp + '.part'
    with wave.open(tmp, 'wb') as w:                              # written in 1 s blocks: constant memory
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        n, block = int(round(SR * dur)), b'\x00\x00' * SR
        while n > 0:
            k = min(n, SR)
            w.writeframes(block[:2 * k])
            n -= k
    os.replace(tmp, vp)
    rows = [dict(word=w['w'], start=s, end=e) for w, (s, e) in zip(words, times)]
    with open(os.path.join(proj, 'timings.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=1)
    print('silent voice.wav: %.2f s | %d words, reading %.2f s (%.2f words/s incl. pauses) | timings.json written'
          % (dur, len(words), last, len(words) / last))
    print('storyboard: set "end_pad": %.2f to make the video %.2f s long' % (dur - last, dur))
    from . import words as W
    return W.main([proj, '--from', os.path.join(proj, 'timings.json'), '--force'])
