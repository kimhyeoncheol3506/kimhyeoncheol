"""[4단계] 타임라인 → ASS 자막 + ffmpeg 커맨드 자동 생성 → mp4 렌더링."""
import os
import shlex
from pathlib import Path

from .ff import FFMPEG, run
from .rules import ROOT


def ass_color(rrggbb, alpha="00"):
    c = rrggbb.lstrip("#")
    return f"&H{alpha}{c[4:6]}{c[2:4]}{c[0:2]}".upper()


def ass_time(t):
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _units(text):
    u = 0.0
    for ch in text:
        if ch == " ":
            u += 0.33
        elif ord(ch) < 128:
            u += 0.62 if ch.isalnum() else 0.4
        else:
            u += 1.0
    return max(u, 1)


def fit_size(text, base, rules):
    sub = rules["editing"]["subtitle"]
    usable = rules["video"]["width"] - 2 * sub["side_margin"]
    return int(max(sub["min_font_size"], min(base, usable / _units(text))))


def _esc(t):
    return t.replace("{", "｛").replace("}", "｝").replace("\\", "＼")


def colorize(text, highlights, hl, base):
    """키워드만 색상 강조."""
    spans = []
    for term in sorted(set(highlights), key=len, reverse=True):
        start = 0
        while (i := text.find(term, start)) >= 0:
            if not any(a < i + len(term) and i < b for a, b in spans):
                spans.append((i, i + len(term)))
            start = i + len(term)
    out, pos = "", 0
    for a, b in sorted(spans):
        out += _esc(text[pos:a]) + "{\\1c" + hl + "}" + _esc(text[a:b]) + "{\\1c" + base + "}"
        pos = b
    return out + _esc(text[pos:])


def _round_rect(w, h, r):
    return (f"m {r} 0 l {w - r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h - r} b {w} {h} {w} {h} {w - r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h - r} l 0 {r} b 0 0 0 0 {r} 0")


