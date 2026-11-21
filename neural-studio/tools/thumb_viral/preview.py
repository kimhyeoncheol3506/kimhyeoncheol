"""유튜브 화면 크기별 썸네일 미리보기 판 (Thumbnail Tester 역할, 무료·API 없음).
  python3 tools/thumb_viral/preview.py 출력.jpg 썸네일1.png:제목1 썸네일2.png:제목2 ...
가로줄마다 한 시안: PC 홈(360×202) · PC 오른쪽 추천(168×94) · 휴대폰 피드(358×201, 실제 폰 화면 비율로 축소) · 검색 결과(246×138). 다크 모드 배경."""
import sys, os
from PIL import Image, ImageDraw, ImageFont
NS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
F = lambda s: ImageFont.truetype(os.path.join(NS, "assets", "fonts", "Pretendard-SemiBold.otf"), s)
out, items = sys.argv[1], [a.split(":", 1) for a in sys.argv[2:]]
S = 2   # 2배로 그려 또렷하게
cols = [("PC 홈", 360, 202), ("PC 추천(옆)", 168, 94), ("휴대폰 피드", 358, 201), ("검색 결과", 246, 138)]
W = sum(c[1] for c in cols) * S + 60 * S * len(cols); H = (60 + len(items) * 300) * S
im = Image.new("RGB", (W, H), "#0f0f0f"); d = ImageDraw.Draw(im)
x = 30 * S
for name, w, h in cols:
    d.text((x, 18 * S), name, fill="#aaaaaa", font=F(16 * S))
    for r, (path, title) in enumerate(items):
        y = (60 + r * 300) * S
        t = Image.open(path).convert("RGB").resize((w * S, h * S), Image.LANCZOS)
        mask = Image.new("L", t.size, 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, t.size[0] - 1, t.size[1] - 1], 12 * S, fill=255)
        im.paste(t, (x, y), mask)
        tf = F(14 * S if w > 200 else 11 * S); words, line, lines = title, "", []
        for ch in words:
            if d.textlength(line + ch, font=tf) > w * S: lines.append(line); line = ch
            else: line += ch
        lines.append(line)
        for i, ln in enumerate(lines[:2]): d.text((x, y + h * S + (8 + i * 20) * S), ln, fill="#f1f1f1", font=tf)
        d.text((x, y + h * S + 50 * S), "월급쟁이 재테크 · 조회수 —", fill="#aaaaaa", font=F(11 * S))
    x += (w + 60) * S
im = im.resize((W // 2, H // 2), Image.LANCZOS); im.save(out, quality=90); print(out)
