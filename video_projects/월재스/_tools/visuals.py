#!/usr/bin/env python3
"""월재스 공용 그림: 국기 배경(훅·B-roll), 썸네일(HTML → PNG, Playwright), 제목 카드.

  python visuals.py hookbg <국가코드 is|us|jp|kr> <출력.png> [--tilt]
  python visuals.py thumb <설정.json> <출력.png>
실존 인물 사진·합성은 쓰지 않는다. 국기·그래픽·숫자만 쓴다.
"""
import json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".claude", "skills", "neogul-edit", "scripts", "fonts"))


def flag_svg(code):
    """국기 SVG (비율은 각국 공식 비율 근사)."""
    if code == "is":   # 아이슬란드 18:25, 파랑 #02529C, 흰 십자 + 빨강 #DC1E35
        return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 25 18' preserveAspectRatio='xMidYMid slice'>"
                "<rect width='25' height='18' fill='#02529C'/><rect x='7' width='4' height='18' fill='#fff'/><rect y='7' width='25' height='4' fill='#fff'/>"
                "<rect x='8' width='2' height='18' fill='#DC1E35'/><rect y='8' width='25' height='2' fill='#DC1E35'/></svg>")
    if code == "jp":   # 일본 2:3, 흰 바탕 빨간 원(지름 = 세로의 3/5)
        return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 20' preserveAspectRatio='xMidYMid slice'>"
                "<rect width='30' height='20' fill='#fff'/><circle cx='15' cy='10' r='6' fill='#BC002D'/></svg>")
    if code == "us":   # 미국 10:19, 줄 13개, 별 50개
        h = 10.0; sh = h / 13
        s = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 19 10' preserveAspectRatio='xMidYMid slice'><rect width='19' height='10' fill='#fff'/>"]
        for i in range(0, 13, 2):
            s.append("<rect y='%.4f' width='19' height='%.4f' fill='#B22234'/>" % (i * sh, sh))
        cw, ch = 19 * 0.4, sh * 7
        s.append("<rect width='%.4f' height='%.4f' fill='#3C3B6E'/>" % (cw, ch))
        for r in range(9):
            n = 6 if r % 2 == 0 else 5
            for c in range(n):
                x = cw / 12 * (2 * c + 1 + (0 if r % 2 == 0 else 1)); y = ch / 10 * (r + 1)
                s.append("<text x='%.3f' y='%.3f' font-size='0.55' fill='#fff' text-anchor='middle' dominant-baseline='central'>&#9733;</text>" % (x, y))
        s.append("</svg>")
        return "".join(s)
    if code == "kr":   # 태극기 3:2 (괘·태극 근사)
        return ("<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='-36 -24 72 48' preserveAspectRatio='xMidYMid slice'>"
                "<rect x='-36' y='-24' width='72' height='48' fill='#fff'/>"
                "<g transform='rotate(-56.31)'><g id='b2'><path id='b' d='M-6-25H6M-6-22H6M-6-19H6' stroke='#000' stroke-width='2'/>"
                "<use xlink:href='#b' y='44'/></g><path stroke='#fff' stroke-width='1' d='M0,17v10'/>"
                "<circle fill='#CD2E3A' r='12'/><path fill='#0047A0' d='M0-12A6,6 0 0 0 0,0A6,6 0 0 1 0,12A12,12 0 0 1 0-12Z'/></g>"
                "<g transform='rotate(-123.69)'><use xlink:href='#b2'/><path stroke='#fff' stroke-width='1' d='M0-23.5v3M0,17v3.5M0,23.5v3'/></g></svg>")
    if code in ("chart_red", "chart_blue"):   # 국기 대신 쓰는 차트 배경(캔들+선)
        import random as _r
        rnd = _r.Random(7 if code == "chart_red" else 3)
        up = code == "chart_blue"
        bg, line = ("#1a0b0c", "#f2262b") if not up else ("#0a1424", "#4FA3FF")
        s = ["<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 90' preserveAspectRatio='xMidYMid slice'><rect width='160' height='90' fill='%s'/>" % bg]
        for gy in range(10, 90, 12):
            s.append("<line x1='0' y1='%d' x2='160' y2='%d' stroke='#ffffff' stroke-opacity='.06' stroke-width='.3'/>" % (gy, gy))
        y = 30.0 if not up else 70.0; pts = []
        for i in range(32):
            d = rnd.uniform(-3, 3) + (1.4 if not up else -1.4)
            o, c = y, max(8, min(84, y + d)); hi, lo = min(o, c) - rnd.uniform(.5, 3), max(o, c) + rnd.uniform(.5, 3)
            x = 3 + i * 5; col = "#f2262b" if c > o else "#4FA3FF"
            s.append("<line x1='%.1f' y1='%.1f' x2='%.1f' y2='%.1f' stroke='%s' stroke-width='.4' opacity='.75'/>" % (x, hi, x, lo, col))
            s.append("<rect x='%.1f' y='%.1f' width='2.6' height='%.1f' fill='%s' opacity='.8'/>" % (x - 1.3, min(o, c), max(.6, abs(c - o)), col))
            pts.append("%.1f,%.1f" % (x, c)); y = c
        s.append("<polyline points='%s' fill='none' stroke='%s' stroke-width='1.1' opacity='.9'/></svg>" % (" ".join(pts), line))
        return "".join(s)
    raise SystemExit("국기 코드 없음: " + code)


