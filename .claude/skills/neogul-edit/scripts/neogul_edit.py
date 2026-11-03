# -*- coding: utf-8 -*-
"""
너굴경제 스타일 자동 편집기 (Python 표준 라이브러리 + ffmpeg)

  python neogul_edit.py render  project.json [--preview] [--out out.mp4]
  python neogul_edit.py tighten voice.wav --srt voice.srt --out-dir outdir
  python neogul_edit.py analyze reference.mp4 [--out dir]
  python neogul_edit.py new     <폴더>          # 프로젝트 템플릿 생성
  python neogul_edit.py demo    <폴더>          # Windows TTS로 데모 영상 생성

규칙 수치는 같은 폴더의 rules.json(규칙집 R-코드)에서 읽는다.
"""
import argparse, glob, json, math, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

RULES = json.load(open(os.path.join(HERE, "rules.json"), encoding="utf-8"))


# ---------------------------------------------------------------- utils
def find_bin(name):
    p = shutil.which(name)
    if p:
        return p
    env = os.environ.get(name.upper())
    if env and os.path.exists(env):
        return env
    pats = [os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "*FFmpeg*", "**", "bin", name + ".exe"),
            r"C:\ffmpeg\bin\%s.exe" % name]
    for pat in pats:
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    sys.exit("[오류] %s 를 찾을 수 없습니다. winget install Gyan.FFmpeg 로 설치하세요." % name)


FFMPEG = None
FFPROBE = None


def ff(args, cwd=None, quiet=True):
    cmd = [FFMPEG, "-hide_banner", "-y"] + (["-loglevel", "error"] if quiet else []) + args
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("\n".join(r.stderr.splitlines()[-25:]))
        raise RuntimeError("ffmpeg 실패: " + " ".join(args[:6]) + " ...")
    return r.stderr


def probe_duration(p):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def hexc(c, alpha=None):
    c = c.lstrip("#")
    s = "0x" + c.upper()
    return s + ("@%.2f" % alpha if alpha is not None else "")


def assc(c, a=0):
    c = c.lstrip("#")
    r, g, b = c[0:2], c[2:4], c[4:6]
    return "&H%02X%s%s%s" % (a, b.upper(), g.upper(), r.upper())


def text_w(text, size):
    w = 0.0
    for ch in text:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F:
            w += 0.93
        elif ch == " ":
            w += 0.27
        elif ch.isdigit():
            w += 0.6
        elif ch.isupper():
            w += 0.66
        elif ch.isalpha():
            w += 0.55
        elif ch in "%":
            w += 0.85
        else:
            w += 0.36
    return w * size


def ass_text(t):
    t = str(t).replace("\\", "＼").replace("{", "(").replace("}", ")")
    return t.replace("\r", "").replace("\n", "\\N")


def ts_ass(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


# ---------------------------------------------------------------- SRT
def parse_srt(path):
    raw = open(path, encoding="utf-8-sig").read().replace("\r\n", "\n")
    out = []
    for block in re.split(r"\n\s*\n", raw.strip()):
        lines = [l for l in block.split("\n") if l.strip()]
        if len(lines) < 2:
            continue
        idx = 0 if "-->" in lines[0] else 1
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", lines[idx])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        st = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        en = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        out.append({"start": st, "end": en, "text": " ".join(lines[idx + 1:]).strip()})
    return out


def write_srt(subs, path):
    def f(t):
        ms = int(round(t * 1000)); h = ms // 3600000; m = ms % 3600000 // 60000; s = ms % 60000 // 1000
        return "%02d:%02d:%02d,%03d" % (h, m, s, ms % 1000)
    with open(path, "w", encoding="utf-8") as fp:
        for i, s in enumerate(subs, 1):
            fp.write("%d\n%s --> %s\n%s\n\n" % (i, f(s["start"]), f(s["end"]), s["text"]))


# ---------------------------------------------------------------- tighten (R-A1)
def detect_silences(audio, noise_db, min_d):
    err = ff(["-i", audio, "-vn", "-af", "silencedetect=noise=%ddB:d=%.2f" % (noise_db, min_d), "-f", "null", "-"], quiet=False)
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en))


def tighten(audio, srt_subs, out_audio, extra_times=None):
    cfg = RULES["audio"]["tighten"]
    sil = detect_silences(audio, cfg["noise_db"], cfg["min_silence"])
    dur = probe_duration(audio)
    keep = cfg["keep"]
    removed = []
    for a, b in sil:
        a = max(0.0, a); b = min(dur, b)
        if a <= 0.01:            # 맨 앞 무음은 0.05초만 남김
            if b - 0.05 > 0:
                removed.append((0.0, b - 0.05))
            continue
        if b >= dur - 0.01:      # 맨 끝 무음은 0.3초만 남김
            if dur - a > 0.3:
                removed.append((a + 0.3, dur))
            continue
        if b - a > keep:
            half = keep / 2
            removed.append((a + half, b - half))
    if not removed:
        shutil.copy(audio, out_audio)
    else:
        expr = "+".join("between(t,%.3f,%.3f)" % r for r in removed)
        script = out_audio + ".filter.txt"
        open(script, "w", encoding="utf-8").write("[0:a]aselect='not(%s)',asetpts=N/SR/TB[a]" % expr)
        ff(["-i", audio, "-/filter_complex", script, "-map", "[a]", "-ar", "48000", out_audio])

    def fmap(t):
        return t - sum(min(max(0.0, t - a), b - a) for a, b in removed)
    subs2 = [dict(s, start=fmap(s["start"]), end=fmap(s["end"])) for s in (srt_subs or [])]
    total_cut = sum(b - a for a, b in removed)
    print("[tighten] 무음 %d곳 압축, %.1f초 단축 (%.1f → %.1f초)" % (len(removed), total_cut, dur, dur - total_cut))
    return subs2, fmap


# ---------------------------------------------------------------- SFX (R-S*)
SFX_DEF = {
    "impact": "aevalsrc='0.9*sin(2*PI*(48+70*exp(-9*t))*t)*exp(-3.2*t)+0.25*(random(0)*2-1)*exp(-14*t)':s=48000:d=1.3",
    "whoosh": "anoisesrc=d=0.7:c=pink:a=0.9:r=48000,highpass=f=350,lowpass=f=5200,afade=t=in:d=0.35:curve=exp,afade=t=out:st=0.35:d=0.35",
    "pop": "aevalsrc='0.8*sin(2*PI*(1250-5200*t)*t)*exp(-30*t)':s=48000:d=0.16",
    "click": "aevalsrc='0.9*sin(2*PI*2600*t)*exp(-80*t)+0.4*sin(2*PI*1300*t)*exp(-50*t)':s=48000:d=0.08",
    "ding": "aevalsrc='0.5*sin(2*PI*1568*t)*exp(-5*t)+0.3*sin(2*PI*2349*t)*exp(-6*t)':s=48000:d=0.9",
}


def ensure_sfx(build, custom):
    os.makedirs(os.path.join(build, "sfx"), exist_ok=True)
    paths = {}
    for k, expr in SFX_DEF.items():
        if custom and custom.get(k) and os.path.exists(custom[k]):
            paths[k] = os.path.abspath(custom[k]); continue
        p = os.path.join(build, "sfx", k + ".wav")
        if not os.path.exists(p):
            ff(["-f", "lavfi", "-i", expr, "-ac", "2", p])
        paths[k] = p
    return paths


