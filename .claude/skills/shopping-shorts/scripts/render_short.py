"""쇼핑 쇼츠 렌더러 (Python 표준 라이브러리 + ffmpeg).

사용:  python render_short.py <프로젝트 폴더>
입력:  <프로젝트>/project.json  (형식은 SKILL.md '4. project.json')
       장면마다 media(사진/영상, 프로젝트 기준 상대경로), voice(wav, 없으면 무음)
출력:  <프로젝트>/out/final.mp4 (1080x1920, 30fps), out/sheet.jpg(검수용 프레임 시트), render_log.txt
"""
import glob
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
W, H, FPS = 1080, 1920, 30
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".bmp")


def find_tool(name):
    p = shutil.which(name)
    if p:
        return p
    pats = [os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*FFmpeg*\*\bin\%s.exe" % name),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\%s.exe" % name),
            r"C:\ffmpeg\bin\%s.exe" % name]
    for pat in pats:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    raise SystemExit(f"{name} 를 찾지 못함. 'winget install Gyan.FFmpeg' 로 설치하세요.")


FFMPEG, FFPROBE = find_tool("ffmpeg"), find_tool("ffprobe")
LOG = None


def run(args, cwd):
    LOG.write("\n$ " + " ".join(f'"{a}"' if " " in str(a) else str(a) for a in args) + "\n")
    LOG.flush()
    r = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = r.stdout.decode("utf-8", "replace")
    LOG.write(out[-3000:])
    if r.returncode != 0:
        raise SystemExit(f"ffmpeg 실패 (render_log.txt 확인): {args[:6]}")
    return out


def duration(path, cwd):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        return float(r.stdout.decode().strip())
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- ASS 자막
def ass_color(hexrgb):
    h = hexrgb.lstrip("#")
    return "&H00%s%s%s" % (h[4:6], h[2:4], h[0:2])


def ass_text(s, hl="FFE400", base="FFFFFF"):
    """*강조*  → 노랑,  줄바꿈 \\n → \\N.  중괄호는 지운다."""
    s = s.replace("{", "(").replace("}", ")").replace("\\n", "\\N").replace("\n", "\\N")
    out, on = "", False
    for part in s.split("*"):
        out += part
        on = not on
        out += "{\\c%s&}" % ass_color(hl) if on else "{\\c%s&}" % ass_color(base)
    # 마지막에 붙은 색 태그 정리
    return out.rsplit("{", 1)[0] if out.endswith("&}") else out


