"""롱폼 렌더러 (1920x1080): '지도 한 장' 화이트보드 + 콩 캐릭터 꽁트 + 타이틀 카드.

샷 종류
  map   : 3840x2160 지도 캔버스 위를 카메라가 이동/줌. 요소는 장면 진행률에 맞춰 손글씨로 등장.
  skit  : 파스텔 배경 + 콩 캐릭터 대화 (말풍선 자막, 실제 음성 크기로 입 모양 싱크)
  title : 지도 블러 배경 + 검은 박스 타이틀 (혼잡스 썸네일 스타일)
"""
from __future__ import annotations

import json
import math
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from . import audio as A
from . import doodle as D
from .core import (FPS, INK, MINT, ORANGE, PAPER, PEACH, SKY, WHITE, YELLOW, clamp, draw_rich_line, ease_in_out,
                   ease_out_back, ease_out_cubic, font, hand_arrow, lerp, marker_circle, parse_markup,
                   paste_scaled, rich_block, strip_markup, wrap_text)
from .timeline import FrameWriter, build

W, H = 1920, 1080
MW, MH = 3840, 2160
BG = {"peach": PEACH, "mint": MINT, "sky": SKY, "paper": PAPER, "lilac": (226, 216, 240),
      "storm": (196, 198, 208), "blush": (248, 205, 205), "night": (60, 58, 82)}
EL_DUR = {"heading": 0.45, "text": 0.7, "check": 0.8, "circle": 0.5, "arrow": 0.45, "icon": 0.4, "titlebox": 0.5}


