"""유튜브 썸네일(thumbnail.jpg) — 최종 영상·youtube.txt 와 한 세트(현철님 2026-11-04, PUB-02).

모양(현철님이 준 본보기 두 장): 위 2/3 는 3D 일러스트 그림, 아래에 아주 굵은 두 줄 제목.
  첫 줄 흰색, 둘째 줄은 강조 낱말만 주황/민트. 굵은 검은 테두리 + 그림자로 작은 화면에서도 읽힌다.
그림(bg)은 AI 로 '글자 없이' 만들고(글자는 AI 가 틀리게 그리므로) 글자는 여기서 폰트로 얹는다.
대본 yaml:
  thumbnail:
    bg: assets/thumbs/aside_bg.png      # 없으면 네온 기본 배경
    tag: "AI 브라우저 · 사용법 총정리"     # 왼쪽 위 작은 띠(선택)
    line1: "엑셀 옮겨 적기 그만!"
    mid: "작은 가운데 줄"                 # 선택: line1 과 line2 사이 설명 줄(작게, 노란빛)
    line2: "[[어사이드]]가 다 해 줘요"     # [[ ]] = 강조색
    size1 / size_mid / size2: 글자 크기(px). 안 주면 줄 수에 맞춰 자동, 넓으면 화면 폭에 맞게 줄인다
    accent: "#FF8A3D"                    # 선택(기본 주황)
    align: left | center                 # 기본 left
크기: 1920x1080(유튜브 권장 1280x720 보다 크게), JPEG 2MB 이하(유튜브 상한).
"""
import html as _h
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W, H = 1920, 1080
MAX_BYTES = 2 * 1024 * 1024


def _mk(s, accent):
    s = _h.escape(s)
    return re.sub(r"\[\[(.+?)\]\]", rf'<span style="color:{accent}">\1</span>', s)


def page(t, bg_url):
    accent = t.get("accent", "#FF8A3D")
    align = t.get("align", "left")
    fonts = (ROOT / "assets" / "fonts").as_uri()
    bg = (f"background:#05070c url('{bg_url}') center/cover no-repeat;" if bg_url else
          "background:radial-gradient(ellipse at 70% 35%,#0f3b3a 0%,#07121a 45%,#03050a 100%);")
    tag = f'<div class="tag">{_h.escape(t["tag"])}</div>' if t.get("tag") else ""
    has_mid = bool(t.get("mid"))
    s1, s2 = t.get("size1", t.get("size", 132 if has_mid else 168)), t.get("size2", t.get("size", 150 if has_mid else 168))
    sm = t.get("size_mid", 70)
    mid = f'<div id="lm">{_mk(t["mid"], accent)}</div>' if has_mid else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts}/Pretendard-Black.otf')}}
@font-face{{font-family:K;font-weight:800;src:url('{fonts}/Pretendard-ExtraBold.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif}}
#bg{{position:absolute;inset:0;{bg}}}
#fade{{position:absolute;left:0;right:0;bottom:0;height:62%;background:linear-gradient(to top,rgba(0,0,0,.92) 0%,rgba(0,0,0,.72) 38%,rgba(0,0,0,0) 100%)}}
#txt{{position:absolute;left:96px;right:96px;bottom:70px;text-align:{align}}}
.l{{font-weight:900;line-height:1.08;letter-spacing:-4px;color:#fff;white-space:nowrap;
   -webkit-text-stroke:14px #000;paint-order:stroke fill;text-shadow:0 10px 0 #000,0 18px 40px rgba(0,0,0,.85)}}
#l1{{font-size:{s1}px}} #l2{{font-size:{s2}px}}
#lm{{font-weight:800;font-size:{sm}px;line-height:1.25;letter-spacing:-2px;color:#FFE27A;white-space:nowrap;margin:6px 0 10px;
   -webkit-text-stroke:10px #000;paint-order:stroke fill;text-shadow:0 6px 0 #000,0 12px 30px rgba(0,0,0,.85)}}
.tag{{position:absolute;left:96px;top:70px;padding:14px 30px;border-radius:14px;background:{accent};color:#111;font-weight:800;font-size:54px;letter-spacing:-1px;
     box-shadow:0 8px 30px rgba(0,0,0,.5)}}
</style></head><body><div id="bg"></div><div id="fade"></div>{tag}
<div id="txt"><div class="l" id="l1">{_mk(t.get('line1', ''), accent)}</div>{mid}<div class="l" id="l2">{_mk(t.get('line2', ''), accent)}</div></div>
<script>for(const id of ['l1','lm','l2']){{const e=document.getElementById(id);if(!e)continue;let f=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>{W - 192}&&f>80){{f-=4;e.style.fontSize=f+'px'}}}}</script>
</body></html>"""


def make(proj, out_dir, proj_dir=".", log=print):
    t = proj.get("thumbnail")
    if not t:
        log("  ⚠ thumbnail: 대본에 thumbnail 칸이 없어 썸네일을 만들지 않음(PUB-02)")
        return None
    from PIL import Image
    from playwright.sync_api import sync_playwright
    bg = t.get("bg")
    bgp = None
    if bg:
        for base in (Path(proj_dir), ROOT):
            if (base / bg).exists():
                bgp = (base / bg).resolve()
                break
        if not bgp:
            log(f"  ⚠ thumbnail: 배경 그림 {bg} 없음 → 기본 네온 배경")
    html = (Path(out_dir) / "_thumb.html").resolve()
    html.write_text(page(t, bgp.as_uri() if bgp else None), encoding="utf-8")
    exe = "/opt/pw-browsers/chromium" if Path("/opt/pw-browsers/chromium").exists() else None
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(html.as_uri())
        pg.evaluate("document.fonts.ready")
        png = pg.screenshot()
        b.close()
    html.unlink()
    im = Image.open(io.BytesIO(png)).convert("RGB")
    out = Path(out_dir) / "thumbnail.jpg"
    for q in (95, 92, 88, 84, 80):
        im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        if out.stat().st_size <= MAX_BYTES:
            break
    log(f"  썸네일: {out} ({W}x{H}, {out.stat().st_size / 1024:.0f}KB)")
    return out
