# -*- coding: utf-8 -*-
"""아침 경제뉴스 3줄 영상 생성기.
사용: python make_news.py <작업폴더>   (작업폴더 안에 news.json)
출력: long.mp4(16:9 롱폼), shorts.mp4(9:16 쇼츠), thumb.jpg, shorts_thumb.jpg, upload.json
"""
import json, os, re, subprocess, sys, time, shutil, datetime, urllib.request
from PIL import Image, ImageDraw, ImageFont
try:  # 발음 사전(ko-tts-pronounce): 음성에 넣는 문장만 읽는 대로 바꾼다. KO_TTS_RAW=1이면 끔
    for _kp in (os.path.join(os.path.expanduser("~"), ".orca", "bots", "bot", "skills", "ko-tts-pronounce"),  # PC 원본 사전
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ko-tts-pronounce")):  # 저장소/클라우드: .claude/skills/ko-tts-pronounce
        if os.path.isdir(_kp): sys.path.insert(0, _kp); break
    from ko_tts import normalize as _ko_norm
    if os.environ.get("KO_TTS_RAW") == "1": raise ImportError
except Exception:
    _ko_norm = lambda s: s


HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
F_BLACK = os.path.join(FONT_DIR, "BlackHanSans-Regular.ttf")
F_XB = os.path.join(FONT_DIR, "Pretendard-ExtraBold.otf")
F_M = os.path.join(FONT_DIR, "Pretendard-Medium.otf")
VOICEBOX_URL = os.environ.get("VOICEBOX_URL", "http://127.0.0.1:17493")
VOICE = os.environ.get("NEWS_VOICE") or os.environ.get("TTS_VOICE") or "여의도여자"
SPEED = float(os.environ.get("NEWS_SPEED", "1.2"))  # 말 속도 배수
INSTRUCT = ("차분하고 또렷한 아침 뉴스 아나운서 톤, 신뢰감 있게, 약간 빠른 속도. 쉼표에서 짧게 끊고 문장 끝은 자연스럽게 내려 닫는다. "
            "숫자와 핵심 낱말은 또박또박 읽는다. 단조롭지 않게.")
WEEK = "월화수목금토일"

# 색상
BG = (13, 22, 41); PANEL = (22, 34, 60); WHITE = (245, 247, 250); GREY = (150, 163, 185)
ACCENT = (255, 196, 0); BLUE = (64, 140, 255)
CAT_COLOR = {"증시": (231, 76, 60), "환율": (46, 204, 113), "금리": (52, 152, 219), "부동산": (230, 126, 34),
             "산업": (155, 89, 182), "기업": (155, 89, 182), "정책": (26, 188, 156), "글로벌": (52, 73, 94),
             "채권": (41, 128, 185), "가상자산": (243, 156, 18)}


def find_bin(name):
    p = shutil.which(name)
    if p:
        return p
    base = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages")
    for root, _, files in os.walk(base):
        if name + ".exe" in files:
            return os.path.join(root, name + ".exe")
    sys.exit("[오류] %s 를 찾을 수 없습니다" % name)


FFMPEG = find_bin("ffmpeg"); FFPROBE = find_bin("ffprobe")


def ff(args):
    r = subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise RuntimeError("ffmpeg 실패: %s" % r.stderr[-800:])


def dur(p):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip())


