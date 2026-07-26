from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "#1a1a2e"
HIGHLIGHT_COLOR = "#e94560"
ACCENT_COLOR = "#0f3460"
TEXT_COLOR = WHITE

class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("Visualizing Differential Equations", color=TEXT_COLOR, font_size=48).to_edge(UP)
        equation = Text("dy/dx = x - y", color=HIGHLIGHT_COLOR, font_size=72)
        
        self.play(Write(title), run_time=2.0)
        self.play(FadeIn(equation, shift=UP), run_time=1.5)
        self.play(Indicate(equation), run_time=2.0)
        self.wait(15.6)
        self.play(FadeOut(VGroup(title, equation)), run_time=1.5)

class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        axes = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1], x_length=8, y_length=6, axis_config={"include_tip": True})
        axes.set_color(TEXT_COLOR)
        
        self.play(Create(axes), run_time=2.0)
        
        # Create Slope Field
        field = VGroup()
        for x in np.arange(-3.5, 4, 0.8):
            for y in np.arange(-2.5, 3, 0.8):
                slope = x - y
                angle = np.arctan(slope)
                line = Line(start=LEFT*0.2, end=RIGHT*0.2, color=ACCENT_COLOR)
                line.rotate(angle)
                line.move_to(axes.c2p(x, y))
                field.add(line)
        
        self.play(GrowFromCenter(field), run_time=3.0)
        self.wait(19.02)
        self.play(FadeOut(VGroup(axes, field)), run_time=1.5)

class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        axes = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1], x_length=8, y_length=6)
        axes.set_color(TEXT_COLOR)
        
        # Recreate field for context
        field = VGroup()
        for x in np.arange(-3.5, 4, 0.8):
            for y in np.arange(-2.5, 3, 0.8):
                line = Line(start=LEFT*0.2, end=RIGHT*0.2, color=ACCENT_COLOR).rotate(np.arctan(x-y)).move_to(axes.c2p(x, y))
                field.add(line)
        
        # Solution curve
        curve = axes.plot(lambda x: x - 1 + 2*np.exp(-x), color=HIGHLIGHT_COLOR, x_range=[-2, 3])
        
        self.add(axes, field)
        self.play(Create(curve), run_time=4.0)
        
        label = Text("y(x)", color=HIGHLIGHT_COLOR, font_size=36).next_to(curve.get_end(), RIGHT)
        self.play(Write(label), run_time=1.5)
        self.wait(16.08)
        self.play(FadeOut(VGroup(axes, field, curve, label)), run_time=1.5)

class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        title = Text("The Landscape of Solutions", color=TEXT_COLOR, font_size=40).to_edge(UP)
        self.play(Write(title), run_time=1.5)
        
        axes = Axes(x_range=[-4, 4, 1], y_range=[-3, 3, 1], x_length=8, y_length=6)
        axes.set_color(TEXT_COLOR)
        
        curves = VGroup()
        for c in [-2, -1, 0, 1, 2]:
            curves.add(axes.plot(lambda x, c=c: x - 1 + c*np.exp(-x), color=HIGHLIGHT_COLOR, x_range=[-2, 3]))
            
        self.play(FadeIn(axes), LaggedStart(*[Create(c) for c in curves], lag_ratio=0.5), run_time=4.0)
        self.play(Circumscribe(curves), run_time=2.0)
        self.wait(13.72)