class LongRenderer:
    def __init__(self, project: Path):
        self.dir = project
        self.script = json.loads((project / "script.json").read_text(encoding="utf-8"))
        self.scenes, self.total = build(project, self.script)
        self.els = {e["id"]: e for e in self.script["map"]["elements"]}
        self.cams = self.script["map"]["cams"]
        self.reveal_t = {}
        for s in self.scenes:
            vd = s.voice_end - s.voice_start
            for eid, frac in s.data.get("reveal", []):
                self.reveal_t[eid] = s.voice_start + vd * frac
        self._baked: set = set()
        self._canvas = None
        self._icon_cache = {}
        self._env = {}
        for s in self.scenes:
            if s.audio:
                x = A.read_wav(s.audio)
                hop = A.SR // FPS
                n = len(x) // hop
                rms = np.sqrt(np.mean(x[: n * hop].reshape(n, hop) ** 2, axis=1))
                self._env[s.id] = rms / (rms.max() + 1e-9)
        self._title_bg = None

    # ---------------- 지도 요소 ----------------
    def el_box(self, e):
        """circle 대상의 강조 단어 bbox."""
        f = self.el_font(e)
        x, y = e["x"], e["y"]
        if e["kind"] == "check":
            x += 110
        for seg, key in parse_markup(e["text"]):
            w = f.getlength(seg)
            if key:
                asc, desc = f.getmetrics()
                return (x, y, x + w, y + asc + desc * 0.3)
            x += w
        w = f.getlength(strip_markup(e["text"]))
        return (e["x"], y, e["x"] + w, y + sum(f.getmetrics()))

    @staticmethod
    def el_font(e):
        if e["kind"] == "heading":
            return font("hand", e.get("size", 140))
        return font("pen", e.get("size", 92 if e["kind"] == "text" else 86))

    def icon_layer(self, e):
        k = e["id"]
        if k not in self._icon_cache:
            s = e.get("size", 240)
            im = Image.new("RGBA", (int(s * 2.2), int(s * 2.2)), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            c = im.width / 2
            kind = e["icon"]
            if kind == "money":
                D.money_stack(d, c - s / 2, c, s, 3)
            elif kind == "ticket":
                D.ticket(d, c, c, s)
            elif kind == "heart":
                D.heart(d, c, c, s / 2)
            elif kind == "chat":
                D.chat_bubble_icon(d, c, c, s / 2)
            elif kind == "clock":
                D.clock(d, c, c, s / 2, 2.0)
            elif kind == "soju":
                D.soju(d, c - s * 0.2, c + s / 2, s)
            elif kind == "phone":
                D.phone(d, c, c, s)
            elif kind == "sparkle":
                D.sparkle(d, c, c, s / 2)
            self._icon_cache[k] = im
        return self._icon_cache[k]

    def draw_el(self, canvas: Image.Image, e, p: float):
        """p: 등장 진행률 0~1"""
        d = ImageDraw.Draw(canvas)
        kind = e["kind"]
        if kind in ("heading", "text"):
            f = self.el_font(e)
            txt = e["text"]
            if kind == "text" and p < 1:  # 타자기
                plain = strip_markup(txt)
                n = int(len(plain) * ease_in_out(p))
                txt = self._cut_markup(txt, n)
            yoff = (1 - ease_out_cubic(p)) * 30 if kind == "heading" else 0
            if kind == "heading":
                f2 = f
                if p < 1:
                    # 페이드: 종이색과 섞인 잉크
                    a = ease_out_cubic(p)
                    ink = tuple(int(lerp(c1, c2, a)) for c1, c2 in zip(PAPER, INK))
                    key = tuple(int(lerp(c1, c2, a)) for c1, c2 in zip(PAPER, ORANGE))
                else:
                    ink, key = INK, ORANGE
                draw_rich_line(d, (e["x"], e["y"] + yoff), txt, f2, ink, key, anchor_center=False)
                # 밑줄
                if p > 0.5:
                    w = f2.getlength(strip_markup(e["text"]))
                    q = ease_out_cubic((p - 0.5) / 0.5)
                    asc, desc = f2.getmetrics()
                    yy = e["y"] + asc + desc * 0.5
                    d.line((e["x"], yy, e["x"] + w * q, yy + 4), fill=INK, width=6)
            else:
                draw_rich_line(d, (e["x"], e["y"]), txt, f, INK, ORANGE, anchor_center=e.get("center", False))
        elif kind == "check":
            f = self.el_font(e)
            s = 66
            D.check_box(d, e["x"], e["y"] + 16, s, True, clamp((p - 0.1) / 0.5))
            if p > 0.3:
                plain = strip_markup(e["text"])
                n = int(len(plain) * ease_in_out((p - 0.3) / 0.7))
                draw_rich_line(d, (e["x"] + 110, e["y"]), self._cut_markup(e["text"], n), f, INK, ORANGE,
                               anchor_center=False)
        elif kind == "circle":
            t = self.els[e["target"]]
            x0, y0, x1, y1 = self.el_box(t)
            pad = e.get("pad", 26)
            marker_circle(d, (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + pad, (y1 - y0) / 2 + pad * 0.7,
                          ease_out_cubic(p), seed=zlib.crc32(e["id"].encode()) % 1000)
        elif kind == "arrow":
            p1, p2 = e["p1"], e["p2"]
            q = ease_out_cubic(p)
            end = (lerp(p1[0], p2[0], q), lerp(p1[1], p2[1], q))
            if q > 0.05:
                hand_arrow(d, p1, end, INK, 6, seed=zlib.crc32(e["id"].encode()) % 1000, head=26 * q)
        elif kind == "icon":
            lay = self.icon_layer(e)
            k = ease_out_back(p, 2.2)
            paste_scaled(canvas, lay, (e["x"], e["y"]), max(0.01, k))
        elif kind == "titlebox":
            lay = self.titlebox_layer(e["text"], e.get("small"))
            paste_scaled(canvas, lay, (e["x"], e["y"]), lerp(0.6, 1.0, ease_out_back(p, 1.6)))

    @staticmethod
    def _cut_markup(txt, n):
        out, cnt = "", 0
        for ch in txt:
            if ch == "*":
                out += ch
                continue
            if cnt >= n:
                break
            out += ch
            cnt += 1
        if out.count("*") % 2:
            out += "*"
        return out

    def titlebox_layer(self, text, small=None, scale=1.0):
        key = ("tb", text, small, scale)
        if key not in self._icon_cache:
            self._icon_cache[key] = self._titlebox_layer(text, small, scale)
        return self._icon_cache[key]

    def _titlebox_layer(self, text, small=None, scale=1.0):
        f = font("impact", int(150 * scale))
        tw = f.getlength(strip_markup(text))
        w, h = int(tw + 200 * scale), int((300 if small else 240) * scale)
        im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((36, 40, 36 + w, 40 + h), int(20 * scale), fill=(0, 0, 0, 90))
        d.rounded_rectangle((30, 30, 30 + w, 30 + h), int(20 * scale), fill=(22, 22, 22), outline=WHITE, width=int(8 * scale))
        y = 30 + 40 * scale
        if small:
            fs = font("bold", int(64 * scale))
            sw = fs.getlength(small)
            bx = 30 + w / 2 - sw / 2 - 40 * scale
            d.rounded_rectangle((bx, y, bx + 56 * scale, y + 56 * scale), 12, fill=ORANGE)
            d.text((bx + 28 * scale, y + 28 * scale), "*", font=font("bold", int(60 * scale)), fill=WHITE, anchor="mm")
            d.text((bx + 76 * scale, y - 8 * scale), small, font=fs, fill=WHITE)
            y += 90 * scale
        draw_rich_line(d, (30 + w / 2, y), text, f, WHITE, ORANGE)
        return im

    def map_canvas(self, t):
        done = {k for k, rt in self.reveal_t.items()
                if t >= rt + EL_DUR[self.els[k]["kind"]] and self.els[k]["kind"] != "titlebox"}
        if self._canvas is None or not self._baked <= done:
            self._canvas = Image.new("RGB", (MW, MH), PAPER)
            self._baked = set()
        order = [e["id"] for e in self.script["map"]["elements"]]
        for k in order:
            if k in done and k not in self._baked:
                self.draw_el(self._canvas, self.els[k], 1.0)
                self._baked.add(k)
        canvas = self._canvas.copy()
        for k in order:
            if k in self.reveal_t and k not in done and t >= self.reveal_t[k] and self.els[k]["kind"] != "titlebox":
                p = (t - self.reveal_t[k]) / EL_DUR[self.els[k]["kind"]]
                self.draw_el(canvas, self.els[k], clamp(p))
        return canvas

    def cam_at(self, s, t):
        name = s.data.get("cam", "overview")
        c = self.cams[name]
        lt = t - s.start
        prev = next((x for x in reversed(self.scenes[: s.idx]) if x.data.get("shot") == "map"), None)
        drift = 1 + 0.015 * clamp(lt / 8)
        if prev is not None and prev.data.get("cam") != name and lt < 0.8 and \
                self.scenes[s.idx - 1].data.get("shot") == "map":
            pc = self.cams[prev.data.get("cam", "overview")]
            k = ease_in_out(lt / 0.8)
            # 줌아웃했다가 들어가는 아크 (지도 위를 날아가는 느낌)
            z = lerp(pc["zoom"], c["zoom"], k) * (1 - 0.18 * math.sin(math.pi * k))
            return lerp(pc["x"], c["x"], k), lerp(pc["y"], c["y"], k), z
        return c["x"], c["y"], c["zoom"] * drift

    def render_map(self, s, t):
        canvas = self.map_canvas(t)
        cx, cy, z = self.cam_at(s, t)
        vw, vh = MW / z, MH / z
        x0 = clamp(cx - vw / 2, 0, MW - vw) if vw <= MW else cx - vw / 2
        y0 = clamp(cy - vh / 2, 0, MH - vh) if vh <= MH else cy - vh / 2
        box = (int(x0), int(y0), int(x0 + vw), int(y0 + vh))
        if box[0] < 0 or box[1] < 0 or box[2] > MW or box[3] > MH:
            pad = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), PAPER)
            pad.paste(canvas, (-box[0], -box[1]))
            view = pad
        else:
            view = canvas.crop(box)
        im = view.resize((W, H), Image.BILINEAR).convert("RGBA")
        # 중앙 타이틀 박스: 전체 보기일 때만 화면 위에 얹는다
        sc = W / vw
        for e in self.script["map"]["elements"]:
            if e["kind"] == "titlebox" and e["id"] in self.reveal_t and t >= self.reveal_t[e["id"]] and z < 1.3:
                p = clamp((t - self.reveal_t[e["id"]]) / EL_DUR["titlebox"])
                lay = self.titlebox_layer(e["text"], e.get("small"))
                fade = clamp((1.3 - z) / 0.2)
                paste_scaled(im, lay, ((e["x"] - x0) * sc, (e["y"] - y0) * sc),
                             sc * 1.25 * lerp(0.6, 1.0, ease_out_back(p, 1.6)), alpha=fade)
        return im

    # ---------------- 꽁트 ----------------
    def talk_level(self, s, t):
        env = self._env.get(s.id)
        if env is None:
            return abs(math.sin(t * 14)) if s.voice_start <= t < s.voice_end else 0.0
        i = int((t - s.voice_start) * FPS)
        if 0 <= i < len(env):
            return clamp(env[i] * 1.6)
        return 0.0

    def render_skit(self, s, t):
        v = s.data["skit"]
        im = Image.new("RGBA", (W, H), BG.get(v.get("bg", "peach")) + (255,))
        d = ImageDraw.Draw(im)
        lt = t - s.start
        for pr in v.get("props", []):
            kind, x, y, size = pr
            k = ease_out_back((lt - 0.15) / 0.4, 2.0)
            if k <= 0:
                continue
            if kind == "sparkle":
                D.sparkle(d, x, y, size * k, t=t)
            else:
                lay = self.icon_layer({"id": f"skit_{kind}_{size}", "icon": kind, "size": size})
                paste_scaled(im, lay, (x, y + math.sin(t * 2 + x) * 6), k)
        # 누가 말하나: "who"(캐릭터 role) 지정 > 목소리로 추정. "narr": true 면 내레이션(말풍선 대신 자막 바)
        speaker = s.data.get("who") or ("m" if s.data.get("voice", "여의도남자") == "여의도남자" else "f")
        narr = s.data.get("narr", False)
        talk = self.talk_level(s, t)
        # 흔들림(막장 장면 강조)
        sh = 0.0
        sa = v.get("shake_at_chunk")
        if sa is not None and len(s.chunks) > sa and 0 <= t - s.chunks[sa].start < 0.4:
            sh = 22 * (1 - (t - s.chunks[sa].start) / 0.4)
        ox = math.sin(t * 90) * sh
        for ch in v.get("chars", []):
            g = ch["g"]
            role = ch.get("role", g)
            D.bean(d, ch["x"] + ox, ch.get("base", 1180), ch.get("h", 700), g, ch.get("expr", "neutral"),
                   talking=talk if (role == speaker and not narr) else 0.0, t=t, look=ch.get("look", 0.0),
                   arm=ch.get("arm", "down"), seed={"m": 1, "f": 4, "mom": 7, "gm": 9, "gp": 11}.get(g, 2))
        if v.get("title"):
            draw_rich_line(d, (W / 2, 50), v["title"], font("hand", 116), INK, ORANGE)
        # 말풍선 자막
        i, c = s.chunk_at(t)
        if v.get("vignette"):  # 막장 분위기: 붉은/어두운 가장자리
            vg = Image.new("L", (W, H), 0)
            ImageDraw.Draw(vg).ellipse((-W * 0.2, -H * 0.3, W * 1.2, H * 1.3), fill=255)
            vg = vg.filter(ImageFilter.GaussianBlur(120)).point(lambda x: int((255 - x) * 0.75))
            col = Image.new("RGBA", (W, H), {"red": (120, 0, 10), "dark": (0, 0, 0)}[v["vignette"]] + (255,))
            col.putalpha(vg)
            im.alpha_composite(col)
            d = ImageDraw.Draw(im)
        if narr:
            self.draw_caption_bar(im, s, t)
            return im
        if c is not None and t >= s.voice_start - 0.05:
            f = font("hand", 78)
            lines = wrap_text(c.text, f, 900)
            sp = next((ch for ch in v.get("chars", []) if ch.get("role", ch["g"]) == speaker), None)
            left = sp is not None and sp["x"] < W / 2
            bub = D.speech_bubble(None, lines, f, tail="left" if left else "right")
            bx = sp["x"] + (260 if left else -260) if sp else W / 2
            bx = clamp(bx, bub.width / 2 + 30, W - bub.width / 2 - 30)
            k = ease_out_back((t - c.start) / 0.18, 2.0)
            paste_scaled(im, bub, (bx, 340), lerp(0.7, 1.0, k))
        return im

    # ---------------- 타이틀 ----------------
    def render_title(self, s, t):
        if self._title_bg is None:
            full = Image.new("RGB", (MW, MH), PAPER)
            for e in self.script["map"]["elements"]:
                if e["kind"] != "titlebox":
                    self.draw_el(full, e, 1.0)
            bg = full.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(5))
            self._title_bg = ImageEnhance.Brightness(bg).enhance(0.92).convert("RGBA")
        im = self._title_bg.copy()
        v = s.data["title"]
        lt = t - s.start
        k = ease_out_back(lt / 0.45, 1.8)
        th = self.script.get("thumbnail", {})
        if th.get("lines"):  # 썸네일과 같은 박스를 영상 속 타이틀 카드로 (썸네일-영상 일치 → 이탈 감소)
            if getattr(self, "_tbox", None) is None:
                self._tbox = thumb_box(th["lines"], th.get("small", "연애 공략"))
            lay = self._tbox
        else:
            lay = self.titlebox_layer(v["big"], v.get("small"), 0.95)
        paste_scaled(im, lay, (W / 2, H / 2 - 40), lerp(0.3, 1.0, k) * min(1.0, 1500 / lay.width),
                     alpha=clamp(lt / 0.15))
        d = ImageDraw.Draw(im)
        D.bean(d, 300, 1200, 520, "m", "think" if lt < 2 else "neutral", t=t, arm="think", look=0.6)
        D.bean(d, 1640, 1200, 500, "f", "smirk", t=t, look=-0.6, seed=4)
        return im

    # ---------------- 자막 바 ----------------
    def draw_caption_bar(self, im, s, t):
        i, c = s.chunk_at(t)
        if c is None or t < s.voice_start - 0.05:
            return
        f = font("semi", 52)
        lines = wrap_text(c.text, f, 1500)
        lay = rich_block(lines, f, INK, ORANGE, pad=0, line_gap=1.2)
        w, h = lay.width + 150, lay.height + 44
        bar = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bar)
        bd.rounded_rectangle((10, 14, 10 + w, 14 + h), h // 2 if h < 120 else 34, fill=(0, 0, 0, 60))
        bd.rounded_rectangle((10, 10, 10 + w, 10 + h), h // 2 if h < 120 else 34, fill=WHITE, outline=INK, width=4)
        # 화자 아바타
        g = "m" if s.data.get("voice", "여의도남자") == "여의도남자" else "f"
        if s.data.get("who") in ("mom", "gm"):
            g = s.data["who"]
        av = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        ad = ImageDraw.Draw(av)
        ad.ellipse((4, 4, 116, 116), fill={"m": (205, 226, 245), "f": (252, 214, 222), "mom": (255, 200, 170), "gm": (225, 235, 210)}[g],
                   outline=INK, width=4)
        D.bean(ad, 60, 190, 190, g, "angry" if g == "mom" else "neutral", talking=self.talk_level(s, t), t=t,
               seed={"m": 1, "f": 4, "mom": 7, "gm": 9}[g])
        m = Image.new("L", (120, 120), 0)
        ImageDraw.Draw(m).ellipse((4, 4, 116, 116), fill=255)
        bar.paste(av, (26, 10 + (h - 120) // 2 + 2), m)
        bar.alpha_composite(lay, (10 + 130, 10 + 22))
        k = ease_out_back((t - c.start) / 0.15, 1.5)
        paste_scaled(im, bar, (W / 2, H - 110), lerp(0.92, 1.0, k))

    # ---------------- 프레임 ----------------
    def shot_frame(self, s, t):
        shot = s.data.get("shot", "map")
        if shot == "skit":
            return self.render_skit(s, t)
        if shot == "title":
            im = self.render_title(s, t)
        else:
            im = self.render_map(s, t)
        self.draw_caption_bar(im, s, t)
        return im

    def render_frame(self, t):
        if t < self.script.get("cover_sec", 0.0):  # 영상 맨 앞 = 썸네일 그대로 (클릭 후 '그 장면' 확인)
            if getattr(self, "_cover", None) is None:
                self._cover = thumb_image(self)
            return self._cover.copy()
        s = next((x for x in self.scenes if x.start <= t < x.end), self.scenes[-1])
        im = self.shot_frame(s, t)
        lt = t - s.start
        prev = self.scenes[s.idx - 1] if s.idx > 0 else None
        if prev is not None and lt < 0.4 and self._needs_wipe(prev, s):
            k = ease_out_cubic(lt / 0.4)
            old = self.shot_frame(prev, prev.end - 0.001)
            frame = Image.new("RGBA", (W, H))
            frame.paste(old, (int(-W * 0.35 * k), 0))
            frame.paste(im, (int(W * (1 - k)), 0))
            sh = Image.new("RGBA", (40, H), (0, 0, 0, 70))
            frame.alpha_composite(sh, (max(0, int(W * (1 - k)) - 40), 0))
            im = frame
        if 0 <= t - self.script.get("cover_sec", 0.0) < 0.25 and self.script.get("cover_sec", 0.0) == 0:
            im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - t / 0.25)))))
        if t > self.total - 0.6:
            im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * clamp((t - self.total + 0.6) / 0.6)))))
        return im

    @staticmethod
    def _needs_wipe(a, b):
        sa, sb = a.data.get("shot", "map"), b.data.get("shot", "map")
        if sa != sb:
            return True
        if sa == "skit" and a.data["skit"].get("title") != b.data["skit"].get("title"):
            return True
        return False

    def sfx_events(self):
        ev = []
        for s in self.scenes:
            for name, off in s.data.get("sfx", []):
                ev.append((s.voice_start + off, name, 1.0))
            prev = self.scenes[s.idx - 1] if s.idx > 0 else None
            if prev is not None and (self._needs_wipe(prev, s) or
                                     (s.data.get("shot") == "map" and prev.data.get("shot") == "map"
                                      and prev.data.get("cam") != s.data.get("cam"))):
                ev.append((s.start - 0.05, "whoosh", 0.8))
        for eid, rt in self.reveal_t.items():
            k = self.els[eid]["kind"]
            if k == "circle":
                ev.append((rt, "marker", 0.9))
            elif k in ("icon", "titlebox"):
                ev.append((rt, "pop", 0.7))
            elif k == "heading":
                ev.append((rt, "tick", 1.0))
            elif k == "check":
                ev.append((rt + 0.15, "pop", 0.5))
        return ev

    def render(self, out: Path, preview_only_frames=None):
        out.parent.mkdir(parents=True, exist_ok=True)
        if preview_only_frames:
            for ft in preview_only_frames:
                self._canvas = None
                self.render_frame(ft).convert("RGB").save(out.parent / f"long_{ft:06.2f}.png")
            return
        voices = [(s.voice_start, A.read_wav(s.audio)) for s in self.scenes if s.audio]
        mixed = A.mix(self.total, voices, self.sfx_events(), A.bgm_lofi(self.total), bgm_gain=0.32 if voices else 0.8)
        wav = out.with_suffix(".wav")
        A.write_wav(wav, mixed)
        fw = FrameWriter(out, (W, H), wav)
        n = int(self.total * FPS)
        for i in range(n):
            fw.write(self.render_frame(i / FPS))
            if i % 300 == 0:
                print(f"  {i}/{n}", flush=True)
        fw.close()
        wav.unlink()
        return out


