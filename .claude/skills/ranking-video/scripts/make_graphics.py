# -*- coding: utf-8 -*-
"""랭킹 영상 그래픽 생성기 (ranking-video 스킬 v1.3.0) — '클린 미니멀' 스타일

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


def title_card(photo, rank, name, tagline, accent):
    """순위 타이틀 카드: 사진 전면 + 왼쪽 아래 어두운 그라데이션 + 큰 점포명 (PPT 표지 느낌)"""
    im = Image.open(photo).convert("RGB")
    sc = max(W / im.width, H / im.height); im = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((x0, y0, x0 + W, y0 + H)).convert("RGBA")
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = int(200 * max(0, (y - H * 0.35) / (H * 0.65)) ** 1.3); gd.line((0, y, W, y), fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, g); d = ImageDraw.Draw(im)
    pill(d, 210, 640, f"{rank}위", F(64, "ExtraBold"), bg=accent, fg=(255, 255, 255), padx=38, pady=14)
    d.text((120, 700), name, font=F(190, "ExtraBold"), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
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
    center_text(d, (W / 2, 530), c["big"], F(150 if len(c["big"]) <= 7 else 110, "ExtraBold"), (17, 17, 17))
    if c.get("caption"): center_text(d, (W / 2, 680), c["caption"], F(40, "SemiBold"), (110, 115, 120))
    d.rounded_rectangle((W / 2 - 60, 790, W / 2 + 60, 800), radius=5, fill=accent)
    return img


def summary_cards(items, upto, accent):
    """items: [(번호, 이름)] — upto개까지 채운 요약 카드"""
    img = Image.new("RGB", (W, H), (255, 255, 255)); d = ImageDraw.Draw(img)
    d.text((40, 30), "오늘의 요약", font=F(44, "ExtraBold"), fill=(255, 255, 255), stroke_width=5, stroke_fill=(20, 20, 20))
    title = items[upto - 1][1] if upto else "TOP10 한눈에"
    center_text(d, (W / 2, 150), title if upto < len(items) else f"TOP{len(items)} 한눈에", F(54, "ExtraBold"), (17, 17, 17))
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
            if img_dir and s.get("title_image"):
                nm = s["name"].split(" ", 1)[1] if " " in s["name"] else s["name"]
                title_card(os.path.join(img_dir, s["title_image"] + ".jpg"), s["rank"], nm, s.get("tagline"), acc).save(f"{dirs['08_타이틀카드']}/{i:02d}_{s['name']}.png"); n += 1
    for j, c in enumerate(G.get("info_cards", []), 1):
        info_card(c, acc).save(f"{dirs['04_정보카드']}/{j:02d}_{c['section']}.png"); n += 1
    items = [tuple(x) for x in G["summary"]]
    for k in range(0, len(items) + 1):
        summary_cards(items, k, acc).save(f"{dirs['05_요약카드']}/{k:02d}.png"); n += 1
    end_card(G.get("channel_name", "채널명")).save(f"{dirs['06_엔드카드']}/엔드카드.png"); n += 1
    for t, lines in enumerate(G.get("thumbnail_lines", []), 1):
        thumb_frame(lines, G.get("thumbnail_badge", "TOP10"), acc).save(f"{dirs['07_썸네일틀']}/썸네일_{t}안.png"); n += 1
    print(f"그래픽 {n}장 생성 → {root}")


if __name__ == "__main__":
    a = sys.argv[1:]; img = None
    if "--img" in a: k = a.index("--img"); img = a[k + 1]; a = a[:k] + a[k + 2:]
    main(a[0], a[1], img)