# ---------------- Voicebox ----------------
def _vb(path, body=None, raw=False, timeout=600):
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(VOICEBOX_URL + path, data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with op.open(req, timeout=timeout) as r:
        d = r.read()
    return d if raw else json.loads(d)


def ensure_voicebox():
    for i in range(40):
        try:
            return _vb("/profiles", timeout=5)
        except Exception:
            if i == 0:
                exe = r"C:\Program Files\Voicebox\voicebox.exe"
                if os.path.exists(exe):
                    subprocess.Popen(["explorer.exe", exe])
                    print("Voicebox 켜는 중...", flush=True)
            time.sleep(3)
    sys.exit("[오류] Voicebox(%s)에 연결할 수 없습니다. Voicebox 앱을 켜 주세요." % VOICEBOX_URL)


def tts(text, out_wav, seed=7):
    if os.path.exists(out_wav) and os.path.getsize(out_wav) > 1000:
        return
    profs = ensure_voicebox()
    profs = profs.get("profiles", profs) if isinstance(profs, dict) else profs
    p = next((x for x in profs if x.get("name") == VOICE), None)
    if not p:
        sys.exit("[오류] Voicebox에 '%s' 프로필이 없습니다" % VOICE)
    eng = p.get("default_engine") or "qwen"
    body = {"profile_id": p["id"], "text": _ko_norm(text), "language": p.get("language") or "ko", "model_size": "1.7B", "engine": eng, "seed": seed}
    if eng == "qwen_custom_voice":
        body["instruct"] = INSTRUCT
    gid = _vb("/generate", body)["id"]
    for _ in range(900):
        h = _vb("/history/%s" % gid, timeout=30)
        if h.get("status") == "completed":
            break
        if h.get("status") == "failed":
            raise RuntimeError("Voicebox 생성 실패: %s" % h.get("error"))
        time.sleep(1.5)
    raw = out_wav + ".raw.wav"
    open(raw, "wb").write(_vb("/audio/%s" % gid, raw=True))
    # 48k 모노로 정규화 + 앞뒤 무음 정리
    ff(["-i", raw, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo=%.3f,loudnorm=I=-16:TP=-1.5" % SPEED,
        "-ar", "48000", "-ac", "1", out_wav])
    os.remove(raw)


def speakable(s):
    s = re.sub(r"\*\*", "", s)
    s = s.replace("%p", "퍼센트포인트").replace("%", "퍼센트").replace("bp", "bp")
    s = s.replace("↑", " 상승").replace("↓", " 하락").replace("~", "에서 ")
    return s.strip()


# ---------------- 그리기 ----------------
def font(p, size):
    return ImageFont.truetype(p, size)


def wrap(draw, text, fnt, maxw):
    """한국어 줄바꿈: 공백 단위, 넘치면 글자 단위."""
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
            continue
        if cur:
            lines.append(cur)
        cur = word
        while draw.textlength(cur, font=fnt) > maxw:
            k = len(cur)
            while k > 1 and draw.textlength(cur[:k], font=fnt) > maxw:
                k -= 1
            lines.append(cur[:k]); cur = cur[k:]
    if cur:
        lines.append(cur)
    return lines


def draw_rich(draw, xy, text, fnt, base, hl):
    """**강조** 부분을 hl 색으로."""
    x, y = xy
    for i, part in enumerate(re.split(r"\*\*", text)):
        if not part:
            continue
        draw.text((x, y), part, font=fnt, fill=hl if i % 2 else base)
        x += draw.textlength(part, font=fnt)


def wrap_rich(draw, text, fnt, maxw):
    plain = text.replace("**", "")
    out = wrap(draw, plain, fnt, maxw)
    # 강조 표시를 줄 단위로 복원
    marks, pos, res, on = [], 0, [], False
    flags = []
    for ch_i, part in enumerate(re.split(r"(\*\*)", text)):
        if part == "**":
            on = not on; continue
        flags += [on] * len(part)
    idx = 0
    for ln in out:
        while idx < len(flags) and plain[idx] == " " and not ln.startswith(" "):
            idx += 1
        seg, cur_on = "", False
        for c in ln:
            f = flags[idx] if idx < len(flags) else False
            if f != cur_on:
                seg += "**"; cur_on = f
            seg += c; idx += 1
        if cur_on:
            seg += "**"
        res.append(seg)
    return res


def date_label(d):
    return "%d월 %d일 (%s)" % (d.month, d.day, WEEK[d.weekday()])


def card_long(item, n, total, d, out):
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    # 상단 바
    dr.rectangle([0, 0, W, 110], fill=(9, 15, 30))
    dr.text((70, 28), "출근길 경제뉴스 3줄", font=font(F_BLACK, 52), fill=ACCENT)
    dr.text((560, 40), date_label(d), font=font(F_XB, 40), fill=WHITE)
    cnt = "%02d / %02d" % (n, total)
    fc = font(F_BLACK, 56)
    dr.text((W - 70 - dr.textlength(cnt, font=fc), 24), cnt, font=fc, fill=WHITE)
    # 카테고리 칩 + 출처
    cat = item.get("cat") or "경제"
    cc = CAT_COLOR.get(cat, BLUE); fcat = font(F_XB, 40)
    cw = dr.textlength(cat, font=fcat) + 56
    dr.rounded_rectangle([90, 170, 90 + cw, 236], 33, fill=cc)
    dr.text((118, 177), cat, font=fcat, fill=WHITE)
    if item.get("source"):
        dr.text((110 + cw, 182), "출처: " + item["source"], font=font(F_M, 34), fill=GREY)
    # 제목
    ft = font(F_BLACK, 84)
    tl = wrap_rich(dr, item["title"], ft, W - 200)[:2]
    y = 270
    for ln in tl:
        draw_rich(dr, (90, y), ln, ft, WHITE, ACCENT); y += 108
    # 3줄 패널
    y += 30
    fl = font(F_XB, 54)
    wl = [wrap_rich(dr, line, fl, W - 360)[:2] for line in item["lines"][:3]]
    ph = 45 + sum(len(x) * 70 + 34 for x in wl) + 20
    y = max(y, (y + H - 60 - ph) // 2)
    dr.rounded_rectangle([70, y, W - 70, y + ph], 28, fill=PANEL)
    y += 45
    for i, line in enumerate(item["lines"][:3]):
        dr.ellipse([115, y + 4, 175, y + 64], fill=cc)
        num = str(i + 1); fn = font(F_BLACK, 40)
        dr.text((145 - dr.textlength(num, font=fn) / 2, y + 9), num, font=fn, fill=WHITE)
        for ln in wl[i]:
            draw_rich(dr, (210, y), ln, fl, WHITE, ACCENT); y += 70
        y += 34
    # 진행바
    dr.rectangle([0, H - 14, W, H], fill=(30, 42, 70))
    dr.rectangle([0, H - 14, int(W * n / total), H], fill=ACCENT)
    im.save(out)


def card_intro_long(items, d, out):
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    dr.text((110, 120), date_label(d), font=font(F_XB, 64), fill=ACCENT)
    dr.text((110, 210), "출근길 경제뉴스", font=font(F_BLACK, 150), fill=WHITE)
    dr.text((110, 380), "%d개, 한 줄씩 3줄 요약" % len(items), font=font(F_BLACK, 100), fill=ACCENT)
    y = 560; f = font(F_XB, 50)
    dr.text((110, y), "오늘의 핵심", font=font(F_XB, 44), fill=GREY); y += 70
    for it in items[:4]:
        t = it["title"].replace("**", "")
        while dr.textlength("• " + t, font=f) > W - 220:
            t = t[:-2]
        dr.text((110, y), "• " + t, font=f, fill=WHITE); y += 78
    im.save(out)


def card_outro_long(d, out):
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    f = font(F_BLACK, 120)
    for i, (t, c) in enumerate([("오늘도 성투하세요!", WHITE), ("구독 · 좋아요 · 알림설정", ACCENT)]):
        w = dr.textlength(t, font=f if i == 0 else font(F_BLACK, 90))
        dr.text(((W - w) / 2, 380 + i * 170), t, font=f if i == 0 else font(F_BLACK, 90), fill=c)
    dr.text((W / 2 - 360, 800), "매일 영업일 아침 업로드 · 투자 판단은 본인 책임", font=font(F_M, 40), fill=GREY)
    im.save(out)


def card_short(item, n, total, d, out, label=None):
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    dr.text((70, 150), date_label(d), font=font(F_XB, 52), fill=ACCENT)
    dr.text((70, 225), "출근길 경제뉴스", font=font(F_BLACK, 100), fill=WHITE)
    dr.text((70, 345), label or ("TOP %d" % n), font=font(F_BLACK, 90), fill=ACCENT)
    cat = item.get("cat") or "경제"; cc = CAT_COLOR.get(cat, BLUE); fcat = font(F_XB, 44)
    cw = dr.textlength(cat, font=fcat) + 60
    dr.rounded_rectangle([70, 520, 70 + cw, 592], 36, fill=cc); dr.text((100, 527), cat, font=fcat, fill=WHITE)
    if item.get("source"):
        dr.text((95 + cw, 535), item["source"], font=font(F_M, 38), fill=GREY)
    ft = font(F_BLACK, 86); y = 640
    for ln in wrap_rich(dr, item["title"], ft, W - 140)[:3]:
        draw_rich(dr, (70, y), ln, ft, WHITE, ACCENT); y += 110
    y += 30
    dr.rounded_rectangle([40, y, W - 40, H - 260], 30, fill=PANEL); y += 45
    fl = font(F_XB, 52)
    for i, line in enumerate(item["lines"][:3]):
        dr.ellipse([75, y + 4, 135, y + 64], fill=cc)
        dr.text((95, y + 9), str(i + 1), font=font(F_BLACK, 40), fill=WHITE)
        for ln in wrap_rich(dr, line, fl, W - 250)[:3]:
            draw_rich(dr, (165, y), ln, fl, WHITE, ACCENT); y += 68
        y += 28
    dr.rectangle([0, H - 14, int(W * n / total), H], fill=ACCENT)
    im.save(out)


def thumb(items, d, out, size=(1280, 720), head=None):
    W, H = size
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    vertical = H > W
    s = W / 1280
    dr.rectangle([0, 0, W, int(16 * s)], fill=ACCENT)
    dr.text((int(60 * s), int(50 * s)), date_label(d), font=font(F_BLACK, int(70 * s)), fill=ACCENT)
    dr.text((int(60 * s), int(140 * s)), "출근길 경제뉴스", font=font(F_BLACK, int(120 * s)), fill=WHITE)
    dr.text((int(60 * s), int(285 * s)), head or ("%d개 3줄 요약" % len(items)), font=font(F_BLACK, int(110 * s)), fill=ACCENT)
    top = items[0]["title"].replace("**", "")
    ft = font(F_BLACK, int(64 * s)); y = int(450 * s)
    for ln in wrap(dr, top, ft, W - int(120 * s))[:2 if not vertical else 4]:
        dr.rectangle([int(50 * s), y - int(6 * s), int(50 * s) + dr.textlength(ln, font=ft) + int(24 * s), y + int(76 * s)], fill=(200, 30, 45))
        dr.text((int(62 * s), y), ln, font=ft, fill=WHITE); y += int(96 * s)
    im.convert("RGB").save(out, quality=92)


# ---------------- 조립 ----------------
def segment(png, wav, out, pad=0.45, fps=30):
    d = dur(wav) + pad
    ff(["-loop", "1", "-framerate", str(fps), "-i", png, "-i", wav,
        "-filter_complex", "[1:a]apad=pad_dur=%.2f,aresample=48000[a]" % pad, "-map", "0:v", "-map", "[a]",
        "-t", "%.3f" % d, "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", out])
    return d


def concat(segs, out):
    lst = out + ".txt"
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write("file '%s'\n" % s.replace("\\", "/"))
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out])
    os.remove(lst)


