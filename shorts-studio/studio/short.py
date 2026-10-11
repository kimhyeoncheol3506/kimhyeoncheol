"""쇼츠 렌더러: 블라인드 스샷 사연 낭독 + 판정소 (1080x1920)."""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from . import audio as A
from .core import (FPS, INK, RED, WHITE, YELLOW, clamp, ease_in_out, ease_out_back, ease_out_cubic, font,
                   lerp, paste_scaled, rich_block, rounded_card, wrap_text)
from .doodle import chat_bubble_icon
from .timeline import FrameWriter, build

W, H = 1080, 1920
CARD_W = 980
CAP_Y = 1455          # 자막 중심 (쇼츠 하단 UI 위)
SAFE_BOTTOM = 1600


class ShortRenderer:
    def __init__(self, project: Path):
        import json
        self.dir = project
        self.script = json.loads((project / "script.json").read_text(encoding="utf-8"))
        self.scenes, self.total = build(project, self.script)
        src = Image.open(project / self.script["source"]["image"]).convert("RGB")
        self.card_scale = CARD_W / src.width
        cw, ch = CARD_W, int(src.height * self.card_scale)
        card = src.resize((cw, ch), Image.LANCZOS).convert("RGBA")
        mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, ch), 36, fill=255)
        card.putalpha(mask)
        self.card_raw = card
        shadow, pad = rounded_card((cw, ch), 36, (0, 0, 0, 0), shadow=True, shadow_blur=30, shadow_alpha=160)
        self.card_shadow, self.card_pad = shadow, pad
        # 배경: 카드 확대 블러 + 어둡게
        bg = src.resize((int(H * src.width / src.height * 1.0), H), Image.LANCZOS)
        left = (bg.width - W) // 2
        bg = bg.crop((left, 0, left + W, H)).filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg).enhance(0.22)
        self.bg = bg.convert("RGBA")
        self.regions = {k: [v * self.card_scale for v in r] for k, r in self.script.get("card_regions", {}).items()}
        self.hook_img = rich_block(self.script["hook"], font("impact", 104), WHITE, YELLOW, stroke=8, stroke_fill=INK)
        self._cap_cache = {}
        self.rng = random.Random(3)

    # ---------- 타이밍 ----------
    def sfx_events(self):
        ev = []
        for s in self.scenes:
            for name, off in s.data.get("sfx", []):
                ev.append((s.voice_start + off, name, 1.0))
            v = s.visual
            if v.get("mode") == "judge" and "stamp_at_chunk" in v and len(s.chunks) > v["stamp_at_chunk"]:
                ev.append((s.chunks[v["stamp_at_chunk"]].start, "stamp", 1.0))
                ev.append((s.chunks[v["stamp_at_chunk"]].start + 0.02, "boom", 0.7))
        return ev

    # ---------- 그리기 ----------
    def caption_img(self, text):
        if text not in self._cap_cache:
            f = font("bold", 84)
            lines = wrap_text(text, f, 900)
            self._cap_cache[text] = rich_block(lines, f, WHITE, YELLOW, stroke=10, stroke_fill=INK, line_gap=1.12)
        return self._cap_cache[text]

    def focus_key(self, s, t):
        v = s.visual
        i, _ = s.chunk_at(t)
        fc = v.get("focus_chunks", {})
        key = v.get("focus")
        for k in sorted(fc, key=int):
            if i >= int(k):
                key = fc[k]
        return key

    def render_frame(self, t):
        frame = self.bg.copy()
        # 배경 미세 줌 (정지 화면 느낌 제거)
        z = 1 + 0.04 * (t / self.total)
        if z > 1.001:
            bw, bh = int(W * z), int(H * z)
            frame = frame.resize((bw, bh), Image.BILINEAR).crop(((bw - W) // 2, (bh - H) // 2, (bw - W) // 2 + W, (bh - H) // 2 + H))
        d = ImageDraw.Draw(frame)
        s = next((x for x in self.scenes if x.start <= t < x.end), self.scenes[-1])
        lt = t - s.start
        mode = s.visual.get("mode", "post")

        # ---- 카드 위치/스케일 ----
        prev = self.scenes[s.idx - 1] if s.idx > 0 else None
        target = self.card_pose(s, t)
        if prev is not None and lt < 0.35:
            target = tuple(lerp(a, b, ease_in_out(lt / 0.35)) for a, b in zip(self.card_pose(prev, s.start - 0.001), target))
        cx, cy, sc, dim = target
        if s.idx == 0:  # 첫 등장: 아래에서 튀어오름
            k = ease_out_back(lt / 0.45)
            cy = lerp(H + 500, cy, k)
        # 흔들림
        shake = 0.0
        sa = s.visual.get("shake_at_chunk")
        if sa is not None and len(s.chunks) > sa:
            dt = t - s.chunks[sa].start
            if 0 <= dt < 0.35:
                shake = 18 * (1 - dt / 0.35)
        if mode == "judge":
            st = self.stamp_time(s)
            if st is not None and 0 <= t - st < 0.3:
                shake = max(shake, 26 * (1 - (t - st) / 0.3))
        ox = self.rng.uniform(-shake, shake)
        oy = self.rng.uniform(-shake, shake)

        card = self.card_raw.copy()
        # 형광펜 하이라이트
        fk = self.focus_key(s, t) if mode == "post" else None
        if fk and fk in self.regions:
            x0, y0, x1, y1 = self.regions[fk]
            # 하이라이트 시작 시간: 포커스가 바뀐 시점
            hs = self.focus_start(s, fk)
            p = ease_out_cubic((t - hs) / 0.45)
            hl = Image.new("RGB", card.size, (255, 255, 255))
            ImageDraw.Draw(hl).rounded_rectangle((x0 - 8, y0 + 4, lerp(x0 - 8, x1 + 8, p), y1 - 2), 10, fill=(255, 226, 60))
            from PIL import ImageChops
            a = card.getchannel("A")
            card = ImageChops.multiply(card.convert("RGB"), hl).convert("RGBA")
            card.putalpha(a)
        if dim > 0:
            ov = Image.new("RGBA", card.size, (10, 10, 14, int(200 * dim)))
            ov.putalpha(Image.composite(ov.getchannel("A"), Image.new("L", card.size, 0), card.getchannel("A")))
            card = Image.alpha_composite(card, ov)
        sh = self.card_shadow
        paste_scaled(frame, sh, (cx + ox, cy + oy + 6), sc)
        paste_scaled(frame, card, (cx + ox, cy + oy), sc)

        # ---- 모드별 오버레이 ----
        if mode == "judge":
            self.draw_judge(frame, s, t)
        elif mode == "cta":
            self.draw_cta(frame, s, t)

        # ---- 상단 후크 타이틀 ----
        if t < 1.0:
            k = ease_out_back(t / 0.35, 2.2)
            hs_scale = lerp(1.7, 1.0, k)
        else:
            hs_scale = 1.0
        paste_scaled(frame, self.hook_img, (W / 2, 300), hs_scale * (0.92 if self.hook_img.width > 1000 else 1))

        # ---- 자막 ----
        i, c = s.chunk_at(t)
        if c is not None and t >= s.voice_start - 0.05 and mode != "judge":
            ct = t - c.start
            k = ease_out_back(ct / 0.16, 2.5)
            paste_scaled(frame, self.caption_img(c.text), (W / 2, CAP_Y), lerp(0.75, 1.0, k))
        elif c is not None and mode == "judge" and i != s.visual.get("stamp_at_chunk"):
            ct = t - c.start
            k = ease_out_back(ct / 0.16, 2.5)
            paste_scaled(frame, self.caption_img(c.text), (W / 2, CAP_Y), lerp(0.75, 1.0, k))

        # ---- 진행바 (리텐션) ----
        d = ImageDraw.Draw(frame)
        d.rectangle((0, 0, int(W * t / self.total), 10), fill=YELLOW)

        # ---- 장면 전환 펀치 + 첫 프레임 플래시 ----
        if t < 0.1:
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - t / 0.1))))
            frame = Image.alpha_composite(frame, fl)
        if s.idx > 0 and lt < 0.12:
            z = 1 + 0.05 * (1 - lt / 0.12)
            bw, bh = int(W * z), int(H * z)
            frame = frame.resize((bw, bh), Image.BILINEAR).crop(((bw - W) // 2, (bh - H) // 2, (bw - W) // 2 + W, (bh - H) // 2 + H))
        return frame

    def card_pose(self, s, t):
        mode = s.visual.get("mode", "post")
        base_cy = 905
        if mode == "hook":
            return (W / 2, base_cy, 0.92, 0.0)
        if mode == "judge":
            return (W / 2, 1010, 0.78, 0.75)
        if mode == "cta":
            return (W / 2, 900, 0.62, 0.55)
        fk = self.focus_key(s, t)
        if fk and fk in self.regions:
            # 해당 줄이 화면 중앙 근처에 오도록 확대 + 이동
            x0, y0, x1, y1 = self.regions[fk]
            cw, ch = self.card_raw.size
            zoom = 1.2
            # 후크(~420)와 자막(~1390) 사이에 카드를 고정 — 확대해도 겹치지 않게
            cy = base_cy - ((y0 + y1) / 2 - ch / 2) * zoom * 0.08
            # 강조 줄이 화면 밖으로 나가지 않게 가로 이동
            lx0 = W / 2 + (x0 - cw / 2) * zoom
            lx1 = W / 2 + (x1 - cw / 2) * zoom
            dx = 0.0
            if lx1 - lx0 < W - 60:
                dx = max(0.0, 30 - lx0) - max(0.0, lx1 - (W - 30))
            return (W / 2 + dx, cy, zoom, 0.0)
        return (W / 2, base_cy, 1.0, 0.0)

    def focus_start(self, s, key):
        fc = s.visual.get("focus_chunks", {})
        for k in sorted(fc, key=int):
            if fc[k] == key and key != s.visual.get("focus"):
                return s.chunks[int(k)].start
        return s.voice_start + 0.1

    def stamp_time(self, s):
        k = s.visual.get("stamp_at_chunk")
        if k is not None and len(s.chunks) > k:
            return s.chunks[k].start
        return None

    def draw_judge(self, frame, s, t):
        lt = t - s.start
        # 판정소 배지
        k = ease_out_back(lt / 0.35, 2.0)
        badge = Image.new("RGBA", (520, 150), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.rounded_rectangle((4, 4, 516, 146), 30, fill=RED, outline=WHITE, width=6)
        bd.text((260, 76), "판 정 소", font=font("impact", 92), fill=WHITE, anchor="mm")
        paste_scaled(frame, badge, (W / 2, 640), lerp(0.2, 1.0, k), alpha=clamp(lt / 0.15))
        st = self.stamp_time(s)
        if st is not None and t >= st:
            dt = t - st
            k = ease_out_cubic(dt / 0.18)
            stamp = self.stamp_img(s.visual.get("stamp_text", "확정"))
            paste_scaled(frame, stamp, (W / 2, 1000), lerp(2.6, 1.0, k), alpha=clamp(dt / 0.08), rotate=-12)
            if dt < 0.12:
                fl = Image.new("RGBA", (W, H), (255, 255, 255, int(180 * (1 - dt / 0.12))))
                frame.alpha_composite(fl)

    def stamp_img(self, text):
        f = font("impact", 210)
        tw = int(f.getlength(text))
        im = Image.new("RGBA", (tw + 140, 330), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((10, 10, im.width - 10, im.height - 10), 40, outline=RED, width=22)
        d.text((im.width / 2, im.height / 2), text, font=f, fill=RED, anchor="mm")
        # 도장 질감: 무작위 구멍
        a = im.getchannel("A")
        rnd = random.Random(5)
        hole = Image.new("L", im.size, 255)
        hd = ImageDraw.Draw(hole)
        for _ in range(260):
            x, y, r = rnd.uniform(0, im.width), rnd.uniform(0, im.height), rnd.uniform(1, 5)
            hd.ellipse((x - r, y - r, x + r, y + r), fill=0)
        from PIL import ImageChops
        im.putalpha(ImageChops.multiply(a, hole))
        return im

    def draw_cta(self, frame, s, t):
        lt = t - s.start
        d = ImageDraw.Draw(frame)
        k = ease_out_back((lt - 0.2) / 0.4, 2.0)
        if k > 0:
            r = 120 * k * (1 + 0.05 * math.sin(lt * 8))
            chat_bubble_icon(d, W - 210, 1180, r)

    # ---------- 출력 ----------
    def render(self, out: Path, preview_only_frames=None):
        out.parent.mkdir(parents=True, exist_ok=True)
        voices = [(s.voice_start, A.read_wav(s.audio)) for s in self.scenes if s.audio]
        bgm = A.bgm_tension(self.total) if self.script.get("bgm") == "tension" else A.bgm_lofi(self.total)
        mixed = A.mix(self.total, voices, self.sfx_events(), bgm, bgm_gain=0.42 if voices else 0.9)
        wav = out.with_suffix(".wav")
        A.write_wav(wav, mixed)
        if preview_only_frames:
            for ft in preview_only_frames:
                self.render_frame(ft).convert("RGB").save(out.parent / f"frame_{ft:05.2f}.png")
            return
        fw = FrameWriter(out, (W, H), wav)
        n = int(self.total * FPS)
        for i in range(n):
            fw.write(self.render_frame(i / FPS))
        fw.close()
        wav.unlink()
        return out
