from manim import *
import numpy as np
from typing import Optional


from manim import *

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene 1: Introduction ────────────────────────
class Scene01Introduction(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("The Pythagorean Theorem", color=TEXT_COLOR).scale(1.0).to_edge(UP)
        
        # Right Triangle
        triangle = Polygon(ORIGIN, 3*RIGHT, 3*RIGHT + 2*UP, color=HIGHLIGHT_COLOR)
        right_angle = RightAngle(Line(ORIGIN, 3*RIGHT), Line(3*RIGHT, 3*RIGHT + 2*UP), length=0.3, color=TEXT_COLOR)
        
        label_a = Text("a").next_to(1.5*RIGHT, DOWN)
        label_b = Text("b").next_to(3*RIGHT + UP, RIGHT)
        label_c = Text("c").next_to(1.5*RIGHT + UP, UP, buff=0.1)
        
        labels = VGroup(label_a, label_b, label_c)
        
        self.play(Write(title))
        self.play(Create(triangle), Create(right_angle))
        self.play(FadeIn(labels))
        self.wait(2)

# ── Scene 2: The Formula ────────────────────────
class Scene02Formula(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        equation = Text("a^2 + b^2 = c^2", color=HIGHLIGHT_COLOR).scale(2.0)
        
        self.play(GrowFromCenter(equation))
        self.wait(2)

# ── Scene 3: Concrete Example ──────────────────
class Scene03Example(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        eq1 = Text("3^2 + 4^2 = c^2", color=TEXT_COLOR).to_edge(UP)
        eq2 = Text("9 + 16 = 25", color=TEXT_COLOR)
        eq3 = Text("c = 5", color=HIGHLIGHT_COLOR).scale(1.5).to_edge(DOWN)
        
        self.play(Write(eq1))
        self.wait(1)
        self.play(Write(eq2))
        self.wait(1)
        self.play(Write(eq3))
        self.wait(2)

# ── Scene 4: Conclusion ────────────────────────
class Scene04Conclusion(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        text = Text("Happy Calculating!", color=TEXT_COLOR).scale(1.2)
        
        self.play(FadeIn(text))
        self.wait(3)

# ── Combined Scene ──────────────────────────────
class CombinedVideoScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Scene 1
        s1 = Scene01Introduction()
        s1.construct()
        self.clear()
        
        # Scene 2
        s2 = Scene02Formula()
        s2.construct()
        self.clear()
        
        # Scene 3
        s3 = Scene03Example()
        s3.construct()
        self.clear()
        
        # Scene 4
        s4 = Scene04Conclusion()
        s4.construct()
        self.clear()