"""제미나이 아르곤 '생각 단계' 개념 그림(약 7초). 숫자 없음(개념 그림): 생각을 더 시킬수록 정확도는 조금씩 오르다 평평해지고, 시간·비용은 가파르게 오른다.
실행: /root/.cache/manim-venv/bin/manim -qh tools/motion/manim/argon_think.py ThinkLevels
"""
from pathlib import Path
import manimpango
from manim import *

for f in (Path(__file__).resolve().parents[3] / "assets" / "fonts").glob("Pretendard-*.otf"):
    manimpango.register_font(str(f))
config.background_color = "#071226"
K = dict(font="Pretendard")


class ThinkLevels(Scene):
    def construct(self):
        title = Text("생각을 더 시키면?", weight=BOLD, font_size=56, **K).to_edge(UP, buff=0.5)
        ax = Axes(x_range=[0, 3, 1], y_range=[0, 10, 2], x_length=8.0, y_length=4.2, tips=False,
                  axis_config={"color": GREY_B, "include_ticks": False}).shift(DOWN * 0.4 + LEFT * 0.8)
        xl = VGroup(*[Text(t, font_size=30, **K).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.25) for i, t in enumerate(["낮음", "보통", "높음"])])
        acc = ax.plot(lambda x: 8.5 - 5.5 * (2.718 ** (-1.6 * x)), x_range=[0.05, 3], color="#46F2C4", stroke_width=7)
        cost = ax.plot(lambda x: 0.6 + 0.9 * x ** 2.1, x_range=[0.05, 3], color="#FFD54F", stroke_width=7)
        la = Text("정확도", font_size=34, color="#46F2C4", **K).move_to(ax.c2p(0.75, 9.2))
        lc = Text("시간 · 비용", font_size=34, color="#FFD54F", **K).next_to(cost.get_end(), RIGHT, buff=0.2)
        note = Text("개념 그림 · 실제 숫자 아님", font_size=24, color=GREY_B, **K).to_corner(DR, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=0.6)
        self.play(Create(ax), FadeIn(xl), run_time=0.8)
        self.play(Create(acc), run_time=1.4)
        self.play(FadeIn(la), run_time=0.3)
        self.play(Create(cost), run_time=1.4)
        self.play(FadeIn(lc), FadeIn(note), run_time=0.4)
        self.wait(2.0)
