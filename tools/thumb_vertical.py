"""쇼츠용 세로 썸네일(1080x1920 JPG)을 thumb_layouts 플러그인으로 그린다(2026-11-21).
사용: python3 tools/thumb_vertical.py projects/<쇼츠>.yaml <출력.jpg> [--wide 가로본.jpg]
"""
import importlib, sys, yaml
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def render(t, out, W, H):
    mod = importlib.import_module(f"facetube.thumb_layouts.{t['layout']}")
    html = Path(out).with_suffix(".html")
    html.write_text(mod.page(t, (ROOT / "assets" / "fonts").as_uri(), W, H), encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(html.as_uri()); pg.wait_for_timeout(400)
        pg.screenshot(path=str(out), type="jpeg", quality=90)
        b.close()
    html.unlink()


if __name__ == "__main__":
    proj = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
    render(proj["thumbnail"], sys.argv[2], 1080, 1920)
    if "--wide" in sys.argv:
        render(proj["thumbnail"], sys.argv[sys.argv.index("--wide") + 1], 1920, 1080)
    print(sys.argv[2])