def thumb_box(lines, small="연애 공략"):
    """썸네일·타이틀 카드 공용 검은 박스: 작은 라벨 + 2줄 초대형 문구(둘째 줄 주황)."""
    from pronounce import join_won  # timeline이 voice 경로를 등록해 둠
    lines = [join_won(x) for x in lines]
    f = font("impact", 190)
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * 1.02)
    tw = max(f.getlength(strip_markup(l)) for l in lines)
    bw = int(min(1260, tw + 120))
    bh = lh * len(lines) + 150
    im = Image.new("RGBA", (bw + 30, bh + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 14, bw + 10, bh + 14), 28, fill=(0, 0, 0, 90))
    d.rounded_rectangle((0, 0, bw, bh), 28, fill=(20, 20, 20), outline=WHITE, width=10)
    d.rounded_rectangle((50, 38, 106, 94), 12, fill=ORANGE)
    d.text((78, 66), "*", font=font("bold", 60), fill=WHITE, anchor="mm")
    d.text((124, 30), small, font=font("bold", 62), fill=WHITE)
    sc = min(1.0, (bw - 100) / tw)
    for i, l in enumerate(lines):
        lay = rich_block([l], f, WHITE, ORANGE, pad=0)
        paste_scaled(im, lay, (bw / 2, 120 + lh * i + lh / 2), sc)
    return im


