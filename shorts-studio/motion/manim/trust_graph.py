"""Manim 그래프 설명 장면 예시: '거짓말이 쌓일수록 신뢰가 떨어진다' (세로 1080x1920, 5초).

LaTeX 없이 동작하도록 Text(한글 폰트)만 쓴다 — 컨테이너에 TeX가 없음.
렌더: $MANIM -qh --fps 30 -r 1080,1920 trust_graph.py TrustGraph -o trust_graph.mp4
"""
from pathlib import Path

import manimpango
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Axes, Create, Dot, FadeIn, FadeOut, Flash, Scene, Text, Write, config,
                   ValueTracker, always_redraw)

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"
manimpango.register_font(str(FONT_DIR / "Pretendard-ExtraBold.otf"))
manimpango.register_font(str(FONT_DIR / "BlackHanSans-Regular.ttf"))
config.background_color = "#1b1430"
config.frame_height = 16
config.frame_width = 9


class TrustGraph(Scene):
    def construct(self):
        title = Text("거짓말 횟수 vs 신뢰", font="Black Han Sans", font_size=72, color="#FFD23F").to_edge(UP, buff=2.2)
        ax = Axes(x_range=[0, 5, 1], y_range=[0, 100, 25], x_length=7, y_length=6,
                  axis_config={"color": "#bbbbbb", "include_numbers": False}).move_to(ORIGIN).shift(DOWN * 0.6 + RIGHT * 0.2)
        xl = Text("거짓말 횟수", font="Pretendard", font_size=34).next_to(ax.x_axis, DOWN, buff=0.3)
        yl = Text("신뢰", font="Pretendard", font_size=34).next_to(ax.y_axis, UP, buff=0.2).shift(LEFT * 0.2)
        curve = ax.plot(lambda x: 100 * (0.45 ** x), x_range=[0, 5], color="#ff4d6d", stroke_width=10)
        t = ValueTracker(0)
        dot = always_redraw(lambda: Dot(ax.c2p(t.get_value(), 100 * 0.45 ** t.get_value()), radius=0.16, color="#ffffff"))
        note = Text("두 번째부터 급락", font="Pretendard", font_size=44, color="#ff4d6d").move_to(ax.c2p(3.2, 55))
        self.play(Write(title), run_time=0.6)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=0.6)
        self.add(dot)
        self.play(Create(curve), t.animate.set_value(5), run_time=2.0)
        self.play(Flash(ax.c2p(2, 100 * 0.45 ** 2), color="#ff4d6d"), FadeIn(note, shift=UP * 0.2), run_time=0.8)
        self.wait(0.6)
        self.play(*[FadeOut(m) for m in (title, ax, xl, yl, curve, dot, note)], run_time=0.4)
