#!/usr/bin/env python3
"""ReachMora(v2 카툰) 편 업로드 묶음.  python3 tools/rm_package.py <P> <mp4> <thumb.png> <dst> <date>
<P>/upload_meta.json: {"title", "description"(줄바꿈 포함 본문), "sources":[[이름, 날짜, 제목, url]...], "tags":[...], "chapters":[[초, 제목]...]}
만드는 것: video.mp4.part000…(90MB) · video.mp4.sha256 · thumb.png(1280x720, 2MB 이하) · upload.json. READY 는 만들지 않는다."""
import sys, os, json, hashlib, subprocess, glob
from PIL import Image
P, mp4, thumb, dst, date = sys.argv[1:6]
os.makedirs(dst, exist_ok=True)
for f in glob.glob(os.path.join(dst, "video.mp4.part*")): os.remove(f)
subprocess.run(["split", "-b", "90m", "-d", "-a", "3", mp4, os.path.join(dst, "video.mp4.part")], check=True)
h = hashlib.sha256()
with open(mp4, "rb") as f:
    for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
open(os.path.join(dst, "video.mp4.sha256"), "w").write(h.hexdigest() + "\n")
im = Image.open(thumb).convert("RGB").resize((1280, 720), Image.LANCZOS); tp = os.path.join(dst, "thumb.png"); im.save(tp, optimize=True)
if os.path.getsize(tp) > 2_000_000: os.remove(tp); tp = os.path.join(dst, "thumb.jpg"); im.save(tp, quality=92)
m = json.load(open(os.path.join(P, "upload_meta.json"), encoding="utf-8"))
def ts(s): s = int(s); return f"{s // 60:02d}:{s % 60:02d}"
desc = m["description"].rstrip() + "\n\n⏱ 챕터\n" + "\n".join(f"{ts(t)} {n}" for t, n in m["chapters"])
desc += "\n\n📚 출처\n" + "\n".join(f"· {a} {b} 「{c}」 {u}" for a, b, c, u in m["sources"])
desc += ("\n\n이 영상은 DART 공시와 회사 발표, 언론 보도를 바탕으로 한 교양 콘텐츠입니다. " + m.get("asof", "") +
         " 기준이며 이후 바뀔 수 있습니다. 특정 종목의 매수·매도를 권하지 않으며 투자 권유가 아닙니다. 인물은 실제 모습을 그리지 않은 일반 캐릭터입니다.")
desc += "\n\n" + " ".join("#" + t for t in m["tags"])
json.dump({"date": date, "long": {"file": "video.mp4", "title": m["title"], "description": desc, "tags": m["tags"], "thumb": os.path.basename(tp)}},
          open(os.path.join(dst, "upload.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(dst, "조각", len(glob.glob(os.path.join(dst, "video.mp4.part*"))), "sha", h.hexdigest()[:12], "설명란", len(desc), "자")
