"""컨셉 B "카톡 판독소": 카톡 대화를 재현 → 읽씹/답장 속마음 판독 → 그린/레드라이트 도장.

script.json
  "concept": "kakao", "chat": {"name": "소개팅녀", "date": "10월 11일 토요일"}
  scene.visual.mode = "chat" | "judge" | "cta" | "hook"
    add:   [{"from": "me"|"them", "text", "time", "unread": true}]  장면 음성에 맞춰 차례로 등장
    typing: true            상대 메시지 앞에 '...' 입력 중 표시
    highlight: "them_time"  마지막 상대 메시지 시간에 주황 마커 동그라미
    read_at_chunk: n        n번째 자막 시점에 내 메시지의 '1'이 사라짐 (읽씹 연출)
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

from .core import INK, ORANGE, WHITE, clamp, ease_out_back, ease_out_cubic, font, marker_circle
from .short import ShortBase, W

PW, PH = 960, 900               # 카톡 패널 크기
KAKAO_BG = (178, 199, 217)      # 카톡 기본 채팅 배경
ME = (254, 229, 0)
TYPING_SEC = 0.7


class KakaoShort(ShortBase):
    badge_text = "카톡 판독소"

    def __init__(self, project: Path):
        super().__init__(project)
        self.chat = self.script.get("chat", {})
        self.msgs = []      # (msg, appear_t, read_t)
        last_me = None
        for s in self.scenes:
            v = s.visual
            adds = v.get("add", [])
            vd = max(0.1, s.voice_end - s.voice_start)
            for i, m in enumerate(adds):
                at = s.voice_start + vd * i / max(1, len(adds))
                self.msgs.append([m, at, None])
                if m["from"] == "me":
                    last_me = self.msgs[-1]
            if "read_at_chunk" in v and last_me is not None and len(s.chunks) > v["read_at_chunk"]:
                last_me[2] = s.chunks[v["read_at_chunk"]].start
        self.f_msg = font("body", 46)
        self.f_time = font("body", 26)
        self.f_name = font("semi", 30)

    def extra_sfx(self):
        ev = []
        for m, at, rt in self.msgs:
            ev.append((at, "pop", 0.6 if m["from"] == "me" else 0.8))
            if rt:
                ev.append((rt, "tick", 1.0))
        return ev

    # ---------- 그리기 ----------
    def wrap(self, text, maxw=560):
        lines, cur = [], ""
        for ch in text:
            if self.f_msg.getlength(cur + ch) > maxw and cur:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        return lines + ([cur] if cur else [])

    def bubble_h(self, m):
        return len(self.wrap(m["text"])) * 60 + 38

    def main_layer(self, s, t):
        im = Image.new("RGBA", (PW, PH), KAKAO_BG + (255,))
        d = ImageDraw.Draw(im)
        # 헤더
        d.rectangle((0, 0, PW, 96), fill=(168, 190, 209))
        d.text((40, 48), "<", font=font("semi", 44), fill=INK, anchor="lm")
        d.text((90, 48), self.chat.get("name", "상대"), font=font("semi", 38), fill=INK, anchor="lm")
        for i in range(3):
            d.line((PW - 60, 34 + i * 14, PW - 30, 34 + i * 14), fill=INK, width=4)
        # 메시지 목록 (아래로 쌓이다 넘치면 위로 스크롤)
        visible = [(m, at, rt) for m, at, rt in self.msgs if t >= at]
        typing = s.visual.get("typing") and s.start <= t < s.voice_start + 0.05
        items, y = [], 0
        items.append(("date", None, y))
        y += 70
        prev_from = None
        for m, at, rt in visible:
            items.append(("msg", (m, at, rt), y))
            if m["from"] == "them" and prev_from != "them":
                y += 44  # 이름 줄
            y += self.bubble_h(m) + 14
            prev_from = m["from"]
        if typing:
            items.append(("typing", None, y))
            y += 90 + (44 if prev_from != "them" else 0)
        top, avail = 110, PH - 130
        scroll = max(0, y - avail)
        clip = Image.new("RGBA", (PW, PH - top), (0, 0, 0, 0))
        cd = ImageDraw.Draw(clip)
        prev_from = None
        for kind, data, iy in items:
            yy = iy - scroll
            if kind == "date":
                txt = self.chat.get("date", "")
                w = self.f_time.getlength(txt) + 40
                cd.rounded_rectangle((PW / 2 - w / 2, yy + 10, PW / 2 + w / 2, yy + 50), 20, fill=(150, 170, 190))
                cd.text((PW / 2, yy + 30), txt, font=self.f_time, fill=WHITE, anchor="mm")
                continue
            if kind == "typing":
                self.draw_them_header(cd, yy, prev_from)
                bx, by = 120, yy + (44 if prev_from != "them" else 0)
                cd.rounded_rectangle((bx, by, bx + 130, by + 70), 26, fill=WHITE)
                for k in range(3):
                    a = 0.5 + 0.5 * math.sin(t * 9 - k * 0.9)
                    c = int(180 - 90 * a)
                    cd.ellipse((bx + 30 + k * 30 - 9, by + 35 - 9, bx + 30 + k * 30 + 9, by + 35 + 9), fill=(c, c, c))
                continue
            m, at, rt = data
            pop = ease_out_back((t - at) / 0.22, 2.0)
            if m["from"] == "them":
                self.draw_them_header(cd, yy, prev_from)
                if prev_from != "them":
                    yy += 44
            self.draw_bubble(cd, clip, m, yy, pop, unread=(m.get("unread") and (rt is None or t < rt)))
            if s.visual.get("highlight") == "them_time" and m["from"] == "them" and data == self.last_them(t):
                p = ease_out_cubic((t - s.voice_start - 0.2) / 0.5)
                tx = self._time_pos
                marker_circle(cd, tx[0], tx[1], 70, 30, p, seed=3, fill=ORANGE, width=7)
            prev_from = m["from"]
        im.alpha_composite(clip, (0, top))
        mask = Image.new("L", (PW, PH), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, PW, PH), 40, fill=255)
        im.putalpha(mask)
        return im

    def last_them(self, t):
        them = [(m, at, rt) for m, at, rt in self.msgs if m["from"] == "them" and t >= at]
        return them[-1] if them else None

    def draw_them_header(self, d, y, prev_from):
        if prev_from == "them":
            return
        d.rounded_rectangle((24, y, 100, y + 76), 28, fill=(200, 210, 222))
        d.ellipse((47, y + 14, 77, y + 44), fill=WHITE)
        d.pieslice((36, y + 44, 88, y + 96), 180, 360, fill=WHITE)
        d.text((120, y + 2), self.chat.get("name", "상대"), font=self.f_name, fill=(60, 66, 76))

    def draw_bubble(self, d, layer, m, y, pop, unread=False):
        lines = self.wrap(m["text"])
        w = max(self.f_msg.getlength(l) for l in lines) + 44
        h = len(lines) * 60 + 38
        if pop <= 0.01:
            return
        if m["from"] == "me":
            x1 = PW - 30
            x0 = x1 - w
            fill = ME
        else:
            x0 = 120
            x1 = x0 + w
            fill = WHITE
        # 팝: 크기 대신 아래에서 살짝 떠오름
        yy = y + (1 - min(1.0, pop)) * 30
        d.rounded_rectangle((x0, yy, x1, yy + h), 26, fill=fill)
        for i, l in enumerate(lines):
            d.text((x0 + 24, yy + 18 + i * 60), l, font=self.f_msg, fill=(25, 25, 25))
        tm = m.get("time", "")
        tw = self.f_time.getlength(tm)
        if m["from"] == "me":
            tx = x0 - 12 - tw
            d.text((tx, yy + h - 30), tm, font=self.f_time, fill=(80, 92, 105))
            if unread:
                d.text((x0 - 14 - 24, yy + h - 74), "1", font=font("bold", 40), fill=(236, 190, 0))
        else:
            tx = x1 + 12
            d.text((tx, yy + h - 30), tm, font=self.f_time, fill=(80, 92, 105))
            self._time_pos = (tx + tw / 2, yy + h - 18)

    def pose(self, s, t):
        mode = s.visual.get("mode", "chat")
        if mode in ("chat", "hook"):
            return (W / 2, 905, 1.08, 0.0)
        return super().pose(s, t)

    def cover_scene(self):
        # 대화가 가장 많이 쌓인 장면을 표지로
        chats = [s for s in self.scenes if s.visual.get("mode") == "chat"]
        return chats[-1] if chats else self.scenes[0]

    def cover_time(self):
        return self.cover_scene().end - 0.01
