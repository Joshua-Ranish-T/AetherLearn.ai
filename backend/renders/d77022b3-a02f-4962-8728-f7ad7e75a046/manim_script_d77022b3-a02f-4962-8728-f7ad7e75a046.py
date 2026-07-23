from manim import *
import numpy as np
from typing import Optional


from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = ManimColor("#1a1a2e")
HIGHLIGHT_COLOR = ManimColor("#e94560")
ACCENT_COLOR = ManimColor("#0f3460")
TEXT_COLOR = WHITE


# ── Scene 1: Introduction to Addition ────────────────────────
class Scene01IntroductionToAddition(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create objects
        title = Text("Understanding 1 + 1 = 2", color=HIGHLIGHT_COLOR, font_size=1.5 * DEFAULT_FONT_SIZE).to_edge(UP)
        subtitle = Text("The Foundation of Addition", color=TEXT_COLOR, font_size=0.9 * DEFAULT_FONT_SIZE)
        subtitle.next_to(title, DOWN, buff=0.5) # Position slightly below title
        
        plus_symbol = Text("+", color=ACCENT_COLOR, font_size=3.0 * DEFAULT_FONT_SIZE).move_to(ORIGIN)
        
        # Animate
        self.play(Write(title), run_time=2.0)
        self.wait(0.5)
        self.play(FadeIn(subtitle, shift=DOWN * 0.5), run_time=1.5)