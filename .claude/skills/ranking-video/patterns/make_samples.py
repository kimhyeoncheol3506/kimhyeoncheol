# -*- coding: utf-8 -*-
"""패턴 10가지 5초 샘플(HyperFrames) + 썸네일 틀 → patterns/samples/
사용: python3 make_samples.py [번호 ...] [--render]   (기본: 스틸만, --render면 5초 mp4도)
샘플 숫자는 실제 조사값(주간 시세 #5 · 헤럴드 방어 기사 · 광어수율 편)만 쓴다."""
import json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import theme as TH
R = "/home/user/kimhyeoncheol"; VP = f"{R}/video_projects"; FONTDIR = os.path.expanduser("~/.cache/ranking-video/fonts")
OUT = f"{HERE}/samples"; WORK = os.environ.get("PATTERN_WORK", "/tmp/claude-0/pattern_samples"); HFV = ["npx", "--yes", "hyperframes@0.8.214"]
TPL = f"{R}/.claude/skills/ranking-video/templates/hyperframes_movers"
IMG = {"광어": f"{VP}/3대시장_광어비교/09_소재/img_final/wc1917760.jpg", "방어": f"{VP}/노량진_일본산방어/09_소재/img_final/wc2223058.jpg",
       "부시리": f"{VP}/방어대안/09_소재/img_final/c3abbf87-4881-464c-8e4c-8b378f9d7097.jpg",
       "킹크랩": f"{VP}/겨울_시즌데이터_킹크랩_대방어_대게/09_소재/img_final/274fa460-fb16-4969-8942-434730ae5bf5.jpg",
       "시장": f"{VP}/3대시장_광어비교/09_소재/img_final/wc3999742.jpg"}


def K(T, s, extra=""): return f'<div style="font:700 32px PX;letter-spacing:.28em;color:{T["c"]["acc"]};{extra}">{s}</div>'


