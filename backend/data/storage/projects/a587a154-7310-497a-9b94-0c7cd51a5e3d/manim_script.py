from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene 1: Introduction to Squares ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("Introduction to Squares", font_size=36).to_edge(UP)
        self.play(Write(title), run_time=1.5)
        
        square = Square(side_length=3, color=HIGHLIGHT_COLOR)
        label = Text("Side = 3", font_size=24).next_to(square, DOWN)
        
        self.play(Create(square), run_time=2.0)
        self.play(Write(label), run_time=1.0)
        
        # Continuous animation: Wiggle the square to emphasize its properties
        self.play(Indicate(square), run_time=2.0)
        self.play(square.animate.rotate(PI/4), run_time=2.0)
        self.play(square.animate.rotate(-PI/4), run_time=2.0)
        
        self.play(FadeOut(VGroup(title, square, label)), run_time=1.5)

# ── Scene 2: The Formula ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        formula = Text("A = s^2", font_size=72, color=TEXT_COLOR)
        explanation = Text("Area = side x side", font_size=36, color=HIGHLIGHT_COLOR).next_to(formula, DOWN, buff=1.0)
        
        self.play(Write(formula), run_time=2.0)
        self.play(FadeIn(explanation, shift=UP), run_time=1.5)
        
        # Visual representation of s^2
        square_rep = Square(side_length=2, color=HIGHLIGHT_COLOR).shift(LEFT * 3)
        s_label = Text("s", font_size=24).next_to(square_rep, LEFT)
        s_label_bottom = Text("s", font_size=24).next_to(square_rep, DOWN)
        
        self.play(Create(square_rep), Write(s_label), Write(s_label_bottom), run_time=2.5)
        self.play(Circumscribe(formula), run_time=2.0)
        
        self.play(FadeOut(VGroup(formula, explanation, square_rep, s_label, s_label_bottom)), run_time=1.5)

# ── Scene 3: Application ──
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Start with formula
        eq1 = Text("A = s^2", font_size=48)
        self.play(Write(eq1), run_time=1.5)
        
        # Transform to substitution
        eq2 = Text("A = 3^2", font_size=48, color=HIGHLIGHT_COLOR)
        self.play(ReplacementTransform(eq1, eq2), run_time=2.0)
        
        # Expand to multiplication
        eq3 = Text("A = 3 x 3", font_size=48, color=HIGHLIGHT_COLOR)
        self.play(ReplacementTransform(eq2, eq3), run_time=2.0)
        
        # Visual grid to show 3x3
        grid = VGroup(*[
            Square(side_length=1, color=TEXT_COLOR).move_to(np.array([x, y, 0]))
            for x in [-1, 0, 1] for y in [-1, 0, 1]
        ]).scale(0.8).shift(DOWN * 1.5)
        
        self.play(LaggedStart(*[Create(s) for s in grid], lag_ratio=0.1), run_time=3.0)
        self.play(Indicate(grid), run_time=2.0)
        
        self.play(FadeOut(VGroup(eq3, grid)), run_time=1.5)

# ── Scene 4: Conclusion ──
class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        final_text = Text("A = 9", font_size=96, color=HIGHLIGHT_COLOR)
        sub_text = Text("Area = 9 square units", font_size=36).next_to(final_text, DOWN)
        
        self.play(GrowFromCenter(final_text), run_time=2.0)
        self.play(Write(sub_text), run_time=1.5)
        
        # Final flourish
        self.play(Flash(final_text, color=HIGHLIGHT_COLOR, line_length=0.5), run_time=2.0)
        self.play(final_text.animate.scale(1.2).set_color(WHITE), run_time=1.5)
        
        self.wait(2.0)
        self.play(FadeOut(VGroup(final_text, sub_text)), run_time=1.5)