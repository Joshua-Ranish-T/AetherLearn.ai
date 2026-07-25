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
        
        # Equilateral Triangle
        triangle = Polygon(
            LEFT * np.sqrt(3) + DOWN,
            RIGHT * np.sqrt(3) + DOWN,
            UP * 2,
            color=TEXT_COLOR
        )
        label = Text("Side = 2", font_size=36).next_to(triangle, UP)
        
        self.play(DrawBorderThenFill(triangle), run_time=2.0)
        self.play(Write(label), run_time=1.0)
        
        # Add internal angle labels
        angle_text = Text("60 degrees", font_size=24).move_to(triangle.get_top() + DOWN * 0.5)
        self.play(FadeIn(angle_text), run_time=1.5)
        self.wait(12.18)
        self.play(FadeOut(VGroup(triangle, label, angle_text)), run_time=1.5)

class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Reconstruct triangle
        triangle = Polygon(
            LEFT * np.sqrt(3) + DOWN,
            RIGHT * np.sqrt(3) + DOWN,
            UP * 2,
            color=TEXT_COLOR
        )
        bisector = Line(UP * 2, DOWN, color=HIGHLIGHT_COLOR)
        angle_label = Text("30 degrees", color=HIGHLIGHT_COLOR, font_size=32).move_to(UP * 1.5)
        
        self.add(triangle)
        self.play(Create(bisector), run_time=2.0)
        self.play(FadeIn(angle_label), run_time=1.0)
        
        # Highlight the right angle
        right_angle = Square(side_length=0.2, color=HIGHLIGHT_COLOR).shift(DOWN + RIGHT * 0.1)
        self.play(Create(right_angle), run_time=1.0)
        
        self.wait(14.1)
        self.play(FadeOut(VGroup(triangle, bisector, angle_label, right_angle)), run_time=1.5)

class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Right triangle representation
        tri = Polygon(ORIGIN, RIGHT * np.sqrt(3), UP * 2, color=TEXT_COLOR)
        opp_label = Text("Opposite = 1", font_size=32).next_to(RIGHT * (np.sqrt(3)/2) + UP, RIGHT)
        hyp_label = Text("Hypotenuse = 2", font_size=32).rotate(np.arctan(2/np.sqrt(3))).next_to(UP * 1 + RIGHT * (np.sqrt(3)/2), UP)
        
        self.play(Create(tri), run_time=1.5)
        self.play(Write(opp_label), run_time=1.5)
        self.play(Write(hyp_label), run_time=1.5)
        
        self.wait(11.29)
        self.play(FadeOut(VGroup(tri, opp_label, hyp_label)), run_time=1.5)

class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        eq = Text("sin(30 degrees) = 1 / 2 = 0.5", color=HIGHLIGHT_COLOR, font_size=48)
        
        self.play(Write(eq), run_time=2.0)
        self.play(Indicate(eq), run_time=1.0)
        
        # Add a visual ratio bar
        bar = VGroup(
            Rectangle(height=0.5, width=1, fill_opacity=1, color=TEXT_COLOR),
            Rectangle(height=1, width=1, fill_opacity=1, color=HIGHLIGHT_COLOR)
        ).arrange(DOWN).shift(DOWN * 2)
        
        self.play(GrowFromCenter(bar), run_time=2.0)
        self.wait(12.42)
        self.play(FadeOut(eq, bar), run_time=1.5)