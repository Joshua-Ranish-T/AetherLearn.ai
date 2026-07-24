from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
ACCENT_COLOR = "#0f3460"
TEXT_COLOR = WHITE

class PythagoreanTheoremVideo(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        self.scene_01_intro()
        self.clear()
        self.scene_02_visualizing()
        self.clear()
        self.scene_03_formula()
        self.clear()
        self.scene_04_conclusion()

    def scene_01_intro(self):
        title = Text("Right-Angled Triangle", color=TEXT_COLOR).to_edge(UP)
        
        # Triangle vertices
        A = np.array([-2, -1, 0])
        B = np.array([2, -1, 0])
        C = np.array([-2, 2, 0])
        
        triangle = Polygon(A, B, C, color=TEXT_COLOR)
        right_angle = Square(side_length=0.4, color=TEXT_COLOR).shift(np.array([-1.6, -0.6, 0]))
        
        label_a = Text("a", color=TEXT_COLOR).next_to(C, LEFT)
        label_b = Text("b", color=TEXT_COLOR).next_to(B, DOWN)
        label_c = Text("c", color=TEXT_COLOR).next_to(np.array([0, 0.5, 0]), UR)
        
        self.play(Write(title))
        self.play(Create(triangle), Create(right_angle))
        self.play(Write(label_a), Write(label_b), Write(label_c))
        self.wait(2)

    def scene_02_visualizing(self):
        # Triangle base
        tri = Polygon([-2, -1, 0], [2, -1, 0], [-2, 2, 0], color=TEXT_COLOR)
        
        sq_a = Square(side_length=3, color=BLUE).shift(LEFT * 3.5 + UP * 0.5)
        sq_b = Square(side_length=4, color=GREEN).shift(DOWN * 3)
        sq_c = Square(side_length=5, color=RED).rotate(np.arctan(3/4)).shift(RIGHT * 1.5 + UP * 0.5)
        
        label_a2 = Text("a^2", color=BLUE).move_to(sq_a.get_center())
        label_b2 = Text("b^2", color=GREEN).move_to(sq_b.get_center())
        label_c2 = Text("c^2", color=RED).move_to(sq_c.get_center())
        
        self.play(GrowFromCenter(sq_a), GrowFromCenter(sq_b), GrowFromCenter(sq_c))
        self.play(Write(label_a2), Write(label_b2), Write(label_c2))
        self.wait(2)
        self.play(sq_a.animate.move_to(sq_c.get_center()), sq_b.animate.move_to(sq_c.get_center()))
        self.wait(2)

    def scene_03_formula(self):
        equation = Text("a^2 + b^2 = c^2", color=HIGHLIGHT_COLOR).scale(2.0)
        self.play(Write(equation))
        self.wait(3)

    def scene_04_conclusion(self):
        eq1 = Text("3^2 + 4^2 = 5^2", color=TEXT_COLOR).shift(UP)
        eq2 = Text("9 + 16 = 25", color=HIGHLIGHT_COLOR).shift(DOWN)
        
        self.play(FadeIn(eq1))
        self.wait(1)
        self.play(FadeIn(eq2))
        self.wait(3)