def shot(html, out, w=1920, h=1080):
    d = tempfile.mkdtemp()
    hp = os.path.join(d, "p.html"); open(hp, "w", encoding="utf-8").write(html)
    js = os.path.join(d, "s.js")
    open(js, "w").write("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:%d,height:%d}});"
                        "await p.goto('file://%s');await p.waitForTimeout(400);await p.screenshot({path:'%s'});await b.close();})();" % (w, h, hp, os.path.abspath(out)))
    subprocess.run(["node", js], check=True)


def font_css():
    return ("@font-face{font-family:P;src:url(file://%s/Pretendard-ExtraBold.otf);font-weight:900}"
            "@font-face{font-family:P;src:url(file://%s/Pretendard-Bold.otf);font-weight:700}" % (FONTS, FONTS))


def hookbg(code, out, tilt=True):
    """국기가 기울어진 채 화면을 채우고, 아래·가장자리를 어둡게(헤드라인 박스가 잘 보이게)."""
    svg = flag_svg(code).replace("'", "\\'")
    html = ("<!doctype html><html><head><meta charset='utf-8'><style>*{margin:0}body{width:1920px;height:1080px;overflow:hidden;background:#0b0a09}"
            ".f{position:absolute;inset:-12%%;background:url(\"data:image/svg+xml;utf8,%s\") center/cover;transform:%s;filter:saturate(1.05)}"
            ".v{position:absolute;inset:0;background:radial-gradient(ellipse 75%% 70%% at 60%% 45%%,transparent 35%%,rgba(8,6,5,.78) 100%%),"
            "linear-gradient(180deg,rgba(0,0,0,.15),rgba(0,0,0,.55))}"
            ".g{position:absolute;inset:0;background:repeating-linear-gradient(115deg,rgba(255,255,255,.05) 0 40px,rgba(0,0,0,.06) 40px 120px)}"
            "</style></head><body><div class='f'></div><div class='g'></div><div class='v'></div></body></html>"
            % (svg.replace('"', "'").replace("#", "%23"), "rotate(-6deg) scale(1.05)" if tilt else "none"))
    shot(html, out)


