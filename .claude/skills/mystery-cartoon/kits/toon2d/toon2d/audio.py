"""Voice + optional music bed -> one normalised track (-14 LUFS integrated, -1.5 dBTP).

Music is used ONLY if the project folder contains music.mp3 / music.wav / music.m4a / music.ogg (a file the owner
supplied). The bed sits ~14 dB under the speech level for the whole video, with fades, looping if it is too short.
"""
import json
import os
import re
import subprocess

import numpy as np

from .words import ffmpeg_exe

MUSIC_NAMES = ('music.mp3', 'music.wav', 'music.m4a', 'music.ogg', 'music.flac')
BED_DB = -14.0
TARGET_LUFS = -14.0


def _decode(path, sr=48000, ch=1):
    raw = subprocess.run([ffmpeg_exe(), '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'],
                         stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, np.float32)


def speech_db(x, sr=48000):
    """RMS level (dBFS) of the active parts (50 ms windows above -45 dBFS)."""
    n = sr // 20
    k = len(x) // n
    if k == 0:
        return -30.0
    w = x[:k * n].reshape(k, n)
    rms = np.sqrt((w ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    act = db[db > -45]
    return float(20 * np.log10(np.sqrt(np.mean((10 ** (act / 20)) ** 2)))) if len(act) else -30.0


def find_music(project):
    for n in MUSIC_NAMES:
        p = os.path.join(project, n)
        if os.path.exists(p):
            return p
    return None


def _loudnorm_measure(path):
    r = subprocess.run([ffmpeg_exe(), '-hide_banner', '-i', path, '-af',
                        'loudnorm=I=%.1f:TP=-1.5:LRA=11:print_format=json' % TARGET_LUFS, '-f', 'null', '-'],
                       stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr, re.S)
    return json.loads(m.group(0))


SILENT_DBFS = -70.0


def peak_dbfs(path):
    """Sample peak of a file in dBFS (-inf for digital silence)."""
    x = _decode(path)
    p = float(np.max(np.abs(x))) if len(x) else 0.0
    return 20 * np.log10(p) if p > 0 else float('-inf')


def is_silent(path):
    """True when the track peaks below -70 dBFS: nothing to loudness-normalise."""
    return peak_dbfs(path) < SILENT_DBFS


def build_mix(project, duration):
    voice = os.path.join(project, 'voice.wav')
    music = find_music(project)
    work = os.path.join(project, '.cache')
    os.makedirs(work, exist_ok=True)
    pre = os.path.join(work, 'mix_pre.wav')
    dur = '%.3f' % duration
    if music:
        v_db = speech_db(_decode(voice))
        m = _decode(music)
        m_db = 20 * np.log10(np.sqrt(np.mean(m ** 2)) + 1e-9)
        gain = v_db + BED_DB - m_db
        fc = ('[0:a]aformat=channel_layouts=stereo,apad[v];'
              '[1:a]aformat=channel_layouts=stereo,volume=%.2fdB,afade=t=in:d=0.4,afade=t=out:st=%.3f:d=1.2[m];'
              '[v][m]amix=inputs=2:normalize=0:duration=first,atrim=0:%s[out]' % (gain, max(0.0, duration - 1.2), dur))
        cmd = [ffmpeg_exe(), '-v', 'error', '-y', '-i', voice, '-stream_loop', '-1', '-i', music,
               '-filter_complex', fc, '-map', '[out]', '-ar', '48000', pre]
    else:
        cmd = [ffmpeg_exe(), '-v', 'error', '-y', '-i', voice, '-af', 'aformat=channel_layouts=stereo,apad,atrim=0:%s' % dur,
               '-ar', '48000', pre]
    subprocess.run(cmd, check=True)
    out = os.path.join(work, 'mix.wav')
    if is_silent(pre):
        # captions-only Short without music: the track peaks below -70 dBFS, loudnorm does not apply
        print('audio: silent track (peak below %.0f dBFS): loudness normalisation skipped' % SILENT_DBFS)
        os.replace(pre, out)
        return out
    # Peaky voices (raw mics, TTS) need more gain than linear loudnorm allows under TP -1.5, and loudnorm then falls
    # back to dynamic mode and lands short. So: bring the level near the target with peaks held by a limiter,
    # then linear loudnorm, then verify and correct once.
    m0 = _loudnorm_measure(pre)
    gain = TARGET_LUFS - float(m0['input_i']) + 0.5
    lim = os.path.join(work, 'mix_lim.wav')
    subprocess.run([ffmpeg_exe(), '-v', 'error', '-y', '-i', pre, '-af',
                    'volume=%.2fdB,alimiter=limit=0.79:attack=2:release=60:level=false' % gain, '-ar', '48000', lim],
                   check=True)
    meas = _loudnorm_measure(lim)
    af = ('loudnorm=I=%.1f:TP=-1.5:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true'
          % (TARGET_LUFS, meas['input_i'], meas['input_tp'], meas['input_lra'], meas['input_thresh'], meas['target_offset']))
    subprocess.run([ffmpeg_exe(), '-v', 'error', '-y', '-i', lim, '-af', af, '-ar', '48000', out], check=True)
    i, tp = measure_lufs(out)
    if abs(i - TARGET_LUFS) > 0.7:
        tmp = os.path.join(work, 'mix_fix.wav')
        subprocess.run([ffmpeg_exe(), '-v', 'error', '-y', '-i', out, '-af',
                        'volume=%.2fdB,alimiter=limit=0.84:level=false' % (TARGET_LUFS - i), '-ar', '48000', tmp],
                       check=True)
        os.replace(tmp, out)
    print('audio: %.1f LUFS after normalisation' % measure_lufs(out)[0])
    return out


def measure_lufs(path):
    m = _loudnorm_measure(path)
    return float(m['input_i']), float(m['input_tp'])
