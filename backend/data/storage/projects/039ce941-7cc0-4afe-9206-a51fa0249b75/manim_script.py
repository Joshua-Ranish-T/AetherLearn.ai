from manim import *
import numpy as np
from typing import Optional


from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("What is a Derivative?", color=TEXT_COLOR, font_size=48).to_edge(UP)
        self.play(Write(title), run_time=2.0)
        
        axes = Axes(x_range=[-2, 2], y_range=[-0.5, 4], x_length=6, y_length=4, axis_config={"include_tip": False})
        graph = axes.plot(lambda x: x**2, color=HIGHLIGHT_COLOR)
        
        self.play(Create(axes), run_time=1.5)
        self.play(Create(graph), run_time=2.0)
        
        dot = Dot(color=HIGHLIGHT_COLOR)
        tracker = ValueTracker(-1.5)
        dot.add_updater(lambda d: d.move_to(axes.c2p(tracker.get_value(), tracker.get_value()**2)))
        
        self.add(dot)
        self.play(tracker.animate.set_value(1.5), run_time=10, rate_func=linear)
        self.play(FadeOut(VGroup(title, axes, graph, dot)), run_time=2.0)

class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        axes = Axes(x_range=[-2, 2], y_range=[-0.5, 4], x_length=6, y_length=4)
        graph = axes.plot(lambda x: x**2, color=HIGHLIGHT_COLOR)
        
        x0, x1 = -1, 1
        p1 = Dot(axes.c2p(x0, x0**2), color=BLUE)
        p2 = Dot(axes.c2p(x1, x1**2), color=BLUE)
        secant = always_redraw(lambda: Line(p1.get_center(), p2.get_center(), color=BLUE))
        
        equation = Text("f(x+h) - f(x) / h", color=TEXT_COLOR, font_size=36).to_edge(DOWN)
        
        self.add(axes, graph, p1, p2, secant)
        self.play(Create(secant), run_time=2.0)
        self.play(FadeIn(equation), run_time=1.5)
        
        self.play(p2.animate.move_to(axes.c2p(0.5, 0.25)), run_time=5)
        self.play(FadeOut(VGroup(axes, graph, p1, p2, secant, equation)), run_time=2.0)

class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        axes = Axes(x_range=[-2, 2], y_range=[-0.5, 4], x_length=6, y_length=4)
        graph = axes.plot(lambda x: x**2, color=HIGHLIGHT_COLOR)
        
        x0 = 0.5
        h = ValueTracker(1.0)
        
        p1 = Dot(axes.c2p(x0, x0**2), color=BLUE)
        p2 = always_redraw(lambda: Dot(axes.c2p(x0 + h.get_value(), (x0 + h.get_value())**2), color=BLUE))
        line = always_redraw(lambda: Line(p1.get_center(), p2.get_center(), color=BLUE))
        
        limit_eq = Text("lim (h -> 0) [f(x+h) - f(x)] / h", color=TEXT_COLOR, font_size=32).to_edge(DOWN)
        
        self.add(axes, graph, p1, p2, line)
        self.play(Write(limit_eq), run_time=2.0)
        self.play(h.animate.set_value(0.01), run_time=8, rate_func=linear)
        self.play(FadeOut(VGroup(axes, graph, p1, p2, line, limit_eq)), run_time=2.0)

class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        final_eq = Text("f'(x) = lim (h -> 0) [f(x+h) - f(x)] / h", color=HIGHLIGHT_COLOR, font_size=40)
        summary_text = Text("Instantaneous Rate of Change", color=TEXT_COLOR, font_size=32).next_to(final_eq, DOWN, buff=1)
        
        self.play(GrowFromCenter(final_eq), run_time=2.0)
        self.play(FadeIn(summary_text, shift=UP), run_time=2.0)
        self.play(Indicate(final_eq), run_time=2.0)
        self.wait(5)