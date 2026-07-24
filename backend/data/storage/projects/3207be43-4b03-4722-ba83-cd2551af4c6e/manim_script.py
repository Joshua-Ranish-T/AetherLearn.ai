from manim import *
import numpy as np
from typing import Optional


from manim import *

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene Classes ─────────────────────────────────

class Scene01FirstObject(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        circle = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).shift(LEFT * 2)
        label = Text("1", font_size=72).next_to(circle, UP)
        
        self.play(GrowFromCenter(circle), Write(label), run_time=1.0)
        self.wait(2)

class Scene02AdditionOperator(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        c1 = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).shift(LEFT * 3)
        plus = Text("+", font_size=96, color=TEXT_COLOR)
        c2 = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).shift(RIGHT * 3)
        
        self.add(c1)
        self.play(Write(plus))
        self.play(FadeIn(c2))
        self.wait(2)

class Scene03Equality(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        c1 = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).shift(LEFT * 3)
        plus = Text("+", font_size=96, color=TEXT_COLOR)
        c2 = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).shift(RIGHT * 3)
        equals = Text("=", font_size=96, color=TEXT_COLOR)
        
        self.add(c1, plus, c2)
        self.play(FadeIn(equals))
        self.wait(2)

class Scene04Result(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        expr = Text("1 + 1 = 2", font_size=72, color=TEXT_COLOR)
        
        self.play(Create(expr), run_time=1.5)
        self.wait(3)

# ── Combined Scene ────────────────────────────────

class CombinedVideoScene(Scene):
    """Renders all scenes in sequence for the complete video."""
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Scene 1
        c1 = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).shift(LEFT * 2)
        l1 = Text("1", font_size=72).next_to(c1, UP)
        self.play(GrowFromCenter(c1), Write(l1), run_time=1.0)
        self.wait(1)
        
        # Scene 2
        plus = Text("+", font_size=96, color=TEXT_COLOR)
        c2 = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).shift(RIGHT * 2)
        self.play(Write(plus))
        self.play(FadeIn(c2))
        self.wait(1)
        
        # Scene 3
        equals = Text("=", font_size=96, color=TEXT_COLOR)
        self.play(FadeIn(equals))
        self.wait(1)
        
        # Scene 4
        result = Text("2", font_size=144, color=HIGHLIGHT_COLOR).next_to(equals, RIGHT)
        self.play(Create(result), run_time=1.5)
        self.wait(2)
        
        # Final expression
        final_group = VGroup(l1, c1, plus, c2, equals, result)
        self.play(FadeOut(final_group))
        final_text = Text("1 + 1 = 2", font_size=96)
        self.play(Write(final_text))
        self.wait(3)