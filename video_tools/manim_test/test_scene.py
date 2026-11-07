# Manim 테스트(가상 값 — 실제 영상에 쓰지 말 것): 주간 가격 꺾은선 그래프 (설명형 장면 예시, LaTeX 없이 Text만 사용)
import os, manimpango
from manim import *
manimpango.register_font(os.path.expanduser("~/.cache/ranking-video/fonts/Pretendard-Bold.otf"))
config.background_color = "#0D0E11"

class PriceLine(Scene):
    def construct(self):
        title = Text("부시리 kg당 경락가", font="Pretendard", weight=BOLD, color="#D6B26E").scale(0.8).to_edge(UP)
        ax = Axes(x_range=[0, 3, 1], y_range=[4000, 11000, 2000], x_length=9, y_length=4.5,
                  axis_config={"color": "#8C919B", "include_ticks": True}).shift(DOWN * 0.4)
        pts = [(0, 10000), (1, 8200), (2, 7100), (3, 5500)]
        line = ax.plot_line_graph([p[0] for p in pts], [p[1] for p in pts], line_color="#5FB7A6",
                                  vertex_dot_style={"color": "#F2EDE3"}, stroke_width=8)
        lab = Text("▼45%", font="Pretendard", weight=BOLD, color="#5FB7A6").scale(1.1).next_to(ax.c2p(3, 5500), UR)
        self.play(FadeIn(title), Create(ax), run_time=1.2)
        self.play(Create(line), run_time=2.0)
        self.play(Write(lab), run_time=0.8)
        self.wait(1.0)