def build_ass(tl, rules, font_name):
    v, sub = rules["video"], rules["editing"]["subtitle"]
    W, H = v["width"], v["height"]
    white, hl = ass_color(sub["color"]), ass_color(sub["highlight_color"])
    oc = ass_color(sub["outline_color"])
    fmt = ("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
           "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
           "Alignment, MarginL, MarginR, MarginV, Encoding")

    def style(name, size, align, mv, color=white, outline=sub["outline"], border=1, back="&H96000000"):
        return (f"Style: {name},{font_name},{size},{color},{color},{oc},{back},-1,0,0,0,100,100,0,0,"
                f"{border},{outline},{sub['shadow']},{align},{sub['side_margin']},{sub['side_margin']},{mv},1")

    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
             "WrapStyle: 2", "ScaledBorderAndShadow: yes", "", "[V4+ Styles]", fmt,
             style("Hook", sub["hook_font_size"], 2, sub["hook_margin_v"]),
             style("Main", sub["font_size"], 2, sub["margin_v"]),
             style("Badge", 64, 2, sub["badge_margin_v"], color=ass_color(sub["highlight_color"]), border=1,
                   outline=8),
             style("Btn", 60, 5, 0, outline=0),
             style("Outro", 110, 5, 0),
             style("Guide", 40, 8, 180, outline=0, border=3, back="&H80000000"),
             "", "[Events]",
             "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]

    def ev(layer, a, b, st, text):
        lines.append(f"Dialogue: {layer},{ass_time(a)},{ass_time(b)},{st},,0,0,0,,{text}")

    pop = sub.get("pop_in", True)
    for s in tl["subtitles"]:
        st = {"hook": "Hook", "badge": "Badge"}.get(s["style"], "Main")
        base = {"Hook": sub["hook_font_size"], "Badge": 64}.get(st, sub["font_size"])
        size = fit_size(s["text"], base, rules)
        if s["kind"] == "typing":
            done = s["text"][: len(s["text"]) - len(s["new_word"])]
            body = colorize(done, s["highlights"], hl, white)
            newp = colorize(s["new_word"], s["highlights"], hl, white)
            anim = "{\\fscx135\\fscy135\\t(0,130,\\fscx100\\fscy100)}" if pop else ""
            text = f"{{\\fs{size}}}{body}{anim}{newp}"
        else:
            anim = "{\\fscx112\\fscy112\\t(0,110,\\fscx100\\fscy100)}" if pop else ""
            text = f"{{\\fs{size}}}{anim}" + colorize(s["text"], s["highlights"], hl, white)
        ev(2, s["start"], s["end"], st, text)

    # 촬영 가이드(임시 배경일 때만): 어떤 컷을 찍어 넣으면 되는지 표시
    if rules["editing"]["placeholder"]["show_shot_guide"]:
        for c in tl["cuts"]:
            if c["source"]["kind"] == "placeholder":
                ev(1, c["start"], c["end"], "Guide", _esc(f" 컷{c['id']} · {c['shot']} "))

    # CTA: 화면 하단 고정 버튼 (0.5초마다 살짝 펄스)
    cta = tl["cta"]
    bw, bh, y = 640, 132, cta["y"]
    rect = _round_rect(bw, bh, 44)
    t = cta["start_sec"]
    first = True
    while t < cta["end"] - 1e-6:
        t2 = min(t + 0.5, cta["end"])
        intro = "\\fscx60\\fscy60\\t(0,150,\\fscx100\\fscy100)" if first else "\\t(0,220,\\fscx106\\fscy106)\\t(220,450,\\fscx100\\fscy100)"
        ev(3, t, t2, "Btn", f"{{\\an5\\pos({W // 2},{y})\\p1\\bord0\\shad3\\1c{ass_color(cta['button_color'])}{intro}}}{rect}")
        ev(4, t, t2, "Btn", f"{{\\an5\\pos({W // 2},{y})\\1c{ass_color(cta['text_color'])}{intro}}}{_esc(cta['button_text'])}")
        first = False
        t = t2

    # 아웃트로: 로고(이미지 없으면 브랜드명 텍스트) + 구매 버튼
    out = tl["outro"]
    if not (ROOT / out["logo"]).exists():
        ev(5, out["start"], out["end"], "Outro",
           f"{{\\an5\\pos({W // 2},{int(H * 0.42)})\\fscx70\\fscy70\\t(0,200,\\fscx100\\fscy100)}}{_esc(out['brand'])}")
    ev(5, out["start"], out["end"], "Main",
       f"{{\\an5\\pos({W // 2},{int(H * 0.52)})\\fs{fit_size(tl['meta']['product'], 64, rules)}}}{_esc(tl['meta']['product'])}")
    return "\n".join(lines) + "\n"


def _zoom_expr(c, fps, ramp, hold):
    d = max(c["end"] - c["start"], 1 / fps)
    t = f"(in/{fps})"
    z = f"({c['zoom']['from']}+{c['zoom']['to'] - c['zoom']['from']:.4f}*min({t}/{d:.3f},1))"
    punches = []
    for p in c["zoom"]["punches"]:
        up = f"clip(({t}-{p['t']:.3f})/{ramp},0,1)"
        down = f"(1-clip(({t}-{p['t'] + ramp + hold:.3f})/{ramp * 2},0,1))"
        punches.append(f"{p['scale'] - 1:.3f}*{up}*{down}")
    if punches:
        m = punches[0]
        for p in punches[1:]:
            m = f"max({m},{p})"
        z = f"{z}+{m}"
    return z


