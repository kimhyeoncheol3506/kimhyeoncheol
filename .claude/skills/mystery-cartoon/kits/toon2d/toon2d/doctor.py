"""Preflight: python t2d.py doctor [--install]

Checks that the required packages import (skia-python, numpy, imageio-ffmpeg + its ffmpeg binary) and reports
the optional ones (faster-whisper for word timings, Pillow for checks). If something is missing it checks whether
pip can reach the package index and says in plain words what to do. --install runs pip for missing packages.
Never prints environment variables or secrets.
"""
import importlib
import os
import subprocess
import sys

REQUIRED = [('skia', 'skia-python'), ('numpy', 'numpy'), ('imageio_ffmpeg', 'imageio-ffmpeg')]
OPTIONAL = [('faster_whisper', 'faster-whisper', 'word timings from a voice (not needed for `silent` or --from)'),
            ('PIL', 'Pillow', 'still checks and contact sheets')]

NO_NET = ('pip cannot reach the package index, so the packages cannot be installed here.\n'
          'Turn on Code execution and file creation and Use internet while making files in Settings > Capabilities '
          'on claude.ai in your browser (not in the app), then start a NEW chat.')


def _try(mod):
    try:
        importlib.import_module(mod)
        return True, ''
    except Exception as e:                                   # ImportError or a broken binary wheel
        return False, '%s: %s' % (type(e).__name__, str(e).split('\n')[0][:120])


def index_reachable(timeout=8.0):
    """True if the pip package index answers (uses the same proxy settings pip would)."""
    import urllib.request
    url = os.environ.get('PIP_INDEX_URL', 'https://pypi.org/simple/').rstrip('/') + '/pip/'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'toon2d-doctor'})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return 200 <= r.status < 400
    except Exception:
        return False


def main(argv):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print('python %s on %s' % (sys.version.split()[0], sys.platform))
    missing = []
    for mod, pkg in REQUIRED:
        ok, err = _try(mod)
        print('  %-16s %s' % (pkg, 'OK' if ok else 'MISSING (%s)' % err))
        if not ok:
            missing.append(pkg)
    if 'imageio-ffmpeg' not in missing:
        try:
            import imageio_ffmpeg
            exe = os.environ.get('TOON2D_FFMPEG') or imageio_ffmpeg.get_ffmpeg_exe()
            r = subprocess.run([exe, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            print('  %-16s %s' % ('ffmpeg', 'OK' if r.returncode == 0 else 'FAILED to run'))
            if r.returncode != 0:
                missing.append('imageio-ffmpeg')
        except Exception as e:
            print('  %-16s FAILED (%s)' % ('ffmpeg', type(e).__name__))
            missing.append('imageio-ffmpeg')
    for mod, pkg, why in OPTIONAL:
        ok, _ = _try(mod)
        print('  %-16s %s' % (pkg, 'OK' if ok else 'not installed (optional: %s)' % why))
    if not missing:
        print('DOCTOR OK: ready to make Shorts.')
        return 0
    print('\nMissing: %s' % ', '.join(missing))
    reach = index_reachable()
    if not reach:
        print('\n' + NO_NET)
        print('\nDOCTOR FAILED: no network for pip.')
        return 3
    req = os.path.join(here, 'requirements.txt')
    cmd = [sys.executable, '-m', 'pip', 'install', '-r', req] if os.path.exists(req) else \
          [sys.executable, '-m', 'pip', 'install'] + missing
    if '--install' in argv:
        print('\nInstalling: %s' % ' '.join(cmd[3:]))
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print('\npip failed. If it could not download anything:\n' + NO_NET)
            return 3
        print('\nInstalled. Run `python t2d.py doctor` again to confirm.')
        return 0
    print('\nThe package index is reachable. Install with:\n  pip install -r requirements.txt\n'
          '(or run `python t2d.py doctor --install`), then run doctor again.')
    print('\nDOCTOR FAILED: packages missing.')
    return 3
