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


# ── layout: tiles (2026-11-04, 현철님 본보기 'Git과 GitHub' 썸네일 분위기) ──────────────────────────────
# 어두운 바탕 · 위쪽 가운데 제목(둘째 줄의 [[강조]]는 밝은 형광 상자) · 아래쪽에 반짝이는 검은 앱 타일 줄(가운데가 가장 큼)
# · 타일 뒤에서 빼꼼 내다보는 원본 마스코트. 실제 로고 대신 직접 그린 아이콘(SVG).
ICONS = {
    "branch": '<circle cx="30" cy="22" r="9"/><circle cx="30" cy="78" r="9"/><circle cx="70" cy="40" r="9"/><path d="M30 31v38M70 49c0 18-40 10-40 20" fill="none" stroke-width="7"/>',
    "commit": '<path d="M8 50h84" stroke-width="7"/><circle cx="50" cy="50" r="15"/>',
    "cloud": '<path d="M30 72h44a18 18 0 0 0 0-36 26 26 0 0 0-50 6 15 15 0 0 0 6 30z"/><path d="M52 66V44M42 54l10-10 10 10" fill="none" stroke="#111" stroke-width="6"/>',
    "save": '<path d="M20 18h48l14 14v50H20z"/><rect x="32" y="18" width="30" height="20" fill="#111"/><rect x="30" y="54" width="42" height="22" rx="3" fill="#111"/>',
    "folder": '<path d="M12 28h28l8 9h40v43H12z"/>',
    "merge": '<circle cx="28" cy="22" r="9"/><circle cx="72" cy="22" r="9"/><circle cx="50" cy="80" r="9"/><path d="M28 31c0 25 22 25 22 40M72 31c0 25-22 25-22 40" fill="none" stroke-width="7"/>',
    "cursor": '<path d="M24 10v66l17-15 12 27 11-5-12-26 23-1z" stroke="#111" stroke-width="3" stroke-linejoin="round"/>',
    "browser": '<rect x="10" y="18" width="80" height="64" rx="8"/><rect x="10" y="18" width="80" height="16" rx="8" fill="#111" opacity=".35"/><rect x="62" y="38" width="22" height="38" rx="3" fill="#111" opacity=".45"/>',
    "form": '<rect x="18" y="12" width="64" height="76" rx="6"/><rect x="28" y="28" width="44" height="9" rx="3" fill="#111"/><rect x="28" y="46" width="44" height="9" rx="3" fill="#111"/><rect x="28" y="64" width="26" height="11" rx="3" fill="#111"/>',
    "shield": '<path d="M50 10l34 12v24c0 22-15 36-34 44C31 82 16 68 16 46V22z"/><path d="M36 50l10 10 18-20" fill="none" stroke="#111" stroke-width="7"/>',
    "chat": '<path d="M14 20h72v46H44L26 82V66H14z"/><circle cx="34" cy="43" r="5" fill="#111"/><circle cx="50" cy="43" r="5" fill="#111"/><circle cx="66" cy="43" r="5" fill="#111"/>',
    "people": '<circle cx="36" cy="34" r="12"/><circle cx="66" cy="38" r="10"/><path d="M14 82c2-22 42-22 44 0zM52 82c2-18 34-18 36 0z"/>',
}


def page_tiles(t, accent):
    import json as _j
    fonts = (ROOT / "assets" / "fonts").as_uri()
    tiles = t.get("tiles") or ["folder", "commit", "branch", "cloud", "merge", "save", "people"]
    colors = t.get("tile_colors") or ["#2B2F36", "#3A3F47", "#F05033", "#FFFFFF", "#FF8A3D", "#3A3F47", "#2B2F36"]
    n = len(tiles); mid = (n - 1) / 2
    cells = []
    for i, (ic, col) in enumerate(zip(tiles, colors)):
        d = abs(i - mid); sz = int(300 - d * 44); y = int(d * 30); z = 10 - int(d)
        cells.append(f'<div class="tile" style="width:{sz}px;height:{sz}px;margin-top:{y}px;z-index:{z}">'
                     f'<svg viewBox="0 0 100 100" width="{int(sz*.5)}" height="{int(sz*.5)}" fill="{col}" stroke="{col}">{ICONS.get(ic, ICONS["commit"])}</svg></div>')
    l2 = _mk(t.get("line2", ""), accent).replace(f'<span style="color:{accent}">', '<span class="box">')
    mid_line = f'<span id="lm">{_mk(t["mid"], accent)}</span>' if t.get("mid") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:K;font-weight:900;src:url('{fonts}/Pretendard-Black.otf')}}
