# -*- coding: utf-8 -*-
"""영상에 실제로 쓰인 이미지의 출처·라이선스 목록 생성 (ranking-video v1.2.0)

사용법: python3 -I make_credits.py <이미지폴더> <작업폴더>
입력: <이미지폴더>/meta.json, <작업폴더>/08_완성영상/타임라인.json
출력: <작업폴더>/08_완성영상/이미지_출처.txt  (CC BY는 저작자 표시 의무 → 설명란이나 고정댓글에 붙여넣기)
"""
import json, os, sys

LIC = {"by": "CC BY", "by-sa": "CC BY-SA", "cc0": "CC0", "pdm": "퍼블릭 도메인"}


def main(img, proj):
    meta = {m["id"]: m for m in json.load(open(os.path.join(img, "meta.json"), encoding="utf-8"))}
    used = json.load(open(os.path.join(proj, "08_완성영상", "타임라인.json"), encoding="utf-8"))["images_used"]
    lines = ["[이미지 출처] 이 영상의 사진은 실제 소개 매장의 사진이 아닌, 이해를 돕기 위한 자유 이용 이미지입니다.", ""]
    for k, i in enumerate(used, 1):
        m = meta.get(i)
        if not m: continue
        lic = LIC.get(m["license"], m["license"].upper()) + (f" {m['license_version']}" if m.get("license_version") and m["license"] not in ("cc0", "pdm") else "")
        lines.append(f"{k}. \"{(m.get('title') or '무제')[:60]}\" — {m.get('creator') or '작자 미상'} / {lic} / {m.get('foreign') or m['url']}")
    out = os.path.join(proj, "08_완성영상", "이미지_출처.txt")
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"{len(lines) - 2}개 → {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
