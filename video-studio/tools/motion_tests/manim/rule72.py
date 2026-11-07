from manim import *

class Rule72(Scene):
    def construct(self):
        self.camera.background_color = "#1b2330"
        title = Text("72의 법칙: 해마다 7%면 약 10년마다 두 배", font="Noto Sans CJK KR", font_size=34, color="#F2C14E").to_edge(UP)
        ax = Axes(x_range=[0, 30, 10], y_range=[0, 9, 2], x_length=10, y_length=5, axis_config={"color": "#9aa6b5"}, tips=False).shift(DOWN * 0.4)
        curve = ax.plot(lambda t: 1.07 ** t, x_range=[0, 30], color="#DE5B41", stroke_width=6)
        dots = VGroup(*[Dot(ax.c2p(t, 1.07 ** t), color="#F2C14E", radius=0.09) for t in (10, 20, 30)])
        labels = VGroup(*[Text(f"{t}년 ×{1.07 ** t:.1f}", font="Noto Sans CJK KR", font_size=24, color="#F1E3C2").next_to(ax.c2p(t, 1.07 ** t), UL, buff=0.15) for t in (10, 20, 30)])
        self.play(Write(title), Create(ax), run_time=1.2)
        self.play(Create(curve), run_time=2.0, rate_func=linear)
        self.play(LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.3), LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in labels], lag_ratio=0.3), run_time=1.2)
        self.wait(0.6)
