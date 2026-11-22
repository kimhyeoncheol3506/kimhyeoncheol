# -*- coding: utf-8 -*-
"""
와따마 스타일 개그 짤(세로 쇼츠) 편집기 - Python 표준 라이브러리 + ffmpeg

  python wadda_edit.py render project.json [--out out.mp4]

레이아웃(720x1280, 와따마 실측):
  흰 배경 / 상단 챕터 제목 "주제;" (y≈300) / 가운데 원본 클립 띠 720x520 (y=360)
  클립 안 하단 컬러 자막 / 클립 아래 가짜 댓글 한 줄 / 아래 1/4 여백
"""
import json, os, re, shutil, subprocess, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

W, H, FPS = 720, 1280, 30
BAND_Y, BAND_H = 360, 520
TITLE_Y = 300
SUB_Y = BAND_Y + BAND_H - 34
COMMENT_Y = BAND_Y + BAND_H + 58
BG = "#FFFEF9"
COLORS = {"yellow": "#FFE83A", "green": "#8CFF3F", "red": "#FF2A2A", "white": "#FFFFFF", "pink": "#FF6FD8",
          "blue": "#4FC3FF", "orange": "#FF9A1F"}
AVATAR = ["#3FB5A3", "#7A5CFF", "#4F8BFF", "#FF7A59", "#B05CFF", "#2EC4F1"]


def find_bin(name):
    p = shutil.which(name)
    if p:
        return p
    hits = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "*FFmpeg*", "**", "bin", name + ".exe"), recursive=True)
    if hits:
        return hits[0]
    sys.exit("ffmpeg 없음: winget install Gyan.FFmpeg")


FFMPEG, FFPROBE = find_bin("ffmpeg"), find_bin("ffprobe")