def build_command(tl, rules, run_dir, font_file, voice_path=None):
    """ffmpeg 인자 목록 + filter_complex 스크립트를 만든다."""
    v, ed = rules["video"], rules["editing"]
    W, H, fps, dur = v["width"], v["height"], v["fps"], float(v["duration"])
    em = ed["emphasis"]
    args = [FFMPEG, "-y", "-hide_banner"]
    fc = []
    idx = 0

    def add_input(*a):
        nonlocal idx
        args.extend(a)
        idx += 1
        return idx - 1

    # ── 영상: 컷별 소스 → 크기 맞춤 → 줌(전환/강조) → 이어붙이기 ──
    logo = ROOT / ed["outro"]["logo"]
    for c in tl["cuts"]:
        d = round(c["end"] - c["start"], 3)
        src = c["source"]
        if src["kind"] == "image":
            i = add_input("-loop", "1", "-framerate", str(fps), "-t", str(d), "-i", src["path"])
        elif src["kind"] == "video":
            i = add_input("-stream_loop", "-1", "-ss", str(src.get("offset", 0)), "-t", str(d), "-i", src["path"])
        elif src["kind"] == "outro":
            i = add_input("-f", "lavfi", "-t", str(d), "-i",
                          f"color=c=0x{ed['outro']['bg_color']}:s={W}x{H}:r={fps}")
        else:
            c0, c1 = src["colors"]
            i = add_input("-f", "lavfi", "-t", str(d), "-i",
                          f"gradients=s={W}x{H}:c0=0x{c0}:c1=0x{c1}:x0=0:y0=0:x1={W}:y1={H}:r={fps}:speed=0.03")
        chain = f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}"
        if src["kind"] == "placeholder":  # 줌이 눈에 보이도록 제품 자리 카드
            cw, ch = int(W * 0.56), int(W * 0.56)
            chain += (f",drawbox=x={(W - cw) // 2}:y={int(H * 0.30)}:w={cw}:h={ch}:color=white@0.30:t=fill"
                      f",drawbox=x={(W - cw) // 2}:y={int(H * 0.30)}:w={cw}:h={ch}:color=white@0.85:t=8")
        if src["kind"] == "outro":
            if logo.exists():
                li = add_input("-i", str(logo))
                fc.append(f"[{li}:v]scale={int(W * 0.5)}:-1[logo{c['id']}]")
                chain += f"[bg{c['id']}];[bg{c['id']}][logo{c['id']}]overlay=(W-w)/2:H*0.42-h/2"
        else:
            z = _zoom_expr(c, fps, em["ramp_sec"], em["hold_sec"])
            chain += (f",scale={W * 2}:{H * 2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                      f":d=1:s={W}x{H}:fps={fps}")
        chain += f",trim=duration={d},setpts=PTS-STARTPTS,format=yuv420p[v{c['id']}]"
        fc.append(chain)
    fc.append("".join(f"[v{c['id']}]" for c in tl["cuts"]) + f"concat=n={len(tl['cuts'])}:v=1:a=0[base]")
    fontsdir = os.path.relpath(Path(font_file).parent, run_dir).replace("\\", "/")
    fc.append(f"[base]ass=subs.ass:fontsdir='{fontsdir}'[vout]")

    # ── 오디오: 효과음(컷/키워드/타이핑) + BGM(3초부터 페이드인) + 내레이션 ──
    mix = []
    sil = add_input("-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo")
    mix.append(f"[{sil}:a]")
    sfx_labels = sfx_graph(tl, rules, fc, add_input)
    mix += sfx_labels
    bgm = tl["bgm"]
    if (ROOT / bgm["file"]).exists():
        bi = add_input("-stream_loop", "-1", "-i", str(ROOT / bgm["file"]))
        blen = dur - bgm["start_sec"]
        fc.append(f"[{bi}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
                  f"atrim=0:{blen:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d={bgm['fade_in_sec']},"
                  f"afade=t=out:st={blen - bgm['fade_out_sec']:.3f}:d={bgm['fade_out_sec']},volume={bgm['volume']},"
                  f"adelay={int(bgm['start_sec'] * 1000)}:all=1[bgm]")
        bgm_label = "[bgm]"
        if voice_path:
            vi = add_input("-i", str(voice_path))
            fc.append(f"[{vi}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asplit=2[vo][vsc]")
            if bgm.get("duck_under_voice"):
                fc.append("[bgm][vsc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[bgmd]")
                bgm_label = "[bgmd]"
            else:
                fc.append("[vsc]anullsink")
            mix.append("[vo]")
        mix.append(bgm_label)
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:duration=longest:normalize=0,"
              f"apad,atrim=0:{dur},alimiter=limit=0.95[aout]")

    (Path(run_dir) / "filter_complex.txt").write_text(";\n".join(fc) + "\n", encoding="utf-8")
    args += ["-filter_complex_script", "filter_complex.txt", "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", v["preset"], "-crf", str(v["crf"]), "-pix_fmt", "yuv420p",
             "-r", str(fps), "-c:a", "aac", "-b:a", "192k", "-t", str(dur), "-movflags", "+faststart", "final.mp4"]
    return args


