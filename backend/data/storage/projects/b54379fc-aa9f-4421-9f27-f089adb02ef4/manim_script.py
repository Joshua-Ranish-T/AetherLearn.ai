from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene 1: Introduction to RAG ──────────────────
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("Retrieval-Augmented Generation (RAG)", color=HIGHLIGHT_COLOR, font_size=48)
        
        self.play(FadeIn(title.scale(0.5)), run_time=2.0)
        self.play(Indicate(title), run_time=2.0)
        
        # Simulate AI Agent icon
        agent = Circle(radius=0.5, color=TEXT_COLOR).shift(DOWN * 2)
        self.play(Create(agent), run_time=2.0)
        self.play(agent.animate.set_fill(HIGHLIGHT_COLOR, opacity=0.5), run_time=2.0)
        
        self.play(FadeOut(VGroup(title, agent)), run_time=2.0)
        self.wait(7.98)

# ── Scene 2: The Open Book Analogy ────────────────
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        memory = Text("Memory (LLM)", color=TEXT_COLOR, font_size=40).shift(LEFT * 3)
        kb = Text("Knowledge Base (RAG)", color=TEXT_COLOR, font_size=40).shift(RIGHT * 3)
        
        self.play(Create(memory), run_time=2.0)
        self.play(Create(kb), run_time=2.0)
        
        box1 = SurroundingRectangle(memory, color=HIGHLIGHT_COLOR)
        box2 = SurroundingRectangle(kb, color=HIGHLIGHT_COLOR)
        
        self.play(Create(box1), run_time=2.0)
        self.play(Create(box2), run_time=2.0)
        
        self.play(memory.animate.shift(UP * 2), kb.animate.shift(UP * 2), run_time=2.0)
        self.wait(10.95)

# ── Scene 3: Vector Embeddings ────────────────────
class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        vec_text = Text("v = [x1, x2, ..., xn]", color=HIGHLIGHT_COLOR, font_size=60)
        
        self.play(Write(vec_text), run_time=3.0)
        
        # Visualizing transformation
        dots = VGroup(*[Dot(point=np.array([np.random.uniform(-3, 3), np.random.uniform(-2, 2), 0])) for _ in range(20)])
        self.play(FadeIn(dots), run_time=3.0)
        self.play(dots.animate.arrange_in_grid(rows=4, cols=5), run_time=4.0)
        
        self.play(Circumscribe(vec_text), run_time=2.0)
        self.wait(10.01)

# ── Scene 4: Synthesis ────────────────────────────
class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        equation = Text("LLM + Context = Accurate Response", color=TEXT_COLOR, font_size=40)
        
        self.play(FadeIn(equation, shift=UP), run_time=3.0)
        
        # Highlight components
        llm_part = equation[0:3]
        ctx_part = equation[6:13]
        
        self.play(llm_part.animate.set_color(HIGHLIGHT_COLOR), run_time=2.0)
        self.play(ctx_part.animate.set_color(HIGHLIGHT_COLOR), run_time=2.0)
        
        # Pulse effect
        self.play(equation.animate.scale(1.2), run_time=2.0)
        self.play(equation.animate.scale(1/1.2), run_time=2.0)
        
        self.wait(11.99)