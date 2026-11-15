"""롱폼(16:9)에서 구간을 잘라 세로 쇼츠(1080x1920)로 만든다(2026-11-15).
목소리는 이미 듣기 검수를 통과한 롱폼 것을 그대로 쓴다. 롱폼에 박힌 아래 자막 띠는 잘라 내고, 쇼츠용 큰 자막(1.3배)을 새로 얹는다.
사용: python tools/cut_short.py spec.yaml
spec: {src, srt, out, title:[줄1, 줄2], segs:[[시작초, 끝초], ...], fix:{원래자막: 바꿀자막}, tail: "끝 문구"}
"""
import re, subprocess, sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "assets" / "fonts"


def srt_cues(path):
    out = []
    for b in Path(path).read_text(encoding="utf-8").strip().split("\n\n"):
        l = b.strip().split("\n")
        if len(l) < 3:
            continue
        a, c = l[1].split(" --> ")
        ts = lambda s: int(s[:2]) * 3600 + int(s[3:5]) * 60 + float(s[6:].replace(",", "."))
        out.append((ts(a), ts(c), " ".join(l[2:])))
    return out


def ass_time(t):
    h, t = divmod(t, 3600); m, s = divmod(t, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def main(spec_path):
    sp = yaml.safe_load(open(spec_path, encoding="utf-8"))
    src, segs = str(ROOT / sp["src"]), sp["segs"]
    cues = srt_cues(ROOT / sp["srt"])
    fix = sp.get("fix") or {}
    # 자막: 구간마다 겹치는 큐를 새 시간축으로 옮긴다
    ev, off = [], 0.0
    for a, b in segs:
        for c0, c1, txt in cues:
            s, e = max(a, c0), min(b, c1)
            if e - s > 0.25:
                ev.append((off + s - a, off + e - a, fix.get(txt, txt)))
        off += b - a
    total = off
    ass = ROOT / (sp["out"] + ".ass")
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Cap,Pretendard Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,70,70,500,1\n"
            "Style: Title,Black Han Sans,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,3,8,50,50,250,1\n"
            "Style: Title2,Black Han Sans,104,&H00F979E8,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,7,3,8,50,50,385,1\n"
            "Style: Tail,Pretendard Black,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,14,0,2,70,70,170,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    L = [head]
    t1, t2 = sp["title"]
    L.append(f"Dialogue: 1,{ass_time(0)},{ass_time(total)},Title,,0,0,0,,{t1}\n")
    L.append(f"Dialogue: 1,{ass_time(0)},{ass_time(total)},Title2,,0,0,0,,{t2}\n")
    for s, e, txt in ev:
        L.append(f"Dialogue: 2,{ass_time(s)},{ass_time(e)},Cap,,0,0,0,,{txt}\n")
    if sp.get("tail"):
        L.append(f"Dialogue: 1,{ass_time(0)},{ass_time(total)},Tail,,0,0,0,,{sp['tail']}\n")
    ass.write_text("".join(L), encoding="utf-8")
    # 영상: 구간을 잘라 이어 붙이고(음성 포함), 흐린 배경 + 가운데 16:9(아래 자막 띠 잘라냄) + 새 자막
    parts, fc = [], []
    for i, (a, b) in enumerate(segs):
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.04,afade=t=out:st={b-a-0.05:.3f}:d=0.05[a{i}]")
        parts.append(f"[v{i}][a{i}]")
    n = len(segs)
    fc.append("".join(parts) + f"concat=n={n}:v=1:a=1[cv][ca]")
    fc.append("[cv]split[c1][c2]")
    fc.append("[c1]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.25[bg]")
    fc.append("[c2]crop=1920:960:0:0,scale=1080:-2[fg]")
    fc.append(f"[bg][fg]overlay=0:620,ass={ass}:fontsdir={FONTS}[outv]")
    out = ROOT / (sp["out"] + ".mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fc), "-map", "[outv]", "-map", "[ca]",
           "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(out, round(total, 2), "초")


if __name__ == "__main__":
    main(sys.argv[1])
