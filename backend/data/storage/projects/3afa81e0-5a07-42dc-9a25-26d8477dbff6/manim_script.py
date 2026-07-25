from manim import *
import numpy as np
from typing import Optional


from manim import *

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene 1: Introduction ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        circle = Circle(radius=1.5, color=HIGHLIGHT_COLOR)
        radius_label = Text("r = 2", color=TEXT_COLOR, font_size=36).next_to(circle, RIGHT, buff=0.5)
        
        self.play(Create(circle), run_time=3.0)
        self.play(Write(radius_label), run_time=2.0)
        self.play(Indicate(circle), run_time=2.0)
        self.play(circle.animate.set_stroke(width=8), run_time=2.0)
        self.wait(3.02)

# ── Scene 2: The Formula ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        formula = Text("A = pi * r^2", color=HIGHLIGHT_COLOR, font_size=72)
        
        self.play(FadeIn(formula, scale=0.5), run_time=3.0)
        self.play(Circumscribe(formula, color=TEXT_COLOR, fade_out=True), run_time=4.0)
        self.play(formula.animate.shift(UP * 0.5), run_time=2.0)
        self.wait(5.62)

# ── Scene 3: Substitution ──
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        old_formula = Text("A = pi * r^2", color=HIGHLIGHT_COLOR, font_size=72)
        new_formula = Text("A = pi * (2)^2", color=TEXT_COLOR, font_size=72)
        
        self.add(old_formula)
        self.play(Transform(old_formula, new_formula), run_time=4.0)
        self.play(Indicate(new_formula[6:9]), run_time=3.0)
        self.play(new_formula.animate.set_color(HIGHLIGHT_COLOR), run_time=3.0)
        self.wait(4.02)

# ── Scene 4: Final Calculation ──
class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        step1 = Text("A = pi * (2)^2", color=HIGHLIGHT_COLOR, font_size=48)
        step2 = Text("A = 4 * pi", color=TEXT_COLOR, font_size=48)
        step3 = Text("A = 4 * pi = 12.57", color=HIGHLIGHT_COLOR, font_size=48)
        
        self.add(step1)
        self.play(Transform(step1, step2), run_time=3.0)
        self.play(Write(step3), run_time=4.0)
        self.play(step3.animate.scale(1.2).set_color(WHITE), run_time=3.0)
        self.play(Flash(step3, color=HIGHLIGHT_COLOR), run_time=3.0)
        self.wait(3.92)