def thumb(cfg, out):
    """썸네일 공식 1·2(국기/상징 + 큰 결과 단어 + 노란 띠 부제) / 4(모순 문장 말풍선)."""
    c = json.load(open(cfg, encoding="utf-8")) if isinstance(cfg, str) else cfg
    svg = flag_svg(c["flag"]).replace('"', "'").replace("#", "%23")
    big = c["big"]; sub = c.get("sub", ""); kicker = c.get("kicker", ""); bubble = c.get("bubble", ""); num = c.get("num", "")
    color = c.get("color", "#FFE24A"); badge = c.get("badge", "")
    html = ("<!doctype html><html><head><meta charset='utf-8'><style>%s*{margin:0;padding:0;box-sizing:border-box}"
            "body{width:1280px;height:720px;overflow:hidden;font-family:P;background:#0b0a09}"
            ".f{position:absolute;inset:-14%%;background:url(\"data:image/svg+xml;utf8,%s\") center/cover;transform:rotate(-7deg)}"
            ".v{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.05) 30%%,rgba(0,0,0,.78) 100%%),radial-gradient(ellipse at 70%% 30%%,transparent 40%%,rgba(0,0,0,.45))}"
            ".k{position:absolute;left:40px;top:34px;font-weight:900;font-size:54px;color:#fff;text-shadow:0 5px 0 #000;letter-spacing:-2px}"
            ".big{position:absolute;left:36px;bottom:150px;font-weight:900;font-size:%dpx;line-height:1;color:%s;letter-spacing:-5px;-webkit-text-stroke:12px #000;paint-order:stroke fill;text-shadow:0 9px 0 #000}"
            ".sub{position:absolute;left:36px;bottom:46px;background:#FFE24A;color:#111;font-weight:900;font-size:50px;padding:10px 22px;border:5px solid #000;border-radius:10px;letter-spacing:-1.5px}"
            ".num{position:absolute;right:40px;top:40px;font-weight:900;font-size:150px;color:#4FA3FF;-webkit-text-stroke:10px #000;paint-order:stroke fill;transform:rotate(-6deg);text-shadow:0 8px 0 #000}"
            ".bub{position:absolute;right:50px;top:200px;background:#fff;color:#111;font-weight:900;font-size:44px;padding:18px 26px;border-radius:26px;border:5px solid #000;transform:rotate(3deg);max-width:560px}"
            ".bdg{position:absolute;left:36px;top:30px;background:#FD000A;color:#fff;font-weight:900;font-size:48px;padding:6px 20px 10px;border:5px solid #000;border-radius:10px;transform:rotate(-4deg)}"
            "</style></head><body><div class='f'></div><div class='v'></div>%s%s%s%s<div class='big'>%s</div>%s</body></html>"
            % (font_css(), svg, c.get("big_size", 150), color,
               "<div class='bdg'>%s</div>" % badge if badge else "", "<div class='k'>%s</div>" % kicker if kicker and not badge else "",
               "<div class='num'>%s</div>" % num if num else "", "<div class='bub'>%s</div>" % bubble if bubble else "",
               big, "<div class='sub'>%s</div>" % sub if sub else ""))
    shot(html, out, 1280, 720)


def arrow_svg(up, col):
    """두꺼운 지그재그 화살표(하락=오른쪽 아래, 상승=오른쪽 위)."""
    pts = "40,110 300,330 430,230 690,540" if not up else "40,570 300,350 430,450 690,140"
    tip = "600,620 760,450 780,640" if not up else "600,60 760,230 780,40"
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 680'>"
            "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='%s' stop-opacity='.1'/><stop offset='1' stop-color='%s'/></linearGradient></defs>"
            "<polyline points='%s' fill='none' stroke='url(#g)' stroke-width='62' stroke-linejoin='round' stroke-linecap='round'/>"
            "<polygon points='%s' fill='%s'/></svg>" % (col, col, pts, tip, col))


def _uri(svg):
    return "data:image/svg+xml;utf8," + svg.replace('"', "'").replace("#", "%23")


