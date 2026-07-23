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


# ── Scene 1: Introduction: The Iconic 'Hello, World!' ────────────────────────
class Scene01IntroductionTheIconicHelloWorld(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create objects
        title = Text(
            "Hello, World! Your First Step into Programming",
            color=TEXT_COLOR,
            font_size=48
        ).to_edge(UP)
        
        hello_world_text = Text(
            "Hello, World!",
            color=HIGHLIGHT_COLOR,
            font_size=96, # Adjusted scale to font_size
            weight=BOLD
        ).move_to(ORIGIN)
        
        # Create a rectangle behind the "Hello, World!" text
        # Adjust width and height based on the text's dimensions
        text_width = hello_world_text.width
        text_height = hello_world_text.height
        
        # Add some padding
        padding_width = 1.5
        padding_height = 1.0
        
        hello_world_rect = Rectangle(
            width=text_width + padding_width,
            height=text_height + padding_height,
            color=ACCENT_COLOR,
            fill_opacity=0.8,
            stroke_width=0
        ).move_to(hello_world_text)
        
        # Group the rectangle and text for easier positioning if needed,
        # but here they are centered independently.
        
        # Animate
        self.play(FadeIn(title, run_time=2.0))
        self.wait(0.5)
        
        self.play(FadeIn(hello_world_rect, run_time=1.5))
        self.wait(0.5)
        
        self.play(GrowFromCenter(hello_world_text, run_time=2.5))
        self.wait(2.0) # Longer wait for voiceover

        # Transition (handled by CombinedVideoScene)
        # self.play(FadeOut(VGroup(title, hello_world_rect, hello_world_text)))


# ── Scene 2: Why 'Hello, World!'? Testing Your Setup ────────────────────────
class Scene02WhyHelloWorldTestingYourSetup(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create objects
        # Icons as abstract shapes or text
        laptop_icon = VGroup(
            Rectangle(width=2, height=1.5, color=TEXT_COLOR, fill_opacity=0.2),
            Rectangle(width=1.5, height=0.9, color=TEXT_COLOR, fill_opacity=0.5).shift(UP * 0.1)
        ).scale(0.8).shift(LEFT * 5)
        
        laptop_text = Text("Your Setup", font_size=28, color=TEXT_COLOR).next_to(laptop_icon, DOWN, buff=0.2)
        
        code_editor_icon = VGroup(
            Rectangle(width=2, height=1.5, color=ACCENT_COLOR, fill_opacity=0.8),
            Line(laptop_icon.get_right(), laptop_icon.get_right() + RIGHT * 0.5, color=GRAY),
            Line(laptop_icon.get_right(), laptop_icon.get_right() + RIGHT * 0.5, color=GRAY).shift(UP * 0.3),
            Line(laptop_icon.get_right(), laptop_icon.get_right() + RIGHT * 0.5, color=GRAY).shift(DOWN * 0.3)
        ).scale(0.8).shift(LEFT * 2)
        
        code_editor_text = Text("Code Editor", font_size=28, color=TEXT_COLOR).next_to(code_editor_icon, DOWN, buff=0.2)
        
        gear_icon = VGroup(
            Circle(radius=0.7, color=HIGHLIGHT_COLOR, fill_opacity=0.8),
            *[Rectangle(width=0.2, height=0.4, color=HIGHLIGHT_COLOR, fill_opacity=0.8).rotate(i * 360/8 * DEGREES) for i in range(8)]
        ).scale(0.8).move_to(ORIGIN)
        
        gear_text = Text("Compiler/Interpreter", font_size=28, color=TEXT_COLOR).next_to(gear_icon, DOWN, buff=0.2)
        
        monitor_icon = VGroup(
            Rectangle(width=2, height=1.5, color=TEXT_COLOR, fill_opacity=0.2),
            Rectangle(width=1.8, height=1.1, color=ACCENT_COLOR, fill_opacity=0.8).shift(UP * 0.1)
        ).scale(0.8).shift(RIGHT * 5)
        
        monitor_text = Text("Screen Output", font_size=28, color=TEXT_COLOR).next_to(monitor_icon, DOWN, buff=0.2)
        
        hello_world_output = Text("Hello, World!", font_size=36, color=HIGHLIGHT_COLOR).move_to(monitor_icon)
        
        # Arrows
        arrow1 = Arrow(laptop_icon.get_right(), code_editor_icon.get_left(), buff=0.1, color=GRAY, max_stroke_width_to_length_ratio=0.05, max_tip_length_to_length_ratio=0.2)
        arrow2 = Arrow(code_editor_icon.get_right(), gear_icon.get_left(), buff=0.1, color=GRAY, max_stroke_width_to_length_ratio=0.05, max_tip_length_to_length_ratio=0.2)
        arrow3 = Arrow(gear_icon.get_right(), monitor_icon.get_left(), buff=0.1, color=GRAY, max_stroke_width_to_length_ratio=0.05, max_tip_length_to_length_ratio=0.2)
        
        # Question texts
        question1 = Text("Is everything installed?", font_size=24, color=YELLOW).next_to(laptop_icon, UP + LEFT, buff=0.5)
        question2 = Text("Can it communicate?", font_size=24, color=YELLOW).next_to(monitor_icon, UP + RIGHT, buff=0.5)
        
        # Animate
        self.play(Create(laptop_icon), Write(laptop_text), run_time=1.0)
        self.wait(0.2)
        self.play(ShowCreation(arrow1), run_time=0.5)
        self.wait(0.2)
        self.play(Create(code_editor_icon), Write(code_editor_text), run_time=1.0)
        self.wait(0.2)
        self.play(ShowCreation(arrow2), run_time=0.5)
        self.wait(0.2)
        self.play(Create(gear_icon), Write(gear_text), run_time=1.0)
        self.wait(0.2)
        self.play(ShowCreation(arrow3), run_time=0.5)
        self.wait(0.2)
        self.play(Create(monitor_icon), Write(monitor_text), run_time=1.0)
        self.wait(0.5)
        
        self.play(FadeIn(hello_world_output, run_time=1.0))
        self.wait(0.5)
        
        self.play(FadeIn(question1, run_time=1.0))
        self.wait(0.5)
        self.play(FadeIn(question2, run_time=1.0))
        self.wait(2.0) # Longer wait for voiceover

        # Transition (handled by CombinedVideoScene)
        # self.play(FadeOut(VGroup(laptop_icon, laptop_text, code_editor_icon, code_editor_text,
        #                          gear_icon, gear_text, monitor_icon, monitor_text,
        #                          hello_world_output, arrow1, arrow2, arrow3,
        #                          question1, question2)))


# ── Scene 3: How it Works: The Concept of Output ────────────────────────
class Scene03HowItWorksTheConceptOfOutput(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create objects
        code_panel = Rectangle(width=6, height=7, color=ACCENT_COLOR, fill_opacity=0.8).to_edge(LEFT, buff=0.5)
        output_panel = Rectangle(width=6, height=7, color=ACCENT_COLOR, fill_opacity=0.8).to_edge(RIGHT, buff=0.5)
        
        code_label = Text("CODE", font_size=36, color=TEXT_COLOR).next_to(code_panel, UP, buff=0.3)
        output_label = Text("OUTPUT", font_size=36, color=TEXT_COLOR).next_to(output_panel, UP, buff=0.3)
        
        # Python example
        python_code_str = "print(\"Hello, World!\")"
        python_code = Code(
            code=python_code_str,
            language="python",
            font_size=30,
            background="rgba(0,0,0,0)", # Transparent background
            insert_line_no=False
        ).move_to(code_panel.get_center() + UP * 1.5)
        
        python_output_text = Text(
            "Hello, World!",
            font_size=48,
            color=HIGHLIGHT_COLOR
        ).move_to(output_panel.get_center() + UP * 1.5)
        
        # C++ example
        cpp_code_str = """#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}"""
        cpp_code = Code(
            code=cpp_code_str,
            language="cpp",
            font_size=24,
            background="rgba(0,0,0,0)",
            insert_line_no=False
        ).move_to(code_panel.get_center() + DOWN * 1.5)
        
        cpp_output_text = Text(
            "Hello, World!",
            font_size=40,
            color=HIGHLIGHT_COLOR
        ).move_to(output_panel.get_center() + DOWN * 1.5)
        
        # Animate
        self.play(Create(code_panel), Create(output_panel), run_time=1.0)
        self.wait(0.5)
        self.play(Write(code_label), Write(output_label), run_time=0.5)
        self.wait(0.5)
        
        self.play(AddTextLetterByLetter(python_code, run_time=2.0))
        self.wait(0.5)
        self.play(FadeIn(python_output_text, run_time=1.0))
        self.wait(1.0)
        
        self.play(AddTextLetterByLetter(cpp_code, run_time=4.0))
        self.wait(0.5)
        self.play(FadeIn(cpp_output_text, run_time=1.0))
        self.wait(2.0) # Longer wait for voiceover

        # Transition (handled by CombinedVideoScene)
        # self.play(FadeOut(VGroup(code_panel, output_panel, code_label, output_label,
        #                          python_code, python_output_text, cpp_code, cpp_output_text)))


# ── Scene 4: A Global Tradition and Next Steps ────────────────────────
class Scene04AGlobalTraditionAndNextSteps(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create objects
        # Using Text for a globe emoji for simplicity
        globe_icon = Text("🌎", font_size=120).move_to(ORIGIN)
        
        # "Hello, World!" texts in different languages/colors
        hw_python = Text("Hello, World! (Python)", font_size=32, color=ManimColor("#4CAF50")).shift(UP * 2.5 + LEFT * 4)
        hw_cpp = Text("Hello, World! (C++)", font_size=32, color=ManimColor("#2196F3")).shift(UP * 2.5 + RIGHT * 4)
        hw_java = Text("Hello, World! (Java)", font_size=32, color=ManimColor("#FFC107")).shift(DOWN * 2.5 + LEFT * 4)
        hw_js = Text("Hello, World! (JS)", font_size=32, color=ManimColor("#FF9800")).shift(DOWN * 2.5 + RIGHT * 4)
        
        all_hw_texts = VGroup(hw_python, hw_cpp, hw_java, hw_js)
        
        # Question mark icon
        question_mark_icon = Text("?", font_size=100, color=HIGHLIGHT_COLOR).shift(RIGHT * 4)
        
        # Arrow from globe to question mark
        arrow_to_question = Arrow(globe_icon.get_right(), question_mark_icon.get_left(), buff=0.5, color=TEXT_COLOR, max_stroke_width_to_length_ratio=0.05, max_tip_length_to_length_ratio=0.2)
        
        final_message = Text("Your Coding Journey Begins!", font_size=48, color=TEXT_COLOR).to_edge(DOWN, buff=0.5)
        
        # Animate
        self.play(Create(globe_icon, run_time=2.0))
        self.wait(0.5)
        
        # Rotate globe continuously while other animations play
        self.play(
            Rotate(globe_icon, angle=TAU, axis=OUT, rate_func=linear, run_time=15.0),
            FadeIn(hw_python, run_time=1.0),
            FadeIn(hw_cpp, run_time=1.0),
            FadeIn(hw_java, run_time=1.0),
            FadeIn(hw_js, run_time=1.0)
        )
        self.wait(1.0)
        
        self.play(ShowCreation(arrow_to_question, run_time=2.0))
        self.wait(0.5)
        self.play(Create(question_mark_icon, run_time=1.0))
        self.wait(0.5)
        
        self.play(Write(final_message, run_time=2.0))
        self.wait(2.0) # Longer wait for voiceover

        # Transition (handled by CombinedVideoScene)
        # self.play(FadeOut(VGroup(globe_icon, all_hw_texts, arrow_to_question, question_mark_icon, final_message)))


# ── Combined Scene ────────────────────────────────
class CombinedVideoScene(Scene):
    """Renders all scenes in sequence for the complete video."""
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Scene 1
        scene1 = Scene01IntroductionTheIconicHelloWorld()
        scene1.construct()
        self.play(FadeOut(VGroup(*self.mobjects))) # Clear all mobjects from the scene
        self.wait(0.5) # Short pause between scenes
        
        # Scene 2
        scene2 = Scene02WhyHelloWorldTestingYourSetup()
        scene2.construct()
        self.play(FadeOut(VGroup(*self.mobjects)))
        self.wait(0.5)
        
        # Scene 3
        scene3 = Scene03HowItWorksTheConceptOfOutput()
        scene3.construct()
        self.play(FadeOut(VGroup(*self.mobjects)))
        self.wait(0.5)
        
        # Scene 4
        scene4 = Scene04AGlobalTraditionAndNextSteps()
        scene4.construct()
        self.play(FadeOut(VGroup(*self.mobjects)))
        self.wait(0.5)