MAX_SHORTS = float(os.environ.get("NEWS_MAX_SEC", "178"))  # 쇼츠 3분 제한 안전선
MAX_EXTRA = 1.25  # 기본 1.2배에 추가로 올릴 수 있는 최대 배수 (=> 최대 1.5배)


def card_all(item, n, total, d, out):
    """29개 몰아보기 쇼츠 카드 (세로). 하단 380px은 쇼츠 UI에 가려지므로 비워 둔다."""
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    dr.text((60, 150), date_label(d) + "  출근길 경제뉴스", font=font(F_XB, 50), fill=ACCENT)
    cnt = "%02d" % n; fc = font(F_BLACK, 150)
    dr.text((60, 220), cnt, font=fc, fill=ACCENT)
    dr.text((70 + dr.textlength(cnt, font=fc), 300), "/ %d" % total, font=font(F_BLACK, 70), fill=GREY)
    cat = item.get("cat") or "경제"; cc = CAT_COLOR.get(cat, BLUE); fcat = font(F_XB, 52)
    cw = dr.textlength(cat, font=fcat) + 64
    dr.rounded_rectangle([60, 450, 60 + cw, 532], 41, fill=cc); dr.text((92, 459), cat, font=fcat, fill=WHITE)
    if item.get("source"):
        dr.text((88 + cw, 470), item["source"], font=font(F_M, 44), fill=GREY)
    ft = font(F_BLACK, 108); y = 580
    for ln in wrap_rich(dr, item["title"], ft, W - 120)[:3]:
        draw_rich(dr, (60, y), ln, ft, WHITE, ACCENT); y += 138
    y += 45
    fl = font(F_XB, 66)
    wl = [wrap_rich(dr, line, fl, W - 250)[:2] for line in item["lines"][:3]]
    ph = 55 + sum(len(x) * 88 + 46 for x in wl) + 10
    dr.rounded_rectangle([36, y, W - 36, y + ph], 34, fill=PANEL); y += 55
    for i, line in enumerate(item["lines"][:3]):
        dr.ellipse([70, y + 6, 142, y + 78], fill=cc)
        dr.text((93, y + 12), str(i + 1), font=font(F_BLACK, 50), fill=WHITE)
        for ln in wl[i]:
            draw_rich(dr, (170, y), ln, fl, WHITE, ACCENT); y += 88
        y += 46
    # 진행바 (쇼츠 UI 위쪽)
    dr.rounded_rectangle([60, 1500, W - 60, 1524], 12, fill=(30, 42, 70))
    dr.rounded_rectangle([60, 1500, 60 + int((W - 120) * n / total), 1524], 12, fill=ACCENT)
    im.save(out)

