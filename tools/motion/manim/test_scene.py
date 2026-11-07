"""Manim 시험 장면(약 5초): 한글 제목 + 공식 + 그래프. 우리 채널 글꼴(Pretendard)·네온 색.
실행: /root/.cache/manim-venv/bin/manim -qm tools/motion/manim/test_scene.py FormulaDemo -o manim_test
"""
from pathlib import Path
import manimpango
from manim import *

FONT_DIR = Path(__file__).resolve().parents[3] / "assets" / "fonts"
for f in FONT_DIR.glob("Pretendard-*.otf"):
    manimpango.register_font(str(f))
config.background_color = "#0B0E1A"
MINT = "#7CD1BB"


class FormulaDemo(Scene):
    def construct(self):
        title = Text("비용은 이렇게 줄어요", font="Pretendard", weight=BOLD, font_size=54).to_edge(UP)
        eq = MathTex(r"\text{cost} = \frac{1}{444}\times \text{LLM}", color=MINT).scale(1.2).next_to(title, DOWN, buff=0.5)
        ax = Axes(x_range=[0, 10, 2], y_range=[0, 10, 2], x_length=6, y_length=3.2, tips=False,
                  axis_config={"color": GREY_B}).to_edge(DOWN, buff=0.6)
        llm = ax.plot(lambda x: x, color="#FF8A3D")
        jev = ax.plot(lambda x: x / 6, color=MINT)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=0.6)
        self.play(Write(eq), run_time=1.2)
        self.play(Create(ax), run_time=0.6)
        self.play(Create(llm), Create(jev), run_time=1.4)
        self.wait(1.2)
