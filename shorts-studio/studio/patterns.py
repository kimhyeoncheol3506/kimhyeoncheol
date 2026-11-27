"""10가지 영상 패턴 (v1.25.0, 현철님 "템플릿이 너무 패턴이 같다 → 인기 유튜버 패턴 10가지를 랜덤으로").

script.json  "concept": "pattern", "pattern": <아래 키>  → PatternShort 가 패턴마다 다른 배경·레이아웃·자막·효과음·표지로 렌더.
패턴 고르기는 tools/pattern_pick.py (최근 3편과 겹치지 않게 랜덤).

| 키 | 이름 | 참고한 인기 포맷 |
| countdown  | 순위 카운트다운 TOP N | 마선생·백설마녀 'BEST 3', 숨겨진심리학 '신호 8가지' |
| translator | 속뜻 번역기          | 숨겨진심리학 '12가지 번역', 아루인사이트 '무심코 하는 말', 그 누나 '진짜 의미' |
| spec       | 스펙 처방전(점수표)  | 한방언니 '스펙 처방'·'결혼 점수는?'·'결혼압박면접' |
| balance    | 밸런스 게임 VS       | 이준우 '커플논쟁 밸런스게임', 무조건 고르기 |
| test       | 연애 심리테스트      | 리얼현장·알고심리·흔한남매 '연애 심리테스트' |
| katalk     | 카톡 NG vs OK        | 박코 '연애고수가 카톡하는 법', 데이라잇·전메리 '카톡 스킬' |
| essay      | 새벽 독백 에세이     | 김달 '연애 오래 못하는 여자들의 공통점' 류 독백 |
| steps      | N단계 공략 로드맵    | 심리조각 '반하는 과정 4단계', 이리유 '꼬시는 4단계' |
| checklist  | 자가진단 체크리스트  | 송나연 '여기에 해당되면', 오마르의 삶 '이런 대화를 하고 있다면' |
| ox         | 가능/불가능 O X 판정 | 박코 '재회 가능한 경우(+불가능)', 이준우 '가능 불가능' |

장면 visual.mode : hook(패턴 타이틀 플레이트) / item(패턴 본문) / question(test) / verdict(도장) / cta(댓글 유도·구독 멘트)
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import audio as A
from .core import (FPS, INK, WHITE, clamp, ease_in_out, ease_out_back, ease_out_cubic, font, lerp, paste_scaled,
                   rich_block, rounded_card, strip_markup, wrap_text)
from .doodle import bean, chat_bubble_icon, check_box, sparkle
from .short import CAP_Y, COVER_SEC, HOOK_Y, H, W, ShortBase
from .timeline import FrameWriter

TOP, BOT = 450, 1360          # 본문 영역 (위 후크·아래 자막 사이)
GOLD, SILVER, BRONZE = (255, 200, 40), (200, 205, 215), (205, 127, 50)
GREEN, RED = (30, 185, 90), (229, 57, 53)

PATTERNS = {
    "countdown": dict(label="순위 카운트다운", plate="TOP {n}", top=(10, 8, 22), bottom=(52, 24, 70), bg="spot",
                      accent=(255, 203, 48), font="impact", text=WHITE, stroke=(0, 0, 0), cap="box", bgm="tension",
                      badge=(200, 40, 60)),
    "translator": dict(label="속뜻 번역기", plate="속뜻 번역기", top=(236, 250, 246), bottom=(186, 230, 218), bg="dots",
                       accent=(0, 140, 110), font="dohyeon", text=(20, 40, 36), stroke=WHITE, cap="pill", bgm="lofi",
                       badge=(0, 140, 110)),
    "spec": dict(label="스펙 처방전", plate="스펙 처방전", top=(250, 244, 230), bottom=(232, 218, 190), bg="paper",
                 accent=(205, 35, 35), font="impact", text=(30, 24, 20), stroke=WHITE, cap="box", bgm="tension",
                 badge=(205, 35, 35)),
    "balance": dict(label="밸런스 게임", plate="밸런스 게임", top=(22, 22, 30), bottom=(34, 30, 44), bg="stripes",
                    accent=(255, 222, 40), font="impact", text=WHITE, stroke=(0, 0, 0), cap="outline", bgm="tension",
                    badge=(255, 170, 0)),
    "test": dict(label="연애 심리테스트", plate="심리 테스트", top=(54, 26, 104), bottom=(150, 86, 210), bg="stars",
                 accent=(255, 228, 92), font="hand", text=WHITE, stroke=(40, 10, 70), cap="pill", bgm="lofi",
                 badge=(120, 60, 200)),
    "katalk": dict(label="카톡 NG vs OK", plate="NG vs OK", top=(255, 240, 150), bottom=(252, 214, 40), bg="grid",
                   accent=(214, 36, 60), font="impact", text=(45, 28, 22), stroke=WHITE, cap="box", bgm="lofi",
                   badge=(60, 34, 28)),
    "essay": dict(label="새벽 연애 노트", plate=None, top=(6, 6, 9), bottom=(24, 22, 30), bg="grain",
                  accent=(255, 206, 150), font="semi", text=(235, 235, 235), stroke=(0, 0, 0), cap="none", bgm="night",
                  badge=(90, 70, 60)),
    "steps": dict(label="N단계 공략", plate="{n}단계 공략", top=(214, 236, 255), bottom=(128, 186, 246), bg="clouds",
                  accent=(240, 96, 40), font="hand", text=(20, 30, 60), stroke=WHITE, cap="outline", bgm="lofi",
                  badge=(240, 96, 40)),
    "checklist": dict(label="자가진단 체크리스트", plate="자가진단", top=(252, 252, 248), bottom=(242, 240, 230),
                      bg="notebook", accent=(220, 40, 50), font="impact", text=(25, 25, 30), stroke=WHITE, cap="box",
                      bgm="lofi", badge=(220, 40, 50)),
    "ox": dict(label="O X 판정", plate="O X 판정", top=(18, 36, 120), bottom=(8, 14, 60), bg="rays",
               accent=(255, 214, 0), font="impact", text=WHITE, stroke=(0, 0, 0), cap="outline", bgm="tension",
               badge=(0, 110, 220)),
}


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def pattern_bg(p, size):
    Wd, Hd = size
    top, bot = p["top"], p["bottom"]
    grad = Image.new("RGB", (1, Hd))
    for y in range(Hd):
        k = y / (Hd - 1)
        grad.putpixel((0, y), tuple(int(a + (b - a) * k) for a, b in zip(top, bot)))
    im = grad.resize((Wd, Hd)).convert("RGBA")
    lay = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    kind = p["bg"]
    rnd = random.Random(11)
    light = lum(top) > 150
    ink = (0, 0, 0, 20) if light else (255, 255, 255, 18)
    if kind == "spot":
        for cx, ang in ((180, 0.35), (900, -0.35)):
            cone = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
            ImageDraw.Draw(cone).polygon([(cx - 40, -40), (cx + 40, -40), (cx + 700 * math.sin(-ang) + 380, Hd),
                                          (cx + 700 * math.sin(-ang) - 380, Hd)], fill=(255, 240, 200, 26))
            lay = Image.alpha_composite(lay, cone.filter(ImageFilter.GaussianBlur(30)))
        d = ImageDraw.Draw(lay)
    elif kind == "dots":
        for y in range(30, Hd, 56):
            for x in range(30 + (y // 56 % 2) * 28, Wd, 56):
                d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(0, 120, 100, 30))
    elif kind == "paper":
        for _ in range(2500):
            x, y = rnd.uniform(0, Wd), rnd.uniform(0, Hd)
            d.point((x, y), fill=(120, 90, 50, 40))
    elif kind == "stripes":
        for x in range(-Hd, Wd, 110):
            d.line((x, Hd, x + Hd, 0), fill=(255, 255, 255, 10), width=40)
    elif kind == "stars":
        for _ in range(90):
            x, y, r = rnd.uniform(0, Wd), rnd.uniform(0, Hd), rnd.uniform(1.5, 4.5)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rnd.uniform(60, 160))))
    elif kind == "grid":
        for x in range(0, Wd, 64):
            d.line((x, 0, x, Hd), fill=ink, width=2)
        for y in range(0, Hd, 64):
            d.line((0, y, Wd, y), fill=ink, width=2)
    elif kind == "grain":
        for _ in range(9000):
            x, y = rnd.uniform(0, Wd), rnd.uniform(0, Hd)
            d.point((x, y), fill=(255, 255, 255, int(rnd.uniform(6, 26))))
    elif kind == "clouds":
        cl = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        for _ in range(9):
            x, y, r = rnd.uniform(-100, Wd + 100), rnd.uniform(0, Hd), rnd.uniform(90, 200)
            cd.ellipse((x - r * 1.6, y - r * 0.6, x + r * 1.6, y + r * 0.6), fill=(255, 255, 255, 90))
        lay = Image.alpha_composite(lay, cl.filter(ImageFilter.GaussianBlur(28)))
        d = ImageDraw.Draw(lay)
    elif kind == "notebook":
        for y in range(120, Hd, 64):
            d.line((0, y, Wd, y), fill=(120, 160, 220, 60), width=3)
        d.line((96, 0, 96, Hd), fill=(230, 80, 80, 90), width=4)
    elif kind == "rays":
        cx, cy = Wd / 2, 905
        for i in range(24):
            a0, a1 = i * 2 * math.pi / 24, (i + 0.5) * 2 * math.pi / 24
            R = 2400
            d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                       (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(255, 255, 255, 14))
    if not light:
        v = Image.new("L", (Wd, Hd), 0)
        ImageDraw.Draw(v).ellipse((-Wd * 0.3, -Hd * 0.15, Wd * 1.3, Hd * 1.15), fill=255)
        v = v.filter(ImageFilter.GaussianBlur(160))
        dark = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 150))
        dark.putalpha(v.point(lambda x: int((255 - x) * 0.6)))
        lay = Image.alpha_composite(lay, dark)
    return Image.alpha_composite(im, lay)


def text_block(text, fname, size, fill, key, maxw, stroke=0, stroke_fill=INK, gap=1.15, pad=10):
    f = font(fname, size)
    lines = []
    for part in text.split("\n"):
        lines += wrap_text(part, f, maxw)
    return rich_block(lines, f, fill, key, stroke=stroke, stroke_fill=stroke_fill, line_gap=gap, pad=pad)


def fit_block(text, fname, size, fill, key, maxw, maxh, **kw):
    """maxw·maxh 안에 들어갈 때까지 글자 크기를 줄여 블록 생성."""
    while True:
        b = text_block(text, fname, size, fill, key, maxw, **kw)
        if b.height <= maxh or size <= 30:
            return b
        size -= 4


def card(size, radius, fill, outline=None, width=0, shadow=True):
    im, pad = rounded_card(size, radius, fill, shadow=shadow, shadow_blur=18, shadow_alpha=90)
    if outline:
        ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + size[0], pad + size[1]), radius, outline=outline,
                                             width=width)
    return im, pad


def paste_card(cv, im, pad, x, y):
    cv.alpha_composite(im, (int(x - pad), int(y - pad)))


class PatternShort(ShortBase):
    def __init__(self, project: Path):
        super().__init__(project)
        self.p = self.script.get("pattern", "countdown")
        meta = PATTERNS[self.p]
        th = dict(meta)
        th.update(name=self.p, stamp=meta["accent"] if lum(meta["accent"]) < 200 else RED, bar=meta["accent"])
        self.theme = th
        self.bg = pattern_bg(meta, (W, H))
        hook_size = 64 if self.p == "essay" else 104
        self.hook_img = rich_block(self.script["hook"], font(th["font"], hook_size), th["text"], th["accent"],
                                   stroke=0 if self.p == "essay" else 9, stroke_fill=th["stroke"])
        n = len(self.script.get("items") or self.script.get("steps") or self.script.get("rounds")
                or self.script.get("cases") or self.script.get("checks") or [])
        self.plate_text = (self.script.get("plate") or meta["plate"] or "").replace("{n}", str(n))
        self.badge_text = self.script.get("badge") or meta["label"].replace("N단계", f"{n}단계")
        self.items = [s for s in self.scenes if s.visual.get("mode") == "item"]
        self.impacts = self._impacts()

    # ---------- 공통 시간 계산 ----------
    def at(self, s, key, default):
        k = s.visual.get(key)
        if k is not None and len(s.chunks) > k:
            return s.chunks[k].start
        return s.voice_start + default

    def reveal_time(self, s):
        mode = s.visual.get("mode", "item")
        if mode == "verdict":
            return self.at(s, "stamp_at_chunk", max(0.3, (s.voice_end - s.voice_start) * 0.6))
        if mode != "item":
            return None
        p = self.p
        if p == "translator":
            return self.at(s, "reveal_at_chunk", 1.0) if len(s.chunks) < 2 or "reveal_at_chunk" in s.visual \
                else s.chunks[1].start
        if p == "balance":
            return self.at(s, "pick_at_chunk", 0) if s.data.get("visual", {}).get("pick") else None
        if p == "ox":
            return self.at(s, "ox_at_chunk", (s.voice_end - s.voice_start) * 0.45) if len(s.chunks) < 2 or \
                "ox_at_chunk" in s.visual else s.chunks[1].start
        return s.voice_start + 0.1

    def _impacts(self):
        ev = []
        for s in self.scenes:
            rt = self.reveal_time(s)
            if rt is None:
                continue
            strong = s.visual.get("mode") == "verdict" or self.p in ("ox", "countdown")
            ev.append((rt, 24 if strong else 0, s))
        return ev

    def shake_amount(self, s, t):
        sh = 0.0
        for rt, amp, _ in self.impacts:
            if amp and 0 <= t - rt < 0.3:
                sh = max(sh, amp * (1 - (t - rt) / 0.3))
        return sh

    def sfx_events(self):
        ev = [(0.0, "boom", 0.9)]
        for s in self.scenes:
            for name, off in s.data.get("sfx", []):
                ev.append((s.voice_start + off, name, 1.0))
            if s.idx > 0 and self.p not in ("essay",):
                ev.append((s.start, "whoosh", 0.45))
        snd = {"countdown": "boom", "translator": "ding", "spec": "marker", "balance": "pop", "test": "ding",
               "katalk": "pop", "essay": None, "steps": "pop", "checklist": "marker", "ox": "stamp"}[self.p]
        for rt, amp, s in self.impacts:
            if s.visual.get("mode") == "verdict":
                ev += [(rt, "stamp", 1.0), (rt + 0.02, "boom", 0.7)]
            elif snd:
                ev.append((rt, snd, 0.9))
        for s in self.scenes:
            if self.p == "translator" and s.visual.get("mode") == "item":
                rt = self.reveal_time(s)
                x = s.voice_start + 0.1
                while x < rt - 0.1:
                    ev.append((x, "tick", 0.35))
                    x += 0.18
            if self.p == "test" and s.visual.get("mode") == "question":
                t0 = self.at(s, "timer_at_chunk", 0.2)
                for k in range(3):
                    ev.append((t0 + k, "tick", 0.8))
            if self.p == "katalk" and s.visual.get("mode") == "item":
                for tt in self.bubble_times(s):
                    ev.append((tt, "pop", 0.6))
        return ev

    # ---------- 자막 스타일 ----------
    def caption_img(self, text):
        if text in self._cap_cache:
            return self._cap_cache[text]
        th = self.theme
        style = th["cap"]
        if style == "none":
            self._cap_cache[text] = None
            return None
        f = font("bold", 80 if style == "outline" else 70)
        lines = wrap_text(text, f, 880)
        if style == "outline":
            dark = lum(th["top"]) < 150
            img = rich_block(lines, f, WHITE if dark else th["text"], th["accent"], stroke=10,
                             stroke_fill=(0, 0, 0) if dark else WHITE, line_gap=1.12)
        else:
            if style == "box":
                bgc, fill = (14, 14, 18, 230), WHITE
                key = th["accent"] if lum(th["accent"]) > 140 else (255, 214, 10)
            else:  # pill
                bgc = th["accent"] + (245,)
                fill = WHITE if lum(th["accent"]) < 150 else (20, 20, 24)
                key = (255, 240, 120) if lum(th["accent"]) < 150 else (180, 20, 60)
            txt = rich_block(lines, f, fill, key, line_gap=1.12, pad=18)
            img = Image.new("RGBA", (txt.width + 40, txt.height + 16), (0, 0, 0, 0))
            ImageDraw.Draw(img).rounded_rectangle((0, 0, img.width - 1, img.height - 1),
                                                  44 if style == "pill" else 26, fill=bgc)
            img.alpha_composite(txt, (20, 8))
        self._cap_cache[text] = img
        return img

    # ---------- 프레임 ----------
    def render_frame(self, t):
        if t < COVER_SEC:
            return self.cover()
        s = self.scene_at(t)
        lt = t - s.start
        mode = s.visual.get("mode", "item")
        frame = self.bg.copy()
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.draw_content(cv, s, t)
        if mode in ("verdict", "cta") and self.p != "essay":
            dim = Image.new("RGBA", (W, H), (8, 8, 12, 150 if mode == "cta" else 110))
            dim.putalpha(Image.eval(cv.getchannel("A"), lambda v: int(v * (0.6 if mode == "cta" else 0.45))))
            cv = Image.alpha_composite(cv, dim)
        if mode == "hook":
            self.draw_plate(cv, s, t)
        elif mode == "verdict":
            self.draw_verdict(cv, s, t)
        elif mode == "cta":
            self.draw_cta2(cv, s, t)
        sh = self.shake_amount(s, t)
        ox, oy = int(self.rng.uniform(-sh, sh)), int(self.rng.uniform(-sh, sh))
        frame.alpha_composite(cv, (0, 0)) if not (ox or oy) else frame.paste(cv, (ox, oy), cv)
        return self._finish(frame, s, t, lt, mode)

    def _finish(self, frame, s, t, lt, mode):
        th = self.theme
        k = ease_out_back((t - COVER_SEC) / 0.25, 2.0)
        hy = 250 if self.p == "essay" else HOOK_Y
        paste_scaled(frame, self.hook_img, (W / 2, hy), lerp(1.12, 1.0, k) * min(1.0, 1000 / self.hook_img.width))
        if self.p == "essay":
            ImageDraw.Draw(frame).line((440, hy + 70, 640, hy + 70), fill=th["accent"], width=3)
        i, c = s.chunk_at(t)
        hide = mode == "verdict" and s.visual.get("stamp_at_chunk") == i
        if c is not None and t >= s.voice_start - 0.05 and not hide:
            img = self.caption_img(c.text)
            if img is not None:
                kk = ease_out_back((t - c.start) / 0.16, 2.5)
                paste_scaled(frame, img, (W / 2, CAP_Y), lerp(0.75, 1.0, kk))
        ImageDraw.Draw(frame).rectangle((0, 0, int(W * t / self.total), 10), fill=th["bar"])
        flash = self.p in ("countdown", "ox", "balance")
        if s.idx > 0 and lt < 0.12 and self.p != "essay":
            z = 1 + 0.05 * (1 - lt / 0.12)
            bw, bh = int(W * z), int(H * z)
            frame = frame.resize((bw, bh), Image.BILINEAR).crop(((bw - W) // 2, (bh - H) // 2,
                                                                  (bw - W) // 2 + W, (bh - H) // 2 + H))
            if flash:
                frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - lt / 0.12)))))
        for rt, amp, sc in self.impacts:
            if sc.visual.get("mode") == "verdict" and 0 <= t - rt < 0.12:
                frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(170 * (1 - (t - rt) / 0.12)))))
        return frame

    def draw_content(self, cv, s, t):
        getattr(self, "draw_" + self.p)(cv, s, t)

    def host(self, cv, s, t, x=890, base=1345, h=300, expr="happy"):
        d = ImageDraw.Draw(cv)
        talking = 0.0
        if s.voice_start <= t < s.voice_end:
            talking = 0.5 + 0.5 * math.sin(t * 17)
        bean(d, x, base, h, gender=self.script.get("host_gender", "f"), expr=expr, talking=talking, t=t, look=-0.6)

    def draw_plate(self, cv, s, t):
        if not self.plate_text:
            return
        lt = t - s.start
        k = ease_out_back((lt - 0.05) / 0.4, 2.2)
        if k <= 0:
            return
        th = self.theme
        f = font("impact", 150)
        tw = int(f.getlength(self.plate_text))
        im = Image.new("RGBA", (tw + 140, 260), (0, 0, 0, 0))
        dd = ImageDraw.Draw(im)
        dd.rounded_rectangle((8, 8, im.width - 8, im.height - 8), 50, fill=th["badge"], outline=WHITE, width=10)
        dd.text((im.width / 2, im.height / 2 + 4), self.plate_text, font=f, fill=WHITE, anchor="mm")
        sc = lerp(0.2, 1.0, k) * min(1.0, 980 / im.width)
        paste_scaled(cv, im, (W / 2, 760), sc, rotate=-4)
        self.host(cv, s, t, x=540, base=1340, h=360)

    def draw_verdict(self, cv, s, t):
        rt = self.reveal_time(s)
        if rt is None or t < rt:
            self.host(cv, s, t, x=540, base=1250, h=340, expr="smug")
            return
        dt = t - rt
        k = ease_out_cubic(dt / 0.18)
        color = {"red": RED, "green": GREEN}.get(s.visual.get("stamp_color"), self.theme["stamp"])
        stamp = self.stamp_img(s.visual.get("stamp_text", "확정"), color)
        paste_scaled(cv, stamp, (W / 2, 900), lerp(2.6, 1.0, k) * min(1.0, 960 / stamp.width),
                     alpha=clamp(dt / 0.08), rotate=-12)

    def draw_cta2(self, cv, s, t):
        lt = t - s.start
        k = ease_out_back((lt - 0.15) / 0.4, 2.0)
        if k > 0:
            r = 120 * k * (1 + 0.05 * math.sin(lt * 8))
            chat_bubble_icon(ImageDraw.Draw(cv), W - 230, 1080 if self.p != "essay" else 1250, r)
        if self.p != "essay":
            self.host(cv, s, t, x=360, base=1330, h=380, expr="happy")

    # ---------- 1. 순위 카운트다운 ----------
    def draw_countdown(self, cv, s, t):
        items = self.script["items"]          # items[0] = 1위
        n = len(items)
        rh = min(170, int((BOT - TOP - 40) / n))
        shown = {}
        cur = None
        for sc in self.items:
            r = sc.visual["rank"]
            rt = self.reveal_time(sc)
            if sc.idx <= s.idx and t >= rt:
                shown[r] = rt
            if sc.idx == s.idx:
                cur = r
        th = self.theme
        y0 = TOP + 10 + (BOT - TOP - rh * n) / 2
        for i in range(n):
            r = i + 1
            y = y0 + i * rh
            is_cur = r == cur and r in shown
            fill = th["accent"] + (255,) if is_cur else (255, 255, 255, 34)
            row = Image.new("RGBA", (960, rh - 16), (0, 0, 0, 0))
            rd = ImageDraw.Draw(row)
            rd.rounded_rectangle((0, 0, 959, rh - 17), 28, fill=fill, outline=(255, 255, 255, 90), width=3)
            mc = {1: GOLD, 2: SILVER, 3: BRONZE}.get(r, (120, 120, 140))
            cy = (rh - 16) / 2
            rd.ellipse((22, cy - 52, 126, cy + 52), fill=mc, outline=WHITE, width=5)
            rd.text((74, cy + 2), str(r), font=font("impact", 76), fill=INK, anchor="mm")
            if r in shown:
                it = items[i]
                txt_c = INK if is_cur else WHITE
                title = fit_block(it["title"], "bold", 56, txt_c, RED if is_cur else th["accent"], 780,
                                  rh - (60 if it.get("sub") else 30), pad=0)
                ty = cy - title.height / 2 - (18 if it.get("sub") else 0)
                row.alpha_composite(title, (150 + int((780 - title.width) / 2), int(ty)))
                if it.get("sub"):
                    rd.text((540, ty + title.height + 22), it["sub"], font=font("body", 34),
                            fill=(60, 50, 30) if is_cur else (210, 210, 220), anchor="mm")
            else:
                rd.text((540, cy), "? ? ?", font=font("impact", 70), fill=(255, 255, 255, 120), anchor="mm")
            ky = 1.0
            if r in shown:
                ky = ease_out_back((t - shown[r]) / 0.3, 1.6)
            sc_ = 1.04 if is_cur else 1.0
            if ky < 0.999:
                row = row.resize((row.width, max(1, int(row.height * max(0.02, ky)))), Image.BICUBIC)
            paste_scaled(cv, row, (W / 2, y + rh / 2), sc_)
            if is_cur and r == 1:
                for kx in range(4):
                    sparkle(ImageDraw.Draw(cv), 120 + kx * 280, y - 10 + (kx % 2) * (rh - 10), 26, t=t + kx)

    # ---------- 2. 속뜻 번역기 ----------
    def draw_translator(self, cv, s, t):
        th = self.theme
        items = self.script["items"]
        cur = s.visual.get("no", 0 if s.visual.get("mode") == "hook" else len(items) - 1)
        if s.visual.get("mode") in ("verdict", "cta"):
            cur = len(items) - 1
        it = items[cur]
        d = ImageDraw.Draw(cv)
        # 앱 상단 바
        bar, pad = card((960, 96), 30, th["accent"] + (255,), shadow=True)
        paste_card(cv, bar, pad, 60, TOP)
        d.text((100, TOP + 48), "언니 번역기", font=font("impact", 52), fill=WHITE, anchor="lm")
        d.text((980, TOP + 48), f"{cur + 1} / {len(items)}", font=font("semi", 40), fill=WHITE, anchor="rm")
        # 겉말 카드
        c1, pad = card((960, 300), 34, (255, 255, 255, 255))
        paste_card(cv, c1, pad, 60, TOP + 126)
        d.text((100, TOP + 166), it.get("who", "그 사람") + "이 한 말", font=font("semi", 36), fill=(110, 120, 118))
        outer = fit_block("“" + it["outer"] + "”", "bold", 70, INK, th["accent"], 860, 200, pad=0)
        cv.alpha_composite(outer, (int(540 - outer.width / 2), int(TOP + 126 + 175 - outer.height / 2 + 20)))
        # 번역 진행
        mode = s.visual.get("mode", "item")
        rt = self.reveal_time(s) if mode == "item" else (s.start - 10)
        if mode == "hook":
            rt = s.end + 10
        ay = TOP + 470
        if t < rt:
            prog = clamp((t - s.voice_start) / max(0.3, rt - s.voice_start))
            d.rounded_rectangle((160, ay - 18, 920, ay + 18), 18, fill=(255, 255, 255, 160))
            d.rounded_rectangle((160, ay - 18, lerp(170, 920, prog), ay + 18), 18, fill=th["accent"])
            dots = "." * (1 + int(t * 4) % 3)
            d.text((540, ay + 62), "번역 중" + dots, font=font("semi", 40), fill=th["text"], anchor="mm")
            if mode == "item":
                self.host(cv, s, t, x=540, base=1330, h=330, expr="shock")
        else:
            d.polygon([(500, ay - 40), (580, ay - 40), (540, ay + 30)], fill=th["accent"])
            k = ease_out_back((t - rt) / 0.35, 1.8)
            c2, pad = card((960, 380), 34, (20, 60, 52, 255), outline=th["accent"], width=8)
            lay = Image.new("RGBA", c2.size, (0, 0, 0, 0))
            lay.alpha_composite(c2)
            ld = ImageDraw.Draw(lay)
            ld.text((pad + 40, pad + 36), "진짜 속뜻", font=font("impact", 46), fill=(140, 255, 220))
            n = len(strip_markup(it["inner"]))
            typed = clamp((t - rt) / max(0.4, min(1.2, n * 0.05)))
            txt = it["inner"] if typed >= 1 else strip_markup(it["inner"])[:max(1, int(n * typed))]
            inner = fit_block(txt, "bold", 72, WHITE, (255, 230, 90), 860, 250, pad=0)
            lay.alpha_composite(inner, (int(pad + 480 - inner.width / 2), int(pad + 110 + (250 - inner.height) / 2)))
            paste_scaled(cv, lay, (W / 2, ay + 90 + 190), lerp(0.7, 1.0, k), alpha=clamp((t - rt) / 0.1))

    # ---------- 3. 스펙 처방전 ----------
    def draw_spec(self, cv, s, t):
        th = self.theme
        stats = self.script["stats"]
        prof = self.script.get("profile", {})
        sheet, pad = card((940, 900), 24, (255, 255, 255, 255))
        paste_card(cv, sheet, pad, 70, TOP - 10)
        d = ImageDraw.Draw(cv)
        d.rounded_rectangle((70, TOP - 10, 1010, TOP + 100), 24, fill=th["accent"])
        d.rectangle((70, TOP + 60, 1010, TOP + 100), fill=th["accent"])
        d.text((540, TOP + 45), prof.get("sheet", "결혼시장 스펙 처방전"), font=font("impact", 60), fill=WHITE,
               anchor="mm")
        bean(d, 165, TOP + 300, 170, gender=prof.get("gender", "f"), expr="neutral", t=t)
        d.text((260, TOP + 150), prof.get("name", "A씨"), font=font("impact", 64), fill=INK)
        d.text((260, TOP + 232), prof.get("line", ""), font=font("semi", 40), fill=(90, 90, 96))
        d.line((110, TOP + 330, 970, TOP + 330), fill=(220, 220, 220), width=3)
        cur = s.visual.get("stat") if s.visual.get("mode") == "item" else None
        filled = {}
        for sc in self.items:
            i = sc.visual["stat"]
            if sc.idx <= s.idx:
                filled[i] = clamp((t - self.reveal_time(sc)) / 0.8) if sc.idx == s.idx else 1.0
        rh = min(120, int((BOT - 40 - (TOP + 345)) / max(1, len(stats))))
        for i, st in enumerate(stats):
            y = TOP + 345 + i * rh
            if i == cur:
                d.rounded_rectangle((95, y - 6, 985, y + rh - 12), 16, fill=(255, 244, 180))
            d.text((120, y + rh / 2 - 9), st["k"], font=font("semi", 42), fill=(80, 80, 86), anchor="lm")
            if i in filled:
                d.text((340, y + rh / 2 - 9), st["v"], font=font("bold", 50), fill=INK, anchor="lm")
                sc_ = st.get("score", 50)
                p = ease_out_cubic(filled[i])
                col = RED if sc_ < 40 else ((245, 150, 20) if sc_ < 70 else GREEN)
                d.rounded_rectangle((680, y + rh / 2 - 27, 960, y + rh / 2 + 9), 18, fill=(236, 236, 236))
                d.rounded_rectangle((680, y + rh / 2 - 27, lerp(690, 960, sc_ / 100 * p), y + rh / 2 + 9), 18,
                                    fill=col)
            else:
                d.text((340, y + rh / 2 - 9), "─ ─ ─", font=font("bold", 44), fill=(200, 200, 200), anchor="lm")

    def draw_spec_grade(self, cv, s, t):
        pass

    # ---------- 4. 밸런스 게임 ----------
    def draw_balance(self, cv, s, t):
        rounds = self.script["rounds"]
        cur = s.visual.get("round", 0 if s.visual.get("mode") == "hook" else len(rounds) - 1)
        r = rounds[cur]
        lt = t - s.start
        slide = 1 - ease_out_cubic(lt / 0.35) if s.visual.get("mode") == "item" and s.visual.get("new", True) else 0
        rt = self.reveal_time(s) if s.visual.get("mode") == "item" else None
        pick = s.visual.get("pick")
        if s.visual.get("mode") in ("verdict", "cta"):
            pick = r.get("pick")
            rt = s.start - 1
        picked = pick and rt is not None and t >= rt
        for side, (y0, y1), col, dx in (("a", (TOP, 880), (214, 40, 60), -1), ("b", (930, BOT), (40, 90, 210), 1)):
            pw = Image.new("RGBA", (960, y1 - y0), (0, 0, 0, 0))
            pd = ImageDraw.Draw(pw)
            pd.rounded_rectangle((0, 0, 959, y1 - y0 - 1), 40, fill=col + (255,),
                                 outline=WHITE if picked and pick == side else None, width=14)
            pd.text((50, 30), side.upper(), font=font("impact", 120), fill=(255, 255, 255, 70))
            tb = fit_block(r[side], "impact", 84, WHITE, (255, 230, 90), 820, y1 - y0 - 80, pad=0)
            pw.alpha_composite(tb, (int(480 - tb.width / 2), int((y1 - y0 - tb.height) / 2)))
            if picked and pick != side:
                ov = Image.new("RGBA", pw.size, (0, 0, 0, 150))
                ov.putalpha(Image.eval(pw.getchannel("A"), lambda v: int(v * 0.6)))
                pw = Image.alpha_composite(pw, ov)
            scl = 1.0
            if picked and pick == side:
                scl = lerp(1.08, 1.03, ease_out_cubic((t - rt) / 0.3))
            paste_scaled(cv, pw, (W / 2 + dx * slide * 1100, (y0 + y1) / 2), scl)
            if picked and pick == side:
                st = self.stamp_img(self.script.get("pick_label", "언니 픽"), (255, 200, 0))
                k = ease_out_cubic((t - rt) / 0.18)
                paste_scaled(cv, st, (790, y0 + 70), lerp(1.6, 0.55, k), alpha=clamp((t - rt) / 0.08), rotate=-10)
        d = ImageDraw.Draw(cv)
        d.ellipse((540 - 92, 905 - 92, 540 + 92, 905 + 92), fill=(255, 222, 40), outline=INK, width=8)
        d.text((540, 908), "VS", font=font("impact", 92), fill=INK, anchor="mm")
        d.text((160, 905), f"ROUND {cur + 1}", font=font("impact", 46), fill=WHITE, anchor="mm",
               stroke_width=5, stroke_fill=INK)

    # ---------- 5. 연애 심리테스트 ----------
    def draw_test(self, cv, s, t):
        th = self.theme
        opts = self.script["options"]
        d = ImageDraw.Draw(cv)
        qc, pad = card((960, 200), 36, (255, 255, 255, 255))
        paste_card(cv, qc, pad, 60, TOP)
        q = fit_block("Q. " + self.script["question"], "hand", 58, (50, 20, 90), (210, 40, 120), 880, 170, pad=0)
        cv.alpha_composite(q, (int(540 - q.width / 2), int(TOP + 100 - q.height / 2)))
        mode = s.visual.get("mode", "item")
        sel = s.visual.get("opt") if mode == "item" else None
        cols = [(255, 140, 170), (120, 200, 255), (140, 225, 150), (255, 200, 100)]
        for i, o in enumerate(opts):
            x = 60 + (i % 2) * 490
            y = TOP + 240 + (i // 2) * 250
            tile = Image.new("RGBA", (470, 230), (0, 0, 0, 0))
            td = ImageDraw.Draw(tile)
            is_sel = sel == o["k"]
            td.rounded_rectangle((0, 0, 469, 229), 34, fill=cols[i % 4] + (255,),
                                 outline=th["accent"] if is_sel else WHITE, width=14 if is_sel else 5)
            td.ellipse((18, 18, 98, 98), fill=WHITE)
            td.text((58, 60), o["k"], font=font("impact", 56), fill=INK, anchor="mm")
            ob = fit_block(o["text"], "hand", 52, INK, (180, 20, 90), 400, 120, pad=0)
            tile.alpha_composite(ob, (int(235 - ob.width / 2), int(140 - ob.height / 2)))
            if sel and not is_sel:
                ov = Image.new("RGBA", tile.size, (30, 10, 50, 0))
                ov.putalpha(Image.eval(tile.getchannel("A"), lambda v: int(v * 0.55)))
                tile = Image.alpha_composite(tile, ov)
            paste_scaled(cv, tile, (x + 235, y + 115), 1.05 if is_sel else 1.0)
        if mode == "question":
            t0 = self.at(s, "timer_at_chunk", 0.2)
            if t >= t0:
                left = 3 - (t - t0)
                cx, cy, r = 540, TOP + 830, 82
                d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, 60))
                if left > 0:
                    d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * (left / 3), fill=th["accent"])
                    d.text((cx, cy + 3), str(math.ceil(left)), font=font("impact", 90), fill=INK, anchor="mm")
                else:
                    d.text((cx, cy + 3), "선택!", font=font("impact", 56), fill=WHITE, anchor="mm")
        elif sel:
            o = next(x for x in opts if x["k"] == sel)
            k = ease_out_back((t - s.voice_start) / 0.35, 1.6)
            rc, pad = card((960, 190), 30, (255, 255, 255, 255), outline=th["accent"], width=8)
            lay = Image.new("RGBA", rc.size, (0, 0, 0, 0))
            lay.alpha_composite(rc)
            ImageDraw.Draw(lay).text((pad + 30, pad + 26), f"{sel}를 고른 당신", font=font("impact", 40),
                                     fill=(150, 60, 200))
            rb = fit_block(o["result"], "bold", 50, INK, (210, 40, 120), 880, 110, pad=0)
            lay.alpha_composite(rb, (int(pad + 480 - rb.width / 2), int(pad + 80 + (110 - rb.height) / 2)))
            paste_scaled(cv, lay, (W / 2, TOP + 830), lerp(0.6, 1.0, k), alpha=clamp((t - s.voice_start) / 0.1))

    # ---------- 6. 카톡 NG vs OK ----------
    def bubble_times(self, s):
        side = s.visual.get("side")
        r = self.script["rounds"][s.visual.get("round", 0)]
        msgs = r.get(side, [])
        dur = max(0.5, s.voice_end - s.voice_start)
        return [s.voice_start + 0.1 + dur * 0.8 * j / max(1, len(msgs)) for j in range(len(msgs))]

    def draw_katalk(self, cv, s, t):
        rounds = self.script["rounds"]
        mode = s.visual.get("mode", "item")
        cur = s.visual.get("round", 0 if mode == "hook" else len(rounds) - 1)
        r = rounds[cur]
        side_now = s.visual.get("side") if mode == "item" else None
        shown = {"ng": 0, "ok": 0}
        for sc in self.items:
            if sc.visual.get("round", 0) != cur:
                continue
            sd = sc.visual.get("side")
            if sc.idx < s.idx:
                shown[sd] = len(r.get(sd, []))
            elif sc.idx == s.idx:
                shown[sd] = sum(1 for tt in self.bubble_times(sc) if t >= tt)
        if mode in ("verdict", "cta"):
            shown = {k: len(r.get(k, [])) for k in shown}
        mark_t = None
        if mode in ("verdict", "cta"):
            mark_t = s.start if mode == "verdict" else s.start - 1
        elif side_now == "ok" and self.bubble_times(s):
            mark_t = self.bubble_times(s)[-1] + 0.6
        marks = mark_t is not None and t >= mark_t
        for side, x0, col, lab in (("ng", 40, RED, "NG"), ("ok", 555, GREEN, "OK")):
            ph = Image.new("RGBA", (485, 880), (0, 0, 0, 0))
            pd = ImageDraw.Draw(ph)
            pd.rounded_rectangle((0, 0, 484, 879), 44, fill=(30, 30, 34, 255))
            pd.rounded_rectangle((14, 14, 470, 865), 34, fill=(186, 206, 224, 255))
            pd.rounded_rectangle((14, 14, 470, 110), 34, fill=(166, 188, 208, 255))
            pd.rectangle((14, 80, 470, 110), fill=(166, 188, 208, 255))
            pd.text((60, 62), r.get("name", "썸녀"), font=font("semi", 34), fill=INK, anchor="lm")
            pd.ellipse((380, 28, 456, 104), fill=col)
            pd.text((418, 67), lab, font=font("impact", 36), fill=WHITE, anchor="mm")
            y = 140
            fnt = font("semi", 36)
            for j, m in enumerate(r.get(side, [])[:shown[side]]):
                lines = wrap_text(m["text"], fnt, 310)
                bh = 50 * len(lines) + 26
                bw = int(max(fnt.getlength(strip_markup(l)) for l in lines)) + 40
                if m["from"] == "me":
                    bx = 450 - bw
                    pd.rounded_rectangle((bx, y, 450, y + bh), 22, fill=(254, 229, 0))
                else:
                    pd.ellipse((30, y, 80, y + 50), fill=(240, 240, 240))
                    bx = 92
                    pd.rounded_rectangle((bx, y, bx + bw, y + bh), 22, fill=WHITE)
                for li, l in enumerate(lines):
                    pd.text((bx + 20, y + 13 + li * 50), strip_markup(l), font=fnt, fill=INK)
                y += bh + 22
            if side_now and side_now != side:
                ov = Image.new("RGBA", ph.size, (0, 0, 0, 0))
                ov.putalpha(Image.eval(ph.getchannel("A"), lambda v: int(v * 0.5)))
                ph = Image.alpha_composite(ph, ov)
            paste_scaled(cv, ph, (x0 + 242, TOP + 450), 1.03 if side_now == side else 1.0)
            if marks:
                rt = mark_t
                k = ease_out_cubic((t - rt) / 0.2)
                mk = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
                md = ImageDraw.Draw(mk)
                if side == "ng":
                    md.line((40, 40, 320, 320), fill=RED, width=46)
                    md.line((320, 40, 40, 320), fill=RED, width=46)
                else:
                    md.ellipse((30, 30, 330, 330), outline=GREEN, width=44)
                paste_scaled(cv, mk, (x0 + 242, TOP + 500), lerp(1.8, 1.0, k), alpha=clamp((t - rt) / 0.08) * 0.92)

    # ---------- 7. 새벽 독백 에세이 ----------
    def draw_essay(self, cv, s, t):
        th = self.theme
        i, c = s.chunk_at(t)
        if c is None or t < s.voice_start - 0.05:
            prev = self.scenes[s.idx - 1] if s.idx > 0 else None
            if prev is None or not prev.chunks:
                return
            c = prev.chunks[-1]
        key = c.text
        cache = self.__dict__.setdefault("_essay", {})
        if key not in cache:
            cache[key] = text_block(key, "semi", 82, th["text"], th["accent"], 880, gap=1.3)
        img = cache[key]
        k = clamp((t - c.start) / 0.45)
        y = 900 + 30 * (1 - ease_out_cubic(k))
        paste_scaled(cv, img, (W / 2, y), 1.0, alpha=ease_in_out(k) if k < 1 else 1.0)
        d = ImageDraw.Draw(cv)
        mx, my = 860, 560 + 8 * math.sin(t * 0.8)
        d.ellipse((mx - 70, my - 70, mx + 70, my + 70), fill=(255, 226, 170))
        d.ellipse((mx - 40, my - 92, mx + 100, my + 48), fill=(14, 13, 18))
        rnd = random.Random(4)
        for _ in range(26):
            px, sp = rnd.uniform(60, 1020), rnd.uniform(12, 30)
            py = 1350 - ((t * sp + rnd.uniform(0, 900)) % 900)
            r_ = rnd.uniform(2, 4.5)
            d.ellipse((px - r_, py - r_, px + r_, py + r_), fill=(255, 220, 170, int(rnd.uniform(40, 120))))
        d.text((540, 1300), "— 꼬인다 언니의 새벽 노트 —", font=font("body", 34), fill=(150, 140, 130), anchor="mm")

    # ---------- 8. N단계 공략 ----------
    def draw_steps(self, cv, s, t):
        th = self.theme
        steps = self.script["steps"]
        n = len(steps)
        mode = s.visual.get("mode", "item")
        cur = s.visual.get("step", -1 if mode == "hook" else n - 1)
        d = ImageDraw.Draw(cv)
        sw = 860 / n
        sh = 120
        base = 1330
        for i in range(n):
            x0 = 110 + i * sw
            top = base - (i + 1) * sh
            lit = i <= cur
            col = th["accent"] if i == cur else ((255, 190, 140) if lit else (255, 255, 255))
            d.rounded_rectangle((x0, top, x0 + sw - 8, base), 18, fill=col + (255 if lit else 150,),
                                outline=INK, width=5)
            d.text((x0 + sw / 2 - 4, top + 50), str(i + 1), font=font("impact", 64),
                   fill=WHITE if i == cur else INK, anchor="mm")
        d.text((110 + (n - 1) * sw + sw / 2, base - n * sh - 40), "커플!", font=font("hand", 54), fill=th["accent"],
               anchor="mm", stroke_width=6, stroke_fill=WHITE)
        # 콩이 계단을 오름
        if cur >= 0:
            lt = t - s.start
            j = clamp(lt / 0.45) if mode == "item" else 1.0
            prev = cur - 1 if mode == "item" else cur
            def pos(k):
                return (110 + k * sw + sw / 2 - 4, base - (k + 1) * sh) if k >= 0 else (60, base)
            (x1, y1), (x2, y2) = pos(prev), pos(cur)
            x = lerp(x1, x2, j)
            y = lerp(y1, y2, j) - math.sin(j * math.pi) * 90
            bean(d, x, y, 170, gender=self.script.get("hero_gender", "m"), expr="happy" if j >= 1 else "shock", t=t)
            st = steps[cur]
            k = ease_out_back((t - s.voice_start) / 0.35, 1.6) if mode == "item" else 1.0
            lab = Image.new("RGBA", (960, 260), (0, 0, 0, 0))
            ld = ImageDraw.Draw(lab)
            ld.rounded_rectangle((0, 0, 959, 259), 34, fill=(255, 255, 255, 240), outline=th["accent"], width=8)
            ld.rounded_rectangle((30, 28, 230, 92), 30, fill=th["accent"])
            ld.text((130, 61), f"STEP {cur + 1}", font=font("impact", 44), fill=WHITE, anchor="mm")
            nb = fit_block(st["name"], "hand", 70, INK, th["accent"], 680, 90, pad=0)
            lab.alpha_composite(nb, (260, int(60 - nb.height / 2)))
            if st.get("sub"):
                sb = fit_block(st["sub"], "semi", 40, (70, 70, 80), th["accent"], 880, 110, pad=0)
                lab.alpha_composite(sb, (int(480 - sb.width / 2), int(185 - sb.height / 2)))
            paste_scaled(cv, lab, (W / 2, TOP + 140), lerp(0.7, 1.0, k))

    # ---------- 9. 자가진단 체크리스트 ----------
    def draw_checklist(self, cv, s, t):
        th = self.theme
        checks = self.script["checks"]
        d = ImageDraw.Draw(cv)
        board, pad = card((900, 910), 30, (150, 100, 60, 255))
        paste_card(cv, board, pad, 90, TOP - 10)
        d.rounded_rectangle((120, TOP + 40, 960, BOT + 60), 14, fill=(255, 255, 252))
        d.rounded_rectangle((420, TOP - 40, 660, TOP + 40), 18, fill=(160, 160, 170), outline=(90, 90, 96), width=5)
        d.text((540, TOP + 105), self.script.get("sheet", "연애 위험 자가진단"), font=font("impact", 60),
               fill=th["accent"], anchor="mm")
        done = {}
        for sc in self.items:
            i = sc.visual["check"]
            if sc.idx < s.idx:
                done[i] = 1.0
            elif sc.idx == s.idx:
                done[i] = clamp((t - self.reveal_time(sc)) / 0.4)
        if s.visual.get("mode") in ("verdict", "cta"):
            done = {i: 1.0 for i in range(len(checks))}
        rh = min(140, int(760 / max(1, len(checks))))
        for i, c in enumerate(checks):
            y = TOP + 170 + i * rh
            d.line((150, y + rh - 6, 930, y + rh - 6), fill=(190, 210, 235), width=3)
            if i in done:
                check_box(d, 160, y + rh / 2 - 38, 66, checked=True, progress=done[i])
                tb = fit_block(c, "pen", 66, INK, th["accent"], 690, rh - 10, pad=0)
                cv.alpha_composite(tb, (240, int(y + rh / 2 - 8 - tb.height / 2)))
            else:
                check_box(d, 160, y + rh / 2 - 38, 66, checked=False)
        if done:
            cnt = sum(1 for v in done.values() if v >= 1)
            d.text((930, TOP + 105), f"{cnt}/{len(checks)}", font=font("impact", 52), fill=th["accent"], anchor="rm")

    # ---------- 10. O X 판정 ----------
    def draw_ox(self, cv, s, t):
        th = self.theme
        cases = self.script["cases"]
        mode = s.visual.get("mode", "item")
        cur = s.visual.get("case", -1 if mode == "hook" else len(cases) - 1)
        d = ImageDraw.Draw(cv)
        decided = {}
        for sc in self.items:
            i = sc.visual["case"]
            rt = self.reveal_time(sc)
            if sc.idx < s.idx or (sc.idx == s.idx and t >= rt):
                decided[i] = rt
        n = len(cases)
        for i in range(n):
            x = 540 + (i - (n - 1) / 2) * 120
            y = TOP + 10
            d.ellipse((x - 44, y - 44, x + 44, y + 44), fill=(255, 255, 255, 40), outline=WHITE, width=4)
            if i in decided:
                ox = cases[i]["ox"]
                col = GREEN if ox == "O" else RED
                d.ellipse((x - 44, y - 44, x + 44, y + 44), fill=col)
                d.text((x, y + 2), ox, font=font("impact", 56), fill=WHITE, anchor="mm")
        if cur < 0:
            return
        c = cases[cur]
        lt = t - s.start
        k = ease_out_back(lt / 0.35, 1.5) if mode == "item" else 1.0
        cc = Image.new("RGBA", (960, 330), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cc)
        cd.rounded_rectangle((0, 0, 959, 329), 36, fill=WHITE)
        cd.rounded_rectangle((30, 24, 230, 86), 30, fill=th["accent"])
        cd.text((130, 56), f"CASE {cur + 1}", font=font("impact", 42), fill=INK, anchor="mm")
        tb = fit_block(c["text"], "bold", 64, INK, (0, 110, 220), 880, 210, pad=0)
        cc.alpha_composite(tb, (int(480 - tb.width / 2), int(205 - tb.height / 2)))
        paste_scaled(cv, cc, (W / 2, TOP + 260), lerp(0.6, 1.0, k))
        if cur in decided and t >= decided[cur]:
            dt = t - decided[cur]
            kk = ease_out_cubic(dt / 0.18)
            mk = Image.new("RGBA", (520, 520), (0, 0, 0, 0))
            md = ImageDraw.Draw(mk)
            if c["ox"] == "O":
                md.ellipse((50, 50, 470, 470), outline=GREEN, width=70)
            else:
                md.line((70, 70, 450, 450), fill=RED, width=80)
                md.line((450, 70, 70, 450), fill=RED, width=80)
            paste_scaled(cv, mk, (W / 2, 1090), lerp(2.2, 1.0, kk), alpha=clamp(dt / 0.08))
            lab = c.get("label") or ("가능" if c["ox"] == "O" else "불가능")
            d.text((540, 1090), lab, font=font("impact", 84), fill=WHITE, anchor="mm", stroke_width=10,
                   stroke_fill=INK)

    # ---------- 표지 (= 썸네일, 영상 0초) ----------
    def cover(self):
        if getattr(self, "_cover", None) is not None:
            return self._cover
        th = self.theme
        im = self.bg.copy()
        sc = self.items[-1] if self.items else self.scenes[min(2, len(self.scenes) - 1)]
        tt = max(sc.voice_end - 0.01, (self.reveal_time(sc) or sc.voice_start) + 1.5)
        tt = min(tt, sc.end - 0.01)
        cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.draw_content(cv, sc, tt)
        hero = cv.crop((0, TOP - 60, W, BOT + 20))
        big = rich_block(self.script.get("cover", self.script["hook"]), font(th["font"] if th["font"] != "semi" else
                                                                             "impact", 150),
                         th["text"] if self.p != "essay" else WHITE, th["accent"], stroke=12,
                         stroke_fill=th["stroke"] if self.p != "essay" else (0, 0, 0), line_gap=1.08)
        bs = min(1.0, 1040 / big.width)
        big_bottom = 440 + big.height * bs / 2
        top = big_bottom - 10
        hs = min(1.0, (1800 - top) / hero.height)
        hcy = top + hero.height * hs / 2
        if self.p == "essay":
            hs, hcy = 1.0, 1180
        paste_scaled(im, hero, (W / 2, hcy), hs)
        paste_scaled(im, big, (W / 2, 440), bs)
        paste_scaled(im, self.badge_img(), (W / 2, min(1760, hcy + hero.height * hs / 2 - 20)), 0.85, rotate=-5)
        self._cover = im
        return im

    # ---------- 출력 (패턴별 BGM) ----------
    def render(self, out: Path, preview_only_frames=None):
        out.parent.mkdir(parents=True, exist_ok=True)
        if preview_only_frames:
            for ft in preview_only_frames:
                self.render_frame(ft).convert("RGB").save(out.parent / f"frame_{ft:05.2f}.png")
            return
        voices = [(s.voice_start, A.read_wav(s.audio)) for s in self.scenes if s.audio]
        kind = self.theme["bgm"]
        if kind == "tension":
            bgm = A.bgm_tension(self.total)
        elif kind == "night":
            bgm = A.bgm_lofi(self.total, bpm=66)
        else:
            bgm = A.bgm_lofi(self.total, bpm=self.script.get("bpm", 88))
        mixed = A.mix(self.total, voices, self.sfx_events(), bgm, bgm_gain=0.42 if voices else 0.9)
        wav = out.with_suffix(".wav")
        A.write_wav(wav, mixed)
        fw = FrameWriter(out, (W, H), wav)
        for i in range(int(self.total * FPS)):
            fw.write(self.render_frame(i / FPS))
        fw.close()
        wav.unlink()
        return out
