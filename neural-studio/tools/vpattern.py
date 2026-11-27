#!/usr/bin/env python3
"""영상 패턴 10종 (plans/영상패턴10.md, 2026-11-28 현철님 지시).

  vpattern.py pick <채널> [--ep 이름]   랜덤으로 패턴을 뽑는다(직전 2편 제외, 경제1은 3~7번 3배). plans/패턴이력.json 에 기록
  vpattern.py apply <P>               story.json 의 "pattern" 대로 mood·라벨 위치를 넣는다(render 전)
  vpattern.py skin <P>                work/video.mp4 에 색·틀·오프닝 카드를 입힌다(render 뒤, audio 전. 길이 그대로)
  vpattern.py samples <base.mp4> <out.jpg> [--at 초]   10종 10초 샘플을 만들어 스틸을 한 장으로

엔진(.claude/skills/reachmora-2d-longform) 원본은 고치지 않는다. 덧입히기만 한다.
"""
import json, os, random, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HIST = os.path.join(ROOT, "plans", "패턴이력.json")
FD = os.path.join(ROOT, "neural-studio", "assets", "fonts")
BH = os.path.join(FD, "BlackHanSans.ttf")
PR = next((p for p in ["/home/user/hf/thumb/assets/fonts/Pretendard-Bold.otf",
                       os.path.join(ROOT, ".claude/skills/reachmora-2d-longform/fonts/Pretendard-Bold.otf")] if os.path.exists(p)), BH)
W, H = 1920, 1080

# label: 라벨·하단 자막 기본 위치 (x, y). None = 엔진 기본
PATTERNS = {
    1: dict(name="시사 썰 다큐", mood="calm", music_db=-18, label=(None, 860),
            grade="colorbalance=rs=.06:gs=.02:bs=-.06,eq=saturation=.92:contrast=1.03", frame="timeline", open="question"),
    2: dict(name="속보 반응", mood="tense", music_db=-15, label=(None, 260),
            grade="eq=contrast=1.12:saturation=1.25", frame="breaking", open="breaking"),
    3: dict(name="진짜 이유 파헤치기", mood="mystery", music_db=-17, label=(1420, None),
            grade="colorbalance=rs=-.08:gs=.02:bs=.10,eq=brightness=-.05:saturation=.8:contrast=1.08", frame="evidence", open="casefile"),
    4: dict(name="몰락의 전말", mood="dramatic", music_db=-17, label=(560, 840),
            grade="BW_TO_COLOR", frame="cinema", open="stamp"),
    5: dict(name="생활 속 돈벌이 비밀", mood="upbeat", music_db=-18, label=(None, 860),
            grade="eq=brightness=.04:saturation=.85,colorbalance=rs=.03:bs=.05", frame="moneyrail", open="everyday"),
    6: dict(name="가문·인물 드라마", mood="dramatic", music_db=-20, label=(None, 880),
            grade="colorbalance=rs=.10:gs=-.02:bs=.02,eq=saturation=.85:contrast=1.06", frame="drama", open="family"),
    7: dict(name="대역전·라이벌전", mood="upbeat", music_db=-16, label=(None, 250),
            grade="eq=contrast=1.08:saturation=1.15", frame="scoreboard", open="versus"),
    8: dict(name="다음 주 시장 변수", mood="calm", music_db=-20, label=(520, 880),
            grade="eq=brightness=.03:saturation=.9", frame="checklist", open="calendar"),
    9: dict(name="수혜·피해 지도", mood="tense", music_db=-18, label=(560, 250),
            grade="eq=saturation=1.05:contrast=1.04", frame="legend", open="sectormap"),
    10: dict(name="나라·거시 위기 스토리", mood="dramatic", music_db=-16, label=(None, 860),
             grade="colorbalance=rs=.10:gs=-.04:bs=-.04,eq=contrast=1.1:saturation=.9", frame="debtclock", open="worldmap"),
}
FAV = {"경제1": {3: 3, 4: 3, 5: 3, 6: 3, 7: 3}}


def F(sz, bold=True): return ImageFont.truetype(BH if bold else PR, sz)


