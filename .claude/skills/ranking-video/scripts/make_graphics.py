# -*- coding: utf-8 -*-
"""랭킹 영상 그래픽 생성기 (ranking-video 스킬 v2.1.0) — '클린 미니멀' 스타일

사용법:
    python3 -I make_graphics.py <대본데이터.json> <출력폴더> [--img <이미지폴더>]
  --img를 주면 섹션의 "title_image"(이미지 id) 사진으로 순위 타이틀 카드(08_타이틀카드)를 만든다.

대본데이터.json의 "graphics" 항목을 읽어 <출력폴더>/07_그래픽/ 에 1920×1080 PNG를 만든다.
  01_챕터카드/      어두운 그리드 + 초록·청록 글로우 + 흰 제목 (섹션 시작 2초)
  02_상단라벨/      좌상단 고정 챕터 라벨 (투명 PNG, 섹션 내내 깔기)
  03_순위배지/      우하단 원형 순위 배지 (투명 PNG, 참고 영상의 원형 PIP 자리)
  04_정보카드/      흰 배경 + 작은 제목 + 검정 필 태그 + 큰 숫자/키워드
  05_요약카드/      흰 배경 '오늘의 요약' 칸이 하나씩 채워지는 연속 이미지
  06_엔드카드/      검정 배경 + 채널명
  07_썸네일틀/      썸네일 레이아웃 (사진 자리 비움)
  08_타이틀카드/    순위별 PPT 표지 같은 화면: 대표 사진 전면 + 순위 + 점포명 + 한 줄 특징
  07_썸네일틀/썸네일_임팩트.png  graphics.thumbnail_bold가 있으면: 사진 전면 + 기울어진 큰 제목 + 하단 칩 3개 (v1.3.1)
폰트: Pretendard (SIL OFL 1.1). 없으면 npm 레지스트리에서 자동으로 받는다.
"""
import json, os, subprocess, sys, tarfile, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
FONT_DIR = os.path.expanduser("~/.cache/ranking-video/fonts")


def font_path(weight):
    p = os.path.join(FONT_DIR, f"Pretendard-{weight}.otf")
    if not os.path.exists(p):
        os.makedirs(FONT_DIR, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["npm", "pack", "pretendard@1.3.9", "--silent"], cwd=td, check=True, capture_output=True)
            with tarfile.open(os.path.join(td, "pretendard-1.3.9.tgz")) as t:
                for w in ("SemiBold", "Bold", "ExtraBold"):
                    m = t.getmember(f"package/dist/public/static/Pretendard-{w}.otf")
                    with open(os.path.join(FONT_DIR, f"Pretendard-{w}.otf"), "wb") as f:
                        f.write(t.extractfile(m).read())
    return p


def F(size, weight="Bold"):
    return ImageFont.truetype(font_path(weight), size)


def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def center_text(d, xy, text, font, fill, stroke=0, stroke_fill=None):
    d.text(xy, text, font=font, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=stroke_fill)


def pill(d, cx, cy, text, font, bg=(17, 17, 17), fg=(255, 255, 255), padx=26, pady=12):
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    w, h = r - l + padx * 2, b - t + pady * 2
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=bg)
    center_text(d, (cx, cy), text, font, fg)