# ---------------------------------------------------------------- ASS writer
class Ass:
    def __init__(self):
        self.styles = []
        self.events = []

    def style(self, name, font, size, primary, outline, back, bold=0, border_style=1, outline_w=0, align=7, margin_v=0):
        self.styles.append("Style: %s,%s,%d,%s,%s,%s,%s,%d,0,0,0,100,100,0,0,%d,%g,0,%d,40,40,%d,1"
                           % (name, font, size, primary, primary, outline, back, bold, border_style, outline_w, align, margin_v))

    def ev(self, start, end, style, text, layer=0):
        self.events.append("Dialogue: %d,%s,%s,%s,,0,0,0,,%s" % (layer, ts_ass(start), ts_ass(end), style, text))

    def save(self, path):
        W, H = RULES["canvas"]["width"], RULES["canvas"]["height"]
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: %d\nPlayResY: %d\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n" % (W, H))
            f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write("\n".join(self.styles) + "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            f.write("\n".join(self.events) + "\n")


FONT_REG = "Pretendard Medium"
FONT_BOLD = "Pretendard Bold"
FONT_BLACK = "Pretendard ExtraBold"


def base_scene_ass():
    a = Ass()
    a.style("T", FONT_BOLD, 40, assc("#FFFFFF"), assc("#000000"), assc("#000000"), align=7)
    a.style("Box", FONT_BLACK, 90, assc("#111111"), assc("#FFFFFF"), assc("#FFFFFF"), border_style=3, outline_w=20, align=8)
    return a


def tag(x, y, size, color, font=FONT_BOLD, an=7, extra=""):
    return "{\\an%d\\pos(%d,%d)\\fn%s\\fs%d\\c%s\\bord0\\shad0%s}" % (an, x, y, font, size, assc(color), extra)


# ---------------------------------------------------------------- subtitle splitting (R-T2)
def split_sub(s, maxc):
    t = s["text"]
    if len(t) <= maxc:
        return [s]
    words = t.split(" ")
    best, bi = 1e9, 1
    for i in range(1, len(words)):
        left = len(" ".join(words[:i]))
        d = abs(left - len(t) / 2)
        if words[i - 1][-1:] in ".?!":
            d -= len(t) * 0.3       # 문장 끝에서 자르기 우선
        elif words[i - 1][-1:] in ",요고면서데":
            d -= len(t) * 0.08
        if d < best:
            best, bi = d, i
    a, b = " ".join(words[:bi]), " ".join(words[bi:])
    if not a or not b:
        return [s]
    mid = s["start"] + (s["end"] - s["start"]) * len(a) / max(1, len(a) + len(b))
    return split_sub(dict(s, end=mid, text=a), maxc) + split_sub(dict(s, start=mid, text=b), maxc)


def classify_sub(text):
    t = text.strip()
    if t.startswith("**") and t.endswith("**") and len(t) > 4:
        return "Emph", t[2:-2].strip()
    if t.startswith("!"):
        return "Emph", t[1:].strip()
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("“") and t.endswith("”")) or t.startswith("[Q]"):
        return "Quote", t.replace("[Q]", "").strip()
    return "Sub", t


def build_sub_ass(subs, path):
    R = RULES["subtitle"]
    a = Ass()
    fs, mv, pad = R["font_size"], R["margin_v"], R["box_pad"]
    for name, key in (("Sub", "normal"), ("Emph", "emph"), ("Quote", "quote")):
        c = R[key]
        a.style(name, FONT_REG if key == "normal" else FONT_BOLD, fs, assc(c["text"]), assc(c["box"], c["box_alpha"]),
                assc(c["box"], c["box_alpha"]), border_style=3, outline_w=pad, align=2, margin_v=mv)
    for s in subs:
        for p in split_sub(s, R["max_chars"]):
            st, txt = classify_sub(p["text"])
            a.ev(p["start"], p["end"], st, ass_text(txt))
    a.save(path)


# ---------------------------------------------------------------- scene builders
class Ctx:
    def __init__(self, W, H, fps, build, proj_dir):
        self.W, self.H, self.fps, self.build, self.dir = W, H, fps, build, proj_dir
        self.S = W / RULES["canvas"]["width"]

    def p(self, v):
        return int(round(v * self.S))

    def path(self, rel):
        if rel is None:
            return None
        p = rel if os.path.isabs(rel) else os.path.join(self.dir, rel)
        if not os.path.exists(p):
            raise FileNotFoundError("파일 없음: " + p)
        return os.path.abspath(p)


def drawbox(ctx, x, y, w, h, color, t="fill", at=None, until=None, alpha=1.0):
    en = ""
    if at is not None and until is not None:
        en = ":enable='between(t,%.3f,%.3f)'" % (at, until)
    elif at is not None:
        en = ":enable='gte(t,%.3f)'" % at
    th = "fill" if t == "fill" else str(max(1, ctx.p(t)))
    return "drawbox=x=%d:y=%d:w=%d:h=%d:color=%s:t=%s%s" % (ctx.p(x), ctx.p(y), max(1, ctx.p(w)), max(1, ctx.p(h)), hexc(color, alpha), th, en)


def is_image(p):
    return os.path.splitext(p)[1].lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def media_input(ctx, src, D, start_from=0.0):
    """returns ffmpeg input args for a media file"""
    if is_image(src):
        return ["-i", src]
    return ["-stream_loop", "-1", "-ss", "%.3f" % start_from, "-i", src]


def zoom_chain(ctx, src, idx, N, zexpr, out):
    """cover-fit media and apply zoompan with expression of time variable T (seconds)."""
    W, H, fps = ctx.W, ctx.H, ctx.fps
    z = zexpr.replace("T", "(on/%d)" % fps)
    if is_image(src):
        return ("[%d:v]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,setsar=1,"
                "zoompan=z='%s':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=%d:s=%dx%d:fps=%d,setsar=1[%s]"
                % (idx, W * 2, H * 2, W * 2, H * 2, z, N, W, H, fps, out))
    return ("[%d:v]fps=%d,scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,setsar=1,"
            "zoompan=z='%s':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=%dx%d:fps=%d,setsar=1[%s]"
            % (idx, fps, W, H, W, H, z, W, H, fps, out))


def theme_colors(theme):
    C = RULES["colors"]
    if theme == "cream":
        return dict(bg=C["cream_bg"], card=C["card_bg_cream"], border=C["card_border_cream"], text=C["text_cream_theme"], muted=C["muted_cream"])
    return dict(bg=C["dark_bg"], card=C["card_bg_dark"], border=C["card_border_dark"], text=C["text_dark_theme"], muted=C["muted_dark"])


def color_of(name, default):
    C = RULES["colors"]
    if not name:
        return default
    if name.startswith("#"):
        return name
    return C.get(name, C.get(name + "_num", default))


