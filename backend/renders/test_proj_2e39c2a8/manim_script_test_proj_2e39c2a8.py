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


# ── Scene 1: Introduction to One ────────────────────────
class Scene01IntroductionToOne(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create objects
        title = Text("The Magic of One Plus One", color=HIGHLIGHT_COLOR, scale=1.2).shift(UP + LEFT * 3)
        subtitle = Text("Understanding Basic Addition", color=TEXT_COLOR, scale=0.8).shift(UP + RIGHT * 3)
        
        red_circle = Circle(color=HIGHLIGHT_COLOR, fill_opacity=1).scale(1.0).shift(LEFT * 2)
        num_one_circle = Text("1", color=TEXT_COLOR).scale(1.5).next_to(red_circle, DOWN, buff=0.5)
        
        # Animate
        self.play(Write(title), run_time=1.5)
        self.play(Write(subtitle), run_time=1.0)
        self.wait(0.5)
        
        self.play(Create(red_circle), run_