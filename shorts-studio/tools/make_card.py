"""스샷 파일이 없을 때(채팅에 붙인 이미지 등) 글 내용으로 블라인드 스타일 카드를 다시 그린다.

  python tools/make_card.py projects/<프로젝트>/card.json
card.json: {"nick": "블라블라", "meta": "9시간 · 언팔로우", "company": "공무원", "mask_ids": ["Abcd12"],
            "title": ["5가지 조건 다 있는 남자랑 결혼하고", "싶다"], "body": ["...", "..."]}
출력: source_card.png + card_regions.json (title1.., body1..) — 줄마다 형광펜 좌표
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
F = ROOT / "assets" / "fonts"


def mask_id(s: str) -> str:
    """개인 아이디는 첫 글자만 남기고 별표: Abcd12 → A*****  (현철님 규칙)"""
    return s[:1] + "*" * max(2, len(s) - 1)


def main():
    spec_f = Path(sys.argv[1])
    spec = json.loads(spec_f.read_text(encoding="utf-8"))
    for i in spec.get("mask_ids", []):  # 화면 어디에 있든 아이디는 가린다
        for k in ("nick", "meta", "company"):
            spec[k] = spec.get(k, "").replace(i, mask_id(i))
        spec["title"] = [t.replace(i, mask_id(i)) for t in spec["title"]]
        spec["body"] = [t.replace(i, mask_id(i)) for t in spec["body"]]
    proj = spec_f.parent
    W = 966
    bold = ImageFont.truetype(str(F / "Pretendard-ExtraBold.otf"), 50)
    reg = ImageFont.truetype(str(F / "Pretendard-Medium.otf"), 37)
    longest = max([reg.getlength(t) for t in spec["body"]] + [1])
    if longest > W - 96:
        reg = ImageFont.truetype(str(F / "Pretendard-Medium.otf"), int(37 * (W - 96) / longest))
    small = ImageFont.truetype(str(F / "Pretendard-Medium.otf"), 30)
    logo = ImageFont.truetype(str(F / "Pretendard-ExtraBold.otf"), 44)
    lines = len(spec["title"]) * 72 + len(spec["body"]) * 62
    H = 300 + lines + 80
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    gray, mid = (190, 190, 196), (120, 120, 128)
    # 헤더: < blind  + 아이콘
    d.line((70, 22, 52, 40, 70, 58), fill=(40, 40, 40), width=5, joint="curve")
    d.text((122, 40), "blind", font=logo, fill=gray, anchor="lm")
    for i, x in enumerate((640, 720, 800)):
        d.rounded_rectangle((x - 16, 24, x + 16, 58), 6, outline=(40, 40, 40), width=4)
    for k in range(3):
        d.ellipse((868 + k * 22 - 6, 34, 868 + k * 22 + 6, 46), outline=(40, 40, 40), width=3)
    # 작성자
    d.ellipse((46, 140, 132, 226), fill=(214, 220, 236))
    for k in range(3):
        d.ellipse((70 + k * 16 - 5, 178, 70 + k * 16 + 5, 188), fill=(150, 160, 190))
    d.text((154, 150), spec.get("nick", "익명"), font=small, fill=(60, 60, 66))
    nw = small.getlength(spec.get("nick", "익명"))
    d.text((154 + nw + 18, 150), spec.get("meta", ""), font=small, fill=gray)
    d.text((154, 190), spec.get("company", ""), font=small, fill=mid)
    regions = {}
    y = 280
    for i, t in enumerate(spec["title"]):
        d.text((48, y), t, font=bold, fill=(20, 20, 22))
        regions[f"title{i + 1}"] = [45, y - 4, int(48 + bold.getlength(t)) + 4, y + 62]
        y += 72
    y += 14
    for i, t in enumerate(spec["body"]):
        if t:
            d.text((48, y), t, font=reg, fill=(34, 34, 38))
            regions[f"body{i + 1}"] = [45, y - 6, int(48 + reg.getlength(t)) + 4, y + 50]
        y += 62
    im.save(proj / "source_card.png")
    (proj / "card_regions.json").write_text(json.dumps(regions, indent=1), encoding="utf-8")
    print(f"카드 {im.size}, 줄 {len(regions)}개 → {proj}")


if __name__ == "__main__":
    main()
