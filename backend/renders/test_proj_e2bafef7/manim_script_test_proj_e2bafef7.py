from manim import *
import numpy as np
from typing import Optional


from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = ManimColor("#1a1a2e")
HIGHLIGHT_COLOR = ManimColor("#e94560")
ACCENT_COLOR = ManimColor("#0f3460") # Not explicitly used in storyboard, but good to keep.
TEXT_COLOR = WHITE


# ── Combined Scene ────────────────────────────────
class CombinedVideoScene(Scene):
    """Renders all scenes in sequence for the complete video."""
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Call each scene method in order
        self._scene_01_the_idea_of_one()
        self._scene_02_one_plus_one_equals_two()
        self._scene_03_the_language_of_math()
        self._scene_04_everyday_addition()

    def _scene_01_the_idea_of_one(self):
        # Scene 1: The Idea of One
        # Learning Objective: Introduce the concept of a single item and its numerical representation '1'.
        
        # Create objects
        title = Text("The Idea of One", color=HIGHLIGHT_COLOR).to_edge(UP)
        
        # Position circle and number '1' relative to each other, centered horizontally
        circle_obj = Circle(radius=0.8, color=HIGHLIGHT_COLOR, fill_opacity=1)
        number_one_text = Text("1", color=TEXT_COLOR, font_size=60)
        
        # Group them to position them together, then arrange
        one_concept_group = VGroup(circle_obj, number_one_text).arrange(RIGHT, buff=1.0).move_to(ORIGIN)
        
        # Re-assign for animation targets
        circle_obj = one_concept_group[0]
        number_one_text = one_concept_group[1]
        
        # Animate
        self.play(FadeIn(title))
        self.wait(0.5)
        
        self.play(Create(circle_obj))
        self.wait(0.5)
        
        self.play(Write(number_one_text))
        self.wait(2.0) # Longer wait for narration
        
        # Transition
        self.play(
            FadeOut(title),
            FadeOut(circle_obj),
            FadeOut(number_one_text)
        )
        self.wait(0.5)

    def _scene_02_one_plus_one_equals_two(self):
        # Scene 2: One Plus One Equals Two
        # Learning Objective: Visually demonstrate the combination of two single items to form two items, introducing the '+' and '=' symbols.
        
        # Create initial objects
        circle_one_left = Circle(radius=0.6, color=HIGHLIGHT_COLOR, fill_opacity=1)
        plus_sign = Text("+", color=TEXT_COLOR, font_size=60)
        circle_one_right = Circle(radius=0.6, color=HIGHLIGHT_COLOR, fill_opacity=1)
        equals_sign = Text("=", color=TEXT_COLOR, font_size=60)
        
        # Arrange the initial expression
        initial_expression_group = VGroup(
            circle_one_left, plus_sign, circle_one_right, equals_sign
        ).arrange(RIGHT, buff=0.7).shift(UP * 0.5) # Shift up to make space for the equation below
        
        # Re-assign for animation targets
        circle_one_left = initial_expression_group[0]
        plus_sign = initial_expression_group[1]
        circle_one_right = initial_expression_group[2]
        equals_sign = initial_expression_group[3]

        # Target for transformation: two circles grouped together
        group_of_two_circles_target = VGroup(
            Circle(radius=0.6, color=HIGHLIGHT_COLOR, fill_opacity=1),
            Circle(radius=0.6, color=HIGHLIGHT_COLOR, fill_opacity=1)
        ).arrange(RIGHT, buff=0.3).next_to(equals_sign, RIGHT, buff=0.7)
        
        number_two_text = Text("2", color=TEXT_COLOR, font_size=60).next_to(group_of_two_circles_target, DOWN, buff=0.5)
        
        equation_text = MathTex("1 + 1 = 2", color=TEXT_COLOR, font_size=72).to_edge(DOWN)
        
        # Animate
        self.play(Create(circle_one_left))
        self.wait(0.3)
        
        self.play(Write(plus_sign))
        self.wait(0.3)
        
        self.play(Create(circle_one_right))
        self.wait(0.3)
        
        self.play(Write(equals_sign))
        self.wait(0.5)
        
        # Transform the two separate circles into the grouped two circles
        initial_circles_group = VGroup(circle_one_left, circle_one_right)
        
        self.play(
            Transform(initial_circles_group, group_of_two_circles_target)
        )
        self.wait(0.5)
        
        self.play(Write(number_two_text))
        self.wait(0.5)
        
        self.play(Write(equation_text))
        self.wait(2.5) # Longer wait for narration
        
        # Transition
        self.play(
            FadeOut(initial_circles_group), # This will be the transformed group_of_two_circles_target
            FadeOut(plus_sign),
            FadeOut(equals_sign),
            FadeOut(number_two_text),
            FadeOut(equation_text)
        )
        self.wait(0.5)

    def _scene_03_the_language_of_math(self):
        # Scene 3: The Language of Math
        # Learning Objective: Understand the meaning of each symbol in the equation '1 + 1 = 2'.
        
        # Create objects
        # Using separate strings for MathTex allows easy indexing for SurroundingRectangle
        full_equation = MathTex("1", "+", "1", "=", "2", color=TEXT_COLOR, font_size=96).move_to(ORIGIN)
        
        # Create highlight boxes for each part
        highlight_one_left = SurroundingRectangle(full_equation[0], color=HIGHLIGHT_COLOR, stroke_width=4, buff=0.1)
        highlight_plus = SurroundingRectangle(full_equation[1], color=HIGHLIGHT_COLOR, stroke_width=4, buff=0.1)
        highlight_one_right = SurroundingRectangle(full_equation[2], color=HIGHLIGHT_COLOR, stroke_width=4, buff=0.1)
        highlight_equals = SurroundingRectangle(full_equation[3], color=HIGHLIGHT_COLOR, stroke_width=4, buff=0.1)
        highlight_two = SurroundingRectangle(full_equation[4], color=HIGHLIGHT_COLOR, stroke_width=4, buff=0.1)
        
        # Animate
        self.play(Write(full_equation))
        self.wait(1.0)
        
        # Highlight first '1'
        self.play(FadeIn(highlight_one_left))
        self.wait(1.5) # Delay for narration
        self.play(FadeOut(highlight_one_left))
        self.wait(0.5)
        
        # Highlight '+'
        self.play(FadeIn(highlight_plus))
        self.wait(1.5)
        self.play(FadeOut(highlight_plus))
        self.wait(0.5)
        
        # Highlight second '1'
        self.play(FadeIn(highlight_one_right))
        self.wait(1.5)
        self.play(FadeOut(highlight_one_right))
        self.wait(0.5)
        
        # Highlight '='
        self.play(FadeIn(highlight_equals))
        self.wait(1.5)
        self.play(FadeOut(highlight_equals))
        self.wait(0.5)
        
        # Highlight '2'
        self.play(FadeIn(highlight_two))
        self.wait(1.5)
        self.play(FadeOut(highlight_two))
        self.wait(2.0) # Longer wait for narration
        
        # Transition
        self.play(FadeOut(full_equation))
        self.wait(0.5)

    def _scene_04_everyday_addition(self):
        # Scene 4: Everyday Addition
        # Learning Objective: Reinforce the concept of 1 + 1 = 2 and its real-world applicability.
        
        # Create objects
        # To simulate the transform from the previous scene, we create the large equation first
        source_equation = MathTex("1 + 1 = 2", color=TEXT_COLOR, font_size=96).move_to(ORIGIN)
        equation_small = MathTex("1 + 1 = 2", color=HIGHLIGHT_COLOR, font_size=48).to_corner(UP + LEFT)
        
        # Placeholder for two fingers using simple shapes (Ellipses)
        finger1 = Ellipse(width=0.5, height=1.5, color=TEXT_COLOR, fill_opacity=1).shift(0.3 * LEFT + 0.5 * UP)
        finger2 = Ellipse(width=0.5, height=1.5, color=TEXT_COLOR, fill_opacity=1).shift(0.3 * RIGHT + 0.5 * UP)
        fingers_example = VGroup(finger1, finger2).scale(1.5).move_to(ORIGIN)
        
        # If 'vector_graphic_two_fingers.svg' is available and preferred, uncomment and use SVGMobject:
        # try:
        #     fingers_example = SVGMobject("vector_graphic_two_fingers.svg").scale(1.5).move_to(ORIGIN)
        # except FileNotFoundError:
        #     # Fallback to simple shapes if SVG not found
        #     finger1 = Ellipse(width=0.5, height=1.5, color=TEXT_COLOR, fill_opacity=1).shift(0.3 * LEFT + 0.5 * UP)
        #     finger2 = Ellipse(width=0.5, height=1.5, color=TEXT_COLOR, fill_opacity=1).shift(