def thumb2(cfg, out):
    """다이나믹 썸네일(2026-11 개편): 어두운 차트 배경 + 거대 화살표 + 마스코트(실존 인물 대신) + 따옴표 헤드라인 + 빛나는 큰 숫자 + 배지.
    cfg 키: mood(down|up), mascot(shock|plead|thumb), flag(선택: 왼쪽 흐린 국기), badge, badge_color, q1, q2, cap, num, (q1_size, num_size)
    q1·q2 안의 <em>강조</em>는 분위기 색(하락 빨강 / 상승 초록)으로 칠한다."""
    c = json.load(open(cfg, encoding="utf-8")) if isinstance(cfg, str) else cfg
    up = c.get("mood", "down") == "up"
    col = c.get("color") or ("#19E36B" if up else "#FF2B2B")
    chart = flag_svg("chart_blue" if up else "chart_red")
    if up:
        chart = chart.replace("#4FA3FF", "#19E36B")
    plain = lambda t: re.sub(r"<[^>]+>", "", t)
    q1, q2, cap, num = c.get("q1", ""), c.get("q2", ""), c.get("cap", ""), c.get("num", "")
    v = dict(font=font_css(), chart=_uri(chart), arrow=_uri(arrow_svg(up, col)), col=col, bcol=c.get("badge_color") or col,
             masc=os.path.join(HERE, "assets", "mascot", "mascot_%s.png" % c.get("mascot", "thumb" if up else "shock")),
             q1s=c.get("q1_size", 100 if len(plain(q1)) <= 8 else (86 if len(plain(q1)) <= 10 else 74)),
             q2s=c.get("q2_size", 74 if len(plain(q2)) <= 9 else 62),
             ns=c.get("num_size", 176 if len(num) <= 5 else (150 if len(num) <= 7 else 120)),
             flag=("<div class='fl' style=\"background-image:url(&quot;%s&quot;)\"></div>" % _uri(flag_svg(c["flag"])).replace("'", "\\'")) if c.get("flag") else "",
             badge=("<div class='bd'>%s</div>" % c["badge"]) if c.get("badge") else "",
             q1=q1, q2=("<div class='q2'>%s</div>" % q2) if q2 else "", cap=("<div class='cap'>%s</div>" % cap) if cap else "",
             num=("<div class='n'>%s</div>" % num) if num else "")
    html = """<!doctype html><html><head><meta charset='utf-8'><style>%(font)s*{margin:0;padding:0;box-sizing:border-box}
body{width:1280px;height:720px;overflow:hidden;font-family:P;background:#07080b}
.ch{position:absolute;inset:-6%%;background:url("%(chart)s") center/cover;opacity:.6;filter:saturate(1.3);transform:scale(1.08) rotate(-3deg)}
.fl{position:absolute;left:-140px;top:-80px;width:780px;height:880px;background-size:cover;background-position:center;opacity:.35;transform:rotate(-8deg);
 -webkit-mask-image:radial-gradient(ellipse 60%% 55%% at 45%% 45%%,#000 30%%,transparent 75%%)}
.glow{position:absolute;inset:0;background:radial-gradient(circle at 80%% 74%%,%(col)s66 0,transparent 40%%),radial-gradient(circle at 20%% 60%%,%(col)s38 0,transparent 36%%),
 linear-gradient(90deg,rgba(0,0,0,.2),rgba(0,0,0,0) 32%%,rgba(0,0,0,.5) 55%%,rgba(0,0,0,.62))}
.ar{position:absolute;right:-30px;top:10px;width:820px;height:700px;background:url("%(arrow)s") center/contain no-repeat;opacity:.6;filter:drop-shadow(0 0 28px %(col)s)}
.m{position:absolute;left:-16px;bottom:-34px;height:640px;filter:drop-shadow(0 0 30px %(col)sbb) drop-shadow(0 18px 18px rgba(0,0,0,.7))}
.logo{position:absolute;left:24px;top:20px;background:#fff;color:#e8131b;font-weight:900;font-size:30px;padding:3px 14px 6px;border-radius:8px;letter-spacing:-1px;box-shadow:0 4px 0 #000}
.logo b{color:#111}
.bd{position:absolute;right:24px;top:20px;background:%(bcol)s;color:#fff;font-weight:900;font-size:46px;padding:2px 22px 8px;border-radius:10px;border:4px solid #fff;
 transform:rotate(3deg);box-shadow:0 0 26px %(bcol)s,0 5px 0 #000;text-shadow:0 3px 0 rgba(0,0,0,.4)}
.t{position:absolute;left:450px;right:20px;top:92px;text-align:center}
.q1{font-weight:900;font-size:%(q1s)spx;line-height:1.08;color:#fff;letter-spacing:-4px;-webkit-text-stroke:11px #000;paint-order:stroke fill;text-shadow:0 8px 0 #000,0 0 34px rgba(0,0,0,.9)}
.q2{margin-top:6px;font-weight:900;font-size:%(q2s)spx;line-height:1.08;color:#fff;letter-spacing:-3px;-webkit-text-stroke:9px #000;paint-order:stroke fill;text-shadow:0 7px 0 #000}
em{font-style:normal;color:%(col)s}
.cap{margin-top:16px;display:inline-block;font-weight:700;font-size:34px;color:#FFE24A;background:rgba(0,0,0,.65);padding:3px 16px 5px;border-radius:6px;letter-spacing:-1px}
.n{margin-top:0;font-weight:900;font-size:%(ns)spx;line-height:1.05;color:%(col)s;letter-spacing:-6px;-webkit-text-stroke:9px #000;paint-order:stroke fill;
 text-shadow:0 0 30px %(col)s,0 0 70px %(col)s99,0 10px 0 #000;transform:rotate(-3deg) skewX(-6deg)}
</style></head><body><div class='ch'></div>%(flag)s<div class='glow'></div><div class='ar'></div>
<img class='m' src='file://%(masc)s'><div class='logo'>월재스</div>%(badge)s
<div class='t'><div class='q1'>%(q1)s</div>%(q2)s%(cap)s%(num)s</div></body></html>""" % v
    shot(html, out, 1280, 720)