def slide_scene(ctx, sc, D, ass, sfx_events):
    R = RULES["slide"]; C = RULES["colors"]
    th = theme_colors(sc.get("theme", "dark"))
    mx = R["margin_x"]; W = RULES["canvas"]["width"]
    boxes = []
    rects = {}
    # header (R-L1)
    if sc.get("section"):
        ass.ev(0, D, "T", tag(mx, R["section_y"], R["section_size"], th["muted"], FONT_REG) + ass_text(sc["section"]))
    if sc.get("source"):
        ass.ev(0, D, "T", tag(W - mx, R["section_y"], R["source_size"], th["muted"], FONT_REG, an=9) + ass_text(sc["source"]))
    title = sc.get("title", "")
    if sc.get("title_style") == "news":   # 뉴스 헤드라인 박스형 제목 (R-L3)
        yy = 40
        for line in title.split("\n"):
            ass.ev(0, D, "Box", "{\\an7\\pos(%d,%d)\\fs72\\bord16}" % (mx - 20, yy) + ass_text(line))
            yy += 112
        sub_y = yy + 8
    else:
        ass.ev(0, D, "T", tag(mx, R["title_y"], R["title_size"], th["text"], FONT_BLACK) + ass_text(title))
        sub_y = R["subtitle_y"]
    if sc.get("subtitle"):
        ass.ev(0, D, "T", tag(mx, sub_y, R["subtitle_size"], th["muted"], FONT_REG) + ass_text(sc["subtitle"]))
    if sc.get("title_style") != "news":
        boxes.append(drawbox(ctx, mx, R["divider_y"], W - 2 * mx, 2, th["border"]))
    if sc.get("underline"):
        uw = text_w(title, R["title_size"])
        boxes.append(drawbox(ctx, mx, R["title_y"] + R["underline_offset"], uw, R["underline_thickness"], C["red"], at=float(sc.get("underline_at", 0.3))))
    top, bot = R["content_top"], R["content_bottom"]
    extra_inputs = []
    overlay = None
    kind = sc.get("layout") or ("cards" if sc.get("cards") else "bars" if sc.get("bars") else "bignum" if sc.get("bignum") else "bullets" if sc.get("bullets") else "image" if sc.get("image") else "none")
    if kind == "cards":
        cards = sc["cards"]; n = len(cards); gap = 96 if n > 1 else 0
        cw = (W - 2 * mx - gap * (n - 1)) / n; ch = sc.get("card_height", 300); y = top + 40
        for i, cd in enumerate(cards):
            x = mx + i * (cw + gap); at = cd.get("at")
            fill = color_of(cd.get("fill"), th["card"])
            boxes.append(drawbox(ctx, x, y, cw, ch, th["border"], at=at))
            boxes.append(drawbox(ctx, x + 2, y + 2, cw - 4, ch - 4, fill, at=at))
            t0 = float(at or 0)
            dark_text = cd.get("fill") is not None and fill.upper() in (C["yellow"].upper(), "#FFFFFF", C["cream_bg"].upper())
            tcol = "#161412" if dark_text else th["text"]
            if "value" in cd:
                if cd.get("label"):
                    ass.ev(t0, D, "T", tag(x + 36, y + 38, 30, th["muted"], FONT_REG) + ass_text(cd["label"]))
                vcol = color_of(cd.get("color"), tcol)
                unit = ("{\\fs%d}" % int(cd.get("size", 100) * 0.42) + ass_text(cd["unit"])) if cd.get("unit") else ""
                ass.ev(t0, D, "T", tag(x + 36, y + 92, cd.get("size", 100), vcol, FONT_BLACK) + ass_text(cd["value"]) + unit)
                if cd.get("caption"):
                    ass.ev(t0, D, "T", tag(x + 36, y + ch - 72, 30, tcol if dark_text else "#D6D0C6" if th["text"] == "#FFFFFF" else "#4A4640", FONT_REG) + ass_text(cd["caption"]))
            else:
                ass.ev(t0, D, "T", tag(int(x + cw / 2), int(y + ch / 2), cd.get("size", 46), tcol, FONT_BLACK, an=5) + ass_text(cd.get("text", "")))
            rects["card:%d" % i] = (x, y, cw, ch)
            if i < n - 1 and sc.get("arrows", True):
                ass.ev(t0, D, "T", tag(int(x + cw + gap / 2), int(y + ch / 2), 54, th["muted"], FONT_BOLD, an=5) + "→")
        if sc.get("banner"):
            bn = sc["banner"]; by = y + ch + 48
            boxes.append(drawbox(ctx, mx, by, W - 2 * mx, 92, th["card"]))
            txt = ass_text(bn.get("text", ""))
            if bn.get("accent"):
                txt += " {\\c%s\\fn%s}%s" % (assc(C["yellow"]), FONT_BLACK, ass_text(bn["accent"]))
            ass.ev(float(bn.get("at", 0)), D, "T", tag(W // 2, by + 46, 36, "#E6E0D6" if th["text"] == "#FFFFFF" else "#2A2723", FONT_BOLD, an=5) + txt)
    elif kind == "bars":
        rows = sc["bars"]; maxv = max(abs(float(r.get("value", 1))) for r in rows) or 1
        x0, maxw = mx + 330, sc.get("bar_max", 1020); rh, gap = 68, 40
        y = top + 40 + max(0, (bot - top - 80 - len(rows) * (rh + gap)) // 2)
        for i, r in enumerate(rows):
            yy = y + i * (rh + gap); at = r.get("at"); t0 = float(at or 0)
            bw = max(8, maxw * abs(float(r.get("value", 0))) / maxv)
            col = color_of(r.get("color"), C["gray_bar"])
            ass.ev(t0, D, "T", tag(x0 - 28, yy + rh // 2, 30, th["muted"] if not r.get("strong") else th["text"], FONT_BOLD, an=6) + ass_text(r.get("label", "")))
            boxes.append(drawbox(ctx, x0, yy, bw, rh, col, at=at))
            ass.ev(t0, D, "T", tag(int(x0 + bw + 24), yy + rh // 2, 40, color_of(r.get("text_color"), th["text"]), FONT_BLACK, an=4) + ass_text(r.get("text", r.get("value", ""))))
            if r.get("arrow"):
                aat = float(r.get("arrow_at", t0 + 0.4))
                boxes.append(drawbox(ctx, x0 + 24, yy + rh // 2 - 4, bw - 90, 8, C["red"], at=aat))
                ass.ev(aat, D, "T", "{\\an4\\pos(%d,%d)\\bord0\\shad0\\c%s\\p1}m 0 -22 l 44 0 l 0 22{\\p0}" % (int(x0 + bw - 70), yy + rh // 2, assc(C["red"])))
                sfx_events.append(("pop", aat))
            rects["bar:%d" % i] = (x0 - 300, yy, bw + 300 + 200, rh)
    elif kind == "bignum":
        b = sc["bignum"]; size = b.get("size", 230); col = color_of(b.get("color"), C["red_num"])
        unit = b.get("unit", "")
        wv = text_w(str(b["value"]), size) + text_w(unit, size * 0.4)
        cx, cy = W // 2, top + 200
        ass.ev(0, D, "T", tag(cx, cy, size, col, FONT_BLACK, an=5) + ass_text(b["value"]) + ("{\\fs%d}%s" % (int(size * 0.4), ass_text(unit)) if unit else ""))
        if b.get("caption"):
            ass.ev(0, D, "T", tag(cx, cy + 190, 32, th["muted"], FONT_REG, an=5) + ass_text(b["caption"]))
        bx, by, bw2, bh = cx - wv / 2 - 50, cy - size * 0.62, wv + 100, size * 1.24
        L, T = 56, 9
        for (xx, yy) in ((bx, by), (bx + bw2 - L, by), (bx, by + bh - T), (bx + bw2 - L, by + bh - T)):
            boxes.append(drawbox(ctx, xx, yy, L, T, col))
        for (xx, yy) in ((bx, by), (bx + bw2 - T, by), (bx, by + bh - L), (bx + bw2 - T, by + bh - L)):
            boxes.append(drawbox(ctx, xx, yy, T, L, col))
        sfx_events.append(("ding", 0.05))
        rects["bignum"] = (bx, by, bw2, bh)
    elif kind == "bullets":
        step = float(sc.get("build_step", 0))
        for i, b in enumerate(sc["bullets"]):
            t0 = float(b.get("at", i * step)) if isinstance(b, dict) else i * step
            txt = b["text"] if isinstance(b, dict) else b
            yy = top + 50 + i * 96
            boxes.append(drawbox(ctx, mx, yy + 8, 14, 44, C["yellow"], at=t0))
            ass.ev(t0, D, "T", tag(mx + 40, yy, 46, th["text"], FONT_BOLD) + ass_text(txt))
            rects["bullet:%d" % i] = (mx - 10, yy - 12, text_w(txt, 46) + 80, 80)
    elif kind == "image":
        src = ctx.path(sc["image"])
        bx, by, bw2, bh = sc.get("image_box", [mx, top + 10, W - 2 * mx, bot - top - 10])
        extra_inputs += media_input(ctx, src, D)
        overlay = (bx, by, bw2, bh, is_image(src))
        rects["image"] = (bx, by, bw2, bh)
    # pointers: red arrows (R-E2)
    for pt in sc.get("pointers", []):
        at = float(pt.get("at", 0.8)); x, y = pt["x"], pt["y"]; ang = float(pt.get("angle", 135))
        ass.ev(at, D, "T", "{\\an7\\pos(%d,%d)\\org(%d,%d)\\frz%.1f\\bord0\\shad0\\c%s\\p1}m 0 15 l 82 15 l 82 0 l 124 26 l 82 52 l 82 37 l 0 37{\\p0}"
               % (x - 124, y - 26, x, y, ang, assc(C["red"])))
        sfx_events.append(("pop", at))
    # highlights (R-E1)
    for hl in sc.get("highlights", []):
        at = float(hl.get("at", 0.8))
        if "rect" in hl:
            x, y, w, h = hl["rect"]
        else:
            if hl.get("target") not in rects:
                print("  [경고] highlight target 없음:", hl.get("target")); continue
            x, y, w, h = rects[hl["target"]]
        pad = R["highlight_pad"]
        boxes.append(drawbox(ctx, x - pad, y - pad, w + 2 * pad, h + 2 * pad, C["red"], t=R["highlight_thickness"], at=at))
        sfx_events.append(("pop", at))
    return th["bg"], boxes, extra_inputs, overlay


def render_scene(ctx, i, sc, D, N, prev_type, next_type, sfx_events, glob_t0):
    """renders one scene to clips/scene_XXX.mp4; returns path"""
    W, H, fps = ctx.W, ctx.H, ctx.fps
    C = RULES["colors"]
    typ = sc.get("type", "slide")
    ass = base_scene_ass()
    local_sfx = []
    inputs = []
    g = []
    cur = None
    if typ == "slide":
        bg, boxes, extra, ov = slide_scene(ctx, sc, D, ass, local_sfx)
        inputs += ["-f", "lavfi", "-i", "color=c=%s:s=%dx%d:r=%d:d=%.3f" % (hexc(bg), W, H, fps, D + 0.5)]
        g.append("[0:v]" + (",".join(boxes) if boxes else "null") + "[b0]")
        cur = "b0"
        if ov:
            inputs += extra
            bx, by, bw, bh, img = ov
            g.append("[1:v]%sscale=%d:%d:force_original_aspect_ratio=decrease,setsar=1[ov]" % ("" if img else "fps=%d," % fps, ctx.p(bw), ctx.p(bh)))
            g.append("[%s][ov]overlay=x=%d+(%d-w)/2:y=%d+(%d-h)/2:shortest=0:eof_action=repeat[b1]" % (cur, ctx.p(bx), ctx.p(bw), ctx.p(by), ctx.p(bh)))
            cur = "b1"
    elif typ in ("hook", "broll"):
        src = ctx.path(sc["media"])
        inputs += media_input(ctx, src, D, float(sc.get("from", 0)))
        if typ == "hook":
            z = "1+%.4f*T/%.3f" % (RULES["hook"]["zoom_to"] - 1, D)
            g.append(zoom_chain(ctx, src, 0, N, z, "z0"))
            Rh = RULES["hook"]; y = Rh["headline_y"]
            heads = sc.get("headline", [])
            if isinstance(heads, str):
                heads = [heads]
            for k, h in enumerate(heads):
                ass.ev(0, D, "Box", "{\\an7\\pos(%d,%d)\\fn%s\\fs%d\\c%s\\3c%s\\4c%s\\bord%d\\shad0}" %
                       (Rh.get("headline_x", 72), y, FONT_BLACK, Rh["headline_size"], assc("#111111"), assc("#FFFFFF"), assc("#FFFFFF"), Rh["box_pad"]) + ass_text(h))
                y += int(Rh["headline_size"] * 1.18) + Rh["headline_gap"] + Rh["box_pad"]
            local_sfx.append((RULES["auto_sfx"]["hook_start"], 0.0))
        else:
            B = RULES["broll"]; lead, zd = B["black_lead"], B["zoom_in_dur"]
            z = ("if(lt(T,%.3f),%.3f,if(lt(T,%.3f),%.3f-%.3f*(T-%.3f)/%.3f,1+%.4f*(T-%.3f)/%.3f))"
                 % (lead, B["zoom_in_from"], lead + zd, B["zoom_in_from"], B["zoom_in_from"] - 1, lead, zd, B["push_to"] - 1, lead + zd, max(0.5, D - lead - zd)))
            g.append(zoom_chain(ctx, src, 0, N, z, "z1"))
            g.append("[z1]fade=t=in:st=%.3f:d=0.12[z0]" % lead)
            local_sfx.append((RULES["auto_sfx"]["broll_start"], max(0, lead - 0.15)))
        cur = "z0"
    elif typ == "pip":
        src = ctx.path(sc["media"]); P = RULES["pip"]
        inputs += ["-f", "lavfi", "-i", "color=c=%s:s=%dx%d:r=%d:d=%.3f" % (hexc(sc.get("bg", P["bg"])), W, H, fps, D + 0.5)]
        inputs += media_input(ctx, src, D, float(sc.get("from", 0)))
        g.append("[1:v]%sscale=%d:%d:force_original_aspect_ratio=decrease,setsar=1,format=rgba,fade=t=in:st=0:d=%.2f:alpha=1[pp]"
                 % ("" if is_image(src) else "fps=%d," % fps, int(W * P["scale"]), int(H * P["scale"]), P["pop_dur"]))
        g.append("[0:v][pp]overlay=x=(W-w)/2:y=(H-h)/2-%d:eof_action=repeat[z0]" % ctx.p(30))
        cur = "z0"
        local_sfx.append((RULES["auto_sfx"]["pip_start"], 0.0))
    elif typ in ("mascot", "subscribe", "outro"):
        M = RULES["mascot"]; src = ctx.path(sc["media"])
        inputs += ["-f", "lavfi", "-i", "color=c=%s:s=%dx%d:r=%d:d=%.3f" % (hexc(M["bg"]), W, H, fps, D + 0.5)]
        inputs += ["-loop", "1", "-i", src] if is_image(src) else ["-stream_loop", "-1", "-i", src]
        hfrac = M["image_height"] if typ == "mascot" else 0.74
        g.append("[1:v]scale=-2:%d,setsar=1[mi]" % int(H * hfrac))
        g.append("[0:v][mi]overlay=x=(W-w)/2:y=H-h:shortest=1[c0]")
        if typ == "mascot":
            at = float(sc.get("at", M["caption_at"])); P, pd = M["punch_zoom"], M["punch_dur"]
            z = "if(lt(T,%.3f),1,min(%.3f,1+%.3f*(T-%.3f)/%.3f))" % (at, P, P - 1, at, pd)
            g.append("[c0]zoompan=z='%s':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=%dx%d:fps=%d,setsar=1[z0]"
                     % (z.replace("T", "(on/%d)" % fps), W, H, fps))
            if sc.get("caption"):
                ass.ev(at, D, "T", "{\\an8\\pos(%d,%d)\\fn%s\\fs%d\\c%s\\3c%s\\bord7\\shad0}" %
                       (RULES["canvas"]["width"] // 2, M["caption_y"], FONT_BLACK, M["caption_size"], assc(color_of(sc.get("color"), C["mascot_caption"])), assc("#111111")) + ass_text(sc["caption"]))
            local_sfx.append((RULES["auto_sfx"]["mascot_caption"], at))
            cur = "z0"
        elif typ == "subscribe":
            Sx = RULES["subscribe"]; at = float(sc.get("click_at", Sx["click_at"]))
            label = sc.get("label", "%s 구독" % sc.get("channel", "너굴경제"))
            fs = Sx["pill_size"]; pw = text_w(label, fs) + 120; ph = fs + 34
            px = RULES["canvas"]["width"] / 2 - pw / 2; py = Sx["pill_y"]
            boxes = [drawbox(ctx, px, py, pw, ph, C["sub_pill"], at=0, until=at),
                     drawbox(ctx, px, py, pw, ph, C["sub_pill_on"], at=at)]
            g.append("[c0]" + ",".join(boxes) + "[z0]")
            ass.ev(0, at, "T", tag(RULES["canvas"]["width"] // 2, int(py + ph / 2), fs, "#333333", FONT_BOLD, an=5) + ass_text(label))
            ass.ev(at, D, "T", tag(RULES["canvas"]["width"] // 2, int(py + ph / 2), fs, "#FFFFFF", FONT_BOLD, an=5) + ass_text(label))
            if sc.get("caption"):
                ass.ev(0, D, "T", tag(RULES["canvas"]["width"] // 2, py + ph + 40, 64, "#111111", FONT_BLACK, an=8) + ass_text(sc["caption"]))
            local_sfx.append((RULES["auto_sfx"]["subscribe_click"], at))
            cur = "z0"
        else:
            if sc.get("caption"):
                ass.ev(0, D, "T", "{\\an8\\pos(%d,%d)\\fn%s\\fs%d\\c%s\\3c%s\\bord6\\shad0}" %
                       (RULES["canvas"]["width"] // 2, 80, FONT_BLACK, 96, assc(color_of(sc.get("color"), C["mascot_caption"])), assc("#111111")) + ass_text(sc["caption"]))
            cur = "c0"
    else:
        raise ValueError("알 수 없는 장면 type: %s" % typ)

    # scene text overlay
    ass_path = "ass/scene_%03d.ass" % i
    ass.save(os.path.join(ctx.build, ass_path))
    if sc.get("sticker"):   # 마스코트 스티커 (R-L4)
        stp = ctx.path(sc["sticker"]); sat = float(sc.get("sticker_at", 0))
        inputs += ["-loop", "1", "-i", stp]
        si = len([x for x in inputs if x == "-i"]) - 1
        g.append("[%d:v]scale=-2:%d,setsar=1,format=rgba[stk]" % (si, ctx.p(sc.get("sticker_height", 300))))
        g.append("[%s][stk]overlay=x=W-w-%d:y=H-h-%d:shortest=1:enable='gte(t,%.3f)'[stk2]" % (cur, ctx.p(60), ctx.p(150), sat))
        cur = "stk2"
        sfx_events.append(("pop", glob_t0 + sat))
    g.append("[%s]subtitles=%s:fontsdir=fonts[t0]" % (cur, ass_path))
    cur = "t0"
    # transitions (R-X*)
    trans_in = sc.get("transition")
    if trans_in is None:
        trans_in = "flash" if (prev_type == "broll" and typ == "slide" and RULES["flash"]["after_broll"]) else "cut"
    if trans_in == "flash":
        fd = RULES["flash"]["duration"]
        g.append("color=c=%s:s=%dx%d:r=%d:d=%.3f,format=rgba,fade=t=out:st=0:d=%.3f:alpha=1[fl]" % (hexc(C["flash"]), W, H, fps, fd, fd))
        g.append("[%s][fl]overlay=eof_action=pass[t1]" % cur); cur = "t1"
    elif trans_in == "fade":
        g.append("[%s]fade=t=in:st=0:d=0.3[t1]" % cur); cur = "t1"
    if next_type == "broll" or sc.get("fade_out"):
        fo = RULES["broll"]["prev_fade_out"]
        g.append("[%s]fade=t=out:st=%.3f:d=%.3f[t2]" % (cur, max(0, D - fo), fo)); cur = "t2"
    g.append("[%s]format=yuv420p[vout]" % cur)
    script = os.path.join(ctx.build, "ass", "scene_%03d.filter.txt" % i)
    open(script, "w", encoding="utf-8").write(";\n".join(g))
    out = "clips/scene_%03d.mp4" % i
    ff(inputs + ["-/filter_complex", os.path.relpath(script, ctx.build).replace("\\", "/"), "-map", "[vout]", "-frames:v", str(N),
                 "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-an", out], cwd=ctx.build)
    for name, t in local_sfx + sfx_events_from(sc):
        if name:
            sfx_events.append((name, glob_t0 + t))
    return out


def sfx_events_from(sc):
    return [(e.get("name"), float(e.get("at", 0))) for e in sc.get("sfx", [])]


# ---------------------------------------------------------------- render
def render(project_path, out=None, preview=False):
    global FFMPEG, FFPROBE
    FFMPEG, FFPROBE = find_bin("ffmpeg"), find_bin("ffprobe")
    proj_dir = os.path.dirname(os.path.abspath(project_path))
    P = json.load(open(project_path, encoding="utf-8-sig"))
    W, H = (960, 540) if preview else (RULES["canvas"]["width"], RULES["canvas"]["height"])
    fps = RULES["canvas"]["fps"]
    build = os.path.join(proj_dir, "_build_preview" if preview else "_build")
    for d in ("", "fonts", "ass", "clips", "sfx"):
        os.makedirs(os.path.join(build, d), exist_ok=True)
    for f in glob.glob(os.path.join(HERE, "fonts", "*.otf")):
        dst = os.path.join(build, "fonts", os.path.basename(f))
        if not os.path.exists(dst):
            shutil.copy(f, dst)
    ctx = Ctx(W, H, fps, build, proj_dir)

    voice = ctx.path(P["voice"])
    subs = parse_srt(ctx.path(P["srt"])) if P.get("srt") else []
    scenes = P["scenes"]
    # scene start (seconds in original voice time or by subtitle line)
    starts = []
    for k, sc in enumerate(scenes):
        if "start_line" in sc:
            starts.append(subs[int(sc["start_line"]) - 1]["start"])
        elif "start" in sc:
            starts.append(float(sc["start"]))
        elif k == 0:
            starts.append(0.0)
        else:
            raise ValueError("장면 %d에 start 또는 start_line이 필요합니다" % (k + 1))
    starts[0] = 0.0
    if P.get("tighten", True):
        tv = os.path.join(build, "voice_tight.wav")
        subs, fmap = tighten(voice, subs, tv)
        starts = [0.0] + [fmap(s) for s in starts[1:]]
        voice = tv
        write_srt(subs, os.path.join(build, "subs_tight.srt"))
    vdur = probe_duration(voice)
    total = vdur + float(P.get("tail", 0.6))
    ends = starts[1:] + [total]
    print("[render] 장면 %d개, 총 %.1f초, %dx%d" % (len(scenes), total, W, H))
    sfx_events = []
    clips = []
    frame_marks = [int(round(s * fps)) for s in starts] + [int(round(total * fps))]
    for k, sc in enumerate(scenes):
        N = frame_marks[k + 1] - frame_marks[k]
        if N <= 0:
            raise ValueError("장면 %d 길이가 0 이하입니다 (start 순서를 확인)" % (k + 1))
        D = N / fps
        prev_t = scenes[k - 1].get("type", "slide") if k > 0 else None
        next_t = scenes[k + 1].get("type", "slide") if k + 1 < len(scenes) else None
        print("  - 장면 %02d %-9s %6.2fs ~ %6.2fs  %s" % (k + 1, sc.get("type", "slide"), starts[k], starts[k] + D, sc.get("title", sc.get("caption", ""))[:30]))
        clips.append(render_scene(ctx, k, sc, D, N, prev_t, next_t, sfx_events, frame_marks[k] / fps))
    with open(os.path.join(build, "concat.txt"), "w", encoding="utf-8") as f:
        for c in clips:
            f.write("file '%s'\n" % c.replace("\\", "/"))
    ff(["-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "body.mp4"], cwd=build)
    # subtitles
    build_sub_ass(subs, os.path.join(build, "ass", "subs.ass"))
    # audio mix (R-A*)
    sfxp = ensure_sfx(build, P.get("sfx_files"))
    vol = RULES["audio"]["sfx_volume"]
    a_in = ["-i", "body.mp4", "-i", voice]
    graph = ["[1:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur=%.3f[vo]" % total]
    mix = ["[vo]"]
    for j, (name, t) in enumerate(sorted(sfx_events, key=lambda x: x[1])):
        if name not in sfxp:
            continue
        a_in += ["-i", sfxp[name]]
        ms = int(max(0, t) * 1000)
        graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,volume=%.3f,adelay=%d|%d[s%d]" % (len(a_in) // 2 - 1, vol.get(name, 0.3), ms, ms, j))
        mix.append("[s%d]" % j)
    if P.get("bgm"):
        bg = ctx.path(P["bgm"])
        a_in += ["-stream_loop", "-1", "-i", bg]
        bi = len([x for x in a_in if x == "-i"]) - 1
        bv = float(P.get("bgm_volume", RULES["audio"]["bgm_volume"]))
        if RULES["audio"]["bgm_in_body"] or P.get("bgm_mode") == "full":
            graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:%.3f,volume=%.3f,afade=t=out:st=%.3f:d=1.5[bgm]" % (bi, total, bv, total - 1.5))
        else:  # 훅 + 아웃트로에만
            h_end = ends[0]; o_st = starts[-1]
            graph.append("[%d:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[bga][bgb]" % bi)
            graph.append("[bga]atrim=0:%.3f,volume=%.3f,afade=t=out:st=%.3f:d=0.6[bg1]" % (h_end, bv, max(0, h_end - 0.6)))
            graph.append("[bgb]atrim=0:%.3f,volume=%.3f,afade=t=in:d=0.5,afade=t=out:st=%.3f:d=0.8,adelay=%d|%d[bg2]" % (total - o_st, bv, max(0, total - o_st - 0.8), int(o_st * 1000), int(o_st * 1000)))
            graph.append("[bg1][bg2]amix=inputs=2:normalize=0[bgm]")
        mix.append("[bgm]")
    A = RULES["audio"]
    graph.append("%samix=inputs=%d:normalize=0:duration=first,loudnorm=I=%d:TP=%.1f:LRA=11,aresample=48000[aout]" % ("".join(mix), len(mix), A["loudness_lufs"], A["true_peak"]))
    graph.append("[0:v]subtitles=ass/subs.ass:fontsdir=fonts,format=yuv420p[vout]")
    open(os.path.join(build, "final.filter.txt"), "w", encoding="utf-8").write(";\n".join(graph))
    out = os.path.abspath(out or os.path.join(proj_dir, ("preview.mp4" if preview else P.get("output", "output.mp4"))))
    print("[render] 최종 합성 중 (자막+오디오, 효과음 %d개)..." % (len(mix) - 1))
    ff(a_in + ["-/filter_complex", "final.filter.txt", "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264",
               "-preset", "veryfast" if preview else "medium", "-crf", "20" if preview else "18", "-c:a", "aac", "-b:a", "192k",
               "-t", "%.3f" % total, "-movflags", "+faststart", out], cwd=build)
    print("[완료] " + out)
    return out


# ---------------------------------------------------------------- analyze
def analyze(video, out_dir=None):
    global FFMPEG, FFPROBE
    FFMPEG, FFPROBE = find_bin("ffmpeg"), find_bin("ffprobe")
    video = os.path.abspath(video)
    name = os.path.splitext(os.path.basename(video))[0]
    out_dir = os.path.abspath(out_dir or os.path.join(os.path.dirname(video), name + "_analysis"))
    os.makedirs(out_dir, exist_ok=True)
    dur = probe_duration(video)
    print("[analyze] %s (%.1f초)" % (name, dur))
    err = ff(["-i", video, "-an", "-vf", "scale=320:-2,select='gt(scene,0.3)',showinfo", "-f", "null", "-"], quiet=False)
    cuts = []
    for t in re.findall(r"pts_time:([\d.]+)", err):
        t = float(t)
        if not cuts or t - cuts[-1] > 0.25:
            cuts.append(t)
    iv = sorted(b - a for a, b in zip([0] + cuts, cuts + [dur]))
    sil = detect_silences(video, -38, 0.25)
    sd = sorted(b - a for a, b in sil) or [0]
    err = ff(["-i", video, "-vn", "-af", "ebur128", "-f", "null", "-"], quiet=False)
    m = re.search(r"Integrated loudness:\s*I:\s*(-?[\d.]+)", err)
    lufs = float(m.group(1)) if m else None
    seg = {}
    for a, b, lab in [(0, 15, "0-15s"), (15, 60, "15-60s"), (60, max(61, dur - 60), "본문"), (max(0, dur - 60), dur, "마지막60s")]:
        seg[lab] = round(len([t for t in cuts if a <= t < b]) / max(1, b - a) * 60, 1)
    res = dict(file=video, duration=round(dur, 1), cuts=len(cuts), cuts_per_min=round(len(cuts) / dur * 60, 2),
               cut_interval_median=round(iv[len(iv) // 2], 2), cut_interval_p25=round(iv[len(iv) // 4], 2), cut_interval_p75=round(iv[3 * len(iv) // 4], 2),
               cuts_per_min_by_segment=seg, silences=len(sil), silence_median=round(sd[len(sd) // 2], 2),
               silence_total=round(sum(sd), 1), integrated_lufs=lufs, cut_times=[round(t, 2) for t in cuts])
    json.dump(res, open(os.path.join(out_dir, "analysis.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for lab, ss, tt, fpsx in [("intro", 0, 60, "0.5"), ("mid", dur / 2 - 90, 180, "1/6"), ("outro", max(0, dur - 60), 60, "0.5")]:
        ff(["-ss", "%.2f" % ss, "-t", str(tt), "-i", video, "-vf", "fps=%s,scale=384:-2,tile=5x6" % fpsx, "-frames:v", "1", os.path.join(out_dir, "sheet_%s.jpg" % lab)])
    ff(["-t", "60", "-i", video, "-lavfi", "showspectrumpic=s=1600x400:legend=1:scale=log:fscale=log", os.path.join(out_dir, "spectrum_intro.png")])
    tgt = "너굴경제 기준: 컷 2.1~2.7회/분(중앙 간격 15~21초), 무음 중앙 0.25~0.35초, 본문 BGM 없음"
    md = ["# 편집 분석: %s" % name, "", "| 항목 | 값 |", "|---|---|"]
    for k in ("duration", "cuts", "cuts_per_min", "cut_interval_median", "cut_interval_p25", "cut_interval_p75", "silences", "silence_median", "silence_total", "integrated_lufs"):
        md.append("| %s | %s |" % (k, res[k]))
    md += ["| 구간별 컷/분 | %s |" % seg, "", tgt, "", "시트: sheet_intro/mid/outro.jpg, spectrum_intro.png (본문 무음 구간이 검은색이면 BGM 없음)"]
    open(os.path.join(out_dir, "report.md"), "w", encoding="utf-8").write("\n".join(md))
    print(json.dumps({k: v for k, v in res.items() if k != "cut_times"}, ensure_ascii=False, indent=1))
    print("[완료] " + out_dir)


# ---------------------------------------------------------------- template / demo
TEMPLATE = {
    "title": "영상 제목",
    "voice": "voice.wav",
    "srt": "voice.srt",
    "tighten": True,
    "output": "output.mp4",
    "scenes": [
        {"type": "hook", "start": 0, "media": "assets/hook.png", "headline": ["뉴스 헤드라인 한 줄", "두 번째 줄(선택)"]},
        {"type": "slide", "start_line": 3, "section": "오프닝", "source": "자료: 출처", "title": "핵심 숫자 한 줄 요약", "subtitle": "부제(회색 한 줄)",
         "cards": [{"label": "지표 A", "value": "15%", "unit": "돌파", "color": "red", "caption": "기간·설명"},
                   {"label": "지표 B", "value": "-4.48%", "color": "blue", "caption": "한 주 하락률"},
                   {"label": "지표 C", "value": "-7.57%", "color": "blue", "caption": "하루 하락률"}],
         "banner": {"text": "원인 →", "accent": "결과 → 파급"},
         "highlights": [{"target": "card:1", "at": 1.5}, {"target": "card:2", "at": 3.0}]},
        {"type": "subscribe", "start_line": 8, "media": "assets/mascot_subscribe.png", "channel": "내채널", "caption": "도와주세요..제발"},
        {"type": "broll", "start_line": 9, "media": "assets/broll.mp4"},
        {"type": "slide", "start_line": 10, "section": "1. 첫 번째 이야기", "theme": "cream", "title": "막대 비교", "underline": True,
         "bars": [{"label": "항목 1", "value": 63, "text": "63억 달러", "color": "blue_num", "arrow": True}, {"label": "항목 2", "value": 34, "text": "34억 달러"}]},
        {"type": "mascot", "start_line": 14, "media": "assets/mascot.png", "caption": "거품이냐 아니냐"},
        {"type": "outro", "start_line": 16, "media": "assets/mascot_outro.png"}
    ]
}


def cmd_new(folder):
    os.makedirs(os.path.join(folder, "assets"), exist_ok=True)
    p = os.path.join(folder, "project.json")
    json.dump(TEMPLATE, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[완료] 템플릿 생성: " + p + "\n voice.wav / voice.srt / assets/* 를 채우고 render 하세요.")


DEMO_LINES = [
    "여러분들 지금 원달러 환율이 1500원을 뚫어버렸죠?",
    "외국인이 한 달 만에 국장에서 12조를 빼갔습니다.",
    "그래서 오늘 영상은요. 환율이 왜 이렇게 미쳐 날뛰는지 아주 쉽고 재밌게 알아보도록 하죠.",
    "그전에 형님들 구독과 좋아요는 꼭 한 번씩만 눌러주시고요. 바로 가보죠.",
    "자, 일단 환율이 뭔지부터 짚고 가야겠죠?",
    "올해 들어 환율은 무려 12퍼센트나 올랐습니다.",
    "**이거 진짜 심각한 겁니다**",
    "그럼 이게 거품이냐 아니냐?",
    "형님들 재밌게 보셨다면 구독과 좋아요 알림설정까지. 그럼 빠이.",
]


VOICEBOX_URL = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")
VOICEBOX_INSTRUCT = {"여의도여자": ("차분하고 또렷한 뉴스 아나운서 톤, 신뢰감 있게, 보통 속도. 쉼표에서 짧게 끊어 읽고 문장 끝은 자연스럽게 내려 닫는다. "
                                 "숫자와 핵심 낱말은 또박또박 조금 힘주어 읽는다. 높낮이를 살려 단조롭지 않게, 기계처럼 일정하게 읽지 않는다.")}


def _vb(path, body=None, raw=False, timeout=600):
    import urllib.request
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(VOICEBOX_URL + path, data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with op.open(req, timeout=timeout) as r:
        data = r.read()
    return data if raw else json.loads(data)


def voicebox_tts(text, out_wav, profile, seed=7):
    """Voicebox(Qwen3-TTS) 프로필로 한 문장 생성 (여의도여자/여의도남자 등). 앱이 켜져 있어야 한다."""
    import time
    try:
        profs = _vb("/profiles", timeout=10)
    except Exception as e:
        sys.exit("[오류] Voicebox(%s)에 연결할 수 없습니다. Voicebox 앱을 켜 주세요: %s" % (VOICEBOX_URL, e))
    profs = profs.get("profiles", profs) if isinstance(profs, dict) else profs
    p = next((x for x in profs if x.get("name") == profile), None)
    if not p:
        sys.exit("[오류] Voicebox에 '%s' 프로필이 없습니다" % profile)
    eng = p.get("default_engine") or "qwen"
    body = {"profile_id": p["id"], "text": text, "language": p.get("language") or "ko", "model_size": "1.7B", "engine": eng, "seed": seed}
    if eng == "qwen_custom_voice" and VOICEBOX_INSTRUCT.get(profile):
        body["instruct"] = VOICEBOX_INSTRUCT[profile]
    gid = _vb("/generate", body)["id"]
    for _ in range(900):
        h = _vb("/history/%s" % gid, timeout=30)
        if h.get("status") == "completed":
            break
        if h.get("status") == "failed":
            raise RuntimeError("Voicebox 생성 실패: %s" % h.get("error"))
        time.sleep(2)
    open(out_wav, "wb").write(_vb("/audio/%s" % gid, raw=True))


def build_voice(lines, out_dir, wavs=None, gap=0.5, voice=None):
    """문장 목록(+문장별 음성파일) -> voice.wav + voice.srt.
    음성파일이 없으면 voice(Voicebox 프로필명, 예: 여의도여자)로 생성, 그것도 없으면 Windows TTS(Heami)."""
    A = os.path.join(out_dir, "assets", "lines"); os.makedirs(A, exist_ok=True)
    if not wavs and voice:
        wavs = []
        for i, line in enumerate(lines):
            w = os.path.join(A, "vb%03d.wav" % i)
            if not os.path.exists(w):
                t0 = __import__("time").time()
                voicebox_tts(re.sub(r"^\s*!|\*\*|\[Q\]", "", line).strip('"“”'), w, voice)
                print("  [voicebox:%s] %d/%d (%.0f초)" % (voice, i + 1, len(lines), __import__("time").time() - t0), flush=True)
            wavs.append(w)
    if not wavs:
        wavs = []
        for i, line in enumerate(lines):
            w = os.path.join(A, "line%03d.wav" % i)
            txt = re.sub(r"^\s*!|\*\*|\[Q\]", "", line)
            open(w + ".txt", "w", encoding="utf-8").write(txt)
            ps = ("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                  "$v=$s.GetInstalledVoices()|?{$_.VoiceInfo.Culture.Name -eq 'ko-KR'}|select -first 1; if($v){$s.SelectVoice($v.VoiceInfo.Name)}; "
                  "$s.Rate=2; $s.SetOutputToWaveFile('%s'); $s.Speak([IO.File]::ReadAllText('%s')); $s.Dispose()" % (w, w + ".txt"))
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
            wavs.append(w)
    if len(wavs) != len(lines):
        raise ValueError("문장 수(%d)와 음성 파일 수(%d)가 다릅니다" % (len(lines), len(wavs)))
    gp = os.path.join(A, "gap.wav")
    ff(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(gap), gp])
    subs, t = [], 0.0
    lst = os.path.join(A, "voice_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for i, w in enumerate(wavs):
            nw = os.path.join(A, "norm%03d.wav" % i)
            ff(["-i", w, "-ar", "48000", "-ac", "1", nw])
            d = probe_duration(nw)
            subs.append({"start": t, "end": t + d, "text": lines[i]})
            t += d + gap
            f.write("file '%s'\nfile '%s'\n" % (nw.replace("\\", "/"), gp.replace("\\", "/")))
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-ar", "48000", os.path.join(out_dir, "voice.wav")])
    write_srt(subs, os.path.join(out_dir, "voice.srt"))
    print("[voice] %d문장, %.1f초 -> voice.wav / voice.srt (srt 줄 번호 = 문장 번호)" % (len(lines), t))


def cmd_demo(folder, voice=None):
    global FFMPEG, FFPROBE
    FFMPEG, FFPROBE = find_bin("ffmpeg"), find_bin("ffprobe")
    folder = os.path.abspath(folder)
    A = os.path.join(folder, "assets"); os.makedirs(A, exist_ok=True)
    fonts = os.path.join(folder, "fonts"); os.makedirs(fonts, exist_ok=True)
    for f in glob.glob(os.path.join(HERE, "fonts", "*.otf")):
        shutil.copy(f, fonts)
    build_voice(DEMO_LINES, folder, gap=0.7, voice=voice)
    # placeholder visuals
    ff(["-f", "lavfi", "-i", "gradients=s=1920x1080:c0=0xC81E1E:c1=0x2A0505:c2=0xF0A030:n=3:seed=7", "-frames:v", "1", os.path.join(A, "hook.png")])
    ff(["-f", "lavfi", "-i", "gradients=s=1920x1080:c0=0x1C3D5A:c1=0x0B0B0B:c2=0x3D97E5:n=3:speed=0.03:seed=3", "-t", "8", "-pix_fmt", "yuv420p", os.path.join(A, "broll.mp4")])
    for nm, col in (("mascot", "0x7BE22E"), ("mascot_subscribe", "0xFF4F86"), ("mascot_outro", "0x3D97E5")):
        ff(["-f", "lavfi", "-i", "color=c=white:s=700x820", "-vf",
            "drawbox=x=150:y=120:w=400:h=400:color=%s:t=fill,drawbox=x=230:y=520:w=240:h=300:color=0x222222:t=fill,"
            "drawtext=fontfile=fonts/Pretendard-ExtraBold.otf:text='MASCOT':x=(w-tw)/2:y=290:fontsize=72:fontcolor=white" % col,
            "-frames:v", "1", os.path.join(A, nm + ".png")], cwd=folder)
    proj = {
        "title": "데모: 환율 1500원", "voice": "voice.wav", "srt": "voice.srt", "tighten": True, "output": "demo_output.mp4",
        "scenes": [
            {"type": "hook", "start": 0, "media": "assets/hook.png", "headline": ["원달러 환율 1,500원 돌파", "'외국인 엑소더스' 가속"]},
            {"type": "slide", "start_line": 2, "section": "오프닝", "source": "자료: 한국거래소 · 한국은행", "title": "외국인, 한 달 만에 12조 순매도", "subtitle": "환율 급등과 동시에 국장 이탈이 빨라졌다",
             "cards": [{"label": "원/달러 환율", "value": "1,500", "unit": "원", "color": "red", "caption": "장중 최고"},
                       {"label": "외국인 순매도", "value": "-12조", "color": "blue", "caption": "최근 한 달"},
                       {"label": "코스피", "value": "-7.6%", "color": "blue", "caption": "같은 기간"}],
             "banner": {"text": "환율 급등 →", "accent": "외국인 이탈 → 지수 하락"},
             "highlights": [{"target": "card:0", "at": 0.6}, {"target": "card:1", "at": 2.0}]},
            {"type": "slide", "start_line": 3, "section": "오프닝", "theme": "cream", "title": "오늘 영상에서 다룰 순서", "subtitle": "아주 쉽고 재밌게 정리",
             "cards": [{"text": "무슨 일이\n벌어지고 있나"}, {"text": "왜 이렇게\n됐나"}, {"text": "그래서,\n어떻게 되나", "fill": "yellow"}], "card_height": 200},
            {"type": "subscribe", "start_line": 4, "media": "assets/mascot_subscribe.png", "channel": "너굴경제", "caption": "도와주세요..제발", "click_at": 1.0},
            {"type": "broll", "start_line": 5, "media": "assets/broll.mp4"},
            {"type": "slide", "start_line": 6, "section": "1. 환율이 뭐길래", "source": "자료: 한국은행", "title": "올해만 12% 올랐다", "underline": True,
             "bars": [{"label": "원/달러", "value": 12, "text": "+12%", "color": "blue_num", "arrow": True, "strong": True},
                      {"label": "엔/달러", "value": 6, "text": "+6%"}, {"label": "유로/달러", "value": 3, "text": "+3%"}]},
            {"type": "slide", "start_line": 7, "section": "1. 환율이 뭐길래", "title": "심리적 마지노선 붕괴", "bignum": {"value": "1,500", "unit": "원", "caption": "2009년 금융위기 이후 처음"}},
            {"type": "mascot", "start_line": 8, "media": "assets/mascot.png", "caption": "거품이냐 아니냐"},
            {"type": "outro", "start_line": 9, "media": "assets/mascot_outro.png"}
        ]
    }
    pj = os.path.join(folder, "project.json")
    json.dump(proj, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return render(pj)


def main():
    ap = argparse.ArgumentParser(description="너굴경제 스타일 자동 편집기")
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("render"); r.add_argument("project"); r.add_argument("--out"); r.add_argument("--preview", action="store_true")
    t = sp.add_parser("tighten"); t.add_argument("audio"); t.add_argument("--srt"); t.add_argument("--out-dir", default=".")
    a = sp.add_parser("analyze"); a.add_argument("video"); a.add_argument("--out")
    n = sp.add_parser("new"); n.add_argument("folder")
    d = sp.add_parser("demo"); d.add_argument("folder"); d.add_argument("--voice", help="Voicebox 프로필명 (예: 여의도여자)")
    v = sp.add_parser("voice"); v.add_argument("script"); v.add_argument("--out-dir", default="."); v.add_argument("--wav-dir")
    v.add_argument("--voice", help="Voicebox 프로필명 (예: 여의도여자)")
    args = ap.parse_args()
    global FFMPEG, FFPROBE
    if args.cmd == "render":
        render(args.project, args.out, args.preview)
    elif args.cmd == "tighten":
        FFMPEG, FFPROBE = find_bin("ffmpeg"), find_bin("ffprobe")
        os.makedirs(args.out_dir, exist_ok=True)
        subs = parse_srt(args.srt) if args.srt else []
        oa = os.path.join(args.out_dir, "voice_tight.wav")
        subs2, _ = tighten(args.audio, subs, oa)
        if args.srt:
            write_srt(subs2, os.path.join(args.out_dir, "voice_tight.srt"))
        print("[완료] " + oa)
    elif args.cmd == "analyze":
        analyze(args.video, args.out)
    elif args.cmd == "new":
        cmd_new(args.folder)
    elif args.cmd == "demo":
        cmd_demo(args.folder, args.voice)
    elif args.cmd == "voice":
        FFMPEG, FFPROBE = find_bin("ffmpeg"), find_bin("ffprobe")
        lines = [l.strip() for l in open(args.script, encoding="utf-8-sig") if l.strip()]
        wavs = None
        if args.wav_dir:
            wavs = sorted(glob.glob(os.path.join(args.wav_dir, "*.wav")) + glob.glob(os.path.join(args.wav_dir, "*.mp3")))
        os.makedirs(args.out_dir, exist_ok=True)
        build_voice(lines, os.path.abspath(args.out_dir), wavs, voice=args.voice)


if __name__ == "__main__":
    main()