def card_all_intro(items, d, out):
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    dr.text((60, 330), date_label(d), font=font(F_XB, 70), fill=ACCENT)
    dr.text((60, 430), "출근길", font=font(F_BLACK, 170), fill=WHITE)
    dr.text((60, 620), "경제뉴스", font=font(F_BLACK, 170), fill=WHITE)
    dr.text((60, 820), "%d개 3분 요약" % len(items), font=font(F_BLACK, 120), fill=ACCENT)
    f = font(F_XB, 50); y = 1060
    for it in items[:5]:
        t = it["title"].replace("**", "")
        while dr.textlength("• " + t, font=f) > W - 120:
            t = t[:-2]
        dr.text((60, y), "• " + t, font=f, fill=WHITE); y += 80
    im.save(out)


def card_all_outro(total, out):
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H), BG); dr = ImageDraw.Draw(im)
    for t, fs, c, y in [("오늘도", 150, WHITE, 640), ("성투하세요!", 150, WHITE, 820), ("구독하고 매일 아침", 80, ACCENT, 1060), ("경제뉴스 받아보기", 80, ACCENT, 1160)]:
        fnt = font(F_BLACK, fs); dr.text(((W - dr.textlength(t, font=fnt)) / 2, y), t, font=fnt, fill=c)
    im.save(out)