def sfx_graph(tl, rules, fc, add_input, prefix=""):
    """효과음 파일별로 1번 읽어 asplit → 각 시점에 adelay. 라벨 목록을 돌려준다."""
    sx = rules["editing"]["sfx"]
    groups = {}
    for i, s in enumerate(tl["sfx"]):
        groups.setdefault(s["file"], []).append((i, s))
    labels = []
    for f, items in groups.items():
        k = add_input("-i", str(ROOT / f))
        trim = ",silenceremove=start_periods=1:start_threshold=-50dB" if sx.get("trim_leading_silence") else ""
        outs = "".join(f"[{prefix}s{i}]" for i, _ in items)
        fc.append(f"[{k}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo{trim},"
                  f"volume={sx['volume']},asplit={len(items)}{outs}" if len(items) > 1 else
                  f"[{k}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo{trim},"
                  f"volume={sx['volume']}{outs}")
        for i, s in items:
            ms = int(round(s["t"] * 1000))
            fc.append(f"[{prefix}s{i}]adelay={ms}:all=1[{prefix}d{i}]")
            labels.append(f"[{prefix}d{i}]")
    return labels


def render(tl, rules, run_dir, font_file, font_name, voice_path=None, log=print):
    run_dir = Path(run_dir)
    (run_dir / "subs.ass").write_text(build_ass(tl, rules, font_name), encoding="utf-8")
    args = build_command(tl, rules, run_dir, font_file, voice_path)
    sh = "#!/usr/bin/env bash\n# 자동 생성된 렌더링 커맨드 — 이 폴더에서 실행: bash render.sh\ncd \"$(dirname \"$0\")\"\n"
    sh += " \\\n  ".join(shlex.quote(a) for a in args) + "\n"
    (run_dir / "render.sh").write_text(sh, encoding="utf-8")
    log("  · ffmpeg 렌더링 중... (1~3분)")
    run(args, cwd=run_dir)
    return run_dir / "final.mp4"


def render_stems(tl, rules, run_dir):
    """검증용: 효과음만 / BGM만 따로 뽑는다."""
    dur = float(rules["video"]["duration"])
    run_dir = Path(run_dir)
    # 효과음 스템
    args, fc, idx = [FFMPEG, "-y", "-hide_banner"], [], 0

    def add_input(*a):
        nonlocal idx
        args.extend(a)
        idx += 1
        return idx - 1

    sil = add_input("-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo")
    labels = [f"[{sil}:a]"] + sfx_graph(tl, rules, fc, add_input)
    fc.append("".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,atrim=0:{dur}[a]")
    run(args + ["-filter_complex", ";".join(fc), "-map", "[a]", str(run_dir / "stem_sfx.wav")])
    # BGM 스템 (BGM이 3초 전에 새어 나오지 않는지 확인)
    bgm = tl["bgm"]
    blen = dur - bgm["start_sec"]
    run([FFMPEG, "-y", "-hide_banner", "-stream_loop", "-1", "-i", str(ROOT / bgm["file"]),
         "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex",
         f"[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,atrim=0:{blen:.3f},"
         f"asetpts=PTS-STARTPTS,afade=t=in:st=0:d={bgm['fade_in_sec']},volume={bgm['volume']},"
         f"adelay={int(bgm['start_sec'] * 1000)}:all=1[b];[1:a][b]amix=inputs=2:duration=longest:normalize=0,"
         f"atrim=0:{dur}[a]", "-map", "[a]", str(run_dir / "stem_bgm.wav")])
    return run_dir / "stem_sfx.wav", run_dir / "stem_bgm.wav"
