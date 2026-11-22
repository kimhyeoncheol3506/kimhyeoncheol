"""toon2d command line.  python t2d.py <command> <project_dir> [options]

  doctor  [--install]                       preflight: checks the packages; says what to do if pip has no network
  silent  PROJECT [--script script.txt] [--rate 2.3] [--pause 0.35] [--duration 15]
                                            no-voice mode: silent voice.wav + reading-pace timings, then words
  words   PROJECT [--from FILE] [--offline] [--force] [--model small.en]
                                            word timings -> words.json. Keeps an existing words.json; imports
                                            timings.json/csv (ElevenLabs or word,start,end); else whisper;
                                            else (no download possible) the built-in aligner
  plan    PROJECT                           storyboard.json + words.json -> plan.json (camera beats, captions)
  stills  PROJECT [--at 1.0,5.2] [--out DIR] PNG stills (default: one per scene + every 3rd beat)
  render  PROJECT [--budget 200] [--workers 2] [--start S] [--end E]
                                            render missing 2-second chunks until the time budget is used;
                                            run again until it prints DONE (resumable)
  join    PROJECT [--end E]                 chunks + voice (+ music.* if present) -> final.mp4 at -14 LUFS
  check   PROJECT                           numeric checks on plan, stills and final.mp4
  bench   PROJECT [--frames 20]             seconds per frame in this process
"""
import json
import os
import sys
import time


def _opt(argv, name, default=None, cast=str):
    if name in argv:
        try:
            return cast(argv[argv.index(name) + 1])
        except (IndexError, ValueError):
            raise SystemExit('%s needs a value (see python t2d.py --help)' % name)
    return default


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == 'doctor':
        from . import doctor
        return doctor.main(argv[1:])
    if len(argv) < 2 or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    cmd, proj = argv[0], os.path.abspath(argv[1])
    if cmd == 'silent':
        from . import silent
        return silent.main([proj] + argv[2:])
    if cmd == 'words':
        from . import words
        return words.main([proj] + argv[2:])
    elif cmd == 'plan':
        from . import director
        p = director.build(proj)
        nb = sum(len(s['beats']) for s in p['scenes'])
        print('plan: %.2f s, %d scenes, %d framing beats (%.1f/min), %d caption chunks'
              % (p['duration'], len(p['scenes']), nb, nb / p['duration'] * 60, len(p['captions'])))
    elif cmd == 'stills':
        from . import render
        at = _opt(argv, '--at')
        if at:
            try:
                times = [float(x) for x in at.split(',')]
            except ValueError:
                raise SystemExit('--at needs seconds separated by commas, e.g. --at 1.0,5.2')
            if not all(map(lambda v: v == v and abs(v) != float('inf'), times)):
                raise SystemExit('--at needs finite seconds')
        else:
            p = json.load(open(os.path.join(proj, 'plan.json'), encoding='utf-8'))
            times = []
            for s in p['scenes']:
                times.append(round((s['t0'] + s['t1']) / 2, 2))
                times += [round(b['t'] + 0.4, 2) for b in s['beats'][::3] if b['t'] + 0.4 < s['t1']]
            times = sorted(set(times))
        for pth in render.stills(proj, times, _opt(argv, '--out')):
            print(pth)
    elif cmd == 'render':
        from . import render
        render.chunks(proj, budget=_opt(argv, '--budget', 200.0, float), workers=_opt(argv, '--workers', 2, int),
                      start=_opt(argv, '--start', None, float), end=_opt(argv, '--end', None, float))
    elif cmd == 'join':
        from . import render
        print(render.join(proj, end=_opt(argv, '--end', None, float)))
    elif cmd == 'check':
        from . import qa
        return qa.run(proj)
    elif cmd == 'bench':
        from . import render
        rt = render.load(proj)
        n = _opt(argv, '--frames', 20, int)
        nf = render.n_frames(rt.plan)
        rt.frame(0)
        t0 = time.time()
        for k in range(n):
            rt.frame(int(k * nf / n))
        dt = (time.time() - t0) / n
        print('%.3f s/frame (one process); a %d-frame video ~ %.1f min on 1 core' % (dt, nf, dt * nf / 60))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