def speed_up(src, dst, factor):
    ff(["-i", src, "-af", "atempo=%.4f" % factor, "-ar", "48000", "-ac", "1", dst])


def build_all_shorts(cfg, items, d, A, wd):
    total = len(items)
    intro_say = cfg.get("shorts_intro") or "%d월 %d일 출근길 경제뉴스 %d개, 3분 요약!" % (d.month, d.day, total)
    outro_say = cfg.get("shorts_outro") or "구독하고 매일 아침 받아보세요!"
    tts(speakable(intro_say), os.path.join(A, "a_intro.wav"))
    t0 = time.time()
    for i, it in enumerate(items):
        tts(speakable(it.get("say") or it["title"]), os.path.join(A, "a%02d.wav" % i))
        print("  음성 %d/%d (%.0f초)" % (i + 1, total, time.time() - t0), flush=True)
    tts(speakable(outro_say), os.path.join(A, "a_outro.wav"))
    wavs = [os.path.join(A, "a_intro.wav")] + [os.path.join(A, "a%02d.wav" % i) for i in range(total)] + [os.path.join(A, "a_outro.wav")]
    raw = [dur(w) for w in wavs]
    # 시간 안배: 카드 최소 노출 2.2초, 컷 사이 여백 0.25초 -> 넘치면 여백 축소 -> 그래도 넘치면 말 속도 추가 상승
    min_show, pad = 2.2, 0.25
    def total_len(f, p):
        return sum(max(r / f + p, min_show) for r in raw) + 0.6
    factor = 1.0
    if total_len(1.0, pad) > MAX_SHORTS:
        pad = 0.12
    while total_len(factor, pad) > MAX_SHORTS and factor < MAX_EXTRA:
        factor = round(factor + 0.01, 3)
    # 남으면: 목표 길이까지 카드별 노출 시간을 고르게 늘려 화면 3줄을 읽을 시간을 준다 (카드당 최대 +3초)
    target = float(os.environ.get("NEWS_TARGET_SEC", "170"))
    if total_len(factor, pad) < target:
        pad = min(pad + (target - total_len(factor, pad)) / len(raw), pad + 3.0)
    est = total_len(factor, pad)
    print("쇼츠 시간 안배: 원래 %.1f초 -> 추가배속 x%.2f, 여백 %.2f초 -> 예상 %.1f초" % (total_len(1.0, 0.25), factor, pad, est), flush=True)
    if est > MAX_SHORTS:
        sys.exit("[오류] 1.5배로도 %.0f초라 3분을 넘습니다. say 문장을 더 짧게(20자 내외) 줄이세요." % est)
    if factor > 1.0:
        fw = []
        for w in wavs:
            o = w.replace(".wav", "_fit.wav"); speed_up(w, o, factor); fw.append(o)
        wavs = fw
    pngs = [os.path.join(A, "c_intro.png")] + [os.path.join(A, "c%02d.png" % i) for i in range(total)] + [os.path.join(A, "c_outro.png")]
    card_all_intro(items, d, pngs[0]); card_all_outro(total, pngs[-1])
    for i, it in enumerate(items):
        card_all(it, i + 1, total, d, pngs[i + 1])
    segs = []
    for k, (p, w) in enumerate(zip(pngs, wavs)):
        sp = os.path.join(A, "v%02d.mp4" % k)
        need = max(dur(w) + pad, min_show) - dur(w)
        segment(p, w, sp, pad=need + (0.6 if k == len(pngs) - 1 else 0))
        segs.append(sp)
    concat(segs, os.path.join(wd, "shorts.mp4"))
    real = dur(os.path.join(wd, "shorts.mp4"))
    if real > 179.5:
        sys.exit("[오류] 쇼츠가 %.1f초로 3분을 넘었습니다" % real)
    return real


