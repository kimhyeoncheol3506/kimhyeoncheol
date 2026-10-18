"""장면 한 컷 미리보기 (영상 렌더 없이 헤드라인·그림·자막·워터마크 합성). 사용: python tools/preview_frame.py project.json s05 [out.png]"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image
from studio import render as R
from studio.scenes import render_visual

def frame(p, sc, out):
    td = tempfile.mkdtemp()
    bg, top = R.chrome_pngs(p, "long", td)
    L = R.LAYOUT["long"]; cy0, ch = 0, L["H"]
    if sc.get("headline"):
        cy0, ch = R.HEADLINE_H, L["H"] - R.HEADLINE_H
    img = Image.open(bg).convert("RGBA")
    img.alpha_composite(render_visual(dict(sc["visual"]), L["W"], ch, sc.get("bg"), 0).convert("RGBA"), (0, cy0))
    sub = R.split_subtitles(sc.get("caption", sc["text"]), L["chunk"])[0]
    R.subtitle_png("long", sub, td + "/s.png", 1460 if p.get("corner_mascot") else 1600)
    img.alpha_composite(Image.open(td + "/s.png"))
    if sc.get("headline"):
        R.headline_png(sc["headline"], td + "/h.png", p)
        img.alpha_composite(Image.open(td + "/h.png"), (0, 0))
    img.alpha_composite(Image.open(top))
    img.convert("RGB").save(out)

if __name__ == "__main__":
    p = json.load(open(sys.argv[1], encoding="utf-8"))
    ids = sys.argv[2].split(",")
    for sid in ids:
        sc = next(s for s in p["scenes"] if s["id"] == sid)
        frame(p, sc, (sys.argv[3] if len(sys.argv) > 3 and len(ids) == 1 else f"/tmp/preview_{sid}.png"))
