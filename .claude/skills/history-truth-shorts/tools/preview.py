# -*- coding: utf-8 -*-
"""풀 렌더 전 '앞 N초 미리보기' mp4 (자막·음성 포함, 기본 20초, 540x960).
Stickman Video Director 의 흐름처럼: 대본 + 20초 미리보기를 먼저 보여주고 OK 받은 뒤 풀 렌더.
첫 3초 훅(그림 변화·첫 문장·자막)과 목소리 톤을 싸게 확인하는 용도.
사용: python preview.py <프로젝트> [--sec 20] [--start 0] [--workers 4] [--audio voice.wav] [--out preview.mp4]
  - plan 이 끝난 프로젝트(plan.json). 렌더 청크와 무관하게 따로 그림.
  - --audio 를 final_sfx.mp4 처럼 효과음 믹스 파일로 주면 그 소리로 미리보기.
엔진 경로: TOON2D_DIR 또는 ../../mystery-cartoon/kits/toon2d
"""
import argparse, os, subprocess, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.environ.get("TOON2D_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "mystery-cartoon", "kits", "toon2d"))
sys.path.insert(0, ENG)

ap = argparse.ArgumentParser()
ap.add_argument("proj")
ap.add_argument("--sec", type=float, default=20.0)
ap.add_argument("--start", type=float, default=0.0)
ap.add_argument("--workers", type=int, default=os.cpu_count() or 2)
ap.add_argument("--audio", default="voice.wav")
ap.add_argument("--out", default="preview.mp4")
ap.add_argument("--w", type=int, default=540)
a = ap.parse_args()
P = os.path.abspath(a.proj)
W, H = a.w, a.w * 16 // 9
RT = None


def init():
    global RT
    from toon2d import render
    RT = render.load(P)


def draw(i):
    from PIL import Image
    s = RT.frame(i, subframes=1)
    import skia
    arr = s.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    return Image.fromarray(arr[:, :, :3]).resize((W, H)).tobytes()


if __name__ == "__main__":
    try:
        import imageio_ffmpeg
        FF = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        FF = "ffmpeg"
    import json
    fps = json.load(open(os.path.join(P, "plan.json"), encoding="utf-8")).get("fps", 30)
    f0, n = int(a.start * fps), int(a.sec * fps)
    out = os.path.join(P, a.out)
    aud = a.audio if os.path.isabs(a.audio) else os.path.join(P, a.audio)
    cmd = [FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(fps), "-i", "-",
           "-ss", "%.3f" % a.start, "-t", "%.3f" % a.sec, "-i", aud, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-dn", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(a.workers, initializer=init) as pool:
        for k, buf in enumerate(pool.imap(draw, range(f0, f0 + n), chunksize=4)):
            ff.stdin.write(buf)
            if k % 150 == 0:
                print("frame %d/%d" % (k, n), flush=True)
    ff.stdin.close(); ff.wait()
    print("OUT", out)