def main():
    wd = os.path.abspath(sys.argv[1])
    cfg = json.load(open(os.path.join(wd, "news.json"), encoding="utf-8"))
    items = cfg["items"]
    d = datetime.date.fromisoformat(cfg.get("date") or datetime.date.today().isoformat())
    A = os.path.join(wd, "build"); os.makedirs(A, exist_ok=True)
    total = len(items); t0 = time.time()
    srcs = sorted({it.get("source") for it in items if it.get("source")})
    disc = "※ 각 언론 보도를 바탕으로 직접 요약한 내용입니다. 투자 판단과 책임은 본인에게 있습니다."
    meta = {"date": d.isoformat()}

    # ---- 메인: 전체 기사 3분 쇼츠 ----
    print("뉴스 %d개 -> 3분 쇼츠 제작 시작" % total, flush=True)
    sl = build_all_shorts(cfg, items, d, A, wd)
    thumb(items, d, os.path.join(wd, "shorts_thumb.jpg"), size=(1080, 1920), head="%d개 3분 요약" % total)
    sy = cfg.get("shorts_youtube", {})
    meta["shorts"] = {"file": "shorts.mp4",
                      "title": (sy.get("title") or "%s 출근길 경제뉴스 %d개 3분 요약" % (date_label(d), total))[:90] + " #shorts",
                      "description": (sy.get("description") or "매일 영업일 아침, 꼭 알아야 할 경제뉴스를 3분 안에 정리해 드립니다.") + "\n\n"
                                     + "\n".join("%02d. %s" % (i + 1, it["title"].replace("**", "")) for i, it in enumerate(items))
                                     + ("\n\n참고 언론: " + ", ".join(srcs) if srcs else "") + "\n" + disc + "\n#shorts #경제뉴스 #출근길 #재테크 #월급쟁이",
                      "tags": ["shorts", "경제뉴스", "오늘의경제뉴스", "출근길뉴스", "재테크", "월급쟁이재테크"]}
    print("쇼츠 완료: %.1f초" % sl, flush=True)

    # ---- 선택: 롱폼 (news.json 에 "long": true) ----
    if cfg.get("long"):
        print("롱폼 제작...", flush=True)
        intro_txt = cfg.get("intro") or ("%d월 %d일 %s요일, 출근길 경제뉴스입니다. 오늘 꼭 알아야 할 경제뉴스 %d개, 3줄씩 정리해 드릴게요."
                                         % (d.month, d.day, WEEK[d.weekday()], total))
        outro_txt = cfg.get("outro") or "오늘 경제뉴스는 여기까지입니다. 도움이 되셨다면 구독과 좋아요 부탁드리고, 오늘도 성투하세요!"
        tts(speakable(intro_txt), os.path.join(A, "intro.wav"))
        for i, it in enumerate(items):
            tts("%s. %s" % (speakable(it["title"]), " ".join(speakable(x) for x in it["lines"][:3])), os.path.join(A, "n%02d.wav" % i))
            print("  롱폼 음성 %d/%d" % (i + 1, total), flush=True)
        tts(speakable(outro_txt), os.path.join(A, "outro.wav"))
        card_intro_long(items, d, os.path.join(A, "intro.png")); card_outro_long(d, os.path.join(A, "outro.png"))
        segs, chapters, t = [], [], 0.0
        t += segment(os.path.join(A, "intro.png"), os.path.join(A, "intro.wav"), os.path.join(A, "s_intro.mp4"), pad=0.6)
        segs.append(os.path.join(A, "s_intro.mp4"))
        for i, it in enumerate(items):
            png = os.path.join(A, "n%02d.png" % i); card_long(it, i + 1, total, d, png)
            sp = os.path.join(A, "s%02d.mp4" % i)
            chapters.append((t, "%02d %s" % (i + 1, it["title"].replace("**", ""))))
            t += segment(png, os.path.join(A, "n%02d.wav" % i), sp); segs.append(sp)
        segment(os.path.join(A, "outro.png"), os.path.join(A, "outro.wav"), os.path.join(A, "s_outro.mp4"), pad=1.0)
        segs.append(os.path.join(A, "s_outro.mp4"))
        concat(segs, os.path.join(wd, "long.mp4"))
        thumb(items, d, os.path.join(wd, "thumb.jpg"))
        yt = cfg.get("youtube", {})
        chap = "\n".join("%d:%02d %s" % (int(s // 60), int(s % 60), name) for s, name in [(0, "인트로")] + chapters)
        meta["long"] = {"file": "long.mp4", "thumb": "thumb.jpg",
                        "title": yt.get("title") or "%s 출근길 경제뉴스 %d개 3줄 요약 | %s" % (date_label(d), total, items[0]["title"].replace("**", "")),
                        "description": (yt.get("description") or "매일 영업일 아침, 꼭 알아야 할 경제뉴스를 3줄씩 정리해 드립니다.") + "\n\n" + chap
                                       + ("\n\n참고 언론: " + ", ".join(srcs) if srcs else "") + "\n" + disc + "\n\n#경제뉴스 #출근길 #재테크 #주식 #월급쟁이",
                        "tags": yt.get("tags") or ["경제뉴스", "오늘의경제뉴스", "출근길뉴스", "경제뉴스요약", "재테크", "주식", "월급쟁이재테크"]}

    json.dump(meta, open(os.path.join(wd, "upload.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("완료: 총 %.0f초 소요" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