def sig(T):
    """패턴별 대표 장면(2.4~5초). 반환: html"""
    c = T["c"]; n = T["num"]; acc, acc2, tx, card = c["acc"], c["acc2"], c["text"], c["card"]
    if n == 1:
        chips = "".join(f'<span style="padding:10px 28px;border:3px solid {tx};font:700 44px PX;margin-right:18px">{x}</span>' for x in ("크기", "선어", "산지"))
        return (f'<div style="position:absolute;left:150px;top:180px">{K(T, "선어 광어 · 노량진 경락가 kg당")}'
                f'<div style="margin-top:20px;display:inline-block;padding:16px 90px 16px 40px;background:{acc};color:#fff;font:190px BH;clip-path:polygon(0 0,90% 0,100% 50%,90% 100%,0 100%)">4,600원</div>'
                f'<div style="margin-top:44px">{chips}</div></div><div style="position:absolute;right:220px;top:180px;font:420px BH;color:{acc}">?</div>')
    if n == 2:
        rows = "".join(f'<div style="display:flex;align-items:center;gap:30px;margin:22px 0"><span style="width:96px;height:96px;display:flex;align-items:center;justify-content:center;background:{acc2};color:#fff;font:70px BH">✕</span>'
                       f'<span style="font:76px BH;color:{tx}">{x}</span></div>' for x in ("값 폭이 너무 넓은 선어", "물량이 적은 품목", "원산지 표시 없는 활어"))
        return f'<div style="position:absolute;left:170px;top:170px">{K(T, "사기 전 거를 것 3가지", f"color:{acc}")}<div style="margin-top:20px">{rows}</div></div><div style="position:absolute;right:170px;top:200px;font:400px BH;color:{acc}">3</div>'
    if n == 3:
        yr = lambda y, v, h, hl: (f'<div style="display:flex;flex-direction:column;align-items:center;gap:14px"><div style="font:700 44px PX;color:{acc if hl else c["mute"]}">{v}</div>'
                                  f'<div style="width:150px;height:{h}px;background:{acc if hl else c["grey"]}"></div><div class="mj" style="font-size:48px">{y}</div></div>')
        return (f'<div style="position:absolute;left:150px;top:150px;width:760px">{K(T, "노량진 11월 활방어 평균 경락가")}<div class="mj" style="font-size:84px;line-height:1.25;margin-top:20px;word-break:keep-all">10년 새<br>4배 넘게 올랐다</div>'
                f'<div style="font:500 32px PX;color:{c["mute"]};margin-top:24px">헤럴드경제 2026-11-24 · 노량진 경락시세 분석</div></div>'
                f'<div style="position:absolute;right:220px;bottom:250px;display:flex;align-items:flex-end;gap:70px">{yr("2016", "4,870원", 90, False)}{yr("2026", "20,072원", 380, True)}</div>')
    if n == 4:
        return (f'<div style="position:absolute;left:150px;top:170px">{K(T, "보도로 본 수법 · 무게")}<div style="font:800 96px PXB;margin-top:24px;line-height:1.3">주문한 무게와<br>집에서 잰 무게</div>'
                f'<div style="margin-top:36px;display:flex;gap:30px">' + "".join(f'<div style="padding:24px 40px;background:{card};border-top:8px solid {cl}"><div style="font:700 36px PX;color:{c["mute"]}">{a}</div><div style="font:800 110px PXB;color:{cl}">{b}</div></div>'
                                                                         for a, b, cl in (("가게 저울", "?kg", tx), ("집 저울", "?kg", acc))) + '</div></div>'
                f'<div style="position:absolute;right:170px;top:200px;width:520px;padding:34px;border:4px solid {acc};font:700 42px/1.6 PX">✓ 무게 표시 확인<br>✓ 물 빼고 다시 달기<br>✓ 영수증 받기</div>')
    if n == 5:
        top = [("2", "대게(선)", "▼29%"), ("3", "방어", "▼27%"), ("4", "도다리", "▼20%"), ("5", "광어(선)", "▼13%")]
        small = "".join(f'<div style="display:flex;align-items:center;gap:22px;margin:16px 0;padding:14px 26px;background:{card};border-radius:14px"><span style="width:64px;height:64px;border-radius:50%;background:{c["grey"]};display:flex;align-items:center;justify-content:center;font:44px BH">{a}</span>'
                        f'<span style="font:52px BH;width:260px">{b}</span><span style="font:52px BH;color:{c["down"]}">{p}</span></div>' for a, b, p in top)
        return (f'<div style="position:absolute;left:150px;top:180px;width:330px;height:330px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#FFE08A,{acc} 55%,{acc2});display:flex;align-items:center;justify-content:center;font:170px BH;color:#2a1800;box-shadow:0 14px 50px #000a">1위</div>'
                f'<div style="position:absolute;left:520px;top:200px"><div style="font:190px BH">우럭</div><div style="font:120px BH;color:{c["down"]}">▼35%</div><div style="font:700 36px PX;color:{c["mute"]}">kg 28,800원 → 18,700원</div></div>'
                f'<div style="position:absolute;right:120px;top:160px;width:560px">{small}</div>')
    if n == 6:
        ln = lambda a, b, bold=False: f'<div style="display:flex;justify-content:space-between;font:{800 if bold else 700} {58 if bold else 44}px {"PXB" if bold else "PX"};margin:14px 0"><span>{a}</span><span>{b}</span></div>'
        return (f'<div style="position:absolute;left:180px;top:150px;width:700px;padding:40px 50px 60px;background:{card};box-shadow:0 18px 50px #0002">'
                f'<div style="font:700 34px PX;letter-spacing:.3em;color:{c["mute"]};text-align:center">RECEIPT</div><div style="border-top:4px dashed #bbb;margin:20px 0"></div>'
                + ln("예산", "10,000원") + ln("활광어 kg당", "29,700원") + '<div style="border-top:4px dashed #bbb;margin:20px 0"></div>' + ln("살 수 있는 양", "약 337g", True)
                + f'<div style="font:500 28px PX;color:{c["mute"]};margin-top:16px">노량진 경락가 11/23~27 · 도매가 기준</div></div>'
                f'<div style="position:absolute;right:220px;top:180px;width:520px;height:520px;border-radius:50%;overflow:hidden;border:20px solid #fff;box-shadow:0 16px 40px #0003"><img src="assets/img/광어.jpg" style="width:100%;height:100%;object-fit:cover"></div>')
    if n == 7:
        pts = [(0, -47), (1, -23), (2, -45), (3, -32), (4, 70)]
        X = lambda i: 140 + i * 175; Y = lambda v: 470 - v * 3.2
        poly = " ".join(f"{X(i)},{Y(v)}" for i, v in pts)
        dots = "".join(f'<circle cx="{X(i)}" cy="{Y(v)}" r="14" fill="{c["up"] if v > 0 else c["down"]}"/><text x="{X(i)}" y="{Y(v) + (-30 if v > 0 else 60)}" fill="{c["up"] if v > 0 else c["down"]}" font-size="40" font-family="PXB" text-anchor="middle">{"▲" if v > 0 else "▼"}{abs(v)}%</text>' for i, v in pts)
        return (f'<div style="position:absolute;left:150px;top:140px">{K(T, "부시리 · 주간 리포트 5회 변동률")}</div>'
                f'<svg width="1300" height="900" style="position:absolute;left:100px;top:150px"><line x1="120" x2="1200" y1="520" y2="520" stroke="#ffffff55" stroke-dasharray="8 10"/><polyline points="{poly}" fill="none" stroke="{acc}" stroke-width="8"/>{dots}</svg>'
                f'<div style="position:absolute;right:130px;top:260px;text-align:right"><div style="font:800 60px PXB;color:{tx}">이번 주</div><div style="font:800 200px PXB;color:{c["up"]};line-height:1">▲70%</div><div style="font:700 40px PX;color:{c["mute"]}">kg 3,700원 → 6,300원</div></div>')
    if n == 8:
        bx = lambda lab, val, sub, bg, fg: (f'<div style="width:470px;padding:36px 16px;background:{bg};color:{fg};border-radius:20px;text-align:center;box-shadow:0 14px 34px #0f254022">'
                                            f'<div style="font:800 52px PXB">{lab}</div><div style="font:800 88px PXB;margin:10px 0;white-space:nowrap">{val}</div><div style="font:600 32px PX;opacity:.8">{sub}</div></div>')
        arr = f'<div style="font:120px BH;color:{acc2}">➜</div>'
        return (f'<div style="position:absolute;left:150px;top:150px">{K(T, "활방어 1kg 값이 지나는 길")}</div>'
                f'<div style="position:absolute;left:150px;right:150px;top:300px;display:flex;align-items:center;justify-content:space-between">'
                f'{bx("산지", "?원", "위판장 가격", card, tx)}{arr}{bx("경매(노량진)", "16,800원", "11/23~27 경락가", acc, "#fff")}{arr}{bx("소매", "?원", "가게 판매가", c["up"], "#fff")}</div>')
    if n == 9:
        lcd = lambda v, lab: (f'<div style="text-align:center"><div style="font:700 40px PX;color:{c["mute"]};margin-bottom:14px">{lab}</div><div style="width:560px;padding:22px 0;background:#102A43;border-radius:20px">'
                              f'<div style="font:800 150px PXB;color:#7CFFCB;font-variant-numeric:tabular-nums">{v}</div></div></div>')
        return (f'<div style="position:absolute;left:150px;top:150px">{K(T, "활광어 1kg · 수율 40% 가정 (범위 30~50% 낮은 쪽)")}</div>'
                f'<div style="position:absolute;left:150px;right:150px;top:300px;display:flex;align-items:center;justify-content:space-between">{lcd("1,000g", "통째 무게")}'
                f'<div style="font:140px BH;color:{acc}">→</div>{lcd("400g", "회로 먹는 살")}</div>')
    if n == 10:
        side = lambda x, name, price, img: (f'<div style="position:absolute;left:{x}px;top:170px;width:700px;text-align:center"><div style="width:520px;height:300px;margin:0 auto;border:6px solid #fff;overflow:hidden">'
                                            f'<img src="assets/img/{img}.jpg" style="width:100%;height:100%;object-fit:cover"></div><div style="font:130px BH;margin-top:20px">{name}</div><div style="font:90px BH;color:{acc}">{price}</div></div>')
        return (side(110, "방어", "16,800원", "방어") + side(1110, "부시리", "6,300원", "부시리")
                + f'<div style="position:absolute;left:760px;top:330px;width:400px;padding:14px 0;white-space:nowrap;text-align:center;background:#000;border:5px solid {acc};font:56px BH;color:{acc}">ROUND 1 · 가격</div>')
    raise KeyError(n)


