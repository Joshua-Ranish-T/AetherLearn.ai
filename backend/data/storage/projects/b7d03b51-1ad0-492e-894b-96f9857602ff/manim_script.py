from manim import *
import numpy as np
from typing import Optional


from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene 1: Introduction to Neurons — target: 22.66 seconds ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("The Artificial Neuron", color=TEXT_COLOR).scale(1.0).to_edge(UP)
        neuron = Circle(radius=1.0, color=HIGHLIGHT_COLOR, fill_opacity=0.2)
        
        self.play(Write(title), run_time=1.0)
        self.wait(0.5)
        self.play(GrowFromCenter(neuron), run_time=1.5)
        
        # Add input lines for visual context
        lines = VGroup(*[Line(LEFT*4, ORIGIN) for _ in range(3)]).arrange(DOWN, buff=0.5)
        self.play(Create(lines), run_time=2.0)
        
        self.wait(17.66)

# ── Scene 2: Weights and Biases — target: 23.06 seconds ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Using Text for formula as per instructions
        formula = Text("y = f(sum(w_i * x_i) + b)", color=HIGHLIGHT_COLOR).scale(1.5)
        
        self.play(FadeIn(formula), run_time=2.0)
        self.wait(21.06)

# ── Scene 3: Network Architecture — target: 22.32 seconds ──
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        header = Text("Input Layer | Hidden Layer | Output Layer", color=TEXT_COLOR).scale(0.8).to_edge(UP)
        
        # Create simple network visualization
        layers = VGroup()
        for i in range(3):
            layer = VGroup(*[Circle(radius=0.3, color=HIGHLIGHT_COLOR) for _ in range(3)]).arrange(DOWN, buff=0.5)
            layers.add(layer)
        layers.arrange(RIGHT, buff=2.0)
        
        self.play(FadeIn(header), run_time=1.0)
        self.play(Create(layers), run_time=2.0)
        self.wait(19.32)

# ── Scene 4: Learning Process — target: 22.99 seconds ──
class Scene4(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        opt_text = Text("Optimization", color=HIGHLIGHT_COLOR).scale(1.0).to_edge(DOWN)
        
        # Create a visual representation of connections
        dots = VGroup(*[Dot(point=np.array([x, y, 0])) for x in [-2, 2] for y in [-1, 0, 1]])
        lines = VGroup(*[Line(dots[i].get_center(), dots[j].get_center()) for i in range(3) for j in range(3, 6)])
        
        self.add(dots, lines)
        self.play(FadeIn(opt_text), run_time=1.0)
        
        # Pulse effect
        self.play(Indicate(opt_text), run_time=2.0)
        self.play(lines.animate.set_color(HIGHLIGHT_COLOR), run_time=2.0)
        
        self.wait(17.99)