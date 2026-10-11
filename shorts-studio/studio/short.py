"""쇼츠 렌더러 (1080x1920).

  ShortBase  : 공통 — 테마 배경, 표지 프레임, 상단 후크, 자막, 판정 배지/도장, CTA, 진행바, 효과음
  CardShort  : 컨셉 A "사연 판정소" — 블라인드 스샷 카드 + 형광펜 줌
  (studio/kakao.py) KakaoShort : 컨셉 B "카톡 판독소" — 카톡 대화 재현 + 읽씹 + 그린/레드라이트
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

from . import audio as A
from . import themes
from .core import (FPS, WHITE, clamp, ease_in_out, ease_out_back, ease_out_cubic, font, lerp, paste_scaled,
                   rich_block, rounded_card, wrap_text)
from .doodle import chat_bubble_icon
from .timeline import FrameWriter, build

W, H = 1080, 1920
CARD_W = 980
CAP_Y = 1455          # 자막 중심 (쇼츠 하단 UI 위)
HOOK_Y = 300
COVER_SEC = 0.35      # 첫 0.35초 = 표지 프레임 (모바일 업로드 시 '표지'로 선택)


class ShortBase:
    badge_text = "판 정 소"

    def __init__(self, project: Path):
        self.dir = project
        self.script = json.loads((project / "script.json").read_text(encoding="utf-8"))
        self.theme = themes.get(self.script.get("theme"))
        self.scenes, self.total = build(project, self.script)
        th = self.theme
        self.bg = themes.background(th, (W, H))
        self.hook_img = rich_block(self.script["hook"], font(th["font"], 108), th["text"], th["accent"],
                                   stroke=9, stroke_fill=th["stroke"])
        self._cap_cache = {}
        self.rng = random.Random(3)

    # ---------- 하위 클래스가 채우는 부분 ----------
    def main_layer(self, s, t) -> Image.Image:
        raise NotImplementedError

    def pose(self, s, t):
        """주인공(카드/카톡)의 (cx, cy, scale, dim)"""
        mode = s.visual.get("mode", "post")
        if mode == "judge":
            return (W / 2, 1010, 0.78, 0.75)
        if mode == "cta":
            return (W / 2, 900, 0.62, 0.55)
        return (W / 2, 905, 1.0, 0.0)

    def extra_sfx(self):
        return []

    # ---------- 공통 ----------
    def sfx_events(self):
        ev = [(0.0, "boom", 0.9)]
        for s in self.scenes:
            for name, off in s.data.get("sfx", []):
                ev.append((s.voice_start + off, name, 1.0))
            v = s.visual
            if v.get("mode") == "judge" and "stamp_at_chunk" in v and len(s.chunks) > v["stamp_at_chunk"]:
                ev.append((s.chunks[v["stamp_at_chunk"]].start, "stamp", 1.0))
                ev.append((s.chunks[v["stamp_at_chunk"]].start + 0.02, "boom", 0.7))
        return ev + self.extra_sfx()

    def caption_img(self, text):
        if text not in self._cap_cache:
            th = self.theme
            f = font("bold", 84)
            lines = wrap_text(text, f, 900)
            fill = WHITE if sum(th["top"]) < 450 else th["text"]
            stroke = (0, 0, 0) if sum(th["top"]) < 450 else (255, 255, 255)
            self._cap_cache[text] = rich_block(lines, f, fill, th["accent"], stroke=10, stroke_fill=stroke,
                                               line_gap=1.12)
        return self._cap_cache[text]

    def scene_at(self, t):
        return next((x for x in self.scenes if x.start <= t < x.end), self.scenes[-1])

    def stamp_time(self, s):
        k = s.visual.get("stamp_at_chunk")
        if k is not None and len(s.chunks) > k:
            return s.chunks[k].start
        return None

    def shake_amount(self, s, t):
        shake = 0.0
        sa = s.visual.get("shake_at_chunk")
        if sa is not None and len(s.chunks) > sa:
            dt = t - s.chunks[sa].start
            if 0 <= dt < 0.35:
                shake = 18 * (1 - dt / 0.35)
        st = self.stamp_time(s) if s.visual.get("mode") == "judge" else None
        if st is not None and 0 <= t - st < 0.3:
            shake = max(shake, 26 * (1 - (t - st) / 0.3))
        return shake

    def render_frame(self, t):
        if t < COVER_SEC:
            return self.cover()
        frame = self.bg.copy()
        s = self.scene_at(t)
        lt = t - s.start
        mode = s.visual.get("mode", "post")
        prev = self.scenes[s.idx - 1] if s.idx > 0 else None
        target = self.pose(s, t)
        if prev is not None and lt < 0.35:
            target = tuple(lerp(a, b, ease_in_out(lt / 0.35)) for a, b in zip(self.pose(prev, s.start - 0.001), target))
        cx, cy, sc, dim = target
        if s.idx == 0:  # 첫 등장: 아래에서 튀어오름
            k = ease_out_back((t - COVER_SEC) / 0.45)
            cy = lerp(H + 500, cy, k)
        shake = self.shake_amount(s, t)
        ox, oy = self.rng.uniform(-shake, shake), self.rng.uniform(-shake, shake)

        layer = self.main_layer(s, t)
        if dim > 0:
            ov = Image.new("RGBA", layer.size, (10, 10, 14, int(200 * dim)))
            ov.putalpha(ImageChops.multiply(ov.getchannel("A"), layer.getchannel("A")))
            layer = Image.alpha_composite(layer, ov)
        sh, _ = rounded_card(layer.size, 36, (0, 0, 0, 0), shadow=True, shadow_blur=30, shadow_alpha=170) \
            if not hasattr(self, "_shadow") else (self._shadow, 0)
        self._shadow = sh
        paste_scaled(frame, sh, (cx + ox, cy + oy + 6), sc)
        paste_scaled(frame, layer, (cx + ox, cy + oy), sc)

        if mode == "judge":
            self.draw_judge(frame, s, t)
        elif mode == "cta":
            self.draw_cta(frame, s, t)

        k = ease_out_back((t - COVER_SEC) / 0.25, 2.0)
        paste_scaled(frame, self.hook_img, (W / 2, HOOK_Y), lerp(1.12, 1.0, k) * min(1.0, 1000 / self.hook_img.width))

        i, c = s.chunk_at(t)
        stamp_chunk = s.visual.get("stamp_at_chunk") if mode == "judge" else None
        if c is not None and t >= s.voice_start - 0.05 and i != stamp_chunk:
            k = ease_out_back((t - c.start) / 0.16, 2.5)
            paste_scaled(frame, self.caption_img(c.text), (W / 2, CAP_Y), lerp(0.75, 1.0, k))

        ImageDraw.Draw(frame).rectangle((0, 0, int(W * t / self.total), 10), fill=self.theme["bar"])
        if s.idx > 0 and lt < 0.12:
            z = 1 + 0.05 * (1 - lt / 0.12)
            bw, bh = int(W * z), int(H * z)
            frame = frame.resize((bw, bh), Image.BILINEAR).crop(((bw - W) // 2, (bh - H) // 2,
                                                                  (bw - W) // 2 + W, (bh - H) // 2 + H))
        return frame

    # ---------- 표지 (= 썸네일) ----------
    def cover(self):
        if getattr(self, "_cover", None) is None:
            th = self.theme
            im = self.bg.copy()
            # 주인공을 크게 기울여 깔고, 그 위에 초대형 후크
            hero = self.main_layer(self.cover_scene(), self.cover_time())
            hero = hero.rotate(-4, resample=Image.BICUBIC, expand=True)
            sh, _ = rounded_card((int(hero.width * 0.9), int(hero.height * 0.9)), 36, (0, 0, 0, 0),
                                 shadow=True, shadow_blur=34, shadow_alpha=200)
            paste_scaled(im, sh, (W / 2 + 30, 1195), 1.0)
            paste_scaled(im, hero, (W / 2 + 30, 1180), 0.98)
            big = rich_block(self.script.get("cover", self.script["hook"]), font(th["font"], 150), th["text"],
                             th["accent"], stroke=12, stroke_fill=th["stroke"], line_gap=1.08)
            paste_scaled(im, big, (W / 2, 470), min(1.0, 1040 / big.width))
            badge = self.badge_img()
            paste_scaled(im, badge, (W / 2, 1560), 0.9, rotate=-6)
            self._cover = im
        return self._cover

    def cover_scene(self):
        return self.scenes[min(len(self.scenes) - 1, 3)]

    def cover_time(self):
        s = self.cover_scene()
        return s.voice_end - 0.01

    def badge_img(self):
        th = self.theme
        f = font("impact", 92)
        w = int(f.getlength(self.badge_text)) + 120
        badge = Image.new("RGBA", (w, 150), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.rounded_rectangle((4, 4, w - 4, 146), 30, fill=th["badge"], outline=WHITE, width=6)
        bd.text((w / 2, 76), self.badge_text, font=f, fill=WHITE, anchor="mm")
        return badge

    def draw_judge(self, frame, s, t):
        lt = t - s.start
        k = ease_out_back(lt / 0.35, 2.0)
        paste_scaled(frame, self.badge_img(), (W / 2, 640), lerp(0.2, 1.0, k), alpha=clamp(lt / 0.15))
        st = self.stamp_time(s)
        if st is not None and t >= st:
            dt = t - st
            k = ease_out_cubic(dt / 0.18)
            color = {"red": (229, 57, 53), "green": (30, 190, 90)}.get(s.visual.get("stamp_color"), self.theme["stamp"])
            stamp = self.stamp_img(s.visual.get("stamp_text", "확정"), color)
            paste_scaled(frame, stamp, (W / 2, 1000), lerp(2.6, 1.0, k), alpha=clamp(dt / 0.08), rotate=-12)
            if dt < 0.12:
                frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(180 * (1 - dt / 0.12)))))

    def stamp_img(self, text, color):
        f = font("impact", 200)
        tw = int(f.getlength(text))
        im = Image.new("RGBA", (tw + 140, 320), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((10, 10, im.width - 10, im.height - 10), 40, fill=(255, 255, 255, 200), outline=color, width=22)
        d.text((im.width / 2, im.height / 2), text, font=f, fill=color, anchor="mm")
        a = im.getchannel("A")
        rnd = random.Random(5)
        hole = Image.new("L", im.size, 255)
        hd = ImageDraw.Draw(hole)
        for _ in range(110):  # 잉크 빠짐 질감 (흰색으로 메워 지저분한 점 방지)
            x, y, r = rnd.uniform(0, im.width), rnd.uniform(0, im.height), rnd.uniform(1, 3)
            hd.ellipse((x - r, y - r, x + r, y + r), fill=120)
        im.putalpha(ImageChops.multiply(a, hole))
        return im

    def draw_cta(self, frame, s, t):
        lt = t - s.start
        k = ease_out_back((lt - 0.2) / 0.4, 2.0)
        if k > 0:
            r = 120 * k * (1 + 0.05 * math.sin(lt * 8))
            chat_bubble_icon(ImageDraw.Draw(frame), W - 210, 1180, r)

    # ---------- 출력 ----------
    def render(self, out: Path, preview_only_frames=None):
        out.parent.mkdir(parents=True, exist_ok=True)
        if preview_only_frames:
            for ft in preview_only_frames:
                self.render_frame(ft).convert("RGB").save(out.parent / f"frame_{ft:05.2f}.png")
            return
        voices = [(s.voice_start, A.read_wav(s.audio)) for s in self.scenes if s.audio]
        bgm = A.bgm_tension(self.total) if self.script.get("bgm") == "tension" else A.bgm_lofi(self.total)
        mixed = A.mix(self.total, voices, self.sfx_events(), bgm, bgm_gain=0.42 if voices else 0.9)
        wav = out.with_suffix(".wav")
        A.write_wav(wav, mixed)
        fw = FrameWriter(out, (W, H), wav)
        for i in range(int(self.total * FPS)):
            fw.write(self.render_frame(i / FPS))
        fw.close()
        wav.unlink()
        return out


class CardShort(ShortBase):
    """컨셉 A: 사연 판정소 (블라인드 스샷)."""

    def __init__(self, project: Path):
        super().__init__(project)
        src = Image.open(project / self.script["source"]["image"]).convert("RGB")
        self.card_scale = CARD_W / src.width
        cw, ch = CARD_W, int(src.height * self.card_scale)
        card = src.resize((cw, ch), Image.LANCZOS).convert("RGBA")
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, ch), 36, fill=255)
        card.putalpha(mask)
        self.card_raw = card
        # 배경: 테마 그라데이션 위에 카드 블러를 은은하게
        blur = src.resize((W, int(W * src.height / src.width))).resize((W, H)).filter(ImageFilter.GaussianBlur(40))
        blur = ImageEnhance.Brightness(blur).enhance(0.5).convert("RGBA")
        blur.putalpha(60)
        self.bg = Image.alpha_composite(self.bg, blur)
        self.regions = {k: [v * self.card_scale for v in r] for k, r in self.script.get("card_regions", {}).items()}

    def focus_key(self, s, t):
        v = s.visual
        i, _ = s.chunk_at(t)
        key = v.get("focus")
        for k, val in sorted(v.get("focus_chunks", {}).items(), key=lambda kv: int(kv[0])):
            if i >= int(k):
                key = val
        return key

    def focus_start(self, s, key):
        for k, val in sorted(s.visual.get("focus_chunks", {}).items(), key=lambda kv: int(kv[0])):
            if val == key and key != s.visual.get("focus"):
                return s.chunks[int(k)].start
        return s.voice_start + 0.1

    def pose(self, s, t):
        mode = s.visual.get("mode", "post")
        if mode == "hook":
            return (W / 2, 905, 0.92, 0.0)
        fk = self.focus_key(s, t) if mode == "post" else None
        if fk and fk in self.regions:
            x0, y0, x1, y1 = self.regions[fk]
            cw, ch = self.card_raw.size
            zoom = 1.2
            cy = 905 - ((y0 + y1) / 2 - ch / 2) * zoom * 0.08
            lx0 = W / 2 + (x0 - cw / 2) * zoom
            lx1 = W / 2 + (x1 - cw / 2) * zoom
            dx = 0.0
            if lx1 - lx0 < W - 60:
                dx = max(0.0, 30 - lx0) - max(0.0, lx1 - (W - 30))
            return (W / 2 + dx, cy, zoom, 0.0)
        return super().pose(s, t)

    def main_layer(self, s, t):
        card = self.card_raw
        fk = self.focus_key(s, t) if s.visual.get("mode", "post") == "post" else None
        if fk and fk in self.regions:
            x0, y0, x1, y1 = self.regions[fk]
            p = ease_out_cubic((t - self.focus_start(s, fk)) / 0.45)
            hl = Image.new("RGB", card.size, (255, 255, 255))
            ImageDraw.Draw(hl).rounded_rectangle((x0 - 8, y0 + 4, lerp(x0 - 8, x1 + 8, p), y1 - 2), 10,
                                                 fill=(255, 226, 60))
            a = card.getchannel("A")
            card = ImageChops.multiply(card.convert("RGB"), hl).convert("RGBA")
            card.putalpha(a)
        return card

    def cover_scene(self):
        return next((s for s in self.scenes if s.visual.get("focus") == "title1"), self.scenes[0])


def load(project: Path):
    script = json.loads((project / "script.json").read_text(encoding="utf-8"))
    if script.get("concept") == "kakao":
        from .kakao import KakaoShort
        return KakaoShort(project)
    return CardShort(project)


ShortRenderer = CardShort  # 하위 호환
