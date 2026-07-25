from manim import *
import numpy as np
from typing import Optional


from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE


# ── Scene 1: Introduction to Right Triangles — target: 15.14 seconds ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        triangle = Polygon(LEFT*2 + DOWN*1.5, RIGHT*2 + DOWN*1.5, LEFT*2 + UP*1.5, color=TEXT_COLOR)
        right_angle = Square(side_length=0.3).shift(LEFT*1.7 + DOWN*1.2)
        
        label_a = Text("a", font_size=36).next_to(triangle, LEFT)
        label_b = Text("b", font_size=36).next_to(triangle, DOWN)
        label_c = Text("c", font_size=36, color=HIGHLIGHT_COLOR).next_to(triangle, UR, buff=0.1)
        
        labels = VGroup(label_a, label_b, label_c)
        
        self.play(Create(triangle), Create(right_angle), run_time=3)
        self.wait(2)
        self.play(FadeIn(labels), run_time=2)
        self.wait(8.14)


# ── Scene 2: Visualizing the Squares — target: 20.69 seconds ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        sq_a = Square(color=BLUE, fill_opacity=0.5).scale(0.5).shift(LEFT*2)
        sq_b = Square(color=GREEN, fill_opacity=0.5).scale(0.5).shift(DOWN*2)
        sq_c = Square(color=HIGHLIGHT_COLOR, fill_opacity=0.5).scale(0.5).shift(UP*1 + RIGHT*1)
        
        text_a = Text("a^2", font_size=24).move_to(sq_a)
        text_b = Text("b^2", font_size=24).move_to(sq_b)
        text_c = Text("c^2", font_size=24).move_to(sq_c)
        
        squares = VGroup(sq_a, sq_b, sq_c)
        labels = VGroup(text_a, text_b, text_c)
        
        self.play(GrowFromCenter(squares), FadeIn(labels), run_time=3)
        self.wait(2)
        
        # Transform a and b into c
        self.play(
            Transform(sq_a, sq_c.copy()),
            Transform(sq_b, sq_c.copy()),
            run_time=4
        )
        self.wait(11.69)


# ── Scene 3: The Formula — target: 15.5 seconds ──
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        formula = Text("a^2 + b^2 = c^2", font_size=72, color=HIGHLIGHT_COLOR)
        
        self.play(Write(formula), run_time=3)
        self.wait(12.5)


# ── Scene 4: Conclusion — target: 9.7 seconds ──
class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        formula = Text("a^2 + b^2 = c^2", font_size=48, color=HIGHLIGHT_COLOR).shift(UP*1)
        text = Text("Ready to solve?", font_size=48, color=TEXT_COLOR)
        
        self.add(formula)
        self.play(FadeIn(text), run_time=2)
        self.wait(7.7)