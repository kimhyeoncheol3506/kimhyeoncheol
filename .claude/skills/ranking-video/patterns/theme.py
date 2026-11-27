# -*- coding: utf-8 -*-
"""영상 패턴 10가지의 화면 톤(색·배경·장식·자막·전환·썸네일)을 HyperFrames 생성기에 넘겨 주는 공용 모듈.
사용(생성기 안): sys.path.insert(0, PATTERNS); import theme as TH; TM = TH.load(ROOT)
  - 프로젝트 00_data/pattern.json {"num": 3, ...} 이 없으면 0번(기존 먹색+금색) → 예전 편은 그대로 다시 만들어진다.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
THEMES = json.load(open(f"{HERE}/themes.json", encoding="utf-8"))
FONT_FILES = ("NanumMyeongjo-ExtraBold.ttf", "Pretendard-Bold.otf", "Pretendard-SemiBold.otf", "Pretendard-ExtraBold.otf", "BlackHanSans-Regular.ttf")


def load(root=None, num=None):
    if num is None:
        p = f"{root}/00_data/pattern.json" if root else None
        num = json.load(open(p, encoding="utf-8"))["num"] if p and os.path.exists(p) else 0
    T = json.loads(json.dumps(THEMES[str(int(num))])); T["num"] = int(num)
    return T


def fonts(prefix="assets/fonts/"):
    return (f'@font-face{{font-family:"MJ";src:url("{prefix}NanumMyeongjo-ExtraBold.ttf");font-weight:800}}'
            f'@font-face{{font-family:"PX";src:url("{prefix}Pretendard-Bold.otf");font-weight:700}}'
            f'@font-face{{font-family:"PX";src:url("{prefix}Pretendard-SemiBold.otf");font-weight:500}}'
            f'@font-face{{font-family:"PXB";src:url("{prefix}Pretendard-ExtraBold.otf");font-weight:800}}'
            f'@font-face{{font-family:"BH";src:url("{prefix}BlackHanSans-Regular.ttf");font-weight:400}}')


def head_css(T):
    """제목 글꼴(.mj 클래스): 명조(다큐) · 블랙한산스(임팩트) · 프리텐다드 엑스트라볼드(인포그래픽)"""
    return {"MJ": ".mj{font-family:MJ,serif;font-weight:800}",
            "BH": ".mj{font-family:BH,sans-serif;font-weight:400;letter-spacing:-.01em}",
            "PXB": ".mj{font-family:PXB,PX,sans-serif;font-weight:800;letter-spacing:-.02em}"}[T["head"]]


def bg_css(T, w=1920, h=1080):
    c = T["c"]; ink, b2, b3 = c["ink"], c["bg2"], c["bg3"]; k = T["bg"]
    if k == "radial": return f"background:radial-gradient({w * .78:.0f}px {h * .83:.0f}px at 30% 20%,{b2} 0%,{ink} 60%,{b3} 100%)"
    if k == "flat": return f"background:linear-gradient(180deg,{b2} 0%,{ink} 70%,{b3} 100%)"
    if k == "paper": return (f"background:repeating-linear-gradient(0deg,{c['line']}05 0 2px,transparent 2px 5px),"
                             f"radial-gradient({w}px {h}px at 50% 40%,{b2} 0%,{ink} 65%,{b3} 100%)")
    if k == "scan": return (f"background:repeating-linear-gradient(0deg,#ffffff06 0 2px,transparent 2px 6px),"
                            f"linear-gradient(160deg,{b2} 0%,{ink} 55%,{b3} 100%)")
    if k == "rays": return (f"background:repeating-conic-gradient(from 0deg at 50% -10%,#ffffff07 0deg 6deg,transparent 6deg 14deg),"
                            f"radial-gradient({w}px {h}px at 50% 0%,{b2} 0%,{ink} 60%,{b3} 100%)")
    if k == "dots": return f"background:radial-gradient({c['grey']}66 2px,transparent 2.5px) 0 0/34px 34px,linear-gradient(180deg,{b2},{ink})"
    if k == "grid": return (f"background:linear-gradient(#ffffff0c 1px,transparent 1px) 0 0/96px 96px,linear-gradient(90deg,#ffffff0c 1px,transparent 1px) 0 0/96px 96px,"
                            f"linear-gradient(180deg,{b2},{ink} 70%,{b3})")
    if k == "labgrid": return (f"background:linear-gradient({c['acc']}22 1px,transparent 1px) 0 0/120px 120px,linear-gradient(90deg,{c['acc']}22 1px,transparent 1px) 0 0/120px 120px,"
                               f"linear-gradient({c['acc']}0d 1px,transparent 1px) 0 0/24px 24px,linear-gradient(90deg,{c['acc']}0d 1px,transparent 1px) 0 0/24px 24px,{ink}")
    if k == "split": return (f"background:linear-gradient(180deg,#00000000 0%,#000000aa 100%),"
                             f"linear-gradient(100deg,{b2} 0%,{b2}cc 49.6%,{c['acc']} 49.6% 50.4%,{b3}cc 50.4%,{b3} 100%)")
    raise KeyError(k)


def deco_html(T, P="", w=1920, h=1080):
    """장면마다 깔리는 패턴 고유 장식(윗부분·가장자리만 — 가운데 내용·아래 자막 칸은 비움)"""
    c = T["c"]; k = T["deco"]; acc, acc2 = c["acc"], c["acc2"]
    if k == "frame": return f'<div style="position:absolute;left:36px;top:36px;right:36px;bottom:24px;border:1px solid {acc}55"></div>'
    if k == "pricetag":
        return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:14px;background:{acc}"></div>'
                f'<div style="position:absolute;right:70px;top:14px;padding:10px 26px 14px;background:{acc};color:#fff;font:30px BH;letter-spacing:.06em;clip-path:polygon(0 0,100% 0,100% 100%,50% 82%,0 100%)">PRICE CHECK</div>')
    if k == "hazard":
        st = f"repeating-linear-gradient(-45deg,{acc} 0 26px,#000 26px 52px)"
        return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:22px;background:{st}"></div>'
                f'<div style="position:absolute;left:0;top:22px;width:18px;bottom:0;background:{st};opacity:.85"></div>'
                f'<div style="position:absolute;right:60px;top:40px;padding:6px 20px;border:4px solid {acc2};color:{acc2};font:34px BH;letter-spacing:.1em">WARNING</div>')
    if k == "vignette":
        return (f'<div style="position:absolute;inset:0;background:radial-gradient({w * .7:.0f}px {h * .7:.0f}px at 50% 45%,transparent 55%,{c["bg3"]}cc 100%)"></div>'
                f'<div style="position:absolute;left:30px;top:30px;right:30px;bottom:22px;border:2px solid {acc}55;outline:1px solid {acc}33;outline-offset:-10px"></div>')
    if k == "recon":
        br = lambda s: f'<div style="position:absolute;{s};width:70px;height:70px;border-color:{acc};border-style:solid"></div>'
        return (br("left:40px;top:40px;border-width:5px 0 0 5px") + br("right:40px;top:40px;border-width:5px 5px 0 0")
                + f'<div style="position:absolute;right:130px;top:52px;display:flex;align-items:center;gap:12px;font:700 30px PX;color:{acc};letter-spacing:.12em">'
                  f'<span style="width:20px;height:20px;border-radius:50%;background:{acc}"></span>사례 재구성</div>')
    if k == "badge":
        return (f'<div style="position:absolute;right:-90px;top:40px;width:400px;padding:12px 0;transform:rotate(35deg);text-align:center;background:linear-gradient(90deg,{acc2},{acc});'
                f'color:#1a1200;font:32px BH;letter-spacing:.12em;box-shadow:0 6px 20px #0008">RANKING</div>'
                f'<div style="position:absolute;left:0;top:0;width:{w}px;height:8px;background:linear-gradient(90deg,{acc},{acc2})"></div>')
    if k == "receipt":
        zz = f"conic-gradient(from -45deg at 50% 0,{c['card']} 90deg,transparent 0) 0 0/36px 18px repeat-x"
        return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:18px;background:{zz};transform:scaleY(-1)"></div>'
                f'<div style="position:absolute;left:40px;top:40px;right:40px;bottom:26px;border:3px dashed {c["grey"]}"></div>'
                f'<div style="position:absolute;right:80px;top:50px;font:700 28px PX;color:{acc};letter-spacing:.2em">RECEIPT · 영수증 계산</div>')
    if k == "ticker":
        return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:12px;background:linear-gradient(90deg,{c["down"]} 0 50%,{c["up"]} 50% 100%)"></div>'
                f'<div style="position:absolute;right:70px;top:42px;display:flex;align-items:center;gap:12px;font:800 30px PXB;color:{c["up"]};letter-spacing:.1em">'
                f'<span style="width:18px;height:18px;border-radius:50%;background:{c["up"]};box-shadow:0 0 14px {c["up"]}"></span>LIVE 시세 점검</div>')
    if k == "flow":
        steps = "".join(f'<span style="padding:6px 18px;border:2px solid {acc};border-radius:30px;background:{c["card"]}">{s}</span>' + (f'<span style="color:{acc2};font-size:34px">➜</span>' if i < 2 else "")
                        for i, s in enumerate(("산지", "경매", "소매")))
        return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:10px;background:linear-gradient(90deg,{acc2},{acc})"></div>'
                f'<div style="position:absolute;right:70px;top:40px;display:flex;align-items:center;gap:12px;font:700 28px PX;color:{acc}">{steps}</div>')
    if k == "scale":
        ticks = "".join(f'<div style="position:absolute;left:{x}px;top:0;width:2px;height:{26 if x % 120 == 0 else 12}px;background:{acc}"></div>' for x in range(0, w, 24))
        return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:30px">{ticks}</div>'
                f'<div style="position:absolute;right:70px;top:46px;padding:6px 20px;background:{c["text"]};color:#7CFFCB;font:800 30px PXB;letter-spacing:.14em;border-radius:6px">LAB 0.0g</div>')
    if k == "vs":
        return (f'<div style="position:absolute;left:{w / 2 - 70:.0f}px;top:24px;width:140px;height:96px;display:flex;align-items:center;justify-content:center;'
                f'background:{acc};color:#000;font:72px BH;transform:skewX(-10deg);box-shadow:0 8px 30px #000a">VS</div>'
                f'<div style="position:absolute;left:0;top:0;width:{w / 2:.0f}px;height:10px;background:{c["bg2"]};filter:brightness(1.4)"></div>'
                f'<div style="position:absolute;left:{w / 2:.0f}px;top:0;width:{w / 2:.0f}px;height:10px;background:{c["bg3"]};filter:brightness(1.4)"></div>')
    raise KeyError(k)


def wipe_html(T, P):
    """장면 시작 전환용 요소. id는 P+'wipe' (기존 생성기와 같은 이름)"""
    c = T["c"]; k = T["wipe"]; acc = c["acc"]
    if k == "line": return f'<div class="wipe" id="{P}wipe" style="position:absolute;left:0;top:538px;width:1920px;height:3px;background:linear-gradient(90deg,transparent,{c["acc2"]},{acc},transparent)"></div>'
    if k == "push": return f'<div id="{P}wipe" style="position:absolute;left:0;top:0;width:1920px;height:1080px;background:{acc}"></div>'
    if k == "stripes": return f'<div id="{P}wipe" style="position:absolute;left:-200px;top:0;width:2320px;height:1080px;background:repeating-linear-gradient(-45deg,{acc} 0 60px,#000 60px 120px)"></div>'
    if k in ("dissolve", "cut", "zoom", "slideup"):
        bgc = {"dissolve": c["bg3"], "cut": acc, "zoom": c["acc2"], "slideup": c["card"]}[k]
        return f'<div id="{P}wipe" style="position:absolute;inset:0;background:{bgc};opacity:0"></div>'
    if k == "shutter": return f'<div id="{P}wipe" style="position:absolute;inset:0;display:flex">' + "".join(f'<div class="{P}sh" style="flex:1;background:{c["bg3"]};border-right:2px solid {acc}55"></div>' for _ in range(8)) + '</div>'
    if k == "arrow": return (f'<div id="{P}wipe" style="position:absolute;left:0;top:470px;width:1920px;height:140px">'
                             f'<div style="position:absolute;left:0;top:40px;right:120px;height:60px;background:linear-gradient(90deg,{c["acc2"]}00,{acc})"></div>'
                             f'<div style="position:absolute;right:0;top:0;width:0;height:0;border-top:70px solid transparent;border-bottom:70px solid transparent;border-left:130px solid {acc}"></div></div>')
    if k == "scan": return f'<div id="{P}wipe" style="position:absolute;left:0;top:0;width:1920px;height:8px;background:{acc};box-shadow:0 0 30px {acc},0 0 80px {acc}88;opacity:0"></div>'
    if k == "doors": return (f'<div id="{P}wipe" style="position:absolute;inset:0"><div id="{P}dl" style="position:absolute;left:0;top:0;width:960px;height:1080px;background:{c["bg2"]}"></div>'
                             f'<div id="{P}dr" style="position:absolute;left:960px;top:0;width:960px;height:1080px;background:{c["bg3"]}"></div></div>')
    raise KeyError(k)


def wipe_js(T, fade=True, dur=None):
    """GSAP 전환(장면 시작). $()와 tl은 생성기 js0 안에 이미 있다. speed = 전환 길이(초)"""
    s = T["speed"]; k = T["wipe"]; out = []
    cin = lambda frm, extra="": out.append(f'tl.fromTo($("content"), {{ {frm} }}, {{ opacity: 1, x: 0, y: 0, scale: 1, duration: {s:.2f}, ease: "power3.out"{extra} }}, {s * .5:.2f});') if fade else None
    if k == "line":
        out.append('tl.fromTo($("wipe"), { scaleX: 0, opacity: 1, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.57, ease: "power3.inOut" }, 0); tl.to($("wipe"), { opacity: 0, duration: 0.38 }, 0.57);')
        if fade: out.append('tl.fromTo($("content"), { opacity: 0 }, { opacity: 1, duration: 0.6 }, 0.3);')
    elif k == "push":
        out.append(f'tl.fromTo($("wipe"), {{ xPercent: -100 }}, {{ xPercent: 0, duration: {s * .5:.2f}, ease: "power2.in" }}, 0); tl.to($("wipe"), {{ xPercent: 100, duration: {s * .5:.2f}, ease: "power2.out" }}, {s * .5:.2f});')
        cin("opacity: 0, x: 140")
    elif k == "stripes":
        out.append(f'tl.fromTo($("wipe"), {{ xPercent: -100 }}, {{ xPercent: 100, duration: {s * 1.6:.2f}, ease: "none" }}, 0);')
        cin("opacity: 0, scale: 1.08")
    elif k == "dissolve":
        out.append(f'tl.fromTo($("wipe"), {{ opacity: 1 }}, {{ opacity: 0, duration: {s:.2f}, ease: "sine.inOut" }}, 0);')
        if fade: out.append(f'tl.fromTo($("content"), {{ opacity: 0 }}, {{ opacity: 1, duration: {s:.2f}, ease: "sine.inOut" }}, 0.1);')
    elif k == "shutter":
        out.append(f'tl.fromTo($("wipe") + " > div", {{ scaleY: 1, transformOrigin: "50% 0%" }}, {{ scaleY: 0, duration: {s:.2f}, ease: "power3.inOut", stagger: 0.035 }}, 0);')
        cin("opacity: 0")
    elif k == "zoom":
        out.append(f'tl.fromTo($("wipe"), {{ opacity: .9 }}, {{ opacity: 0, duration: {s:.2f} }}, 0);')
        cin("opacity: 0, scale: .82", ', ease: "back.out(1.6)"')
    elif k == "slideup":
        out.append(f'tl.fromTo($("wipe"), {{ opacity: 1, yPercent: 0 }}, {{ yPercent: -100, duration: {s:.2f}, ease: "power3.inOut" }}, 0);')
        cin("opacity: 0, y: 90")
    elif k == "cut":
        out.append(f'tl.fromTo($("wipe"), {{ opacity: .55 }}, {{ opacity: 0, duration: 0.12 }}, 0);')
        if fade: out.append('tl.set($("content"), { opacity: 1 }, 0);')
    elif k == "arrow":
        out.append(f'tl.fromTo($("wipe"), {{ xPercent: -110 }}, {{ xPercent: 110, duration: {s * 1.4:.2f}, ease: "power2.inOut" }}, 0);')
        cin("opacity: 0, x: -80")
    elif k == "scan":
        out.append(f'tl.fromTo($("wipe"), {{ opacity: 1, y: 0 }}, {{ y: 1072, duration: {s * 1.6:.2f}, ease: "none" }}, 0); tl.to($("wipe"), {{ opacity: 0, duration: 0.15 }}, {s * 1.6:.2f});')
        if fade: out.append(f'tl.fromTo($("content"), {{ opacity: 0, clipPath: "inset(0 0 100% 0)" }}, {{ opacity: 1, clipPath: "inset(0 0 0% 0)", duration: {s * 1.6:.2f}, ease: "none" }}, 0);')
    elif k == "doors":
        out.append(f'tl.fromTo($("dl"), {{ xPercent: 0 }}, {{ xPercent: -100, duration: {s * 1.3:.2f}, ease: "power3.inOut" }}, 0.05); tl.fromTo($("dr"), {{ xPercent: 0 }}, {{ xPercent: 100, duration: {s * 1.3:.2f}, ease: "power3.inOut" }}, 0.05);')
        cin("opacity: 0, scale: .94")
    if T.get("zoom") and dur:
        out.append(f'tl.fromTo($("zoomwrap"), {{ scale: 1 }}, {{ scale: {1 + T["zoom"]:.3f}, duration: {dur:.2f}, ease: "none" }}, 0);')
    return "\n".join(x for x in out if x)


def card_css(T, pad="34px 40px"):
    c = T["c"]; light = T["c"]["ink"].upper() > "#AAAAAA"
    sh = "box-shadow:0 12px 34px #0000001f;" if light else ""
    rad = {"6": "18px", "8": "14px", "9": "10px", "5": "16px"}.get(str(T["num"]), "0")
    return f".card{{position:absolute;opacity:0;background:{c['card']};border:{'2px' if light else '1px'} solid {c['acc']}66;padding:{pad};border-radius:{rad};{sh}}}"


def cap_css(T, short=False):
    """자막: 크기는 87px(쇼츠 84px) 그대로, 위치·상자 모양·강조색만 패턴마다 다르다"""
    q = T["cap"]; fs = 84 if short else 87; bot = 440 if short else 56
    base = f'.cap{{position:absolute;left:0;right:0;bottom:{bot}px;text-align:center;overflow:visible}}.cap b{{color:{q["hl"]};font-weight:700}}'
    span = f'display:inline-block;color:{q["text"]};font-size:{fs}px;font-weight:700;line-height:1.2;white-space:nowrap;'
    st = q["style"]; rad = q.get("radius", 0)
    if st == "box": span += f'background:{q["box"]};padding:6px 26px;border-radius:{rad}px;' + (f'border:4px solid {q["border"]};' if q.get("border") else "")
    elif st == "pill": span += f'background:{q["box"]};padding:6px 46px;border-radius:{rad}px;border:3px solid {T["c"]["acc"]};'
    elif st == "plain": span += 'text-shadow:0 0 6px #fff,0 0 14px #fff,0 0 22px #ffffffcc;padding:0 10px;'
    elif st == "underline": span += f'background:{q["box"]};padding:4px 26px;border-bottom:8px solid {T["c"]["acc"]};'
    elif st == "led": span += f'background:{q["box"]};padding:6px 34px;border:4px solid {q["border"]};border-radius:{rad}px;letter-spacing:.03em;box-shadow:0 0 24px {q["border"]}55;'
    elif st == "strip":
        base = (f'.cap{{position:absolute;left:0;right:0;bottom:{bot - 26 if not short else bot}px;text-align:center;background:{q["box"]};border-top:4px solid {T["c"]["acc"]};padding:6px 0 10px}}'
                f'.cap b{{color:{q["hl"]};font-weight:700}}')
        span += 'padding:0 20px;'
    elif st == "bar":
        base = (f'.cap{{position:absolute;left:{70 if not short else 40}px;right:0;bottom:{bot + 10}px;text-align:left;overflow:visible}}.cap b{{color:{q["hl"]};font-weight:700}}')
        span += f'background:{q["box"]};padding:6px 30px 6px 26px;border-left:14px solid {T["c"]["acc"]};'
    return base + f'.cap span{{{span}}}'


def layer(T, P, body, w=1920, h=1080):
    """배경 + 장식 + (천천히 줌되는) 내용. 기존 생성기 scene()의 bg/frame 자리에 넣는다"""
    return (f'<div style="position:absolute;inset:0;{bg_css(T, w, h)}"></div>'
            f'<div id="{P}zoomwrap" style="position:absolute;inset:0;transform-origin:50% 45%">{deco_html(T, P, w, h)}'
            f'<div id="{P}content" style="position:absolute;inset:0">{body}</div></div>')


# ------------------------------------------------------------------ 썸네일 틀 (1280×720) — 패턴마다 구도가 다르다
def thumb_html(T, d, img, img2=None, fontdir="assets/fonts/"):
    """d: top·big·sub·tag (+ 패턴별: from·to·pct·dir·steps·a·b·a_sub·b_sub·rank·budget·q). img/img2: 사진 경로(URL)"""
    c = T["c"]; n = T["num"]; acc, acc2 = c["acc"], c["acc2"]
    css = fonts(fontdir) + "body{margin:0}.t{position:absolute;white-space:nowrap}"
    S = lambda s: f'text-shadow:0 6px 0 {s}'
    ph = lambda st, extra="": f'<img src="{img}" style="position:absolute;{st};object-fit:cover;{extra}">'
    if n == 1:   # 흰 배경 + 빨간 가격표 + 물음표
        h = (f'<div style="position:absolute;inset:0;background:#F7F5F0"></div>' + ph("right:0;top:0;width:560px;height:720px")
             + f'<div style="position:absolute;right:0;top:0;width:560px;height:720px;background:linear-gradient(90deg,#F7F5F0,#F7F5F000 40%)"></div>'
             f'<div class="t" style="left:50px;top:40px;font:58px BH;color:#1B1B1B">{d["top"]}</div>'
             f'<div class="t" style="left:40px;top:150px;padding:10px 40px 10px 30px;background:{acc};color:#fff;font:150px BH;clip-path:polygon(0 0,92% 0,100% 50%,92% 100%,0 100%)">{d["big"]}</div>'
             f'<div class="t" style="left:50px;top:400px;font:92px BH;color:#1B1B1B">{d["sub"]}</div>'
             f'<div class="t" style="right:40px;top:300px;font:330px BH;color:{acc};{S("#00000033")};transform:rotate(12deg)">?</div>'
             f'<div class="t" style="left:50px;bottom:40px;padding:6px 22px;border:5px solid #1B1B1B;font:54px BH;color:#1B1B1B">{d["tag"]}</div>')
    elif n == 2:  # 검정 + 형광 노랑 + 빨간 X + 숫자
        h = ('<div style="position:absolute;inset:0;background:#090909"></div>' + ph("left:0;top:0;width:620px;height:720px", "filter:brightness(.7)")
             + f'<div class="t" style="left:40px;top:60px;width:540px;height:540px;font:560px/540px BH;color:{acc2};text-align:center;{S("#000")}">✕</div>'
             f'<div style="position:absolute;left:0;top:0;width:1280px;height:26px;background:repeating-linear-gradient(-45deg,{acc} 0 26px,#000 26px 52px)"></div>'
             f'<div class="t" style="left:640px;top:70px;font:70px BH;color:#fff">{d["top"]}</div>'
             f'<div class="t" style="left:630px;top:160px;font:250px BH;color:{acc};line-height:1">{d["big"]}</div>'
             f'<div class="t" style="left:640px;top:430px;font:84px BH;color:#fff">{d["sub"]}</div>'
             f'<div class="t" style="left:640px;bottom:46px;padding:6px 22px;background:{acc};font:56px BH;color:#000">{d["tag"]}</div>')
    elif n == 3:  # 베이지 다큐 + 원형 그림 + 질문 한 줄(명조)
        h = ('<div style="position:absolute;inset:0;background:radial-gradient(900px 600px at 70% 50%,#F7EFE2,#E3D3B8)"></div>'
             + f'<div style="position:absolute;right:70px;top:80px;width:560px;height:560px;border-radius:50%;overflow:hidden;border:10px solid #F8F1E5;box-shadow:0 14px 40px #5a402a55">'
             f'<img src="{img}" style="width:100%;height:100%;object-fit:cover;filter:sepia(.45) saturate(.9) contrast(1.05)"></div>'
             f'<div class="t" style="left:60px;top:70px;font:800 46px MJ;color:{acc}">{d["top"]}</div>'
             f'<div style="position:absolute;left:56px;top:150px;width:640px;font:800 92px/1.18 MJ;color:#3B2F25;word-break:keep-all">{d["big"]}</div>'
             f'<div class="t" style="left:60px;bottom:60px;font:800 54px MJ;color:{acc}">{d["sub"]}</div>')
    elif n == 4:  # 남색 + 경고 빨강 + 숫자 대비 + 재구성 도장
        h = (f'<div style="position:absolute;inset:0;background:#0B1530"></div>' + ph("left:0;top:0;width:1280px;height:720px", "filter:brightness(.35) saturate(.6) hue-rotate(-10deg)")
             + f'<div class="t" style="left:50px;top:40px;font:800 52px PXB;color:#fff">{d["top"]}</div>'
             f'<div class="t" style="left:40px;top:150px;font:200px BH;color:#fff;{S("#000")}">{d["from"]}<span style="color:{acc};font-size:150px"> → </span><span style="color:{acc}">{d["to"]}</span></div>'
             f'<div class="t" style="left:50px;top:420px;font:88px BH;color:#fff;{S("#000")}">{d["sub"]}</div>'
             f'<div class="t" style="right:50px;bottom:50px;padding:8px 26px;border:7px solid {acc};color:{acc};font:64px BH;transform:rotate(-8deg)">{d["tag"]}</div>')
    elif n == 5:  # 순위 배지 + 1위 품목 크게
        h = ('<div style="position:absolute;inset:0;background:#101828"></div>' + ph("right:0;top:0;width:760px;height:720px")
             + '<div style="position:absolute;inset:0;background:linear-gradient(90deg,#101828 30%,#10182800 75%)"></div>'
             f'<div style="position:absolute;left:40px;top:60px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFE08A,{acc} 55%,{acc2});'
             f'display:flex;align-items:center;justify-content:center;font:150px BH;color:#2a1800;box-shadow:0 12px 40px #000a">{d["rank"]}</div>'
             f'<div class="t" style="left:380px;top:90px;font:64px BH;color:{acc}">{d["top"]}</div>'
             f'<div class="t" style="left:370px;top:170px;font:190px BH;color:#fff;{S("#000")}">{d["big"]}</div>'
             f'<div class="t" style="left:50px;top:420px;font:110px BH;color:#32D583;{S("#000")}">{d["sub"]}</div>'
             f'<div class="t" style="left:50px;bottom:40px;padding:6px 24px;background:{acc};font:54px BH;color:#111">{d["tag"]}</div>')
    elif n == 6:  # 크림 배경 + 예산 금액 + 접시(원형 사진) + 영수증
        h = ('<div style="position:absolute;inset:0;background:#FFF6E0"></div>'
             f'<div style="position:absolute;right:60px;top:70px;width:540px;height:540px;border-radius:50%;overflow:hidden;border:22px solid #fff;box-shadow:0 18px 40px #0003"><img src="{img}" style="width:100%;height:100%;object-fit:cover"></div>'
             f'<div style="position:absolute;left:50px;top:40px;width:560px;padding:26px 34px 40px;background:#fff;box-shadow:0 10px 30px #0002;clip-path:polygon(0 0,100% 0,100% 94%,95% 100%,90% 94%,85% 100%,80% 94%,75% 100%,70% 94%,65% 100%,60% 94%,55% 100%,50% 94%,45% 100%,40% 94%,35% 100%,30% 94%,25% 100%,20% 94%,15% 100%,10% 94%,5% 100%,0 94%)">'
             f'<div style="font:800 40px PXB;color:#7A7266;letter-spacing:.1em">{d["top"]}</div><div style="font:170px BH;color:{acc};line-height:1.05">{d["budget"]}</div>'
             f'<div style="border-top:4px dashed #ccc;margin:16px 0;padding-top:14px;font:96px BH;color:#222">{d["big"]}</div></div>'
             f'<div class="t" style="left:60px;bottom:44px;padding:6px 24px;background:{acc2};font:56px BH;color:#fff;border-radius:14px">{d["tag"]}</div>')
    elif n == 7:  # 증권 차트 + 화살표 + 퍼센트
        up = d.get("dir", "up") == "up"; col = c["up"] if up else c["down"]
        pts = "40,600 260,560 480,580 700,500 920,330 1240,120" if up else "40,120 260,180 480,160 700,300 920,470 1240,640"
        h = (f'<div style="position:absolute;inset:0;background:linear-gradient(#ffffff10 1px,transparent 1px) 0 0/80px 80px,linear-gradient(90deg,#ffffff10 1px,transparent 1px) 0 0/80px 80px,#0E1117"></div>'
             + ph("right:0;top:0;width:520px;height:720px", "filter:brightness(.55);opacity:.8")
             + f'<svg width="1280" height="720" style="position:absolute;left:0;top:0"><polyline points="{pts}" fill="none" stroke="{col}" stroke-width="14" stroke-linejoin="round"/></svg>'
             f'<div class="t" style="left:50px;top:40px;padding:4px 18px;background:{col};font:800 48px PXB;color:#fff">{d["top"]}</div>'
             f'<div class="t" style="left:40px;top:150px;font:200px BH;color:#fff;{S("#000")}">{d["big"]}</div>'
             f'<div class="t" style="left:40px;top:370px;font:230px BH;color:{col};{S("#000")}">{"▲" if up else "▼"}{d["pct"]}</div>'
             f'<div class="t" style="right:40px;bottom:40px;font:800 52px PXB;color:{acc}">{d["tag"]}</div>')
    elif n == 8:  # 가격 3단 화살표
        st = d["steps"]
        box = lambda i, lab, val, bg, fg: (f'<div style="position:absolute;left:{40 + i * 420}px;top:{430 - i * 120}px;width:360px;padding:22px 20px;background:{bg};color:{fg};border-radius:16px;text-align:center;box-shadow:0 10px 26px #0f254033">'
                                          f'<div style="font:800 46px PXB">{lab}</div><div style="font:96px BH;line-height:1.1">{val}</div></div>')
        h = ('<div style="position:absolute;inset:0;background:#EEF3F8"></div>' + ph("right:0;top:0;width:420px;height:300px", "opacity:.9")
             + f'<div class="t" style="left:50px;top:40px;font:84px BH;color:#0F2540">{d["big"]}</div>'
             + "".join(box(i, a, b, bg, fg) for i, ((a, b), (bg, fg)) in enumerate(zip(st, [("#fff", "#0F2540"), (acc, "#fff"), ("#D64545", "#fff")])))
             + "".join(f'<div class="t" style="left:{385 + i * 420}px;top:{455 - i * 120}px;font:110px BH;color:{acc2}">➜</div>' for i in range(2))
             + f'<div class="t" style="left:50px;bottom:36px;font:800 50px PXB;color:{acc}">{d["tag"]}</div>')
    elif n == 9:  # 실험실 저울 숫자 대비
        lcd = lambda v, x: (f'<div style="position:absolute;left:{x}px;top:250px;width:520px;padding:18px 0;background:#102A43;border-radius:18px;text-align:center;box-shadow:0 12px 30px #102a4344">'
                            f'<div style="font:800 140px PXB;color:#7CFFCB;letter-spacing:.04em;font-variant-numeric:tabular-nums">{v}</div></div>')
        h = (f'<div style="position:absolute;inset:0;background:linear-gradient({acc}22 1px,transparent 1px) 0 0/80px 80px,linear-gradient(90deg,{acc}22 1px,transparent 1px) 0 0/80px 80px,#FAFCFC"></div>'
             + ph("left:0;top:0;width:1280px;height:220px", "opacity:.35")
             + f'<div class="t" style="left:50px;top:50px;font:96px BH;color:#102A43">{d["big"]}</div>' + lcd(d["from"], 40) + lcd(d["to"], 720)
             + f'<div class="t" style="left:575px;top:280px;font:120px BH;color:{acc}">→</div>'
             f'<div class="t" style="left:50px;bottom:50px;font:86px BH;color:{acc}">{d["sub"]}</div>'
             f'<div class="t" style="right:50px;bottom:56px;padding:6px 22px;background:{acc2};font:50px BH;color:#fff;border-radius:10px">{d["tag"]}</div>')
    elif n == 10:  # 좌우 대결 + VS
        h = (f'<div style="position:absolute;left:0;top:0;width:640px;height:720px;background:{c["bg2"]}"></div><div style="position:absolute;left:640px;top:0;width:640px;height:720px;background:{c["bg3"]}"></div>'
             f'<img src="{img}" style="position:absolute;left:0;top:0;width:640px;height:720px;object-fit:cover;opacity:.55;mix-blend-mode:luminosity">'
             f'<img src="{img2 or img}" style="position:absolute;left:640px;top:0;width:640px;height:720px;object-fit:cover;opacity:.55;mix-blend-mode:luminosity">'
             f'<div class="t" style="left:0;width:640px;top:60px;text-align:center;font:150px BH;color:#fff;{S("#000")}">{d["a"]}</div>'
             f'<div class="t" style="left:640px;width:640px;top:60px;text-align:center;font:150px BH;color:#fff;{S("#000")}">{d["b"]}</div>'
             f'<div class="t" style="left:0;width:640px;top:440px;text-align:center;font:96px BH;color:{acc};{S("#000")}">{d["a_sub"]}</div>'
             f'<div class="t" style="left:640px;width:640px;top:440px;text-align:center;font:96px BH;color:{acc};{S("#000")}">{d["b_sub"]}</div>'
             f'<div class="t" style="left:490px;top:230px;width:300px;height:220px;display:flex;align-items:center;justify-content:center;background:{acc};font:170px BH;color:#000;transform:skewX(-10deg);box-shadow:0 14px 40px #000c">VS</div>'
             f'<div class="t" style="left:0;right:0;bottom:30px;text-align:center;font:58px BH;color:#fff;{S("#000")}">{d["tag"]}</div>')
    else:  # 0: 기존
        h = (ph("left:0;top:0;width:1280px;height:720px", "filter:brightness(.45)") + f'<div class="t" style="left:44px;top:40px;font:60px BH;color:{acc}">{d["top"]}</div>'
             f'<div class="t" style="left:40px;top:150px;font:170px BH;color:#fff">{d["big"]}</div><div class="t" style="left:44px;top:420px;font:90px BH;color:#5FE0C4">{d["sub"]}</div>')
    return f"<html><head><meta charset='utf-8'><style>{css}</style></head><body><div style='position:relative;width:1280px;height:720px;overflow:hidden'>{h}</div></body></html>"


LEGACY = {"#D6B26E": "acc", "#F1D9A0": "acc2", "#F2EDE3": "text", "#8C919B": "mute", "#5FB7A6": "down", "#E4775F": "up", "#6B7079": "grey",
          "#0D0E11": "ink", "#13151A": "card", "#16181D": "card2", "#5FE0C4": "down"}


def remap(T, html):
    """대본 데이터에 직접 적힌 옛 먹색+금색 팔레트 색을 이 패턴 색으로 바꾼다(0번이면 그대로)"""
    if T["num"] == 0: return html
    return _sub(T, html)


def _sub(T, html):
    for k, v in LEGACY.items():
        html = html.replace(k, T["c"][v]).replace(k.lower(), T["c"][v])
    return html