SAMPLE = {  # 번호: (kick, 제목, 자막 2줄, 썸네일 문구, 사진, 사진2)
 1: ("PRICE CHECK", "kg 4,600원의 진실", ["선어 광어 kg 4,600원 정말 싼 걸까요", "크기와 선어 산지부터 보겠습니다"],
     dict(top="노량진 선어 광어", big="4,600원", sub="먹을 만할까?", tag="경락가로 계산"), "광어", None),
 2: ("WARNING", "회 좋아하면 이건 거르세요", ["사기 전에 거를 것 3가지입니다", "1위부터 데이터로 보여 드릴게요"],
     dict(top="회 좋아하면", big="3가지", sub="절대 사지 마세요", tag="경락가 근거"), "방어", None),
 3: ("왜 한국만", "왜 한국만 겨울마다<br>방어를 줄 서서 먹을까", ["방어 경락가는 10년 새 4배가 넘었습니다", "그런데도 줄이 길어지는 이유를 따라가 봅니다"],
     dict(top="밥상 위의 질문", big="왜 한국만 겨울마다 방어를 줄 서서 먹을까", sub="10년 새 4배"), "방어", None),
 4: ("사례 재구성", "산 무게와 집 무게가 다르다면", ["보도된 사례를 재구성했습니다", "가게 이름은 밝히지 않습니다"],
     dict(top="보도 사례 재구성", **{"from": "3kg", "to": "?kg"}, sub="이렇게 당합니다", tag="재구성"), "킹크랩", None),
 5: ("RANKING", "이번 주 가장 싸진 생선 TOP5", ["이번 주 1위는 활우럭입니다", "지난주보다 35% 내렸어요"],
     dict(top="노량진 이번 주", big="우럭", sub="▼35% 1위", tag="싸진 것 TOP5", rank="1위"), "시장", None),
 6: ("BUDGET", "1만 원으로 활광어 몇 g?", ["예산 1만 원으로 계산해 보겠습니다", "경락가로는 약 337g입니다"],
     dict(top="예산 고정", budget="1만원", big="광어 몇 g?", tag="시장별 계산"), "광어", None),
 7: ("시세 긴급점검", "부시리 한 주 새 70% 올랐다", ["네 번 연속 내리던 부시리가", "이번 주 70% 올랐습니다"],
     dict(top="긴급 점검", big="부시리", pct="70%", dir="up", tag="지금 사도 될까?"), "부시리", None),
 8: ("유통 구조", "경매 16,800원, 가게에선 얼마?", ["산지에서 경매 소매까지", "값이 어디서 붙는지 단계별로 봅니다"],
     dict(big="산지 ? → 경매 → 마트 ?", steps=[("산지", "?원"), ("경매", "16,800"), ("마트", "?원")], tag="활방어 kg · 노량진 경락가"), "방어", None),
 9: ("LAB TEST", "광어 1kg 사면 회는 몇 g?", ["통째 1kg를 사면", "회로 먹는 살은 약 400g입니다"],
     dict(big="광어 1kg 사면 회는?", **{"from": "1,000g", "to": "400g"}, sub="수율 40% 기준", tag="실험"), "광어", None),
 10: ("VS", "방어 vs 부시리", ["같은 노량진 경락가로", "방어는 16,800원 부시리는 6,300원입니다"],
      dict(a="방어", b="부시리", a_sub="16,800원", b_sub="6,300원", tag="같은 돈이면 무조건 이것?"), "방어", "부시리"),
}