def chapter_card(title, accent, accent2, sub=None):
    img = Image.new("RGB", (W, H), (9, 12, 16))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 64): d.line((x, 0, x, H), fill=(28, 36, 44), width=1)
    for y in range(0, H, 64): d.line((0, y, W, y), fill=(28, 36, 44), width=1)
    glow = Image.new("RGB", (W, H), (0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse((W * 0.45, H * 0.55, W * 1.25, H * 1.5), fill=accent)
    g.ellipse((W * 0.75, H * 0.2, W * 1.3, H * 0.9), fill=accent2)
    glow = glow.filter(ImageFilter.GaussianBlur(260))
    img = Image.blend(img, glow, 0.55)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 64): d.line((x, 0, x, H), fill=(40, 52, 60), width=1)
    for y in range(0, H, 64): d.line((0, y, W, y), fill=(40, 52, 60), width=1)
    center_text(d, (W / 2, H / 2), title, F(112, "ExtraBold"), (255, 255, 255))
    if sub: center_text(d, (W / 2, H / 2 + 110), sub, F(40, "SemiBold"), (210, 220, 225))
    return img


def top_label(text):
    """좌상단 점포명 라벨: v1.3.0부터 2배 크기 + 오른쪽으로 살짝 기울임 + 선명한 외곽선과 은은한 그림자"""
    f = F(88, "ExtraBold")
    layer = Image.new("RGBA", (W, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.text((60, 40), text, font=f, fill=(0, 0, 0, 110), stroke_width=8, stroke_fill=(0, 0, 0, 110))
    layer = layer.filter(ImageFilter.GaussianBlur(6))  # 그림자
    d = ImageDraw.Draw(layer)
    d.text((54, 32), text, font=f, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(17, 17, 17, 255))
    sh = 0.18  # 기울기(오른쪽으로 약 10도)
    layer = layer.transform(layer.size, Image.AFFINE, (1, sh, -sh * 130, 0, 1, 0), resample=Image.BICUBIC)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); img.alpha_composite(layer, (0, 0))
    return img


def title_card(photo, rank, name, tagline, accent, pill_text=None):
    """순위 타이틀 카드: 사진 전면 + 왼쪽 아래 어두운 그라데이션 + 큰 점포명 (PPT 표지 느낌)"""
    im = Image.open(photo).convert("RGB")
    sc = max(W / im.width, H / im.height); im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = int(200 * max(0, (y - H * 0.35) / (H * 0.65)) ** 1.3); gd.line((0, y, W, y), fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, g); d = ImageDraw.Draw(im)
    pt = pill_text or f"{rank}위"; pf = F(64, "ExtraBold"); pl, _, pr, _ = d.textbbox((0, 0), pt, font=pf)
    pill(d, 120 + (pr - pl) / 2 + 38, 640, pt, pf, bg=accent, fg=(255, 255, 255), padx=38, pady=14)
    nf = 190
    while nf > 110 and d.textbbox((0, 0), name, font=F(nf, "ExtraBold"))[2] > W - 220: nf -= 10  # 긴 챕터 이름은 폭에 맞춰 줄임
    d.text((120, 700 + (190 - nf) // 2), name, font=F(nf, "ExtraBold"), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    if tagline: d.text((128, 935), tagline, font=F(54, "SemiBold"), fill=(235, 238, 240))
    return im.convert("RGB")


def rank_badge(n, accent):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    r, cx, cy = 92, W - 150, H - 160
    d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=accent)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255))
    center_text(d, (cx, cy - 8), str(n), F(96, "ExtraBold"), (17, 17, 17))
    center_text(d, (cx, cy + 52), "위", F(30, "Bold"), (90, 90, 90))
    return img


def info_card(c, accent):
    img = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    center_text(d, (W / 2, 170), c["title"], F(58, "ExtraBold"), (17, 17, 17))
    if c.get("tag"): pill(d, W / 2, 255, c["tag"], F(32, "Bold"))
    # 가운데 카드
    d.rounded_rectangle((W / 2 - 430, 360, W / 2 + 430, 760), radius=48, fill=(246, 247, 248), outline=(228, 230, 233), width=3)
    big_col = DOWN_C if c.get("trend") == "down" else (UP_C if c.get("trend") == "up" else (17, 17, 17))  # v2.4.0 시세 카드
    center_text(d, (W / 2, 530), c["big"], F(150 if len(c["big"]) <= 7 else 110, "ExtraBold"), big_col)
    if c.get("caption"): center_text(d, (W / 2, 680), c["caption"], F(40, "SemiBold"), (110, 115, 120))
    if c.get("months"):  # v2.1.0 제철 달력: 12칸 중 제철은 연한 초록, 절정은 진한 초록
        cw_, gap_ = 104, 12; x0_ = (W - (12 * cw_ + 11 * gap_)) / 2; y0_ = 820
        peak = set(c.get("peak", []))
        for k in range(12):
            mth = k + 1; x = x0_ + k * (cw_ + gap_)
            on = mth in c["months"]; pk = mth in peak
            fill = accent if pk else ((200, 240, 222) if on else (240, 241, 243))
            d.rounded_rectangle((x, y0_, x + cw_, y0_ + 84), radius=18, fill=fill)
            center_text(d, (x + cw_ / 2, y0_ + 42), f"{mth}월", F(34, "ExtraBold" if on else "SemiBold"),
                        (255, 255, 255) if pk else ((20, 90, 60) if on else (160, 165, 170)))
        center_text(d, (W / 2, y0_ + 130), "연한 초록 = 제철   진한 초록 = 절정", F(28, "SemiBold"), (130, 135, 140))
    else:
        d.rounded_rectangle((W / 2 - 60, 790, W / 2 + 60, 800), radius=5, fill=accent)
    return img


def summary_cards(items, upto, accent, done_title=None):
    """items: [(번호, 이름)] — upto개까지 채운 요약 카드"""
    img = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    d.text((40, 30), "오늘의 요약", font=F(44, "ExtraBold"), fill=(255, 255, 255), stroke_width=5, stroke_fill=(20, 20, 20))
    title = items[upto - 1][1] if upto else f"TOP{len(items)} 한눈에"
    if not upto and done_title: title = done_title
    center_text(d, (W / 2, 150), title if upto < len(items) else (done_title or f"TOP{len(items)} 한눈에"), F(54, "ExtraBold"), (17, 17, 17))
    cols, cw, ch, gap = 5, 300, 330, 34
    x0 = (W - (cols * cw + (cols - 1) * gap)) / 2
    for i, (num, name) in enumerate(items):
        x = x0 + (i % cols) * (cw + gap); y = 250 + (i // cols) * (ch + 50)
        filled = i < upto
        d.rounded_rectangle((x, y, x + cw, y + ch), radius=30, fill=(255, 255, 255),
                            outline=(17, 17, 17) if filled else (215, 218, 222), width=4 if filled else 3)
        d.ellipse((x + cw / 2 - 28, y - 28, x + cw / 2 + 28, y + 28), fill=(17, 17, 17) if filled else (215, 218, 222))
        center_text(d, (x + cw / 2, y), str(num), F(30, "ExtraBold"), (255, 255, 255))
        if filled:
            center_text(d, (x + cw / 2, y + ch / 2 - 10), name, F(44 if len(name) <= 5 else 36, "ExtraBold"), (17, 17, 17))
            d.rounded_rectangle((x + cw / 2 - 40, y + ch - 70, x + cw / 2 + 40, y + ch - 62), radius=4, fill=accent)
    return img


def end_card(name):
    img = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(img)
    center_text(d, (W / 2, H / 2), name, F(120, "ExtraBold"), (255, 255, 255))
    return img


def thumb_frame(lines, badge, accent):
    img = Image.new("RGB", (1280, 720), (70, 74, 80)); d = ImageDraw.Draw(img)
    center_text(d, (640, 300), "← 여기에 메인 사진 (예: 킹크랩·대방어 클로즈업) →", F(30, "SemiBold"), (200, 205, 210))
    band = Image.new("RGBA", (1280, 720), (0, 0, 0, 0)); b = ImageDraw.Draw(band)
    for y in range(400, 720): b.line((0, y, 1280, y), fill=(0, 0, 0, int(235 * min(1, (y - 400) / 140))))
    img = Image.alpha_composite(img.convert("RGBA"), band); d = ImageDraw.Draw(img)
    pill(d, 640, 80, badge, F(56, "ExtraBold"), bg=accent, fg=(255, 255, 255), padx=40, pady=14)
    y = 720 - 90 - (len(lines) - 1) * 112
    for ln in lines:
        center_text(d, (640, y), ln, F(104, "ExtraBold"), (255, 255, 255), stroke=4, stroke_fill=(0, 0, 0)); y += 112
    return img.convert("RGB")


def _skew_text(size, text, font, fill, stroke, stroke_fill, shadow=True, sh=0.12):
    """기울어진(오른쪽) 굵은 글자 레이어. 그림자는 은은하게."""
    lay = Image.new("RGBA", size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    l, t, r, b = d.textbbox((0, 0), text, font=font, stroke_width=stroke)
    x, y = 30, 20
    if shadow:
        sd = Image.new("RGBA", size, (0, 0, 0, 0)); ImageDraw.Draw(sd).text((x + 8, y + 10), text, font=font, fill=(0, 0, 0, 150), stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
        lay.alpha_composite(sd.filter(ImageFilter.GaussianBlur(7)))
    ImageDraw.Draw(lay).text((x, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    lay = lay.transform(lay.size, Image.AFFINE, (1, sh, -sh * (b + 40), 0, 1, 0), resample=Image.BICUBIC)
    return lay.crop(lay.getbbox() or (0, 0, 1, 1))


def _icon(kind, box, color):
    """칩 아이콘: 단순한 선 아이콘(직접 그림)"""
    ic = Image.new("RGBA", (box, box), (0, 0, 0, 0)); d = ImageDraw.Draw(ic); w = max(4, box // 14)
    if kind == "list":
        d.rounded_rectangle((box * .18, box * .1, box * .82, box * .92), radius=box * .08, outline=color, width=w)
        for k, y in enumerate((.35, .55, .75)):
            d.line((box * .3, box * y, box * .38, box * (y + .06), box * .5, box * (y - .07)), fill=color, width=w)
            d.line((box * .56, box * y, box * .72, box * y), fill=color, width=w)
    elif kind == "chart":
        for k, h in enumerate((.35, .55, .8)):
            x = box * (.18 + k * .24); d.rectangle((x, box * (.92 - h), x + box * .16, box * .92), fill=color)
        d.line((box * .12, box * .55, box * .45, box * .3, box * .85, box * .08), fill=(226, 59, 46), width=w)
    elif kind == "search":
        d.ellipse((box * .12, box * .12, box * .62, box * .62), outline=color, width=w + 2)
        d.line((box * .55, box * .55, box * .88, box * .88), fill=color, width=w + 4)
    elif kind == "crown":
        d.polygon([(box * .1, box * .8), (box * .1, box * .3), (box * .32, box * .55), (box * .5, box * .2), (box * .68, box * .55), (box * .9, box * .3), (box * .9, box * .8)], fill=color)
    return ic


def thumbnail_bold(photo, T, accent):
    """임팩트 썸네일 (1280×720). 참고 썸네일보다 외곽선·채도를 한 단계 낮춘 버전."""
    W2, H2 = 1280, 720
    im = Image.open(photo).convert("RGB"); sc = max(W2 / im.width, H2 / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x0, y0 = (im.width - W2) // 2, (im.height - H2) // 2; im = im.crop((x0, y0, x0 + W2, y0 + H2)).convert("RGBA")
    shade = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    for x in range(W2):  # 왼쪽을 어둡게(글자 가독성), 오른쪽은 사진이 살게
        a = int(150 * max(0, 1 - x / (W2 * 0.75)) ** 1.2) + 30; sd.line((x, 0, x, H2), fill=(5, 12, 28, a))
    im = Image.alpha_composite(im, shade)
    red, yellow = (226, 59, 46), (255, 214, 64)
    top = _skew_text((W2, 200), T["top"], F(78, "ExtraBold"), red, 7, (255, 255, 255))
    im.alpha_composite(top, (28, 22))
    def fit(text, size=150, maxw=1180):  # 긴 제목은 화면 폭에 맞게 글자 크기를 자동으로 줄임
        while size > 70:
            l, t_, r, b_ = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=F(size, "ExtraBold"), stroke_width=11)
            if r - l + 60 <= maxw: break
            size -= 6
        return F(size, "ExtraBold")
    m1 = _skew_text((W2 + 200, 260), T["main"], fit(T["main"]), (255, 255, 255), 11, (12, 16, 24))
    im.alpha_composite(m1, (22, 118))
    m2 = _skew_text((W2 + 200, 260), T["sub"], fit(T["sub"]), yellow, 11, (12, 16, 24))
    im.alpha_composite(m2, (40, 282))
    # 오른쪽 위 시리즈 배지
    d = ImageDraw.Draw(im); bf = F(34, "ExtraBold"); l, t_, r, b = d.textbbox((0, 0), T["badge"], font=bf)
    bw = r - l + 44; d.rounded_rectangle((W2 - bw - 24, 22, W2 - 24, 22 + b - t_ + 26), radius=12, fill=(14, 32, 72), outline=(255, 255, 255), width=3)
    d.text((W2 - bw - 24 + 22, 22 + 11), T["badge"], font=bf, fill=(255, 255, 255))
    # 하단 칩 3개
    cw, ch, gap = 386, 112, 22; y = H2 - ch - 22; x = (W2 - (3 * cw + 2 * gap)) // 2
    for k, c in enumerate(T["chips"][:3]):
        cx = x + k * (cw + gap)
        sh_ = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); ImageDraw.Draw(sh_).rounded_rectangle((cx + 4, y + 6, cx + cw + 4, y + ch + 6), radius=18, fill=(0, 0, 0, 120))
        im.alpha_composite(sh_.filter(ImageFilter.GaussianBlur(5)))
        d = ImageDraw.Draw(im); d.rounded_rectangle((cx, y, cx + cw, y + ch), radius=18, fill=(255, 255, 255), outline=(30, 40, 60), width=3)
        im.alpha_composite(_icon(c.get("icon", "list"), 78, (20, 30, 48)), (cx + 16, y + 17))
        d.text((cx + 106, y + 16), c["l1"], font=F(32, "Bold"), fill=(20, 30, 48))
        d.text((cx + 106, y + 58), c["l2"], font=F(36, "ExtraBold"), fill=red)
    return im.convert("RGB")


def thumbnail_versus(left_photo, right_photo, T, accent):
    """VS 대결형 썸네일 (1280x720, v2.1.0): 왼쪽(기대, 흑백) vs 오른쪽(정답, 컬러) + 아주 큰 2줄 제목 + 하단 초록 띠 + 빨간 원형 스탬프"""
    W2, H2 = 1280, 720
    def cover(p, w, h):
        im = Image.open(p).convert("RGB"); sc = max(w / im.width, h / im.height)
        im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
        x0, y0 = (im.width - w) // 2, (im.height - h) // 2; return im.crop((x0, y0, x0 + w, y0 + h))
    base = Image.new("RGB", (W2, H2))
    L_ = cover(left_photo, W2, H2).convert("L").convert("RGB")
    R_ = cover(right_photo, W2, H2)
    mask = Image.new("L", (W2, H2), 0); ImageDraw.Draw(mask).polygon([(700, 0), (W2, 0), (W2, H2), (520, H2)], fill=255)
    base.paste(L_, (0, 0)); base.paste(R_, (0, 0), mask)
    im = base.convert("RGBA")
    sh = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for y in range(H2):
        a = int(185 * max(0, 1 - y / (H2 * 0.62)) ** 1.1); sd.line((0, y, W2, y), fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, sh); d = ImageDraw.Draw(im)
    d.line((700, 0, 520, H2), fill=(255, 255, 255), width=10)
    for txt, (x, y), col in ((T["left_label"], (60, 540), (90, 95, 100)), (T["right_label"], (900, 540), (226, 59, 46))):
        f = F(58, "ExtraBold"); l, t_, r, b = d.textbbox((0, 0), txt, font=f)
        d.rounded_rectangle((x - 18, y - 8, x + r - l + 18, y + b - t_ + 22), radius=14, fill=col); d.text((x, y), txt, font=f, fill=(255, 255, 255))
    d.ellipse((550, 380, 670, 500), fill=(255, 255, 255), outline=(20, 20, 20), width=6)
    center_text(d, (610, 438), "VS", F(56, "ExtraBold"), (20, 20, 20))
    def fit(text, size, maxw=1200):
        while size > 80:
            l, t_, r, b = d.textbbox((0, 0), text, font=F(size, "ExtraBold"), stroke_width=12)
            if r - l <= maxw: break
            size -= 6
        return F(size, "ExtraBold")
    l1 = _skew_text((W2 + 300, 280), T["line1"], fit(T["line1"], 176), (255, 255, 255), 12, (10, 12, 18), sh=0.08)
    l2 = _skew_text((W2 + 300, 280), T["line2"], fit(T["line2"], 176), (255, 214, 64), 12, (10, 12, 18), sh=0.08)
    im.alpha_composite(l1, (20, 4)); im.alpha_composite(l2, (20, 176))
    st = Image.new("RGBA", (230, 230), (0, 0, 0, 0)); sdr = ImageDraw.Draw(st)
    sdr.ellipse((8, 8, 222, 222), fill=(226, 59, 46), outline=(255, 255, 255), width=8)
    center_text(sdr, (115, 96), T["stamp1"], F(46, "ExtraBold"), (255, 255, 255)); center_text(sdr, (115, 148), T["stamp2"], F(38, "Bold"), (255, 255, 255))
    st = st.rotate(-12, resample=Image.BICUBIC); im.alpha_composite(st, (W2 - 250, 300))
    d = ImageDraw.Draw(im); d.rectangle((0, H2 - 96, W2, H2), fill=accent)
    center_text(d, (W2 / 2, H2 - 48), T["bar"], F(54, "ExtraBold"), (255, 255, 255))
    return im.convert("RGB")


def _cover(photo, w, h):
    im = Image.open(photo).convert("RGB"); sc = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def _fit(text, size, maxw, weight="ExtraBold", stroke=10, minsize=60):
    while size > minsize:
        l, t_, r, b_ = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=F(size, weight), stroke_width=stroke)
        if r - l <= maxw: break
        size -= 6
    return F(size, weight)


def thumbnail_number(photo, T, accent):
    """C. 큰 숫자형 썸네일 (1280x720, v2.3.0): 숫자 하나를 화면 절반 크기로 + 빨간 윗줄 질문 + 큰 흰 제목"""
    W2, H2 = 1280, 720; red, yellow = (226, 59, 46), (255, 214, 64)
    im = _cover(photo, W2, H2).convert("RGBA")
    sh = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for x in range(W2):  # 왼쪽 어둡게 → 숫자와 제목이 또렷하게
        a = int(205 * max(0, 1 - x / (W2 * 0.85)) ** 1.1) + 25; sd.line((x, 0, x, H2), fill=(4, 10, 22, a))
    im = Image.alpha_composite(im, sh)
    top = _skew_text((W2, 180), T["top"], _fit(T["top"], 74, 900, stroke=7), red, 7, (255, 255, 255))
    im.alpha_composite(top, (26, 18))
    num = _skew_text((W2 + 200, 420), T["number"], _fit(T["number"], T.get("number_size", 330), T.get("number_maxw", 760), stroke=14, minsize=110), yellow, 14, (10, 12, 18), sh=0.06)
    im.alpha_composite(num, (24, 108))
    d = ImageDraw.Draw(im)
    if T.get("number_sub"):  # 숫자 옆 흰 칩(없으면 생략)
        nf = F(52, "ExtraBold"); nb = d.textbbox((0, 0), T["number_sub"], font=nf)
        x0, y0 = 60 + num.width - 10, 108 + num.height - 150
        if x0 + nb[2] + 40 > W2: x0, y0 = 60, 108 + num.height - 12
        d.rounded_rectangle((x0 - 18, y0 - 10, x0 + nb[2] - nb[0] + 18, y0 + nb[3] - nb[1] + 22), radius=14, fill=(255, 255, 255))
        d.text((x0, y0), T["number_sub"], font=nf, fill=(17, 17, 17))
    main = _skew_text((W2 + 100, 240), T["main"], _fit(T["main"], 150, 1180, stroke=11), (255, 255, 255), 11, (10, 12, 18))
    im.alpha_composite(main, (20, H2 - main.height - 14))
    bf = F(34, "ExtraBold"); l, t_, r, b = d.textbbox((0, 0), T["badge"], font=bf); bw = r - l + 44
    d = ImageDraw.Draw(im); d.rounded_rectangle((W2 - bw - 24, 22, W2 - 24, 22 + b - t_ + 26), radius=12, fill=accent, outline=(255, 255, 255), width=3)
    d.text((W2 - bw - 24 + 22, 22 + 11), T["badge"], font=bf, fill=(255, 255, 255))
    return im.convert("RGB")


def thumbnail_checklist(photo, T, accent):
    """D. 체크리스트형 썸네일 (1280x720, v2.3.0): 오른쪽 사진 + 왼쪽 큰 2줄 제목 + 체크 3줄 + 빨간 원형 스탬프"""
    W2, H2 = 1280, 720; red, yellow = (226, 59, 46), (255, 214, 64)
    im = _cover(photo, W2, H2).convert("RGBA")
    sh = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for x in range(W2):
        a = int(230 * max(0, 1 - x / (W2 * 0.78)) ** 0.9) + 15; sd.line((x, 0, x, H2), fill=(6, 10, 20, a))
    im = Image.alpha_composite(im, sh); d = ImageDraw.Draw(im)
    tf = F(40, "ExtraBold"); tb = d.textbbox((0, 0), T["top"], font=tf)
    d.rounded_rectangle((40, 28, 40 + tb[2] - tb[0] + 40, 28 + tb[3] - tb[1] + 26), radius=12, fill=red)
    d.text((60, 38), T["top"], font=tf, fill=(255, 255, 255))
    l1 = _skew_text((W2, 220), T["line1"], _fit(T["line1"], 170, 800, stroke=11), (255, 255, 255), 11, (10, 12, 18), sh=0.08)
    l2 = _skew_text((W2, 220), T["line2"], _fit(T["line2"], 150, 860, stroke=11), yellow, 11, (10, 12, 18), sh=0.08)
    im.alpha_composite(l1, (24, 88)); im.alpha_composite(l2, (24, 88 + l1.height - 14))
    d = ImageDraw.Draw(im); y = 88 + l1.height + l2.height + 2
    cf = _fit(max(T["checks"], key=len), 50, 720, weight="ExtraBold", stroke=0, minsize=34)
    for c in T["checks"][:3]:
        d.rounded_rectangle((44, y, 44 + 58, y + 58), radius=12, fill=accent)
        d.line((56, y + 30, 70, y + 44, 92, y + 15), fill=(255, 255, 255), width=8)
        d.text((122, y + 2), c, font=cf, fill=(255, 255, 255), stroke_width=4, stroke_fill=(10, 12, 18)); y += 74
    st = Image.new("RGBA", (240, 240), (0, 0, 0, 0)); sdr = ImageDraw.Draw(st)
    sdr.ellipse((8, 8, 232, 232), fill=red, outline=(255, 255, 255), width=8)
    center_text(sdr, (120, 96), T["stamp1"], F(48, "ExtraBold"), (255, 255, 255)); center_text(sdr, (120, 150), T["stamp2"], F(38, "Bold"), (255, 255, 255))
    st = st.rotate(-12, resample=Image.BICUBIC); im.alpha_composite(st, (W2 - 280, H2 - 290))
    return im.convert("RGB")


DOWN_C, UP_C = (47, 111, 219), (217, 72, 59)  # v2.4.0 시세: 하락 파랑, 상승 빨강 (CVD 검증 통과, 화살표·부호로 이중 표기)


def movers_chart(items, title, sub, accent):
    """주간 시세 '한눈에' 카드: 가운데 0선 기준 좌우로 뻗는 막대(하락 왼쪽 파랑, 상승 오른쪽 빨강) + 품목명 + 변동률"""
    img = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    # 좌상단 라벨(≈y130까지)과 하단 자막(≈y900 아래)을 피해 가운데 영역에만 그린다
    center_text(d, (W / 2, 190), title, F(56, "ExtraBold"), (17, 17, 17))
    if sub: pill(d, W / 2, 262, sub, F(30, "Bold"))
    n = len(items); top, bot = 320, 860; rh = (bot - top) / max(n, 1); bh = min(48, rh * 0.62)
    cx = W / 2 + 120; half = 620; mx = max(abs(x["change"]) for x in items) or 1
    d.line((cx, top - 10, cx, bot), fill=(200, 203, 208), width=3)
    for i, it in enumerate(items):
        y = top + i * rh + rh / 2; v = it["change"]; L = max(6, half * abs(v) / mx)
        col = DOWN_C if v < 0 else UP_C
        x0, x1 = (cx - L, cx - 1) if v < 0 else (cx + 1, cx + L)
        d.rounded_rectangle((x0, y - bh / 2, x1, y + bh / 2), radius=4, fill=col)
        lab = f"{'▼' if v < 0 else '▲'} {abs(v):.0f}%"; lf = F(40, "ExtraBold"); lb = d.textbbox((0, 0), lab, font=lf)
        lx = x0 - (lb[2] - lb[0]) - 16 if v < 0 else x1 + 16
        d.text((lx, y - (lb[3] - lb[1]) / 2 - lb[1]), lab, font=lf, fill=(17, 17, 17))
        nf = F(40, "ExtraBold"); nb = d.textbbox((0, 0), it["name"], font=nf)
        nx = 90; d.text((nx, y - (nb[3] - nb[1]) / 2 - nb[1]), it["name"], font=nf, fill=(17, 17, 17))
        if it.get("note"): d.text((nx + 190, y - 12), it["note"], font=F(24, "SemiBold"), fill=(120, 125, 130))
    ft = "노량진수산 경락시세(도매) · kg 경매 수량 가중 중앙값 · 지난주 대비"; ff = F(24, "SemiBold")
    d.text((W - 80 - d.textbbox((0, 0), ft, font=ff)[2], 870), ft, font=ff, fill=(130, 135, 140))
    return img


def thumbnail_weekly(photo, T, accent):
    """E. 주간 시세 리포트형 썸네일(시리즈 고정 틀, v2.4.0): 회차 배지 + 아주 큰 품목명 + 큰 변동률(파랑/빨강) + 시리즈 제목 띠 + 기간 칩.
    시리즈는 틀을 고정해 한눈에 알아보게 하고, 매주 사진·품목·숫자만 바뀐다."""
    W2, H2 = 1280, 720; yellow = (255, 214, 64)
    im = _cover(photo, W2, H2).convert("RGBA")
    sh = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for x in range(W2):
        a = int(215 * max(0, 1 - x / (W2 * 0.8)) ** 1.0) + 20; sd.line((x, 0, x, H2), fill=(4, 10, 22, a))
    im = Image.alpha_composite(im, sh); d = ImageDraw.Draw(im)
    bf = F(40, "ExtraBold"); bb = d.textbbox((0, 0), T["badge"], font=bf)
    d.rounded_rectangle((36, 30, 36 + bb[2] - bb[0] + 44, 30 + bb[3] - bb[1] + 28), radius=12, fill=accent)
    d.text((58, 42), T["badge"], font=bf, fill=(255, 255, 255))
    df = F(32, "Bold"); db = d.textbbox((0, 0), T["dates"], font=df)
    d.rounded_rectangle((W2 - (db[2] - db[0]) - 80, 34, W2 - 36, 34 + db[3] - db[1] + 26), radius=12, fill=(255, 255, 255))
    d.text((W2 - (db[2] - db[0]) - 58, 46), T["dates"], font=df, fill=(17, 17, 17))
    nm = _skew_text((W2, 300), T["item"], _fit(T["item"], 210, 760, stroke=12, minsize=120), (255, 255, 255), 12, (10, 12, 18), sh=0.07)
    im.alpha_composite(nm, (24, 110))
    col = DOWN_C if T.get("trend", "down") == "down" else UP_C
    pct = _skew_text((W2, 300), T["pct"], _fit(T["pct"], 230, 900, stroke=12, minsize=120), col, 12, (255, 255, 255), sh=0.07)
    im.alpha_composite(pct, (24, 100 + nm.height - 10))
    d = ImageDraw.Draw(im); d.rectangle((0, H2 - 112, W2, H2), fill=(14, 20, 32))
    tf = _fit(T["title"], 70, W2 - 80, stroke=0)
    center_text(d, (W2 / 2, H2 - 56), T["title"], tf, yellow)
    return im.convert("RGB")


# ---------- v2.5.0 손글씨·스티커 팝 썸네일 (주간 시세 시리즈) ----------
FX_URLS = {"BlackHanSans": "blackhansans/BlackHanSans-Regular.ttf", "NanumPen": "nanumpenscript/NanumPenScript-Regular.ttf",
           "Gaegu": "gaegu/Gaegu-Bold.ttf", "Jua": "jua/Jua-Regular.ttf"}  # 모두 SIL OFL (Google Fonts)


def FX(name, size):
    path = os.path.join(FONT_DIR, os.path.basename(FX_URLS[name]))
    if not os.path.exists(path):
        os.makedirs(FONT_DIR, exist_ok=True)
        subprocess.run(["curl", "-sL", "-m", "120", "-o", path, "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/" + FX_URLS[name]], check=True)
    return ImageFont.truetype(path, size)


def _brush(size, color, seed=1):
    """붓으로 칠한 듯한 띠(가장자리가 들쭉날쭉한 다각형)"""
    import random
    r = random.Random(seed); w, h = size; img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    top = [(x, r.uniform(0, h * 0.18)) for x in range(0, w + 1, 18)]; bot = [(x, h - r.uniform(0, h * 0.18)) for x in range(w, -1, -18)]
    left = [(r.uniform(0, 26), y) for y in range(h, 0, -h // 5)]
    d.polygon(top + bot + left, fill=color)
    return img.filter(ImageFilter.GaussianBlur(0.8))


def _rot_paste(base, layer, xy, angle, shadow=True):
    lay = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    if shadow:
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda a: int(a * 0.45)))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (xy[0] + 8, xy[1] + 10))
    base.alpha_composite(lay, xy)


def _fish_doodle(size, color=(255, 255, 255, 255), width=5):
    w, h = size; img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.ellipse((w * 0.05, h * 0.2, w * 0.72, h * 0.8), outline=color, width=width)
    d.polygon([(w * 0.70, h * 0.5), (w * 0.97, h * 0.18), (w * 0.97, h * 0.82)], outline=color, width=width)
    d.ellipse((w * 0.17, h * 0.4, w * 0.25, h * 0.52), fill=color)
    for k in range(3): d.arc((w * (0.30 + k * 0.1), h * 0.3, w * (0.42 + k * 0.1), h * 0.7), 300, 60, fill=color, width=max(2, width - 2))
    return img


def _splash(size, color=(70, 170, 235, 235)):
    w, h = size; img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for (cx, cy, r, ang) in ((0.5, 0.75, 0.16, 0), (0.25, 0.45, 0.10, -30), (0.75, 0.4, 0.11, 30), (0.5, 0.25, 0.08, 0)):
        x, y, rr = cx * w, cy * h, r * w
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=color); d.polygon([(x - rr * 0.8, y - rr * 0.4), (x + rr * 0.8, y - rr * 0.4), (x, y - rr * 2.4)], fill=color)
    d.ellipse((w * 0.44, h * 0.68, w * 0.5, h * 0.74), fill=(255, 255, 255, 220))
    return img


def _sticky(lines, size, bg, fg, accent=None, font="NanumPen", fs=58, tape=True):
    w, h = size; img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=10, fill=bg)
    if tape: d.rectangle((w * 0.32, -2, w * 0.68, 22), fill=(255, 255, 255, 150))
    y = (h - len(lines) * fs * 0.95) / 2
    for i, ln in enumerate(lines):
        col = accent if (accent and i == len(lines) - 1) else fg
        f = FX(font, fs); l, t_, r, b = d.textbbox((0, 0), ln, font=f)
        d.text(((w - (r - l)) / 2 - l, y), ln, font=f, fill=col); y += fs * 0.95
    return img


def thumbnail_weekly_pop(photo, T, accent):
    """주간 시세 리포트 썸네일 v2.5.0 — 손글씨·스티커 팝 스타일(사용자 참고 썸네일 반영).
    시장 사진 배경 + 왼쪽 위 날짜 메모지 + 파란 '노량진수산시장' 간판 + 가운데 큰 붓글씨 제목 2줄 + 손글씨 스티커 3장 + 물방울·물고기 낙서"""
    W2, H2 = 1280, 720
    from PIL import ImageEnhance
    bg = ImageEnhance.Color(_cover(photo, W2, H2)).enhance(1.25)
    bg = ImageEnhance.Brightness(bg).enhance(0.78).convert("RGBA")
    vg = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); vd = ImageDraw.Draw(vg)
    for i in range(60): vd.rectangle((i * 4, i * 3, W2 - i * 4, H2 - i * 3), outline=(0, 0, 0, max(0, 120 - i * 2)), width=4)
    im = Image.alpha_composite(bg, vg.filter(ImageFilter.GaussianBlur(20)))
    navy, orange, sky = (16, 32, 72), (255, 152, 28), (150, 215, 255)
    # 날짜 메모지 (왼쪽 위)
    note = Image.new("RGBA", (420, 280), (0, 0, 0, 0)); nd = ImageDraw.Draw(note)
    nd.rectangle((0, 18, 419, 279), fill=(250, 244, 222))
    for x in range(30, 400, 34): nd.ellipse((x, 6, x + 14, 30), outline=(60, 60, 60), width=4)  # 스프링
    hl = _brush((330, 46), (255, 222, 60, 210), seed=3); note.alpha_composite(hl, (40, 150))
    f1 = FX("BlackHanSans", 112); nd.text((36, 40), T["date1"], font=f1, fill=(24, 60, 32))
    f2 = FX("Gaegu", 60); nd.text((70, 178), T["date2"], font=f2, fill=(24, 24, 24))
    nd.arc((330, 190, 380, 240), 20, 160, fill=(24, 24, 24), width=5); nd.ellipse((342, 198, 350, 206), fill=(24, 24, 24)); nd.ellipse((360, 198, 368, 206), fill=(24, 24, 24))
    for k, (x0, y0, x1, y1) in enumerate(((18, 70, 0, 52), (22, 110, -4, 110), (18, 150, 0, 168))): nd.line((x0, y0, x1 + 4, y1), fill=(255, 196, 40), width=6)
    _rot_paste(im, note, (18, 4), 4)
    clip = Image.new("RGBA", (90, 60), (0, 0, 0, 0)); ImageDraw.Draw(clip).rounded_rectangle((0, 10, 89, 50), radius=6, fill=(30, 30, 30)); _rot_paste(im, clip, (150, 0), 4, shadow=False)
    if T.get("badge"):
        bd_ = Image.new("RGBA", (96, 96), (0, 0, 0, 0)); bdd = ImageDraw.Draw(bd_)  # 빨간 원형 회차 스티커(메모지 오른쪽 아래 모서리)
        bdd.ellipse((2, 2, 93, 93), fill=(226, 59, 46), outline=(255, 255, 255), width=5)
        bf = FX("BlackHanSans", 44); bb = bdd.textbbox((0, 0), T["badge"], font=bf); bdd.text(((96 - bb[2] - bb[0]) / 2, (96 - bb[3] - bb[1]) / 2), T["badge"], font=bf, fill=(255, 255, 255))
        _rot_paste(im, bd_, (392, 150), -10)
    # 파란 간판 (위 가운데)
    sign = Image.new("RGBA", (500, 140), (0, 0, 0, 0)); sd = ImageDraw.Draw(sign)
    sd.rounded_rectangle((0, 0, 499, 139), radius=16, fill=(20, 60, 160), outline=(120, 190, 255), width=5)
    sf = FX("BlackHanSans", 62); l, t_, r, b = sd.textbbox((0, 0), T["sign"], font=sf); sd.text(((500 - r) / 2 + 30, 14), T["sign"], font=sf, fill=(255, 255, 255))
    sign.alpha_composite(_fish_doodle((70, 40), (255, 255, 255, 255), 4), (22, 26))
    ef = F(26, "Bold"); l, t_, r, b = sd.textbbox((0, 0), T.get("sign_en", "Noryangjin Fish Market"), font=ef); sd.text(((500 - r) / 2, 96), T.get("sign_en", "Noryangjin Fish Market"), font=ef, fill=(220, 235, 255))
    glow = sign.filter(ImageFilter.GaussianBlur(14)); im.alpha_composite(glow, (480, 22)); _rot_paste(im, sign, (480, 22), 0)
    # 가운데 큰 제목 1줄 (흰 붓 띠 위 남색)
    t1f = _fit_font("BlackHanSans", T["title1"], 150, 900)
    l, t_, r, b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), T["title1"], font=t1f)
    band = _brush((r - l + 120, b - t_ + 70), (215, 236, 255, 245), seed=7)
    lay = Image.new("RGBA", (band.width, band.height), (0, 0, 0, 0)); lay.alpha_composite(band)
    ld = ImageDraw.Draw(lay); ld.text((60 - l, 35 - t_), T["title1"], font=t1f, fill=navy, stroke_width=4, stroke_fill=(255, 255, 255))
    _rot_paste(im, lay, ((W2 - lay.width) // 2 + 40, 228), -3)
    # 가운데 큰 제목 2줄 (주황 + 하늘, 굵은 검정 외곽선)
    t2f = _fit_font("BlackHanSans", T["title2a"] + T["title2b"], 190, 760)
    lay2 = Image.new("RGBA", (1100, 300), (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay2)
    d2.text((30, 20), T["title2a"], font=t2f, fill=orange, stroke_width=14, stroke_fill=(14, 14, 20))
    wa = d2.textbbox((30, 20), T["title2a"], font=t2f)[2]
    d2.text((wa + 24, 20), T["title2b"], font=t2f, fill=sky, stroke_width=14, stroke_fill=(14, 14, 20))
    lay2 = lay2.crop(lay2.getbbox()); _rot_paste(im, lay2, ((W2 - lay2.width) // 2 + 40, 412), -3)
    # 물방울·물고기 낙서
    im.alpha_composite(_splash((110, 140)), (250, 560)); im.alpha_composite(_splash((100, 130)).transpose(Image.FLIP_LEFT_RIGHT), (1165, 290))
    for (x, y, w_, h_) in ((1050, 440, 120, 64), (110, 610, 110, 60)): im.alpha_composite(_fish_doodle((w_, h_)), (x, y))
    # 손글씨 스티커 3장
    _rot_paste(im, _sticky(T["sticker1"], (250, 190), (255, 238, 90, 255), (20, 20, 20), (226, 59, 46), fs=56), (1012, 40), -6)
    _rot_paste(im, _sticky(T["sticker2"], (230, 170), (34, 34, 38, 240), (255, 255, 255), (255, 214, 64), fs=52, tape=False), (14, 330), 7)
    _rot_paste(im, _sticky(T["sticker3"], (260, 170), (36, 120, 64, 245), (255, 255, 255), (255, 226, 90), fs=52), (1000, 520), 6)
    return im.convert("RGB")


def _fit_font(name, text, size, maxw):
    while size > 60:
        f = FX(name, size); l, t_, r, b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=f, stroke_width=10)
        if r - l <= maxw: return f
        size -= 6
    return FX(name, size)


def checklist_card(c, accent):
    """v2.6.0 목록형 정보 카드: 제목 + 체크 항목 3~6줄 (유입 '이 영상을 보면', 마지막 '체크리스트' 등)"""
    img = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    center_text(d, (W / 2, 200), c["title"], F(64, "ExtraBold"), (17, 17, 17))
    if c.get("tag"): pill(d, W / 2, 285, c["tag"], F(32, "Bold"))
    items = c["items"]; n = len(items); top = 360; gap = min(110, (860 - top) / max(n, 1))
    f = F(50 if n <= 4 else 44, "ExtraBold")
    tw = max(d.textbbox((0, 0), t, font=f)[2] for t in items); x0 = (W - (tw + 96)) / 2  # 목록 덩어리를 가운데로
    for i, t in enumerate(items):
        y = top + i * gap
        d.rounded_rectangle((x0, y, x0 + 64, y + 64), radius=14, fill=accent)
        d.line((x0 + 14, y + 33, x0 + 28, y + 48, x0 + 52, y + 16), fill=(255, 255, 255), width=8)
        d.text((x0 + 96, y + 32), t, font=f, fill=(17, 17, 17), anchor="lm")
    return img


def _caution_tape(w, h=64):
    t = Image.new("RGBA", (w + 200, h), (255, 205, 0, 255)); d = ImageDraw.Draw(t)
    for x in range(-h, w + 200, 72): d.polygon([(x, h), (x + 36, h), (x + 36 + h, 0), (x + h, 0)], fill=(20, 20, 20, 255))
    return t


def thumbnail_alert(photo, T, accent):
    """G. 경고 테이프형 썸네일(v2.6.0, '안 당하는 법'·고발형 주제): 위아래 노랑·검정 경고 테이프 + 빨간 라벨 + 아주 큰 2줄 제목 + 수법 칩 + 빨간 원형 스탬프"""
    W2, H2 = 1280, 720; red, yellow = (226, 59, 46), (255, 214, 64)
    from PIL import ImageEnhance
    im = ImageEnhance.Color(_cover(photo, W2, H2)).enhance(0.8); im = ImageEnhance.Brightness(im).enhance(0.55).convert("RGBA")
    sh = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for x in range(W2): sd.line((x, 0, x, H2), fill=(0, 0, 0, int(140 * max(0, 1 - x / (W2 * 0.9)))))
    im = Image.alpha_composite(im, sh)
    tp = _caution_tape(W2); _rot_paste(im, tp, (-100, -6), -2)
    lab = Image.new("RGBA", (W2, 140), (0, 0, 0, 0)); ld = ImageDraw.Draw(lab)
    lf = _fit_font("BlackHanSans", T["top"], 78, 1000); lb = ld.textbbox((0, 0), T["top"], font=lf)
    ld.rounded_rectangle((0, 0, lb[2] - lb[0] + 56, lb[3] - lb[1] + 40), radius=14, fill=red)
    ld.text((28 - lb[0], 20 - lb[1]), T["top"], font=lf, fill=(255, 255, 255)); lab = lab.crop(lab.getbbox())
    _rot_paste(im, lab, (40, 92), 2)
    m1 = Image.new("RGBA", (W2 + 200, 280), (0, 0, 0, 0)); d1 = ImageDraw.Draw(m1)
    f1 = _fit_font("BlackHanSans", T["main1"] + " " + T["main2"], 230, 1180)
    d1.text((20, 20), T["main1"], font=f1, fill=(255, 255, 255), stroke_width=12, stroke_fill=(10, 10, 14))
    wa = d1.textbbox((20, 20), T["main1"] + " ", font=f1)[2]
    d1.text((wa, 20), T["main2"], font=f1, fill=yellow, stroke_width=12, stroke_fill=(10, 10, 14))
    m1 = m1.crop(m1.getbbox()); _rot_paste(im, m1, (34, 228), -2)
    # 수법 칩
    d = ImageDraw.Draw(im); cf = FX("BlackHanSans", 40); x = 44; y = 520
    for k, c in enumerate(T["chips"]):
        b = d.textbbox((0, 0), c, font=cf); w = b[2] - b[0] + 40
        if x + w > W2 - 260: x = 44; y += 70
        d.rounded_rectangle((x, y, x + w, y + 58), radius=12, fill=(18, 18, 22), outline=red, width=4)
        d.text((x + 20 - b[0], y + 29), c, font=cf, fill=(255, 255, 255), anchor="lm"); x += w + 14
    tp2 = _caution_tape(W2); _rot_paste(im, tp2, (-100, H2 - 70), 1)
    st = Image.new("RGBA", (260, 260), (0, 0, 0, 0)); sdr = ImageDraw.Draw(st)
    sdr.ellipse((8, 8, 252, 252), fill=red, outline=(255, 255, 255), width=9)
    center_text(sdr, (130, 108), T["stamp1"], FX("BlackHanSans", 66), (255, 255, 255)); center_text(sdr, (130, 170), T["stamp2"], FX("BlackHanSans", 36), (255, 236, 160))
    _rot_paste(im, st, (W2 - 300, 400), -12)
    return im.convert("RGB")


def main(data_path, out, img_dir=None):
    D = json.load(open(data_path, encoding="utf-8"))
    G = D["graphics"]
    acc, acc2 = hexrgb(G.get("accent", "#19C37D")), hexrgb(G.get("accent2", "#0EA5B7"))
    root = os.path.join(out, "07_그래픽")
    dirs = {k: os.path.join(root, k) for k in ("01_챕터카드", "02_상단라벨", "03_순위배지", "04_정보카드", "05_요약카드", "06_엔드카드", "07_썸네일틀", "08_타이틀카드")}
    for p in dirs.values(): os.makedirs(p, exist_ok=True)
    n = 0
    for i, s in enumerate(D["sections"]):
        label = s.get("label", s["name"])
        title = s.get("card_title", label)
        chapter_card(title, acc, acc2, s.get("card_sub")).save(f"{dirs['01_챕터카드']}/{i:02d}_{s['name']}.png"); n += 1
        top_label(label).save(f"{dirs['02_상단라벨']}/{i:02d}_{s['name']}.png"); n += 1
        if s.get("rank"):
            rank_badge(s["rank"], acc).save(f"{dirs['03_순위배지']}/{s['rank']:02d}위.png"); n += 1
        if (s.get("rank") or s.get("chapter")) and img_dir and s.get("title_image"):  # v2.3.0: chapter 섹션도 타이틀 카드
            nm = s.get("card_name") or (s["name"].split(" ", 1)[1] if " " in s["name"] else s["name"])
            title_card(os.path.join(img_dir, s["title_image"] + ".jpg"), s.get("rank"), nm, s.get("tagline"), acc, s.get("chapter")).save(f"{dirs['08_타이틀카드']}/{i:02d}_{s['name']}.png"); n += 1
    for j, c in enumerate(G.get("info_cards", []), 1):
        out_ = f"{dirs['04_정보카드']}/{j:02d}_{c['section']}.png"
        if c.get("kind") == "movers": movers_chart(G["movers_items"], c["title"], c.get("sub"), acc).save(out_)  # v2.4.0 시세 막대 카드
        elif c.get("kind") == "checklist": checklist_card(c, acc).save(out_)  # v2.6.0 목록 카드
        else: info_card(c, acc).save(out_)
        n += 1
    items = [tuple(x) for x in G["summary"]]
    for k in range(0, len(items) + 1):
        summary_cards(items, k, acc, G.get("summary_title")).save(f"{dirs['05_요약카드']}/{k:02d}.png"); n += 1
    end_card(G.get("channel_name", "채널명")).save(f"{dirs['06_엔드카드']}/엔드카드.png"); n += 1
    for t, lines in enumerate(G.get("thumbnail_lines", []), 1):
        thumb_frame(lines, G.get("thumbnail_badge", "TOP10"), acc).save(f"{dirs['07_썸네일틀']}/썸네일_{t}안.png"); n += 1
    TV = G.get("thumbnail_versus")
    if TV and img_dir:
        thumbnail_versus(os.path.join(img_dir, TV["left_image"] + ".jpg"), os.path.join(img_dir, TV["right_image"] + ".jpg"), TV, acc).save(f"{dirs['07_썸네일틀']}/썸네일_VS.png"); n += 1
    TB = G.get("thumbnail_bold")
    if TB and img_dir:
        thumbnail_bold(os.path.join(img_dir, TB["image"] + ".jpg"), TB, acc).save(f"{dirs['07_썸네일틀']}/썸네일_임팩트.png"); n += 1
    TN = G.get("thumbnail_number")  # v2.3.0 C. 큰 숫자형
    if TN and img_dir and TN.get("image"):
        thumbnail_number(os.path.join(img_dir, TN["image"] + ".jpg"), TN, acc).save(f"{dirs['07_썸네일틀']}/썸네일_숫자.png"); n += 1
    TC = G.get("thumbnail_checklist")  # v2.3.0 D. 체크리스트형
    if TC and img_dir and TC.get("image"):
        thumbnail_checklist(os.path.join(img_dir, TC["image"] + ".jpg"), TC, acc).save(f"{dirs['07_썸네일틀']}/썸네일_체크리스트.png"); n += 1
    MV = G.get("movers")  # v2.4.0 주간 시세 '한눈에' 막대 카드 → 04_정보카드/00_한눈에.png
    if MV:
        movers_chart(MV["items"], MV["title"], MV.get("sub"), acc).save(f"{dirs['04_정보카드']}/00_한눈에.png"); n += 1
    TA = G.get("thumbnail_alert")  # v2.6.0 G. 경고 테이프형
    if TA and img_dir and TA.get("image"):
        thumbnail_alert(os.path.join(img_dir, TA["image"] + ".jpg"), TA, acc).save(f"{dirs['07_썸네일틀']}/썸네일_경고.png"); n += 1
    TP = G.get("thumbnail_weekly_pop")  # v2.5.0 주간 시세 시리즈 썸네일(손글씨·스티커 팝)
    if TP and img_dir and TP.get("image"):
        thumbnail_weekly_pop(os.path.join(img_dir, TP["image"] + ".jpg"), TP, acc).save(f"{dirs['07_썸네일틀']}/썸네일_주간시세.png"); n += 1
    TW = None if TP else G.get("thumbnail_weekly")  # v2.4.0 E. 주간 시세 리포트형(이전 틀)
    if TW and img_dir and TW.get("image"):
        thumbnail_weekly(os.path.join(img_dir, TW["image"] + ".jpg"), TW, acc).save(f"{dirs['07_썸네일틀']}/썸네일_주간시세.png"); n += 1
    print(f"그래픽 {n}장 생성 → {root}")


if __name__ == "__main__":
    a = sys.argv[1:]; img = None
    if "--img" in a: k = a.index("--img"); img = a[k + 1]; a = a[:k] + a[k + 2:]
    main(a[0], a[1], img)
