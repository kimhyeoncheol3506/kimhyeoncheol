#!/usr/bin/env python3
"""CEO 몰아보기 재료: 편별 3초 연결 화면(1920x1080) + 콜라주 썸네일(1280x720, B안 형식: 큰 CI 여러 개 + 시네마틱 배경 + 큰 숫자).
python3 neural-studio/tools/ceo_compilation_assets.py <출력폴더> <썸네일.png>"""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
R = '/home/user/kimhyeoncheol'
EPS = [(1, '삼성전자', 'samsung'), (2, '삼양식품', 'samyang'), (3, '에스엠', 'sm'), (4, 'SK하이닉스', 'skhynix'), (5, '셀트리온', 'celltrion'),
       (6, '네이버', 'naver'), (7, '농심', 'nongshim'), (8, '크래프톤', 'krafton'), (9, '아모레퍼시픽', 'amore'), (10, '한화에어로스페이스', 'hanwhaaero')]
BH = f'{R}/neural-studio/assets/fonts/BlackHanSans.ttf'; PB = f'{R}/neural-studio/assets/fonts/Pretendard-Bold.otf'
out, thumb = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
# SK하이닉스는 공식 CI가 흰색 SVG뿐 → 크게 변환해 어두운 칸에 얹는다
SKW = f'{out}/skw.png'
DARK = {'skhynix': (34, 34, 38, 255)}
def ci(name, box):
    im = Image.open(SKW if name == 'skhynix' else f'{R}/neural-studio/assets/ci/{name}_ci.png').convert('RGBA'); im.thumbnail(box, Image.LANCZOS); return im
def text_c(d, xy, t, f, fill, stroke=0):
    w = d.textlength(t, font=f); d.text((xy[0] - w / 2, xy[1]), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))
# 1) 연결 화면: 그 편 썸네일을 흐리게 깔고, 가운데 흰 상자에 CI + "N편 · 회사"
for n, name, key in EPS:
    src = subprocess.check_output(['git', '-C', R, 'show', f'HEAD:release_upload/ceo/ep{n}/thumb.png'])
    open(f'{out}/_t.png', 'wb').write(src)
    bg = Image.open(f'{out}/_t.png').convert('RGB').resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))
    bg = ImageEnhance.Brightness(bg).enhance(0.35).convert('RGBA'); d = ImageDraw.Draw(bg)
    d.rounded_rectangle((560, 250, 1360, 650), 36, fill=DARK.get(key, (255, 255, 255, 245)))
    logo = ci(key, (640, 300)); bg.alpha_composite(logo, (960 - logo.width // 2, 450 - logo.height // 2))
    text_c(d, (960, 700), f'{n}편', ImageFont.truetype(BH, 90), (255, 213, 64), 6)
    text_c(d, (960, 810), name, ImageFont.truetype(BH, 120), (255, 255, 255), 8)
    bg.convert('RGB').save(f'{out}/card{n:02d}.png')
os.remove(f'{out}/_t.png')
# 2) 썸네일: 시네마틱 배경 + CI 10개 격자 + 큰 숫자
bg = Image.open(f'{R}/neural-studio/assets/thumb_bg/B_rebound.png').convert('RGB').resize((1280, 720), Image.LANCZOS)
bg = ImageEnhance.Brightness(bg).enhance(0.55).convert('RGBA'); d = ImageDraw.Draw(bg)
W, H, gx, gy, x0, y0 = 220, 96, 14, 14, 30, 28
for i, (n, name, key) in enumerate(EPS):
    x = x0 + (i % 5) * (W + gx); y = y0 + (i // 5) * (H + gy)
    d.rounded_rectangle((x, y, x + W, y + H), 14, fill=DARK.get(key, (255, 255, 255, 250)))
    lg = ci(key, (W - 28, H - 24)); bg.alpha_composite(lg, (x + (W - lg.width) // 2, y + (H - lg.height) // 2))
f1 = ImageFont.truetype(BH, 62); f2 = ImageFont.truetype(BH, 200); f3 = ImageFont.truetype(BH, 54)
d.text((40, 268), '직원 36명 회사가', font=f1, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
d.text((40, 340), '1,148조', font=f2, fill=(255, 213, 64), stroke_width=10, stroke_fill=(0, 0, 0))
d.rounded_rectangle((40, 586, 760, 672), 18, fill=(222, 50, 40))
d.text((62, 594), '대표 기업 10곳 몰아보기', font=f3, fill=(255, 255, 255))
bg.convert('RGB').save(thumb, optimize=True)
print('ok', out, thumb)
