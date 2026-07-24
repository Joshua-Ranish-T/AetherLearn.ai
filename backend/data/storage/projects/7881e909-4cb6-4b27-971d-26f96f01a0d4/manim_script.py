from manim import *
import numpy as np
from typing import Optional


from manim import *

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
CIRCLE_COLOR = "#00d2ff"
TEXT_COLOR = WHITE

# ── Scene Classes ─────────────────────────────────

class Introduction(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        circle = Circle(color=CIRCLE_COLOR, fill_opacity=0.5).shift(ORIGIN)
        self.play(GrowFromCenter(circle), run_time=1.0)
        self.wait(2.0)
        self.play(FadeOut(circle))

class AddingSecondUnit(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        c1 = Circle(color=CIRCLE_COLOR, fill_opacity=0.5).shift(LEFT * 2)
        c2 = Circle(color=CIRCLE_COLOR, fill_opacity=0.5).shift(RIGHT * 2)
        
        self.play(FadeIn(c1))
        self.play(c1.animate.shift(LEFT * 1), run_time=1.0)
        self.play(GrowFromCenter(c2), run_time=1.0)
        self.wait(2.0)
        self.play(FadeOut(c1), FadeOut(c2))

class TheEquation(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        equation = Text("1 + 1 = 2", color=HIGHLIGHT_COLOR).scale(1.5).shift(DOWN * 2)
        self.play(Write(equation), run_time=2.0)
        self.wait(2.0)
        return equation

class Conclusion(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        equation = Text("1 + 1 = 2", color=HIGHLIGHT_COLOR).scale(1.5).shift(DOWN * 2)
        self.add(equation)
        self.play(Indicate(equation), run_time=2.0)
        self.wait(2.0)
        self.play(FadeOut(equation))

# ── Combined Scene ────────────────────────────────

class CombinedVideoScene(Scene):
    """Renders all scenes in sequence for the complete video."""
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Scene 1: Introduction
        circle = Circle(color=CIRCLE_COLOR, fill_opacity=0.5)
        self.play(GrowFromCenter(circle), run_time=1.0)
        self.wait(1.0)
        
        # Scene 2: Adding the second unit
        c1 = circle
        c2 = Circle(color=CIRCLE_COLOR, fill_opacity=0.5).shift(RIGHT * 2)
        self.play(c1.animate.shift(LEFT * 2), run_time=1.0)
        self.play(GrowFromCenter(c2), run_time=1.0)
        self.wait(1.0)
        
        # Scene 3: The Equation
        equation = Text("1 + 1 = 2", color=HIGHLIGHT_COLOR).scale(1.5).shift(DOWN * 2)
        self.play(Write(equation), run_time=2.0)
        self.wait(1.0)
        
        # Scene 4: Conclusion
        self.play(Indicate(equation), run_time=2.0)
        self.wait(1.0)
        self.play(FadeOut(c1), FadeOut(c2), FadeOut(equation))
        self.wait(1.0)