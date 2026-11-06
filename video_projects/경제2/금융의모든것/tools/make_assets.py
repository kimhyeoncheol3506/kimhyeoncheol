#!/usr/bin/env python3
"""자산 만들기: 마스코트(SVG→PNG, Playwright), 차트(matplotlib), 퍼블릭도메인 그림이 없을 때 대체 카드.

  python tools/make_assets.py <작업폴더>
"""
import os, sys, json, subprocess, glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "..", ".claude", "skills", "neogul-edit", "scripts", "fonts")
FONTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".claude", "skills", "neogul-edit", "scripts", "fonts"))

DARK, CREAM = "#181614", "#F4F0E8"
RED, BLUE, YEL, GRAY, MUTED = "#F2262B", "#3D97E5", "#E3C04B", "#5A5752", "#A39D94"


def setup_fonts():
    for f in glob.glob(os.path.join(FONTS, "*.otf")):
        fm.fontManager.addfont(f)
    plt.rcParams["font.family"] = "Pretendard"
    plt.rcParams["axes.unicode_minus"] = False


def fig(theme="dark", w=1728, h=520):
    bg = DARK if theme == "dark" else CREAM
    fg = "#FFFFFF" if theme == "dark" else "#161412"
    f, ax = plt.subplots(figsize=(w / 100, h / 100), dpi=100)
    f.patch.set_facecolor(bg); ax.set_facecolor(bg)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED if theme == "dark" else "#8A847B")
    ax.tick_params(colors=MUTED if theme == "dark" else "#4A4640", labelsize=17)
    ax.grid(axis="y", color="#3D3B37" if theme == "dark" else "#E2DCD2", lw=1)
    ax.set_axisbelow(True)
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    return f, ax, fg


def save(f, path):
    f.tight_layout(pad=0.6)
    f.savefig(path, facecolor=f.get_facecolor())
    plt.close(f)


def label(ax, x, y, t, fg, color=None, dy=12, size=19, ha="center", weight="bold"):
    ax.annotate(t, (x, y), textcoords="offset points", xytext=(0, dy), ha=ha, fontsize=size, color=color or fg, fontweight=weight)


