from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene 1: Defining the Goal ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("Area Under a Curve", color=TEXT_COLOR).scale(0.8).to_edge(UP)
        equation = Text("Integral of f(x) dx", color=HIGHLIGHT_COLOR).scale(1.2)
        
        axes = Axes(x_range=[0, 6, 1], y_range=[0, 4, 1], axis_config={"include_tip": False})
        curve = axes.plot(lambda x: 0.1 * (x-2)**2 + 1, x_range=[0.5, 5.5], color=TEXT_COLOR)
        area = axes.get_area(curve, x_range=[1, 4], color=HIGHLIGHT_COLOR, opacity=0.3)
        
        self.play(Create(axes), Write(title), run_time=3)
        self.play(Create(curve), run_time=3)
        self.play(FadeIn(area), run_time=3)
        self.play(Write(equation), run_time=3)
        self.play(Indicate(equation), run_time=2)
        self.wait(6.69)

# ── Scene 2: Riemann Sums ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        axes = Axes(x_range=[0, 6, 1], y_range=[0, 4, 1], axis_config={"include_tip": False})
        curve = axes.plot(lambda x: 0.1 * (x-2)**2 + 1, x_range=[0.5, 5.5], color=TEXT_COLOR)
        
        def get_rects(n):
            return axes.get_riemann_rectangles(curve, x_range=[1, 4], dx=(3/n), color=HIGHLIGHT_COLOR, fill_opacity=0.5)
        
        rects = get_rects(4)
        eq = Text("Sum f(xi) dx", color=HIGHLIGHT_COLOR).to_edge(UP)
        
        self.add(axes, curve)
        self.play(Create(rects), Write(eq), run_time=4)
        
        for n in [10, 25, 50]:
            new_rects = get_rects(n)
            self.play(Transform(rects, new_rects), run_time=3)
        
        self.play(Circumscribe(rects), run_time=3)
        self.wait(10.93)

# ── Scene 3: The Limit Process ──
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        eq = Text("lim(dx->0) Sum f(x) dx = Integral f(x) dx", color=TEXT_COLOR).scale(0.7)
        
        self.play(FadeIn(eq, scale=0.5), run_time=3)
        self.play(eq.animate.set_color(HIGHLIGHT_COLOR), run_time=2)
        self.play(Indicate(eq), run_time=3)
        
        width_line = Line(LEFT, RIGHT, color=HIGHLIGHT_COLOR).shift(DOWN*2)
        label = Text("dx", color=TEXT_COLOR).next_to(width_line, UP)
        self.add(width_line, label)
        self.play(width_line.animate.scale(0.1), run_time=6)
        self.wait(10.19)

# ── Scene 4: Fundamental Theorem ──
class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("Fundamental Theorem of Calculus", color=TEXT_COLOR).scale(0.7).to_edge(UP)
        formula = Text("Integral f(x) dx = F(b) - F(a)", color=HIGHLIGHT_COLOR).scale(1.2)
        
        self.play(Write(title), run_time=3)
        self.play(Write(formula), run_time=4)
        
        box = SurroundingRectangle(formula, color=TEXT_COLOR, buff=0.3)
        self.play(Create(box), run_time=3)
        
        self.play(formula.animate.set_color(WHITE), run_time=2)
        self.play(FadeOut(VGroup(title, formula, box)), run_time=3)
        self.wait(6.81)