from manim import *
import numpy as np
from typing import Optional

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE
ACCENT_COLOR = "#00ffcc"

# ── Scene 1: Introduction ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        equation = Text("2x + 3 = 0", font_size=72, color=TEXT_COLOR)
        
        self.play(Write(equation), run_time=3.0)
        self.play(Indicate(equation, color=HIGHLIGHT_COLOR), run_time=2.0)
        self.play(equation.animate.scale(1.2).set_color(HIGHLIGHT_COLOR), run_time=2.0)
        self.wait(13.3)

# ── Scene 2: Subtracting Constants ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        eq_start = Text("2x + 3 = 0", font_size=60, color=TEXT_COLOR)
        eq_step = Text("2x + 3 - 3 = 0 - 3", font_size=60, color=HIGHLIGHT_COLOR)
        eq_final = Text("2x = -3", font_size=60, color=TEXT_COLOR)
        
        self.add(eq_start)
        self.play(ReplacementTransform(eq_start, eq_step), run_time=4.0)
        self.play(Circumscribe(eq_step), run_time=3.0)
        self.play(ReplacementTransform(eq_step, eq_final), run_time=4.0)
        self.play(eq_final.animate.shift(UP * 0.5), run_time=2.0)
        self.wait(5.89)

# ── Scene 3: Isolating the Variable ──
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Representing 2x/2 = -3/2
        eq = Text("2x / 2 = -3 / 2", font_size=60, color=HIGHLIGHT_COLOR)
        
        self.play(GrowFromCenter(eq), run_time=4.0)
        self.play(eq.animate.set_color(TEXT_COLOR), run_time=2.0)
        self.play(Indicate(eq), run_time=3.0)
        self.play(eq.animate.scale(1.2), run_time=2.0)
        self.wait(6.45)

# ── Scene 4: Final Result ──
class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        result = Text("x = -1.5", font_size=96, color=ACCENT_COLOR)
        box = SurroundingRectangle(result, color=HIGHLIGHT_COLOR, buff=0.3)
        
        self.play(Write(result), run_time=3.0)
        self.play(Create(box), run_time=2.0)
        self.play(Indicate(result), run_time=3.0)
        self.play(result.animate.scale(1.1), run_time=2.0)
        self.play(FadeOut(box), run_time=1.0)
        self.wait(3.42)