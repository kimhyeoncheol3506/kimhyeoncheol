# -*- coding: utf-8 -*-
"""롱폼 16:9 합성: 세로 toon2d 영상(1080x1920) → 1920x1080.
  가운데 세로 영상(608x1080) + 뒤 배경(같은 영상 크게·흐리게·어둡게)
  왼쪽 패널: 채널명, 장 번호, 장 제목   /  오른쪽 패널: 사료 카드(장마다)
  아래: 문장 자막(words.json 시간, 한 번에 최대 약 26자)
사용: python landscape.py <프로젝트> [--video final_sfx.mp4] [--chapters chapters.json] [--out final_169.mp4] [--brand "역사가 지운 그날"]
chapters.json: [{"w": 시작단어, "no": "1장", "title": "쌀이 없는 섬", "card": "줄1\\n줄2 ..."}, ...]
  - 세로 영상은 자막 없이 렌더한 것(plan.json captions 를 비운 뒤 render)을 쓴다. 자막은 여기서 넣는다.
폰트: 엔진 fonts 폴더의 Pretendard.
"""
import argparse, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.environ.get("TOON2D_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "mystery-cartoon", "kits", "toon2d"))
FD = os.path.join(ENG, "toon2d", "fonts")
try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FF = "ffmpeg"


def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def esc(s):
    return s.replace("{", "(").replace("}", ")")


def chunks(words, maxc=26):
    """문장 단위로 묶되 길면 maxc 글자 근처에서 자른다."""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        text = " ".join(x["w"] for x in cur)
        end_sent = i + 1 == len(words) or words[i + 1].get("sent") != w.get("sent")
        nxt = words[i + 1]["w"] if i + 1 < len(words) else ""
        if end_sent or len(text) + 1 + len(nxt) > maxc or (w["w"][-1:] in ",." and len(text) > maxc * 0.6):
            out.append((cur[0]["s"], cur[-1]["e"], text)); cur = []
    # 다음 자막 시작 전까지 유지(깜빡임 방지, 최대 0.6초)
    res = []
    for k, (s, e, t) in enumerate(out):
        nx = out[k + 1][0] if k + 1 < len(out) else e + 0.6
        res.append((s, min(nx, e + 0.6), t))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proj")
    ap.add_argument("--video", default="final_sfx.mp4")
    ap.add_argument("--chapters", default="chapters.json")
    ap.add_argument("--out", default="final_169.mp4")
    ap.add_argument("--brand", default="역사가 지운 그날")
    ap.add_argument("--crf", default="20")
    a = ap.parse_args()
    P = os.path.abspath(a.proj)
    words = json.load(open(os.path.join(P, "words.json"), encoding="utf-8"))
    chs = json.load(open(os.path.join(P, a.chapters), encoding="utf-8"))
    T = lambda w: words[min(w, len(words) - 1)]["s"]
    end_t = words[-1]["e"] + 5
    fam = "Pretendard ExtraBold"
    hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{f},58,&H00FFFFFF,&H00FFFFFF,&H00141018,&H96000000,0,0,0,0,100,100,0,0,1,5,2,2,60,60,46,1
Style: Brand,{f},34,&H0040D6FF,&H00FFFFFF,&H00141018,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
Style: ChNo,{f},44,&H0040D6FF,&H00FFFFFF,&H00141018,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
Style: ChTitle,{f},66,&H00FFFFFF,&H00FFFFFF,&H00141018,&H00000000,0,0,0,0,100,100,0,0,1,4,0,7,0,0,0,1
Style: CardHead,{f},34,&H0040D6FF,&H00FFFFFF,&H00141018,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1
Style: Card,{f},42,&H00F2EEE6,&H00FFFFFF,&H00141018,&H00000000,0,0,0,0,100,100,0,0,1,2,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".replace("{f}", fam)
    ev = []
    ev.append("Dialogue: 0,%s,%s,Brand,,0,0,0,,{\\pos(64,52)}%s" % (ts(0), ts(end_t), esc(a.brand)))
    for i, c in enumerate(chs):
        t0 = T(c["w"]); t1 = T(chs[i + 1]["w"]) if i + 1 < len(chs) else end_t
        fade = "{\\fad(350,250)}"
        ev.append("Dialogue: 1,%s,%s,ChNo,,0,0,0,,%s{\\pos(64,150)}%s" % (ts(t0), ts(t1), fade, esc(c.get("no", ""))))
        title = c.get("title", "")
        # 왼쪽 패널 폭(약 560px)에 맞춰 8자 근처에서 줄바꿈
        tl, line = [], ""
        for wd in title.split(" "):
            if len(line) + len(wd) + 1 > 8 and line:
                tl.append(line); line = wd
            else:
                line = (line + " " + wd).strip()
        tl.append(line)
        ev.append("Dialogue: 1,%s,%s,ChTitle,,0,0,0,,%s{\\pos(64,215)}%s" % (ts(t0), ts(t1), fade, "\\N".join(map(esc, tl))))
        if c.get("card"):
            ev.append("Dialogue: 1,%s,%s,CardHead,,0,0,0,,%s{\\pos(1310,150)}기록으로 보기" % (ts(t0), ts(t1), fade))
            ev.append("Dialogue: 1,%s,%s,Card,,0,0,0,,%s{\\pos(1310,205)}%s" % (ts(t0), ts(t1), fade, "\\N".join(map(esc, c["card"].split("\n")))))
    for s, e, t in chunks(words):
        ev.append("Dialogue: 2,%s,%s,Sub,,0,0,0,,%s" % (ts(s), ts(e), esc(t)))
    ass = os.path.join(P, "landscape.ass")
    open(ass, "w", encoding="utf-8").write(hdr + "\n".join(ev) + "\n")
    vid = os.path.join(P, a.video)
    out = os.path.join(P, a.out)
    fil = ("[0:v]split=2[a][b];"
           "[a]scale=1920:3413,crop=1920:1080:0:1100,boxblur=28:2,eq=brightness=-0.22:saturation=0.75[bg];"
           "[b]scale=608:1080[fg];"
           "[bg]drawbox=x=0:y=0:w=640:h=1080:color=black@0.35:t=fill,drawbox=x=1280:y=0:w=640:h=1080:color=black@0.35:t=fill[bg2];"
           "[bg2][fg]overlay=656:0,drawbox=x=652:y=0:w=4:h=1080:color=0x40D6FF@0.9:t=fill,drawbox=x=1264:y=0:w=4:h=1080:color=0x40D6FF@0.9:t=fill,"
           "subtitles=filename='%s':fontsdir='%s'[v]" % (ass.replace("'", r"\'").replace(":", r"\:"), FD.replace(":", r"\:")))
    subprocess.run([FF, "-v", "error", "-y", "-i", vid, "-filter_complex", fil, "-map", "[v]", "-map", "0:a",
                    "-c:v", "libx264", "-crf", a.crf, "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out], check=True)
    print("OUT", out)


if __name__ == "__main__":
    main()