def thumb_image(r: "LongRenderer"):
    """롱폼 썸네일 1920x1080 RGBA (채널 고정 포맷).
    흰 지도 배경 + 왼쪽 검은 박스 + 오른쪽 놀란 콩 + X친 소품 + 빨간 화살표.
    script.json "thumbnail": {"small": "연애 공략", "lines": ["25만 원 쓰고", "*차인 이유*"], "icon": "money"}
    """
    th = r.script.get("thumbnail", {})
    lines = th.get("lines") or [th.get("big", "이 지도 *한 장*이면 끝")]
    full = Image.new("RGB", (MW, MH), PAPER)
    for e in r.script["map"]["elements"]:
        if e["kind"] != "titlebox":
            r.draw_el(full, e, 1.0)
    im = full.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.2)).convert("RGBA")
    im.alpha_composite(Image.new("RGBA", (W, H), (250, 249, 246, 90)))
    box = thumb_box(lines, th.get("small", "연애 공략"))
    x0, y0 = 60, (H - box.height) // 2 - 10
    im.alpha_composite(box, (x0, y0))
    d = ImageDraw.Draw(im)
    if th.get("villain"):  # 막장 시리즈: 화난 장모 콩(크게) + 겁먹은 남편 콩(작게) + 빼앗긴 소품
        D.bean(d, 1600, 1260, 760, "mom", "angry", arm="point", look=-0.7, seed=7)
        D.bean(d, 1150, 1150, 360, "m", th.get("victim", "shock"), look=0.6)
    else:
        D.bean(d, 1640, 1240, 760, "m", "shock", arm="point", look=-0.6)
    icon = th.get("icon")
    if icon and th.get("villain"):
        lay = r.icon_layer({"id": "thumb_icon", "icon": icon, "size": 210})
        paste_scaled(im, lay, (1330, 300), 1.0, rotate=-14)
    elif icon:
        lay = r.icon_layer({"id": "thumb_icon", "icon": icon, "size": 230})
        paste_scaled(im, lay, (1560, 260), 1.0, rotate=12)
        d.line((1450, 160, 1680, 380), fill=(229, 57, 53), width=26)
        d.line((1680, 160, 1450, 380), fill=(229, 57, 53), width=26)
    if not th.get("villain"):
        hand_arrow(d, (1500, 600), (x0 + box.width, y0 + box.height - 150), (229, 57, 53), 16, seed=2, head=60)
    return im


def thumbnail(r: "LongRenderer", out: Path):
    thumb_image(r).convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=95)