def charts(out):
    os.makedirs(out, exist_ok=True)
    import numpy as np
    # 1 복리
    f, ax, fg = fig("dark")
    t = np.arange(0, 20.01, 0.25); v = 100 * 1.2 ** t
    ax.plot(t, v, color=RED, lw=5)
    for x, txt in ((3.8, "약 3.8년: 2배"), (10, "10년: 약 6배"), (20, "20년: 약 38배")):
        y = 100 * 1.2 ** x; ax.scatter([x], [y], s=120, color=YEL, zorder=5); label(ax, x, y, txt, fg, YEL, dy=16, ha="right" if x == 20 else "center")
    ax.set_xlabel("년", color=MUTED, fontsize=18); ax.set_ylabel("빚 (세켈)", color=MUTED, fontsize=18)
    ax.set_xlim(0, 20.5); ax.set_ylim(0, 4300)
    save(f, os.path.join(out, "compound.png"))
    # 2 신용창조
    f, ax, fg = fig("cream")
    rounds = np.arange(1, 21); dep = 100 * 0.9 ** (rounds - 1); cum = np.cumsum(dep)
    ax.bar(rounds, dep, color=BLUE, width=0.7, label="각 단계 새 예금")
    ax.plot(rounds, cum, color=RED, lw=4, marker="o", label="누적 예금")
    ax.axhline(1000, color=RED, ls="--", lw=2); ax.text(20.4, 1000, "이론상 최대 1,000만 원", color=RED, fontsize=19, va="bottom", ha="right", fontweight="bold")
    label(ax, 1, 100, "처음 100만 원", "#161412", dy=8, size=17)
    ax.set_xlabel("대출 → 예금이 반복되는 단계", color="#4A4640", fontsize=18); ax.set_ylabel("만 원", color="#4A4640", fontsize=18)
    ax.set_ylim(0, 1150); ax.legend(fontsize=17, frameon=False, loc="center right")
    save(f, os.path.join(out, "credit.png"))
    # 3 튤립 (흐름 예시)
    f, ax, fg = fig("dark")
    xs = ["11월 초", "11월 말", "12월 중", "1월 초", "1월 말", "2월 3일", "2월 중", "5월"]
    ys = [1, 1.6, 3.5, 7, 13, 20, 4, 1.2]
    ax.plot(range(len(xs)), ys, color=RED, lw=5, marker="o", ms=10)
    ax.set_xticks(range(len(xs))); ax.set_xticklabels(xs)
    label(ax, 5, 20, "하를럼 경매, 아무도 사지 않았다", fg, YEL, dy=14, ha="right")
    ax.set_ylabel("상대 가격 (11월 초 = 1)", color=MUTED, fontsize=17)
    ax.text(0, 18, "1636 → 1637, 흐름을 단순화한 예시", color=MUTED, fontsize=16)
    ax.set_ylim(0, 23)
    save(f, os.path.join(out, "tulip.png"))
    # 4 존 로 시스템 (타임라인)
    f, ax, fg = fig("dark"); ax.axis("off"); ax.grid(False)
    ev = [("1716", "일반은행 설립", BLUE), ("1717", "서방회사(미시시피)", BLUE), ("1718", "왕립은행으로", BLUE), ("1719", "국채 → 주식 전환\n주가 20배", RED),
          ("1720.1", "존 로, 재무총감", YEL), ("1720.5", "지폐·주식 가치 인하", RED), ("1720.12", "프랑스 탈출", RED)]
    ax.set_xlim(-0.5, len(ev) - 0.5); ax.set_ylim(-1.3, 1.3)
    ax.plot([-0.3, len(ev) - 0.7], [0, 0], color=MUTED, lw=3)
    for i, (y, t, c) in enumerate(ev):
        ax.scatter([i], [0], s=420, color=c, zorder=5)
        ax.text(i, 0.35, y, ha="center", color=c, fontsize=24, fontweight="bold")
        ax.text(i, -0.4, t, ha="center", va="top", color="#FFFFFF", fontsize=19)
    save(f, os.path.join(out, "law_system.png"))
    # 5 남해회사
    f, ax, fg = fig("dark")
    xs = ["1월", "3월", "4월", "5월", "6월 말", "7월", "8월", "9월 말", "12월"]
    ys = [128, 330, 400, 500, 1050, 950, 800, 300, 190]
    ax.plot(range(len(xs)), ys, color=RED, lw=5, marker="o", ms=10)
    ax.set_xticks(range(len(xs))); ax.set_xticklabels(xs)
    label(ax, 0, 128, "128파운드", fg, dy=14); label(ax, 4, 1050, "1,000파운드 돌파", fg, YEL, dy=14); label(ax, 8, 190, "약 190", fg, dy=14)
    ax.set_ylabel("파운드", color=MUTED, fontsize=18); ax.set_ylim(0, 1250)
    ax.text(0.2, 1120, "1720년, 주요 시점 연결 (근사치)", color=MUTED, fontsize=16)
    save(f, os.path.join(out, "southsea.png"))
    # 6 다우 1924~1929
    f, ax, fg = fig("dark")
    xs = [1924, 1925, 1926, 1927, 1928, 1929.0, 1929.67]
    ys = [95, 120, 156, 155, 200, 300, 381]
    ax.plot(xs, ys, color=RED, lw=5, marker="o", ms=9)
    label(ax, 1924, 95, "약 95", fg, dy=14); label(ax, 1929.67, 381, "381 (1929년 9월)", fg, YEL, dy=14, ha="right")
    ax.set_xticks([1924, 1925, 1926, 1927, 1928, 1929]); ax.set_xticklabels(["1924", "1925", "1926", "1927", "1928", "1929"])
    ax.set_ylim(0, 450)
    save(f, os.path.join(out, "dow1920s.png"))
    # 7 다우 1929~1954
    f, ax, fg = fig("dark")
    pts = [(1929.67, 381), (1929.87, 199), (1930.3, 294), (1930.95, 165), (1931.95, 78), (1932.52, 41), (1937.2, 194), (1938.25, 99),
           (1942.3, 93), (1946.4, 212), (1949.45, 161), (1954.9, 382)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=RED, lw=5, marker="o", ms=8)
    ax.axhline(381, color=YEL, ls="--", lw=2)
    label(ax, 1929.67, 381, "1929 고점 381", fg, YEL, dy=14, ha="left"); label(ax, 1932.52, 41, "1932년 7월 41 (-89%)", fg, BLUE, dy=-34, ha="left")
    label(ax, 1954.9, 382, "1954년 11월 회복", fg, YEL, dy=14, ha="right")
    ax.set_ylim(0, 460); ax.set_xlim(1929, 1955.5)
    save(f, os.path.join(out, "dow_depression.png"))
    # 8 나스닥
    f, ax, fg = fig("dark")
    pts = [(1995.5, 1000), (1998.8, 1400), (1999.95, 4069), (2000.2, 5048), (2001.3, 1638), (2001.7, 1423), (2002.78, 1114), (2007.8, 2859), (2009.2, 1268), (2015.3, 5056)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=RED, lw=5, marker="o", ms=8)
    label(ax, 2000.2, 5048, "2000년 3월 5,048", fg, YEL, dy=14); label(ax, 2002.78, 1114, "2002년 10월 1,114 (-78%)", fg, BLUE, dy=-34, ha="left")
    label(ax, 2015.3, 5056, "2015년 회복", fg, YEL, dy=14, ha="right")
    ax.set_ylim(0, 5900); ax.set_xlim(1995, 2016)
    save(f, os.path.join(out, "nasdaq.png"))
    # 9 폰지 수학
    f, ax, fg = fig("cream")
    m = np.arange(0, 61); need = 10 * 1.1 ** m
    ax.bar(m, need, color=[RED if x in (12, 24, 36, 48, 60) else "#C9C2B6" for x in m], width=0.8)
    for x in (12, 24, 36, 48, 60):
        v = 10 * 1.1 ** x; label(ax, x, v, ("%.0f억" % v) if v < 1000 else ("%.1f조" % (v / 10000) if v >= 10000 else "%s억" % format(int(round(v)), ",")), "#161412", RED, dy=8, size=18)
    ax.set_xlabel("개월", color="#4A4640", fontsize=18); ax.set_ylabel("그달 필요한 신규 자금 (억 원)", color="#4A4640", fontsize=17)
    ax.text(1, 2500, "첫 투자 100억 원, 매달 10% 지급 약속, 실제 수익 0", color="#4A4640", fontsize=17)
    save(f, os.path.join(out, "ponzi_math.png"))
    # 10 메이도프 (예시)
    f, ax, fg = fig("dark")
    yrs = list(range(1991, 2009))
    sp = [30.5, 7.6, 10.1, 1.3, 37.6, 23.0, 33.4, 28.6, 21.0, -9.1, -11.9, -22.1, 28.7, 10.9, 4.9, 15.8, 5.5, -37.0]
    ax.bar([y - 0.2 for y in yrs], sp, width=0.4, color=[BLUE if v < 0 else GRAY for v in sp], label="S&P 500 연간 수익률(실제)")
    ax.bar([y + 0.2 for y in yrs], [10.5] * len(yrs), width=0.4, color=YEL, label="메이도프가 보여 준 수익(예시: 매년 약 10%)")
    ax.axhline(0, color=MUTED, lw=1.5); ax.legend(fontsize=16, frameon=False, labelcolor=fg, loc="lower left")
    ax.set_ylabel("%", color=MUTED, fontsize=18); ax.set_ylim(-42, 42); ax.set_xticks(yrs[::2])
    save(f, os.path.join(out, "madoff.png"))
    print("[charts] 10장 완료")


