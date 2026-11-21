#!/usr/bin/env python3
"""월재스 공용 그림: 국기 배경(훅·B-roll), 썸네일(HTML → PNG, Playwright), 제목 카드.

  python visuals.py hookbg <국가코드 is|us|jp|kr> <출력.png> [--tilt]
  python visuals.py thumb <설정.json> <출력.png>
실존 인물 사진·합성은 쓰지 않는다. 국기·그래픽·숫자만 쓴다.
"""
import json, os, subprocess, sys, tempfile

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