def t(sec):
    sec = max(0.0, sec)
    return "%d:%02d:%05.2f" % (sec // 3600, (sec % 3600) // 60, sec % 60)


def build_ass(p, timings, path):
    st = p.get("style", {})
    hl = st.get("highlight", "FFE400")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Top,Pretendard,{st.get('top_size', 76)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,2,8,60,60,{st.get('top_y', 210)},1
Style: Cap,Pretendard,{st.get('cap_size', 84)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,3,2,50,50,{st.get('cap_y', 470)},1
Style: Badge,Pretendard,{st.get('badge_size', 92)},&H00000000,&H00000000,&H00{ass_color(hl)[4:]},&H00{ass_color(hl)[4:]},-1,0,0,0,100,100,0,0,3,18,0,5,60,60,0,1
Style: Small,Pretendard,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,3,8,0,7,40,40,40,1
Style: Cta,Pretendard,{st.get('cta_size', 64)},&H00FFFFFF,&H00FFFFFF,&H000030FF,&H000030FF,-1,0,0,0,100,100,0,0,3,22,0,2,60,60,{st.get('cta_y', 200)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    total = timings[-1][1]
    ev = []
    if p.get("top_title"):
        ev.append(f"Dialogue: 2,{t(0)},{t(total)},Top,,0,0,0,,{ass_text(p['top_title'], hl)}")
    if p.get("disclosure", True):
        ev.append(f"Dialogue: 3,{t(0)},{t(total)},Small,,0,0,0,,{p.get('disclosure_text', '광고 · 쿠팡 파트너스 활동으로 수수료를 받을 수 있음')}")
    for (s, e), sc in zip(timings, p["scenes"]):
        if sc.get("caption"):
            pop = "{\\fscx112\\fscy112\\t(0,120,\\fscx100\\fscy100)}"
            ev.append(f"Dialogue: 1,{t(s + 0.03)},{t(e)},Cap,,0,0,0,,{pop}{ass_text(sc['caption'], hl)}")
        if sc.get("badge"):
            pos = "{\\an5\\pos(540,%d)\\fscx130\\fscy130\\t(0,160,\\fscx100\\fscy100)}" % st.get("badge_y", 1180)
            ev.append(f"Dialogue: 4,{t(s + 0.1)},{t(e)},Badge,,0,0,0,,{pos}{ass_text(sc['badge'], '000000', '000000')}")
        if sc.get("cta"):
            ev.append(f"Dialogue: 5,{t(s)},{t(e)},Cta,,0,0,0,,{ass_text(sc['cta'], 'FFFFFF')}")
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(head + "\n".join(ev) + "\n")


# ---------------------------------------------------------------- 장면 클립
def scene_clip(i, sc, proj, D, out):
    media = sc.get("media")
    voice = sc.get("voice")
    zoom = float(sc.get("zoom", 0.07))
    fg_w = int(sc.get("fg_width", 1000))
    fg_y = int(sc.get("fg_y_offset", -60))
    args = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error"]
    is_img = media and media.lower().endswith(IMG_EXT)
    if not media:
        args += ["-f", "lavfi", "-t", f"{D:.3f}", "-i", f"color=c=0x111111:s={W}x{H}:r={FPS}"]
    elif is_img:
        args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{D:.3f}", "-i", media]
    else:
        args += ["-stream_loop", "-1", "-ss", str(sc.get("clip_start", 0)), "-t", f"{D:.3f}", "-i", media]
    if voice:
        args += ["-i", voice]
    else:
        args += ["-f", "lavfi", "-t", f"{D:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]
    if not media:
        v = f"[0:v]format=yuv420p,setsar=1[v]"
    elif is_img or sc.get("fit") == "contain":
        zexpr = f"trunc({fg_w}*(1+{zoom}*t/{D:.3f})/2)*2" if zoom >= 0 else f"trunc({fg_w}*(1+{-zoom}*(1-t/{D:.3f}))/2)*2"
        v = (f"[0:v]split[a][b];"
             f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:3,eq=brightness=-0.18:saturation=0.8[bg];"
             f"[b]scale=w='{zexpr}':h=-2:eval=frame[fg];"
             f"[bg][fg]overlay=x='(W-w)/2':y='(H-h)/2+({fg_y})':eval=frame:shortest=1,fps={FPS},format=yuv420p,setsar=1[v]")
    else:
        v = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
             f"fps={FPS},format=yuv420p,setsar=1[v]")
    a = "[1:a]aformat=sample_rates=44100:channel_layouts=stereo,apad[a]"
    args += ["-filter_complex", v + ";" + a, "-map", "[v]", "-map", "[a]", "-t", f"{D:.3f}",
             "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", out]
    run(args, proj)


def main():
    global LOG
    proj = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    os.makedirs(os.path.join(proj, "work"), exist_ok=True)
    os.makedirs(os.path.join(proj, "out"), exist_ok=True)
    LOG = open(os.path.join(proj, "render_log.txt"), "w", encoding="utf-8")
    p = json.load(open(os.path.join(proj, "project.json"), encoding="utf-8"))
    fonts = os.path.join(proj, "work", "fonts")
    os.makedirs(fonts, exist_ok=True)
    shutil.copy(os.path.join(ASSETS, "fonts", "Pretendard-Bold.ttf"), fonts)

    gap = float(p.get("gap", 0.12))
    timings, clips, cur = [], [], 0.0
    for i, sc in enumerate(p["scenes"], 1):
        vd = duration(sc["voice"], proj) if sc.get("voice") else 0.0
        D = round(max(float(sc.get("min_dur", 1.2)), vd + gap) if vd else float(sc.get("dur", 2.0)), 3)
        out = f"work/s{i:02d}.mp4"
        scene_clip(i, sc, proj, D, out)
        clips.append(out)
        timings.append((cur, cur + D))
        cur += D
        print(f"장면 {i}/{len(p['scenes'])}  {D:.2f}초")
    with open(os.path.join(proj, "work", "list.txt"), "w", encoding="utf-8") as f:
        f.writelines(f"file '{os.path.basename(c)}'\n" for c in clips)
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "work/list.txt",
         "-c", "copy", "work/body.mp4"], proj)
    build_ass(p, timings, os.path.join(proj, "work", "subs.ass"))

    total = timings[-1][1]
    bgm = p.get("bgm") or os.path.join(ASSETS, "bgm", "beat.wav")
    inputs = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", "work/body.mp4",
              "-stream_loop", "-1", "-i", bgm]
    fx, mix = [], ["[0:a]", "[b]"]
    k = 2
    for (s, _), sc in zip(timings, p["scenes"]):
        if sc.get("sfx"):
            f = sc["sfx"] if os.path.isabs(sc["sfx"]) else os.path.join(ASSETS, "sfx", sc["sfx"])
            inputs += ["-i", f]
            fx.append(f"[{k}:a]adelay={int(s * 1000)}|{int(s * 1000)},volume={p.get('sfx_gain', 0.6)}[x{k}]")
            mix.append(f"[x{k}]")
            k += 1
    fc = [f"[0:v]subtitles=work/subs.ass:fontsdir=work/fonts[v]",
          f"[1:a]atrim=0:{total:.3f},volume={p.get('bgm_gain', 0.12)},afade=t=out:st={max(0, total - 1):.3f}:d=1[b]"] + fx + \
         [f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]"]
    run(inputs + ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
                  "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "out/final.mp4"], proj)
    run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", "out/final.mp4", "-vf",
         "fps=1,scale=270:-2,tile=6x6", "-frames:v", "1", "out/sheet.jpg"], proj)
    print(f"완료: out/final.mp4 ({total:.1f}초)")
    LOG.write("\nEXIT 0\n")
    LOG.close()


if __name__ == "__main__":
    try:
        main()
    except SystemExit as e:
        if LOG:
            LOG.write(f"\nERROR {e}\nEXIT 1\n")
            LOG.close()
        print(e)
        sys.exit(1)