def ff(args, cwd=None):
    r = subprocess.run([FFMPEG, "-hide_banner", "-y", "-loglevel", "error"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print("\n".join(r.stderr.splitlines()[-20:]))
        raise RuntimeError("ffmpeg 실패")


def fc_opt():
    v = subprocess.run([FFMPEG, "-version"], capture_output=True, text=True).stdout
    m = re.search(r"ffmpeg version n?(\d+)", v)
    return "-/filter_complex" if (int(m.group(1)) if m else 7) >= 7 else "-filter_complex_script"


def assc(c, a=0):
    c = c.lstrip("#")
    return "&H%02X%s%s%s" % (a, c[4:6], c[2:4], c[0:2])


def ts(t):
    t = max(0.0, t)
    return "%d:%02d:%05.2f" % (int(t // 3600), int(t % 3600 // 60), t % 60)


def esc(t):
    return str(t).replace("{", "(").replace("}", ")").replace("\n", "\\N")


def text_w(text, size):
    w = 0
    for ch in text:
        o = ord(ch)
        w += 0.95 if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F else (0.3 if ch == " " else 0.58)
    return w * size


def chapter_ass(ch, D, path, idx):
    title_font = ch.get("title_font", "Black Han Sans")
    sub_font = "Pretendard ExtraBold"
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: %d" % W, "PlayResY: %d" % H, "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
         "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: Title,%s,92,%s,%s,%s,%s,0,0,0,0,100,100,0,0,1,7,3,5,10,10,10,1" % (title_font, assc("#111111"), assc("#111111"), assc("#FFFFFF"), assc("#000000", 0x90)),
         "Style: Sub,%s,44,%s,%s,%s,%s,0,0,0,0,100,100,0,0,1,4,2,2,20,20,10,1" % (sub_font, assc(COLORS["yellow"]), assc(COLORS["yellow"]), assc("#000000"), assc("#000000", 0x60)),
         "Style: Pop,%s,104,%s,%s,%s,%s,0,0,0,0,100,100,0,0,1,7,4,5,10,10,10,1" % (title_font, assc(COLORS["red"]), assc(COLORS["red"]), assc("#FFFFFF"), assc("#000000", 0x70)),
         "Style: Cmt,Pretendard Medium,24,%s,%s,%s,%s,0,0,0,0,100,100,0,0,1,0,0,4,10,10,10,1" % (assc("#333333"), assc("#333333"), assc("#000000"), assc("#000000")),
         "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    ev = lambda s, e, st, tx, layer=0: L.append("Dialogue: %d,%s,%s,%s,,0,0,0,,%s" % (layer, ts(s), ts(e), st, tx))
    # 챕터 제목 (R-W2)
    ev(0, D, "Title", "{\\pos(%d,%d)}%s" % (W // 2, TITLE_Y, esc(ch["title"])))
    # 자막 (R-W4)
    for s in ch.get("subs", []):
        col = COLORS.get(s.get("color", "yellow"), s.get("color", COLORS["yellow"]))
        txt = esc(s["text"])
        if s.get("style") == "paren":           # (상황 설명ㅋㅋ) 흰 글씨 조금 작게
            tag = "{\\pos(%d,%d)\\fs38\\c%s}" % (W // 2, SUB_Y, assc("#FFFFFF"))
        else:
            parts = re.split(r"\[(\w+):([^\]]+)\]", txt)     # [red:단어] 부분 강조
            out = ""
            for i in range(0, len(parts), 3):
                out += parts[i]
                if i + 2 < len(parts):
                    out += "{\\c%s}%s{\\c%s}" % (assc(COLORS.get(parts[i + 1], COLORS["red"])), parts[i + 2], assc(col))
            txt = out
            tag = "{\\pos(%d,%d)\\c%s}" % (W // 2, SUB_Y, assc(col))
        ev(s["t0"], s["t1"], "Sub", tag + txt, 1)
    # 팝 텍스트 (R-W5): 크게 튀어나왔다 줄어듦
    for p in ch.get("pops", []):
        at, du = p["at"], p.get("dur", 1.1)
        col = COLORS.get(p.get("color", "red"), COLORS["red"])
        ev(at, at + du, "Pop", "{\\pos(%d,%d)\\c%s\\fscx170\\fscy170\\t(0,140,\\fscx100\\fscy100)\\fad(0,120)}%s"
           % (W // 2 + p.get("dx", 0), BAND_Y + int(BAND_H * p.get("y", 0.42)), assc(col), esc(p["text"])), 2)
    # 가짜 댓글 줄 (R-W6): 흐린 아바타 + 흐린 닉네임 + 댓글
    for k, c in enumerate(ch.get("comments", [])):
        t0 = c.get("at", 0); t1 = ch["comments"][k + 1]["at"] if k + 1 < len(ch["comments"]) else D
        col = AVATAR[(idx * 2 + k) % len(AVATAR)]
        ev(t0, t1, "Cmt", "{\\an7\\pos(%d,%d)\\bord0\\shad0\\blur6\\c%s\\p1}m 22 0 b 34 0 44 10 44 22 b 44 34 34 44 22 44 b 10 44 0 34 0 22 b 0 10 10 0 22 0{\\p0}" % (88, COMMENT_Y - 22, assc(col)))
        ev(t0, t1, "Cmt", "{\\an7\\pos(%d,%d)\\bord0\\shad0\\blur4\\c%s\\p1}m 0 0 l 130 0 l 130 18 l 0 18{\\p0}" % (150, COMMENT_Y - 24, assc("#CFCFCF")))
        ev(t0, t1, "Cmt", "{\\an7\\pos(%d,%d)}%s" % (150, COMMENT_Y + 4, esc(c["text"])))
    open(path, "w", encoding="utf-8-sig").write("\n".join(L) + "\n")


def render(pj, out=None):
    pdir = os.path.dirname(os.path.abspath(pj))
    P = json.load(open(pj, encoding="utf-8-sig"))
    build = os.path.join(pdir, "_build"); os.makedirs(os.path.join(build, "fonts"), exist_ok=True)
    for f in glob.glob(os.path.join(HERE, "fonts", "*")):
        shutil.copy(f, os.path.join(build, "fonts"))
    FC = fc_opt()
    sfx = os.path.join(build, "pop.wav")
    if not os.path.exists(sfx):
        ff(["-f", "lavfi", "-i", "aevalsrc='0.7*sin(2*PI*(900-3800*t)*t)*exp(-22*t)':s=48000:d=0.22", "-ac", "2", sfx])
    whoosh = os.path.join(build, "whoosh.wav")
    if not os.path.exists(whoosh):
        ff(["-f", "lavfi", "-i", "anoisesrc=d=0.35:c=pink:a=0.5:r=48000,highpass=f=500,afade=t=in:d=0.12,afade=t=out:st=0.12:d=0.23", "-ac", "2", whoosh])
    clips = []
    for i, ch in enumerate(P["chapters"]):
        src = ch["src"] if os.path.isabs(ch["src"]) else os.path.join(pdir, ch["src"])
        a, b = float(ch["in"]), float(ch["out"]); D = b - a
        cx = float(ch.get("x", 0.5)); cy = float(ch.get("y", 0.40)); z = float(ch.get("zoom", 1.0))
        assp = "ch%02d.ass" % i
        chapter_ass(ch, D, os.path.join(build, assp), i)
        # 원본 클립: 하단 원본자막/로고를 피해 위쪽 중심으로 크롭 (R-W3)
        cw = "trunc(min(iw\\,ih*%.4f/%.3f)/2)*2" % (W / BAND_H, z)
        chh = "trunc(%s/%.4f/2)*2" % (cw, W / BAND_H)
        zexpr = "1"
        for p in ch.get("pops", []):
            if p.get("zoom"):
                at = p["at"]; zz = p["zoom"]
                zexpr = "if(between(on/%d,%.3f,%.3f),min(%.3f,1+%.3f*(on/%d-%.3f)/0.12),%s)" % (FPS, at, at + p.get("dur", 1.1) + 0.6, zz, zz - 1, FPS, at, zexpr)
        g = ["color=c=0x%s:s=%dx%d:r=%d:d=%.3f[bg]" % (BG[1:], W, H, FPS, D + 0.2),
             "[0:v]fps=%d,crop=w=%s:h=%s:x=(iw-ow)*%.3f:y=max(0\\,min(ih-oh\\,ih*%.3f-oh/2)),scale=%d:%d,setsar=1,"
             "zoompan=z='%s':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=%dx%d:fps=%d[cl]" % (FPS, cw, chh, cx, cy, W, BAND_H, zexpr, W, BAND_H, FPS),
             "[bg][cl]overlay=0:%d:shortest=1[v1]" % BAND_Y,
             "[v1]subtitles=%s:fontsdir=fonts,format=yuv420p[v]" % assp]
        # 오디오: 원본 + 팝 효과음
        ain = ["[0:a]aresample=48000,aformat=channel_layouts=stereo[a0]"]
        mix = ["[a0]"]; extra = []
        for k, p in enumerate(ch.get("pops", [])):
            ms = int(p["at"] * 1000)
            extra += ["-i", sfx]
            ain.append("[%d:a]volume=0.45,adelay=%d|%d[p%d]" % (len(extra) // 2, ms, ms, k)); mix.append("[p%d]" % k)
        extra += ["-i", whoosh]
        ain.append("[%d:a]volume=0.25[wh]" % (len(extra) // 2)); mix.append("[wh]")
        ain.append("%samix=inputs=%d:normalize=0:duration=first[a]" % ("".join(mix), len(mix)))
        script = os.path.join(build, "ch%02d.txt" % i)
        open(script, "w", encoding="utf-8").write(";\n".join(g + ain))
        o = "ch%02d.mp4" % i
        ff(["-ss", "%.3f" % a, "-t", "%.3f" % D, "-i", src] + extra + [FC, os.path.basename(script), "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", "%.3f" % D, o], cwd=build)
        clips.append(o)
        print("  챕터 %d %-12s %5.1fs" % (i + 1, ch["title"], D))
    open(os.path.join(build, "list.txt"), "w", encoding="utf-8").write("".join("file '%s'\n" % c for c in clips))
    out = os.path.abspath(out or os.path.join(pdir, P.get("output", "short.mp4")))
    ff(["-f", "concat", "-safe", "0", "-i", "list.txt", "-c:v", "copy", "-af", "loudnorm=I=-13:TP=-1.0:LRA=11", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", out], cwd=build)
    print("[완료]", out)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "render":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
        render(sys.argv[2], o)
    else:
        print(__doc__)