@font-face{{font-family:K;font-weight:800;src:url('{fonts}/Pretendard-ExtraBold.otf')}}
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:K,sans-serif;background:radial-gradient(ellipse at 50% 70%,#1d2128 0%,#0b0d11 55%,#050608 100%)}}
#top{{position:absolute;left:0;right:0;top:56px;text-align:center}}
.l{{display:inline-block;font-weight:900;color:#fff;white-space:nowrap;letter-spacing:-4px;line-height:1.12;text-shadow:0 10px 30px rgba(0,0,0,.7)}}
#top>div{{display:block}} #top>div>span.w{{display:inline-block}}
#l1{{font-size:{t.get('size1', 132)}px;color:{t.get('color1', '#fff')}}} #l2{{font-size:{t.get('size2', 150)}px;margin-top:14px}}
.box{{display:inline-block;background:{accent};color:#111;padding:0 26px 6px;border-radius:10px;margin-right:18px;box-shadow:0 0 50px {accent}55}}
#lm{{display:inline-block;font-weight:800;font-size:{t.get('size_mid', 64)}px;color:#FFE27A;letter-spacing:-2px;margin-top:18px;white-space:nowrap}}
#row{{position:absolute;left:0;right:0;bottom:40px;display:flex;justify-content:center;align-items:flex-start}}
.tile{{position:relative;margin-left:-22px;border-radius:22%;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(160deg,#2a2d33 0%,#111317 55%,#07080a 100%);border:2px solid rgba(255,255,255,.08);
  box-shadow:0 30px 60px rgba(0,0,0,.75),inset 0 2px 0 rgba(255,255,255,.14),inset 0 -8px 20px rgba(0,0,0,.6)}}
.tile:first-child{{margin-left:0}}
.tile svg{{filter:drop-shadow(0 4px 10px rgba(0,0,0,.6))}}
#pal{{position:absolute;left:50%;bottom:{40+280}px;transform:translateX(-50%);width:250px;height:160px;border-radius:30px 30px 10px 10px;
  background:{t.get('pal_bg', 'linear-gradient(170deg,#7ff0d4,#2fb894)')};box-shadow:inset 0 6px 0 rgba(255,255,255,.35),0 0 60px {t.get('pal_glow', 'rgba(63,224,181,.35)')}}}
#pal i{{position:absolute;top:58px;width:26px;height:34px;background:#0b0d11;border-radius:12px}}
#pal i:first-child{{left:62px}} #pal i:last-child{{right:62px}}
#pal b{{position:absolute;top:96px;left:50%;transform:translateX(-50%);width:34px;height:14px;border-bottom:6px solid #0b0d11;border-radius:0 0 20px 20px}}
</style></head><body>
<div id="top"><div><span class="l" id="l1">{_mk(t.get('line1', ''), accent)}</span></div><div><span class="l" id="l2">{l2}</span></div><div>{mid_line}</div></div>
{'<div id="pal"><i></i><b></b><i></i></div>' if t.get('mascot', True) else ''}
<div id="row">{''.join(cells)}</div>
<script>for(const id of ['l1','l2','lm']){{const e=document.getElementById(id);if(!e)continue;let f=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>{W - 160}&&f>60){{f-=4;e.style.fontSize=f+'px'}}}}</script>
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
    if bg and t.get("layout") != "tiles":
        for base in (Path(proj_dir), ROOT):
            if (base / bg).exists():
                bgp = (base / bg).resolve()
                break
        if not bgp:
            log(f"  ⚠ thumbnail: 배경 그림 {bg} 없음 → 기본 네온 배경")
    html = (Path(out_dir) / "_thumb.html").resolve()
    if t.get("layout") == "tiles":
        html.write_text(page_tiles(t, t.get("accent", "#D7F25A")), encoding="utf-8")
    else:
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