def brollcard(code, text, out, sub=""):
    """B-roll용: 펄럭이는 느낌의 국기(그라데이션 주름) + 왼쪽 위 장소·연도 라벨."""
    svg = flag_svg(code).replace('"', "'").replace("#", "%23")
    html = ("<!doctype html><html><head><meta charset='utf-8'><style>%s*{margin:0}body{width:1920px;height:1080px;overflow:hidden;background:#0b0a09;font-family:P}"
            ".f{position:absolute;inset:-8%%;background:url(\"data:image/svg+xml;utf8,%s\") center/cover;transform:perspective(1400px) rotateY(-14deg) rotateX(4deg) scale(1.08)}"
            ".w{position:absolute;inset:0;background:repeating-linear-gradient(100deg,rgba(255,255,255,.10) 0 90px,rgba(0,0,0,.16) 160px 260px,rgba(255,255,255,.06) 330px 380px)}"
            ".v{position:absolute;inset:0;background:radial-gradient(ellipse 80%% 75%% at 50%% 45%%,transparent 40%%,rgba(6,5,4,.82) 100%%)}"
            ".t{position:absolute;left:90px;top:80px;color:#fff;font-weight:900;font-size:64px;letter-spacing:-2px;text-shadow:0 6px 0 rgba(0,0,0,.6)}"
            ".s{position:absolute;left:94px;top:166px;color:#FFE24A;font-weight:900;font-size:40px;text-shadow:0 4px 0 rgba(0,0,0,.6)}"
            "</style></head><body><div class='f'></div><div class='w'></div><div class='v'></div><div class='t'>%s</div><div class='s'>%s</div></body></html>"
            % (font_css(), svg, text, sub))
    shot(html, out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "hookbg":
        hookbg(sys.argv[2], sys.argv[3], "--flat" not in sys.argv)
    elif cmd == "broll":
        brollcard(sys.argv[2], sys.argv[4], sys.argv[3], sys.argv[5] if len(sys.argv) > 5 else "")
    elif cmd == "thumb":
        thumb(sys.argv[2], sys.argv[3])
    elif cmd == "thumb2":
        thumb2(sys.argv[2], sys.argv[3])
