#!/usr/bin/env python3
"""CEO 본편 → 약 58초 세로 쇼츠 + 업로드 묶음 (2026-11-25 현철님 지정: 삼성 쇼츠와 같은 형식).
사용: python3 tools/ceo_short.py <편번호> <본편 유튜브 ID> "<쇼츠 제목(#shorts 포함)>" "<위 큰 글자 1줄>" "<위 큰 글자 2줄>" [시작초]
- 본편: release_upload/ceo/epN 조각을 git 객체에서 이어 붙여 sha256 확인 후 사용(디스크 절약, 끝나면 지움).
- 길이: 시작초부터 58.5초 안, 48초 이후 마지막 무음(문장 끝)에서 자름.
- 화면 1080x1920: 흐린 확대 배경 + 가운데 본편(16:9, 자막 포함) + 위 큰 제목 2줄 + 아래 '풀버전은 설명란 링크'.
- 묶음 release_upload/ceo/epN-shorts/: video.mp4.part000 · video.mp4.sha256 · thumb.png(1080x1920, 2MB 이하) · upload.json.
- 설명 첫 줄 '풀버전: https://youtu.be/<ID>'. READY 는 만들지 않는다."""
import sys, os, re, json, hashlib, subprocess, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = os.path.join(REPO, "neural-studio/assets/fonts/BlackHanSans.ttf")
FONT2 = os.path.join(REPO, "neural-studio/assets/fonts/Pretendard-ExtraBold.otf")
n, vid, title, l1, l2 = sys.argv[1:6]
start = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
src_dir = f"release_upload/ceo/ep{n}"; dst = os.path.join(REPO, f"release_upload/ceo/ep{n}-shorts")
W = "/home/user/sh"; os.makedirs(W, exist_ok=True); os.makedirs(dst, exist_ok=True)
run = lambda *a, **k: subprocess.run(a, check=True, **k)

# 1) 본편 꺼내기 + sha 확인
src = f"{W}/ep{n}.mp4"
parts = sorted(subprocess.check_output(["git", "-C", REPO, "ls-tree", "-r", "HEAD", "--name-only", src_dir], text=True).split())
parts = [p for p in parts if ".part" in p]
with open(src, "wb") as fo:
    for p in parts: fo.write(subprocess.check_output(["git", "-C", REPO, "show", f"HEAD:{p}"]))
want = subprocess.check_output(["git", "-C", REPO, "show", f"HEAD:{src_dir}/video.mp4.sha256"], text=True).split()[0]
h = hashlib.sha256(open(src, "rb").read()).hexdigest()
assert h == want, f"본편 sha 불일치 {h[:12]} != {want[:12]}"

# 2) 자를 위치: 48~58.5초 사이 마지막 무음 시작
out = subprocess.run(["ffmpeg", "-hide_banner", "-ss", str(start), "-t", "60", "-i", src, "-af",
                      "silencedetect=noise=-38dB:d=0.25", "-f", "null", "-"], capture_output=True, text=True).stderr
sil = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
cands = [s for s in sil if 52 <= s <= 58.4] or [s for s in sil if 45 <= s <= 58.4]
dur = (max(cands) + 0.2) if cands else 58.0

# 3) 위·아래 글자 판(투명 PNG)
def ov():
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def fit(t, size):
        while True:
            f = ImageFont.truetype(FONT, size)
            if d.textlength(t, font=f) <= 1000 or size < 50: return f
            size -= 4
    y = 250
    for t, col in ((l1, (255, 255, 255)), (l2, (255, 213, 64))):
        f = fit(t, 112); w = d.textlength(t, font=f)
        d.text(((1080 - w) / 2, y), t, font=f, fill=col, stroke_width=8, stroke_fill=(0, 0, 0))
        y += 150
    f = ImageFont.truetype(FONT2, 46); t = "풀버전은 설명란 링크에서"
    w = d.textlength(t, font=f); d.rounded_rectangle(((1080 - w) / 2 - 36, 1500, (1080 + w) / 2 + 36, 1590), 45, fill=(217, 119, 87, 235))
    d.text(((1080 - w) / 2, 1517), t, font=f, fill=(255, 255, 255))
    f = ImageFont.truetype(FONT2, 38); t = "월급쟁이 재테크 스킬 · CEO 계보"
    w = d.textlength(t, font=f); d.text(((1080 - w) / 2, 1640), t, font=f, fill=(230, 230, 230), stroke_width=3, stroke_fill=(0, 0, 0))
    return im
ovp = f"{W}/ov{n}.png"; ov().save(ovp)

# 4) 세로 영상
mp4 = f"{W}/short{n}.mp4"
fc = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:3,eq=brightness=-0.28[bg];"
      "[0:v]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2+40[v1];[v1][1:v]overlay=0:0,format=yuv420p[v]")
run("ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", f"{dur:.2f}", "-i", src, "-loop", "1", "-i", ovp,
    "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-af", f"afade=t=out:st={dur - 0.4:.2f}:d=0.4",
    "-t", f"{dur:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "160k",
    "-movflags", "+faststart", mp4)

# 5) 썸네일(세로): 흐린 본편 썸네일 배경 + 가운데 본편 썸네일 + 위 큰 제목
th = Image.open(os.path.join(REPO, src_dir, [f for f in os.listdir(os.path.join(REPO, src_dir)) if f.startswith("thumb.")][0])).convert("RGB")
bg = th.resize((int(1920 * 16 / 9), 1920)).crop((int((1920 * 16 / 9 - 1080) / 2), 0, int((1920 * 16 / 9 - 1080) / 2) + 1080, 1920))
bg = bg.filter(ImageFilter.GaussianBlur(28)); bg = Image.eval(bg, lambda x: int(x * 0.6))
fg = th.resize((1080, 608)); bg.paste(fg, (0, 656)); bg = bg.convert("RGBA"); bg.alpha_composite(ov())
tp = os.path.join(dst, "thumb.png"); bg.convert("RGB").save(tp, optimize=True)
if os.path.getsize(tp) > 2_000_000:
    os.remove(tp); tp = os.path.join(dst, "thumb.jpg"); bg.convert("RGB").save(tp, quality=90)

# 6) 묶음
for f in glob.glob(os.path.join(dst, "video.mp4.part*")): os.remove(f)
run("split", "-b", "90m", "-d", "-a", "3", mp4, os.path.join(dst, "video.mp4.part"))
hh = hashlib.sha256(open(mp4, "rb").read()).hexdigest()
open(os.path.join(dst, "video.mp4.sha256"), "w").write(hh + "\n")
long_title = json.load(open(os.path.join(REPO, src_dir, "upload.json"), encoding="utf-8"))["long"]["title"]
desc = (f"풀버전: https://youtu.be/{vid}\n\n{long_title}\n본편에서 CEO 계보와 숫자를 끝까지 정리했습니다.\n\n"
        "DART 공시·회사 발표·언론 보도를 바탕으로 한 교양 콘텐츠이며 투자 권유가 아닙니다. 인물은 실제 모습을 그리지 않은 일반 캐릭터입니다.\n\n"
        "#shorts #CEO #기업분석 #주식")
json.dump({"date": f"ceo-ep{n}-shorts", "long": {"file": "video.mp4", "title": title, "description": desc,
           "tags": ["shorts", "CEO", "기업분석", "주식"], "thumb": os.path.basename(tp)}},
          open(os.path.join(dst, "upload.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
dd = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4], text=True))
os.remove(src)
print(f"ep{n}-shorts 길이 {dd:.1f}s 시작 {start}s sha {hh[:12]} 썸네일 {os.path.basename(tp)} → {dst}")