def build(n, render=False):
    T = TH.load(num=n); kick, ttl, caps, th, ph, ph2 = SAMPLE[n]; P = f"p{n}"
    d = f"{WORK}/p{n:02d}"; shutil.rmtree(d, ignore_errors=True); os.makedirs(f"{d}/compositions"); os.makedirs(f"{d}/assets/fonts"); os.makedirs(f"{d}/assets/img")
    for f in ("hyperframes.json", "package.json"): shutil.copy(f"{TPL}/{f}", f"{d}/{f}")
    json.dump(dict(id=f"pattern{n}", name=f"pattern{n}", createdAt="2026-11-28T00:00:00.000Z"), open(f"{d}/meta.json", "w"))
    for f in TH.FONT_FILES: shutil.copy(f"{FONTDIR}/{f}", f"{d}/assets/fonts/{f}")
    for k, p in IMG.items(): shutil.copy(p, f"{d}/assets/img/{k}.jpg")
    c = T["c"]; base = (TH.fonts() + f"#root{{position:absolute;inset:0;overflow:hidden;color:{c['text']};font-family:PX,sans-serif}}#root *{{box-sizing:border-box}}" + TH.head_css(T) + TH.card_css(T)
                        + f".hdr{{position:absolute;left:70px;top:54px;font:700 28px PX;letter-spacing:.18em;color:{c['acc']}}}")
    scenes = [("s1", 0, 2.4, f'<div style="position:absolute;left:0;right:0;top:300px;text-align:center">{K(T, kick)}<div class="mj" style="font-size:{120 if len(ttl) < 16 else 100}px;line-height:1.2;margin-top:26px">{ttl}</div></div>'),
              ("s2", 2.4, 2.6, sig(T))]
    hosts = []
    for sid, t0, du, body in scenes:
        Pp = f"{P}{sid}-"; h = f'<div class="hdr">CHECK ISSUE POINT · 패턴 {n}</div>'
        js = ('const tl = gsap.timeline({ paused: true }); const $ = (i) => "#' + Pp + '" + i;\n' + TH.wipe_js(T, True, du) + f'\nwindow.__timelines["{Pp[:-1]}"] = tl;')
        html = (f'<template><style>{base}</style><div id="root" data-composition-id="{Pp[:-1]}" data-width="1920" data-height="1080">'
                + TH.layer(T, Pp, h + body).replace(f'id="{Pp}content" style="', f'id="{Pp}content" style="opacity:0;') + TH.wipe_html(T, Pp) + f'</div><script>{js}</script></template>')
        open(f"{d}/compositions/{sid}.html", "w", encoding="utf-8").write(html)
        hosts.append(f'<div id="{sid}" data-composition-id="{Pp[:-1]}" data-composition-src="compositions/{sid}.html" data-start="{t0}" data-duration="{du}" data-track-index="1" data-width="1920" data-height="1080"></div>')
    capdiv = "".join(f'<div class="clip cap" id="cap{i}" data-start="{0.3 + i * 2.4}" data-duration="{2.1 if i == 0 else 2.3}" data-track-index="1"><span>{x.replace("4배", "<b>4배</b>").replace("35%", "<b>35%</b>").replace("70%", "<b>70%</b>").replace("337g", "<b>337g</b>").replace("400g", "<b>400g</b>").replace("16,800원", "<b>16,800원</b>").replace("6,300원", "<b>6,300원</b>").replace("4,600원", "<b>4,600원</b>").replace("3가지", "<b>3가지</b>").replace("1만 원", "<b>1만 원</b>")}</span></div>' for i, x in enumerate(caps))
    open(f"{d}/compositions/captions.html", "w", encoding="utf-8").write(
        f'<template><style>{TH.fonts()}#root{{position:absolute;inset:0;font-family:PX,sans-serif}}{TH.cap_css(T)}</style><div id="root" data-composition-id="captions" data-width="1920" data-height="1080">{capdiv}</div>'
        '<script>const tl = gsap.timeline({ paused: true }); window.__timelines["captions"] = tl;</script></template>')
    hosts.append('<div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="5" data-track-index="3" data-width="1920" data-height="1080" style="z-index:50"></div>')
    open(f"{d}/index.html", "w", encoding="utf-8").write(
        '<!doctype html><html lang="ko"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/><script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>'
        f'<style>html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:{c["ink"]}}}</style></head><body>'
        f'<div id="root" data-composition-id="main" data-start="0" data-duration="5" data-width="1920" data-height="1080">{"".join(hosts)}</div>'
        '<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = gsap.timeline({ paused: true });</script></body></html>')
    os.makedirs(OUT, exist_ok=True); nm = f"{n:02d}"
    subprocess.run(HFV + ["snapshot", "-o", f"{d}/snap", "--at", "0.35,1.6,4.2", "."], cwd=d, check=True, capture_output=True)
    shutil.copy(f"{d}/snap/frame-02-at-4.2s.png", f"{OUT}/{nm}_장면.png"); shutil.copy(f"{d}/snap/frame-00-at-0.35s.png", f"{OUT}/{nm}_전환.png"); shutil.copy(f"{d}/snap/frame-01-at-1.6s.png", f"{OUT}/{nm}_제목.png")
    if render:
        subprocess.run(HFV + ["render", "-o", f"{OUT}/{nm}_샘플5초.mp4", "-f", "30", "-q", "draft", "--quiet", "."], cwd=d, check=True)
    # 썸네일 틀
    th_html = TH.thumb_html(T, th, f"file://{IMG[ph]}", f"file://{IMG[ph2]}" if ph2 else None, fontdir=f"file://{FONTDIR}/")
    open(f"{d}/thumb.html", "w", encoding="utf-8").write(th_html)
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:720}});"
          "await p.goto('file://'+process.argv[2]);await p.waitForTimeout(700);await p.screenshot({path:process.argv[3]});await b.close();})();")
    subprocess.run(["node", "-e", js, "x", f"{d}/thumb.html", f"{OUT}/{nm}_썸네일.png"], check=True)
    print("ok", n, T["name"])


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    for n in (map(int, a) if a else range(1, 11)): build(n, "--render" in sys.argv)
