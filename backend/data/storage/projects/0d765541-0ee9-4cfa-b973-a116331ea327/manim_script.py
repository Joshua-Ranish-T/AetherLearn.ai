from manim import *
import numpy as np
from typing import Optional


from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
ACCENT_COLOR = "#0f3460"
TEXT_COLOR = WHITE

# ── Scene 1: Introduction to Trapezium — target: 24.26 seconds ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create trapezium
        trapezium = Polygon([-2, -1, 0], [2, -1, 0], [1, 1, 0], [-1, 1, 0], 
                            color=ACCENT_COLOR, fill_opacity=0.8, stroke_width=4)
        
        label_a = Text("a", font_size=36).next_to(trapezium.get_top(), UP)
        label_b = Text("b", font_size=36).next_to(trapezium.get_bottom(), DOWN)
        height_line = DashedLine(trapezium.get_top(), [1, -1, 0], color=HIGHLIGHT_COLOR)
        label_h = Text("h", font_size=36, color=HIGHLIGHT_COLOR).next_to(height_line, RIGHT)
        
        self.play(Create(trapezium), run_time=3)
        self.play(Write(label_a), Write(label_b), run_time=3)
        self.play(Create(height_line), Write(label_h), run_time=3)
        
        group = VGroup(trapezium, label_a, label_b, height_line, label_h)
        self.play(group.animate.scale(1.2), run_time=2)
        self.play(Indicate(trapezium), run_time=2)
        self.wait(11.26)

# ── Scene 2: The Doubling Transformation — target: 21.41 seconds ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        trapezium = Polygon([-2, -1, 0], [2, -1, 0], [1, 1, 0], [-1, 1, 0], 
                            color=ACCENT_COLOR, fill_opacity=0.8)
        trapezium_copy = trapezium.copy().set_color(HIGHLIGHT_COLOR)
        
        self.add(trapezium)
        self.play(FadeIn(trapezium_copy), run_time=2)
        self.play(Rotate(trapezium_copy, angle=PI), run_time=3)
        self.play(trapezium_copy.animate.next_to(trapezium, RIGHT, buff=0), run_time=3)
        
        parallelogram = VGroup(trapezium, trapezium_copy)
        self.play(parallelogram.animate.center(), run_time=2)
        self.play(Circumscribe(parallelogram), run_time=3)
        self.wait(8.41)

# ── Scene 3: Calculating Area — target: 23.21 seconds ──
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        eq = Text("A = (a + b) * h", font_size=60)
        self.play(Write(eq), run_time=4)
        
        box = SurroundingRectangle(eq, color=HIGHLIGHT_COLOR)
        self.play(Create(box), run_time=2)
        
        self.play(eq.animate.shift(UP * 2), box.animate.shift(UP * 2), run_time=2)
        
        explanation = Text("Base = a + b", font_size=40).next_to(eq, DOWN, buff=1)
        self.play(FadeIn(explanation), run_time=3)
        
        self.play(Indicate(eq), run_time=2)
        self.wait(10.21)

# ── Scene 4: Final Formula Reveal — target: 21.12 seconds ──
class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        old_eq = Text("A = (a + b) * h", font_size=60)
        new_eq = Text("A = (a + b) / 2 * h", font_size=72, color=HIGHLIGHT_COLOR)
        
        self.add(old_eq)
        self.play(Transform(old_eq, new_eq), run_time=4)
        
        self.play(Flash(new_eq), run_time=2)
        self.play(new_eq.animate.scale(1.2), run_time=2)
        
        final_text = Text("Area of a Trapezium", font_size=40).next_to(new_eq, UP, buff=1)
        self.play(Write(final_text), run_time=3)
        
        self.play(Circumscribe(new_eq), run_time=3)
        self.wait(7.12)