#!/usr/bin/env python3
"""이미 만든 CEO 쇼츠 묶음의 마지막 2초 안내를 "왜 그런지는 / 본편 '<회사명>'에서"로 바꾼다 (2026-11-27 현철님 지시).
사용: python3 tools/short_endcard.py <편번호> <회사명>
- release_upload/ceo/epN-shorts 조각을 git 객체에서 이어 붙여 sha 확인 → 마지막 2초에 불투명 안내판을 덮어 다시 인코딩(소리는 그대로 복사).
- 예전 안내판(70,760~1010,1160)을 완전히 덮는 같은 자리·불투명 판. 조각·sha256 을 새로 쓴다. READY 는 만들지 않는다."""
import sys, os, json, hashlib, subprocess, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = os.path.join(REPO, "neural-studio/assets/fonts/BlackHanSans.ttf")
FONT2 = os.path.join(REPO, "neural-studio/assets/fonts/Pretendard-ExtraBold.otf")
W = "/home/user/sh"

def card(company):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 750, 1020, 1170), 40, fill=(217, 119, 87, 255))
    for t, y, sz in (("왜 그런지는", 790, 100), (f"본편 '{company}'에서", 930, 92)):
        while True:
            f = ImageFont.truetype(FONT, sz)
            if d.textlength(t, font=f) <= 900 or sz < 50: break
            sz -= 4
        w = d.textlength(t, font=f)
        # Black Han Sans '야' 글리프는 stroke_width 외곽선이 깨진다 → 글자 마스크를 넓혀(MaxFilter) 외곽선을 만든다
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).text(((1080 - w) / 2, y), t, font=f, fill=255)
        im.paste((0, 0, 0, 255), (0, 0), m.filter(ImageFilter.MaxFilter(11))); im.paste((255, 255, 255, 255), (0, 0), m)
    f = ImageFont.truetype(FONT2, 44); t = "▲ 화면 위 링크를 눌러 주세요"; w = d.textlength(t, font=f)
    d.text(((1080 - w) / 2, 1085), t, font=f, fill=(255, 255, 255))
    return im

if __name__ == "__main__":
    n, co = sys.argv[1], sys.argv[2]
    rel = f"release_upload/ceo/ep{n}-shorts"; dst = os.path.join(REPO, rel); os.makedirs(W, exist_ok=True)
    src = f"{W}/old{n}.mp4"
    parts = sorted(p for p in subprocess.check_output(["git", "-C", REPO, "ls-tree", "-r", "HEAD", "--name-only", rel], text=True).split() if ".part" in p)
    with open(src, "wb") as fo:
        for p in parts: fo.write(subprocess.check_output(["git", "-C", REPO, "show", f"HEAD:{p}"]))
    want = subprocess.check_output(["git", "-C", REPO, "show", f"HEAD:{rel}/video.mp4.sha256"], text=True).split()[0]
    assert hashlib.sha256(open(src, "rb").read()).hexdigest() == want, "옛 쇼츠 sha 불일치"
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], text=True))
    cp = f"{W}/card{n}.png"; card(co).save(cp)
    out = f"{W}/new{n}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-loop", "1", "-i", cp, "-filter_complex",
                    f"[0:v][1:v]overlay=0:0:enable='gte(t,{dur - 2:.2f})':shortest=1,format=yuv420p[v]", "-map", "[v]", "-map", "0:a",
                    "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "copy", "-movflags", "+faststart", "-t", f"{dur:.3f}", out], check=True)
    for f in glob.glob(os.path.join(dst, "video.mp4.part*")): os.remove(f)
    subprocess.run(["split", "-b", "90m", "-d", "-a", "3", out, os.path.join(dst, "video.mp4.part")], check=True)
    h = hashlib.sha256(open(out, "rb").read()).hexdigest(); open(os.path.join(dst, "video.mp4.sha256"), "w").write(h + "\n")
    nd = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out], text=True))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{nd - 1:.2f}", "-i", out, "-frames:v", "1", "-vf", "scale=540:-2", f"{W}/chk{n}.png"], check=True)
    os.remove(src)
    print(f"ep{n}-shorts 끝 안내 교체: 본편 '{co}' · 길이 {dur:.2f}→{nd:.2f}s · sha {h[:12]} · 확인 그림 {W}/chk{n}.png")