# ------------------------------------------------------------------ 뽑기
def pick(channel, ep=None, seed=None):
    h = json.load(open(HIST, encoding="utf-8")) if os.path.exists(HIST) else []
    recent = [x["pattern"] for x in h if x.get("channel") == channel][-2:]
    pool = [k for k in PATTERNS if k not in recent]
    w = [FAV.get(channel, {}).get(k, 1) for k in pool]
    k = random.Random(seed).choices(pool, weights=w)[0]
    h.append(dict(channel=channel, ep=ep, pattern=k, name=PATTERNS[k]["name"]))
    json.dump(h, open(HIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return k


# ------------------------------------------------------------------ story.json
def apply(P):
    sp = os.path.join(P, "story.json"); st = json.load(open(sp, encoding="utf-8"))
    k = int(st["pattern"]); p = PATTERNS[k]; st["mood"] = p["mood"]; x, y = p["label"]
    for sh in st.get("shots", []):
        for L in sh.get("labels", []):
            if y is not None: L.setdefault("y", y)
            if x is not None: L.setdefault("x", x)
        if sh.get("lower_third") and y is not None and y > 600: sh["lower_third"].setdefault("y", min(y + 60, 960))
    json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return k


# ------------------------------------------------------------------ 틀(항상 보이는 겹)
def text(d, xy, s, f, fill, anchor="la", stroke=0, sc=(0, 0, 0)):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sc)


def frame_png(kind, info):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == "timeline":
        d.rectangle([0, 0, W, 64], fill=(40, 34, 28, 190))
        yrs = info.get("years", ["1990", "2000", "2010", "2020", "지금"])
        for i, s in enumerate(yrs):
            x = 160 + i * (W - 320) // max(1, len(yrs) - 1); d.ellipse([x - 9, 23, x + 9, 41], fill=(236, 200, 120, 255))
            text(d, (x + 16, 14), s, F(30, False), (240, 230, 210, 255))
        d.line([160, 32, W - 160, 32], fill=(236, 200, 120, 160), width=3)
    elif kind == "breaking":
        d.rectangle([0, H - 96, W, H], fill=(16, 16, 20, 235)); d.rectangle([0, H - 96, 250, H], fill=(214, 30, 36, 255))
        text(d, (125, H - 48), "속보", F(54), "white", "mm")
        d.rounded_rectangle([40, 36, 210, 92], 10, fill=(214, 30, 36, 255)); text(d, (125, 64), "● LIVE", F(34), "white", "mm")
    elif kind == "evidence":
        for x0, y0, rot in ((-40, 60, 35), (W - 260, 40, -35), (-40, H - 120, -35), (W - 260, H - 130, 35)):
            t = Image.new("RGBA", (300, 60), (230, 196, 60, 215)); ImageDraw.Draw(t).text((20, 8), "EVIDENCE", font=F(36), fill=(30, 30, 30, 255))
            t = t.rotate(rot, expand=True); im.alpha_composite(t, (max(0, x0), max(0, y0)))
        d.rectangle([W - 380, 150, W - 40, 560], outline=(230, 196, 60, 230), width=4)
        text(d, (W - 210, 190), "단서", F(44), (230, 196, 60, 255), "mm")
        for i, s in enumerate(info.get("clues", ["①", "②", "③"])):
            text(d, (W - 350, 250 + i * 95), s, F(40, False), (235, 235, 235, 255))
    elif kind == "cinema":
        d.rectangle([0, 0, W, 132], fill=(0, 0, 0, 255)); d.rectangle([0, H - 132, W, H], fill=(0, 0, 0, 255))
    elif kind == "moneyrail":
        d.rounded_rectangle([24, 140, 120, 940], 48, fill=(255, 255, 255, 150))
        for i in range(6):
            y = 200 + i * 125; d.polygon([(72, y + 70), (48, y + 30), (96, y + 30)], fill=(46, 170, 110, 230))
        text(d, (72, 170), "₩", F(56), (46, 140, 90, 255), "mm")
    elif kind == "drama":
        d.rectangle([0, 0, W - 1, H - 1], outline=(200, 160, 80, 255), width=14); d.rectangle([24, 24, W - 25, H - 25], outline=(120, 30, 40, 220), width=4)
        d.rectangle([0, H - 150, W, H - 14], fill=(30, 8, 14, 170))
    elif kind == "scoreboard":
        d.rounded_rectangle([W // 2 - 420, 24, W // 2 + 420, 120], 18, fill=(20, 22, 30, 225))
        d.rectangle([W // 2 - 420, 24, W // 2 - 140, 120], fill=(210, 40, 50, 235)); d.rectangle([W // 2 + 140, 24, W // 2 + 420, 120], fill=(40, 90, 210, 235))
        a, b = info.get("vs", ("A", "B")); text(d, (W // 2 - 280, 72), a, F(44), "white", "mm"); text(d, (W // 2 + 280, 72), b, F(44), "white", "mm")
        text(d, (W // 2, 72), info.get("score", "0 : 0"), F(54), (255, 220, 80, 255), "mm")
    elif kind == "checklist":
        d.rounded_rectangle([W - 400, 140, W - 40, 700], 20, fill=(255, 255, 255, 215), outline=(28, 44, 90, 255), width=4)
        text(d, (W - 220, 190), "체크할 변수", F(42), (28, 44, 90, 255), "mm")
        for i, s in enumerate(info.get("checks", ["실적 발표일", "공시·소송", "수급"])):
            y = 270 + i * 120; d.rounded_rectangle([W - 370, y, W - 326, y + 44], 8, outline=(28, 44, 90, 255), width=4)
            text(d, (W - 305, y + 2), s, F(36, False), (28, 44, 90, 255))
        d.rounded_rectangle([40, 30, 420, 96], 14, fill=(28, 44, 90, 230)); text(d, (230, 63), info.get("week", "다음 주 체크"), F(36), "white", "mm")
    elif kind == "legend":
        d.rectangle([0, H - 84, W, H], fill=(20, 24, 28, 220))
        d.rounded_rectangle([60, H - 64, 110, H - 20], 8, fill=(40, 180, 100, 255)); text(d, (126, H - 66), "수혜 가능 업종", F(36, False), "white")
        d.rounded_rectangle([520, H - 64, 570, H - 20], 8, fill=(240, 130, 30, 255)); text(d, (586, H - 66), "피해 가능 업종", F(36, False), "white")
        text(d, (W - 60, H - 42), "종목 추천 아님 · 과거 사례(보도)", F(28, False), (200, 200, 200, 255), "rm")
    elif kind == "debtclock":
        d.rounded_rectangle([W - 560, 30, W - 40, 150], 14, fill=(10, 10, 10, 230), outline=(220, 40, 40, 255), width=4)
        text(d, (W - 540, 42), info.get("clock_label", "나랏빚 시계"), F(30, False), (220, 220, 220, 255))
        text(d, (W - 60, 120), info.get("clock", "$ 000,000,000,000"), F(52), (255, 70, 60, 255), "rs")
        d.rectangle([0, H - 70, W, H], fill=(60, 10, 10, 180))
    return im


# ------------------------------------------------------------------ 오프닝 카드(처음 4초)
def open_png(kind, info, bg=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    q = info.get("question", "이 회사에 대체 무슨 일이?"); name = info.get("name", "")

    def panel(box, fill): d.rounded_rectangle(box, 28, fill=fill)
    if kind == "question":
        panel([160, 330, W - 160, 750], (250, 244, 232, 235)); text(d, (W // 2, 470), q, F(84), (40, 34, 28, 255), "mm")
        text(d, (W // 2, 620), name, F(54, False), (150, 110, 60, 255), "mm")
    elif kind == "breaking":
        d.rectangle([0, 360, W, 720], fill=(214, 30, 36, 240)); text(d, (120, 420), "[속보]", F(96), "white")
        text(d, (120, 560), q, F(80), "white")
    elif kind == "casefile":
        c = Image.new("RGBA", (1100, 640), (233, 220, 190, 245)); cd = ImageDraw.Draw(c)
        cd.rectangle([0, 0, 1099, 639], outline=(90, 70, 40, 255), width=8); cd.text((60, 40), "사건 파일 No." + str(info.get("ep", "")), font=F(56), fill=(90, 30, 30, 255))
        cd.text((60, 180), q, font=F(70), fill=(30, 30, 30, 255)); cd.text((60, 470), name, font=F(52, False), fill=(60, 60, 60, 255))
        im.alpha_composite(c.rotate(-3, expand=True, fillcolor=(0, 0, 0, 0)), (390, 200))
    elif kind == "stamp":
        text(d, (W // 2, 440), name or q, F(110), "white", "mm", 6)
        s = Image.new("RGBA", (520, 220), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
        sd.rounded_rectangle([6, 6, 514, 214], 20, outline=(220, 30, 30, 255), width=12); sd.text((260, 110), "전말", font=F(130), fill=(220, 30, 30, 255), anchor="mm")
        im.alpha_composite(s.rotate(12, expand=True), (W // 2 - 300, 560))
    elif kind == "everyday":
        panel([200, 300, W - 200, 780], (255, 255, 255, 230)); d.ellipse([260, 380, 560, 680], fill=(255, 210, 90, 255))
        text(d, (410, 530), "?", F(220), (60, 60, 60, 255), "mm"); text(d, (620, 470), q, F(74), (40, 40, 40, 255))
        text(d, (620, 610), name, F(52, False), (46, 140, 90, 255))
    elif kind == "family":
        d.rectangle([0, 0, W, H], fill=(30, 8, 14, 200))
        for i, (x, y) in enumerate([(W // 2, 300), (W // 2 - 360, 560), (W // 2, 560), (W // 2 + 360, 560)]):
            d.ellipse([x - 70, y - 70, x + 70, y + 70], fill=(200, 160, 80, 255))
            if i: d.line([W // 2, 370, x, y - 70], fill=(200, 160, 80, 200), width=5)
        text(d, (W // 2, 800), q, F(76), "white", "mm"); text(d, (W // 2, 910), name, F(50, False), (200, 160, 80, 255), "mm")
    elif kind == "versus":
        d.rectangle([0, 0, W // 2, H], fill=(210, 40, 50, 215)); d.rectangle([W // 2, 0, W, H], fill=(40, 90, 210, 215))
        a, b = info.get("vs", ("A", "B")); text(d, (W // 4, 480), a, F(110), "white", "mm", 5); text(d, (3 * W // 4, 480), b, F(110), "white", "mm", 5)
        text(d, (W // 2, 480), "VS", F(200), (255, 220, 80, 255), "mm", 8); text(d, (W // 2, 820), q, F(64), "white", "mm", 4)
    elif kind == "calendar":
        panel([300, 220, W - 300, 860], (255, 255, 255, 240)); d.rectangle([300, 220, W - 300, 330], fill=(28, 44, 90, 255))
        text(d, (W // 2, 275), info.get("week", "다음 주 체크"), F(60), "white", "mm")
        for i, s in enumerate(["월", "화", "수", "목", "금"]):
            x = 380 + i * 250; d.rounded_rectangle([x, 370, x + 210, 560], 14, outline=(28, 44, 90, 255), width=4); text(d, (x + 105, 410), s, F(44), (28, 44, 90, 255), "mm")
        text(d, (W // 2, 700), q, F(66), (28, 44, 90, 255), "mm")
    elif kind == "sectormap":
        d.rectangle([0, 0, W, H], fill=(20, 24, 28, 200))
        cols = [(40, 180, 100), (240, 130, 30), (40, 180, 100), (120, 120, 120), (240, 130, 30), (40, 180, 100)]
        for i, c in enumerate(cols):
            x = 260 + (i % 3) * 480; y = 200 + (i // 3) * 260; d.rounded_rectangle([x, y, x + 440, y + 220], 18, fill=c + (235,))
        text(d, (W // 2, 820), q, F(70), "white", "mm", 4)
    elif kind == "worldmap":
        d.rectangle([0, 0, W, H], fill=(12, 12, 16, 215))
        for x0, y0, x1, y1 in ((260, 260, 640, 520), (700, 220, 1000, 600), (1080, 240, 1620, 560), (520, 600, 760, 820), (1440, 640, 1640, 780)):
            d.ellipse([x0, y0, x1, y1], fill=(60, 66, 80, 255))
        d.ellipse([1230, 330, 1290, 390], fill=(255, 60, 50, 255))
        text(d, (W // 2, 880), q, F(74), "white", "mm", 4)
        text(d, (W - 60, 70), info.get("clock", ""), F(52), (255, 70, 60, 255), "rm")
    return im


def _grade(g, dur):
    if g == "BW_TO_COLOR":
        t0 = max(4.0, dur / 3); return f"hue=s='if(lt(t,{t0:.1f}),0,min(1,(t-{t0:.1f})/8))'"
    return g


def skin_video(src, dst, k, info, dur=None, crf=20):
    p = PATTERNS[k]
    if dur is None:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
    td = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(dst)))
    fp, op = os.path.join(td, "frame.png"), os.path.join(td, "open.png")
    frame_png(p["frame"], info).save(fp); open_png(p["open"], info).save(op)
    fc = f"[0:v]{_grade(p['grade'], dur)}[g];[g][1:v]overlay=0:0[f];[2:v]format=rgba,fade=t=in:st=0:d=0.3:alpha=1,fade=t=out:st=3.4:d=0.6:alpha=1[o];[f][o]overlay=0:0:enable='lt(t,4)'"
    if p["frame"] == "breaking":  # 흐르는 속보 티커
        tk = os.path.join(td, "tick.png"); s = "   ·   ".join(info.get("ticker", [info.get("question", "")])) + "      "
        f = F(46, False); tw = int(f.getlength(s)) + 40; t = Image.new("RGBA", (tw, 96), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((10, 20), s, font=f, fill="white"); t.save(tk)
        fc = fc.replace("[f];", "[f0];") + "[t];[3:v]format=rgba[tk];[t][tk]overlay=x='270+W-mod(t*180\\,W+w)':y=H-96"
        inputs = ["-i", src, "-loop", "1", "-i", fp, "-loop", "1", "-t", "4", "-i", op, "-loop", "1", "-i", tk]
        fc = fc.replace("[g][1:v]overlay=0:0[f0];", "[g][1:v]overlay=0:0[f];")
    else:
        inputs = ["-i", src, "-loop", "1", "-i", fp, "-loop", "1", "-t", "4", "-i", op]
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-t", f"{dur:.3f}", "-an",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p", dst]
    subprocess.run(cmd, check=True)
    for f_ in os.listdir(td): os.remove(os.path.join(td, f_))
    os.rmdir(td)


def project_info(P, st):
    info = dict(st.get("pattern_info", {}))
    try:
        um = json.load(open(os.path.join(P, "upload_meta.json"), encoding="utf-8")); info.setdefault("name", um.get("company") or um["title"].split("…")[-1].strip())
    except Exception: pass
    return info


def skin(P):
    st = json.load(open(os.path.join(P, "story.json"), encoding="utf-8")); k = int(st["pattern"])
    v = os.path.join(P, "work", "video.mp4"); tmp = v + ".skin.mp4"
    skin_video(v, tmp, k, project_info(P, st)); os.replace(tmp, v); open(os.path.join(P, "work", "SKINNED"), "w").write(str(k))
    return k


# ------------------------------------------------------------------ 샘플 시트
SAMPLE_INFO = {
    1: dict(question="AI 데이터센터, 정말 버블일까?", name="시사 썰 다큐", years=["1995", "2000", "2008", "2020", "지금"]),
    2: dict(question="오늘 밤 발표, 내 계좌엔?", name="속보 반응", ticker=["발표 직후 시간외 급등(보도)", "다음 체크: 실적 발표일", "투자 권유 아님"]),
    3: dict(question="이사회는 왜 거부했을까?", name="진짜 이유 파헤치기", ep=3, clues=["① 발표 시점", "② 빠진 숫자", "③ 지분 변화"]),
    4: dict(question="", name="○○ 몰락의 전말"),
    5: dict(question="그 많던 터미널은 어디로?", name="생활 속 돈벌이 비밀"),
    6: dict(question="가문은 왜 회사를 잃었나", name="가문·인물 드라마"),
    7: dict(question="꼴찌는 어떻게 1위를 넘었나", name="대역전·라이벌전", vs=("A사", "B사"), score="2 : 3"),
    8: dict(question="다음 주, 이 3가지만 보세요", name="다음 주 시장 변수", week="12/1 ~ 12/5", checks=["금리 결정", "실적 발표", "수급"]),
    9: dict(question="이 일이 끝나면 어느 업종이?", name="수혜·피해 지도"),
    10: dict(question="빚을 숨긴 나라, 들통난 날", name="나라·거시 위기", clock="$ 000,000,000,000"),
}


def samples(base, out, at=60.0):
    td = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out))); clip = os.path.join(td, "base.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(at), "-i", base, "-t", "10", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", clip], check=True)
    tiles = []
    for k in PATTERNS:
        o = os.path.join(td, f"p{k}.mp4"); info = dict(SAMPLE_INFO[k])
        skin_video(clip, o, k, info, dur=10.0)
        for ts in (1.8, 7.0):
            j = os.path.join(td, f"p{k}_{ts}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ts), "-i", o, "-frames:v", "1", j], check=True); tiles.append((k, ts, j))
        os.remove(o)
    tw, th = 640, 360; sheet = Image.new("RGB", (tw * 4 + 50, (th + 56) * 5 + 30), (24, 24, 28)); d = ImageDraw.Draw(sheet)
    for i, (k, ts, j) in enumerate(tiles):
        r, c = divmod(i, 4); x = 10 + c * (tw + 10); y = 10 + r * (th + 56)
        sheet.paste(Image.open(j).convert("RGB").resize((tw, th)), (x, y + 46))
        lab = f"{k}. {PATTERNS[k]['name']} · {'오프닝' if ts < 4 else '본문'} · BGM {PATTERNS[k]['mood']}"
        d.text((x + 4, y + 6), lab, font=F(30, False), fill=(240, 240, 240))
    sheet.save(out, quality=88)
    for f_ in os.listdir(td): os.remove(os.path.join(td, f_))
    os.rmdir(td)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    if a[0] == "pick": print(pick(a[1], a[a.index("--ep") + 1] if "--ep" in a else None))
    elif a[0] == "apply": print(apply(a[1]))
    elif a[0] == "skin": print(skin(a[1]))
    elif a[0] == "samples": samples(a[1], a[2], float(a[a.index("--at") + 1]) if "--at" in a else 60.0)
