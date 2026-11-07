"""Manim 시험 장면: 복리 공식 + 곡선 (약 5초). 경제2 '공식·그래프 설명' 장면용 견본.

  manim -qm compound_scene.py CompoundInterest -o compound_test.mp4 --media_dir <출력폴더>
한글은 Pango(Text)로, 수식은 LaTeX(MathTex)로 그린다. 폰트는 neogul-edit의 Pretendard.
"""
import os
from manim import *
from manimpango import register_font

FONT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".claude", "skills", "neogul-edit", "scripts", "fonts"))
DARK, RED, YEL, MUTED = "#181614", "#F2262B", "#E3C04B", "#A39D94"


class CompoundInterest(Scene):
    def construct(self):
        for f in ("Pretendard-ExtraBold.otf", "Pretendard-Bold.otf", "Pretendard-Medium.otf"):
            register_font(os.path.join(FONT_DIR, f))
        if True:
            self.camera.background_color = DARK
            title = Text("복리, 이자가 이자를 낳는다", font="Pretendard", weight=BOLD, font_size=44).to_edge(UP, buff=0.5)
            formula = MathTex(r"A = P\,(1+r)^{t}", font_size=64, color=YEL).next_to(title, DOWN, buff=0.4)
            ax = Axes(x_range=[0, 20, 5], y_range=[0, 40, 10], x_length=9, y_length=3.6,
                      axis_config={"color": MUTED, "include_numbers": True, "font_size": 22}).to_edge(DOWN, buff=0.5)
            curve = ax.plot(lambda t: 1.2 ** t, x_range=[0, 20], color=RED, stroke_width=6)
            dot = Dot(ax.c2p(20, 1.2 ** 20), color=YEL)
            lab = Text("20년 후 약 38배", font="Pretendard", font_size=28, color=YEL).next_to(dot, LEFT, buff=0.3)
            self.play(FadeIn(title, shift=DOWN * 0.3), run_time=0.6)
            self.play(Write(formula), run_time=1.0)
            self.play(Create(ax), run_time=0.8)
            self.play(Create(curve), run_time=1.6, rate_func=linear)
            self.play(FadeIn(dot, scale=2), FadeIn(lab), run_time=0.5)
            self.wait(0.5)
