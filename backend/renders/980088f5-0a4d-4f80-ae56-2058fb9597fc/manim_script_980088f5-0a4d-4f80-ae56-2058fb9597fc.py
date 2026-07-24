from manim import *

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
TEXT_COLOR = WHITE

# ── Scene Classes ─────────────────────────────────

class Scene01Introduction(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        title = Text("The Pythagorean Theorem", color=TEXT_COLOR).to_edge(UP)
        
        # Right Triangle
        triangle = Polygon(ORIGIN, 3*RIGHT, 3*RIGHT + 2*UP, color=HIGHLIGHT_COLOR)
        square_symbol = Square(side_length=0.3, color=TEXT_COLOR).shift(3*RIGHT + 0.3*UP).rotate(PI/2)
        
        self.play(Write(title))
        self.play(DrawBorderThenFill(triangle))
        self.play(Create(square_symbol))
        self.wait(2)

class Scene02DefiningFormula(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Triangle setup
        triangle = Polygon(ORIGIN, 4*RIGHT, 4*RIGHT + 3*UP, color=HIGHLIGHT_COLOR)
        a_label = Text("a", color=TEXT_COLOR).next_to(triangle.get_center(), UP)
        b_label = Text("b", color=TEXT_COLOR).next_to(triangle.get_center(), RIGHT)
        c_label = Text("c", color=TEXT_COLOR).next_to(triangle.get_center(), DR)
        
        equation = Text("a^2 + b^2 = c^2", color=HIGHLIGHT_COLOR).scale(1.5).to_edge(DOWN)
        
        self.add(triangle)
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.play(FadeIn(equation))
        self.wait(2)

class Scene03VisualizingSquares(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Squares
        sq_a = Square(color=BLUE, fill_opacity=0.5).scale(0.5).shift(LEFT*2)
        sq_b = Square(color=GREEN, fill_opacity=0.5).scale(0.5).shift(DOWN*2)
        sq_c = Square(color=PURPLE, fill_opacity=0.5).scale(0.5).shift(RIGHT*2 + UP*1)
        
        squares = VGroup(sq_a, sq_b, sq_c)
        
        self.play(GrowFromCenter(squares))
        self.wait(2)

class Scene04Conclusion(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        equation = Text("a^2 + b^2 = c^2", color=TEXT_COLOR).scale(2.0)
        
        self.play(FadeIn(equation))
        self.play(Indicate(equation))
        self.wait(2)

# ── Combined Scene ────────────────────────────────
class CombinedVideoScene(Scene):
    """Renders all scenes in sequence for the complete video."""
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Scene 1
        s1 = Scene01Introduction()
        s1.construct()
        self.clear()
        
        # Scene 2
        s2 = Scene02DefiningFormula()
        s2.construct()
        self.clear()
        
        # Scene 3
        s3 = Scene03VisualizingSquares()
        s3.construct()
        self.clear()
        
        # Scene 4
        s4 = Scene04Conclusion()
        s4.construct()
        self.wait(2)