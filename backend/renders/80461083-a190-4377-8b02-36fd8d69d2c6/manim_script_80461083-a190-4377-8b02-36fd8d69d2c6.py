from manim import *
import numpy as np
from typing import Optional


from manim import *
import numpy as np
from typing import Optional


class UnlockingtheSecretsoScene(Scene):
    def construct(self):
        self.camera.background_color = "#1a1a2e"
        title = Text("Unlocking the Secrets of Right Triangles: The Pythagorean Theorem", font_size=48, color=WHITE)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