MASCOT_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 700 820' width='700' height='820'>
<defs><radialGradient id='b' cx='45%' cy='40%' r='60%'><stop offset='0' stop-color='#FFC9D6'/><stop offset='1' stop-color='#F48FAA'/></radialGradient></defs>
<ellipse cx='350' cy='790' rx='210' ry='22' fill='#000' opacity='.12'/>
<!-- legs -->
<rect x='225' y='640' width='70' height='130' rx='30' fill='#E87A98'/><rect x='405' y='640' width='70' height='130' rx='30' fill='#E87A98'/>
<!-- ears -->
<path d='M190 230 L170 90 L290 170 Z' fill='#F48FAA'/><path d='M510 230 L530 90 L410 170 Z' fill='#F48FAA'/>
<path d='M200 205 L190 120 L265 172 Z' fill='#E06C8C'/><path d='M500 205 L510 120 L435 172 Z' fill='#E06C8C'/>
<!-- body -->
<ellipse cx='350' cy='430' rx='270' ry='260' fill='url(#b)'/>
<!-- coin slot -->
<rect x='300' y='185' width='100' height='16' rx='8' fill='#B44C69'/>
<!-- coin -->
<g transform='translate(350,150)'>{coin}</g>
<!-- eyes -->{eyes}
<!-- cheeks --><ellipse cx='215' cy='445' rx='34' ry='20' fill='#FF8FA8' opacity='.8'/><ellipse cx='485' cy='445' rx='34' ry='20' fill='#FF8FA8' opacity='.8'/>
<!-- snout --><ellipse cx='350' cy='455' rx='86' ry='62' fill='#E87A98'/><ellipse cx='322' cy='455' rx='14' ry='20' fill='#9E3B58'/><ellipse cx='378' cy='455' rx='14' ry='20' fill='#9E3B58'/>
<!-- mouth -->{mouth}
<!-- arms -->{arms}
</svg>"""

POSES = {
    "shock": dict(
        coin="<circle r='38' fill='#F2C230' stroke='#B8860B' stroke-width='6'/><text y='14' text-anchor='middle' font-size='40' font-weight='900' fill='#8A6508' font-family='sans-serif'>₩</text>",
        eyes="<ellipse cx='265' cy='350' rx='46' ry='54' fill='#fff' stroke='#222' stroke-width='6'/><circle cx='265' cy='355' r='16' fill='#222'/>"
             "<ellipse cx='435' cy='350' rx='46' ry='54' fill='#fff' stroke='#222' stroke-width='6'/><circle cx='435' cy='355' r='16' fill='#222'/>"
             "<path d='M215 278 L300 300' stroke='#222' stroke-width='9' stroke-linecap='round'/><path d='M485 278 L400 300' stroke='#222' stroke-width='9' stroke-linecap='round'/>",
        mouth="<ellipse cx='350' cy='560' rx='40' ry='48' fill='#7A1F3A'/><ellipse cx='350' cy='585' rx='24' ry='14' fill='#FF6F8E'/>",
        arms="<path d='M95 420 Q40 300 90 230' stroke='#F48FAA' stroke-width='52' fill='none' stroke-linecap='round'/><path d='M605 420 Q660 300 610 230' stroke='#F48FAA' stroke-width='52' fill='none' stroke-linecap='round'/>"
             "<text x='600' y='160' font-size='120' font-weight='900' fill='#FD000A' font-family='sans-serif'>!</text>"),
    "plead": dict(
        coin="<circle r='38' fill='#F2C230' stroke='#B8860B' stroke-width='6'/><text y='14' text-anchor='middle' font-size='40' font-weight='900' fill='#8A6508' font-family='sans-serif'>₩</text>",
        eyes="<circle cx='265' cy='355' r='44' fill='#222'/><circle cx='280' cy='338' r='15' fill='#fff'/><circle cx='252' cy='372' r='7' fill='#fff'/>"
             "<circle cx='435' cy='355' r='44' fill='#222'/><circle cx='450' cy='338' r='15' fill='#fff'/><circle cx='422' cy='372' r='7' fill='#fff'/>"
             "<path d='M228 290 Q265 275 300 300' stroke='#222' stroke-width='8' fill='none' stroke-linecap='round'/><path d='M472 290 Q435 275 400 300' stroke='#222' stroke-width='8' fill='none' stroke-linecap='round'/>"
             "<path d='M232 400 q-10 40 6 60 q16 -20 6 -60z' fill='#7EC8FF'/><path d='M468 400 q-10 40 6 60 q16 -20 6 -60z' fill='#7EC8FF'/>",
        mouth="<path d='M320 565 Q350 545 380 565' stroke='#7A1F3A' stroke-width='9' fill='none' stroke-linecap='round'/>",
        arms="<path d='M140 560 Q250 640 330 600' stroke='#F48FAA' stroke-width='52' fill='none' stroke-linecap='round'/><path d='M560 560 Q450 640 370 600' stroke='#F48FAA' stroke-width='52' fill='none' stroke-linecap='round'/>"),
    "thumb": dict(
        coin="<circle r='38' fill='#F2C230' stroke='#B8860B' stroke-width='6'/><text y='14' text-anchor='middle' font-size='40' font-weight='900' fill='#8A6508' font-family='sans-serif'>₩</text>",
        eyes="<path d='M225 355 Q265 310 305 355' stroke='#222' stroke-width='12' fill='none' stroke-linecap='round'/>"
             "<circle cx='435' cy='350' r='34' fill='#222'/><circle cx='447' cy='337' r='11' fill='#fff'/>",
        mouth="<path d='M300 545 Q350 605 400 545 Z' fill='#7A1F3A'/><path d='M325 575 Q350 595 375 575' fill='#FF6F8E'/>",
        arms="<path d='M95 470 Q50 520 120 600' stroke='#F48FAA' stroke-width='52' fill='none' stroke-linecap='round'/>"
             "<path d='M605 470 Q680 400 640 320' stroke='#F48FAA' stroke-width='52' fill='none' stroke-linecap='round'/>"
             "<rect x='600' y='225' width='70' height='80' rx='26' fill='#F48FAA' stroke='#E06C8C' stroke-width='5'/><rect x='612' y='160' width='34' height='85' rx='17' fill='#F48FAA' stroke='#E06C8C' stroke-width='5'/>"),
}


def mascots(out):
    os.makedirs(out, exist_ok=True)
    html_dir = os.path.join(out, "_svg"); os.makedirs(html_dir, exist_ok=True)
    js = ["const { chromium } = require('playwright');", "(async () => {", "const b = await chromium.launch();", "const p = await b.newPage({viewport:{width:700,height:820}});"]
    for name, parts in POSES.items():
        svg = MASCOT_SVG.format(**parts)
        sp = os.path.join(html_dir, name + ".svg"); open(sp, "w").write(svg)
        js.append("await p.goto('file://%s'); await p.screenshot({path:'%s', omitBackground:true});" % (sp, os.path.join(out, "mascot_%s.png" % name)))
    js += ["await b.close();", "})();"]
    jp = os.path.join(html_dir, "shot.js"); open(jp, "w").write("\n".join(js))
    subprocess.run(["node", jp], check=True)
    print("[mascot] 3종 완료")


def fallback_cards(work):
    """퍼블릭도메인 그림을 못 받은 키는 제목 카드(그라데이션+글자)로 대체."""
    titles = {"clay_tablet": ("메소포타미아 점토판", "기원전 3천 년, 빚의 기록"), "lydia_coin": ("리디아의 동전", "기원전 7세기"),
              "medici": ("메디치 가문", "피렌체, 1397년"), "voc_ships": ("대항해시대", "향신료를 찾아서"), "tulip_semper": ("튤립", "17세기 네덜란드"),
              "goldsmith": ("17세기 런던", "금세공업자의 금고"), "bank_england": ("잉글랜드은행", "1694년 런던"), "panic1907": ("1907년 공황", "뉴욕"),
              "bretton": ("브레턴우즈", "1944년 7월"), "weimar": ("바이마르 독일", "1923년"), "amsterdam_exchange": ("암스테르담 거래소", "1611년"),
              "moneychanger": ("환전상", "14세기 이탈리아"), "jpmorgan": ("J.P. 모건", "1907년 공황을 막은 은행가"), "bankrun": ("뱅크런", "1930년대 미국 은행 앞의 줄")}
    pd = os.path.join(work, "assets", "pd"); made = []
    for k, (t, s) in titles.items():
        p = os.path.join(pd, k + ".jpg")
        if os.path.exists(p):
            continue
        f = plt.figure(figsize=(19.2, 10.8), dpi=100); f.patch.set_facecolor("#14110E")
        ax = f.add_axes([0, 0, 1, 1]); ax.axis("off")
        import numpy as np
        g = np.linspace(0, 1, 256).reshape(1, -1); g = np.vstack([g] * 10)
        ax.imshow(g, extent=[0, 1, 0, 1], cmap=matplotlib.colors.LinearSegmentedColormap.from_list("x", ["#2A1A0E", "#5A3A1A", "#14110E"]), aspect="auto")
        ax.text(0.5, 0.55, t, ha="center", va="center", fontsize=110, color="#F4E6C8", fontweight="heavy")
        ax.text(0.5, 0.38, s, ha="center", va="center", fontsize=52, color="#C9B48A")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        f.savefig(p, facecolor=f.get_facecolor()); plt.close(f); made.append(k)
    print("[fallback] 대체 카드:", ", ".join(made) or "없음")


def wide(work):
    """B-roll/훅용 16:9: 흐린 배경 + 원본 전체 + 약간 어둡게."""
    pd = os.path.join(work, "assets", "pd"); out = os.path.join(work, "assets", "pd16"); os.makedirs(out, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(pd, "*.jpg"))):
        o = os.path.join(out, os.path.basename(f))
        fl = ("[0]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,gblur=sigma=28,eq=brightness=-0.18:saturation=0.8[bg];"
              "[0]scale=1920:1000:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuvj420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-filter_complex", fl, "-frames:v", "1", "-q:v", "3", o], check=True)
    print("[wide] 16:9 버전", len(glob.glob(os.path.join(out, "*.jpg"))), "장")
    # pip용 정지 영상: neogul-edit의 pip는 정지 이미지를 한 프레임만 읽어 페이드인 때문에 검게 나온다 → 짧은 mp4로 넣는다
    pv = os.path.join(work, "assets", "pipv"); os.makedirs(pv, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(pd, "*.jpg"))):
        o = os.path.join(pv, os.path.basename(f)[:-4] + ".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", f, "-t", "2", "-r", "30",
                        "-vf", "scale=1382:778:force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", o], check=True)
    print("[pipv] 정지 영상", len(glob.glob(os.path.join(pv, "*.mp4"))), "개")


if __name__ == "__main__":
    work = sys.argv[1]
    setup_fonts()
    what = sys.argv[2] if len(sys.argv) > 2 else "all"
    if what in ("all", "charts"):
        charts(os.path.join(work, "assets", "charts"))
    if what in ("all", "mascot"):
        mascots(os.path.join(work, "assets", "mascot"))
    if what in ("fallback", "final"):
        fallback_cards(work)
    if what in ("wide", "final"):
        wide(work)
