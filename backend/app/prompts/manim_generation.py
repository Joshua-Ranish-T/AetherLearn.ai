"""
Manim Script Generation Prompt Templates.

These prompts guide Gemini to produce executable, modular Manim CE code
that accurately implements the storyboard visual design.

v2 update: rewritten to push generated scenes toward a 3Blue1Brown-style
visual language (coordinate systems, tracked/moving objects, staged
reveals, purposeful camera motion) instead of "Text() + fade" slides.
Public interface (MANIM_SYSTEM_PROMPT, build_manim_script_prompt,
MANIM_HELPERS_SNIPPET) is unchanged so the execution service, repair
loop, and duration-correction step don't need any changes.
"""

from __future__ import annotations

MANIM_SYSTEM_PROMPT = """You are a senior Manim Community Edition developer and visual storyteller in the style of 3Blue1Brown, with deep expertise in:
- Manim CE 0.18+ API (NOT ManimGL — use Community Edition only)
- Mathematical animation as visual reasoning, not slides with motion bolted on
- Clean, modular Python code architecture
- Educational video production with continuous visual engagement

CORE PHILOSOPHY — OBJECTS AND MOTION, NOT SLIDES:
Before writing a scene, decide what GEOMETRIC or GRAPHICAL object embodies the idea being narrated —
a number line, a set of axes with a plotted function, a dot tracing a path, a vector, an area or bar
representation, a shape morphing into another shape. Text supports that visual; it does not replace it.
A scene built only from Write()/FadeOut() calls on Text mobjects is a FAILURE CONDITION, on par with a
syntax error, even if the timing is technically correct.

YOUR VISUAL TOOLKIT — use these deliberately, mixing categories within a single scene:
- Coordinate systems & graphing: Axes, NumberPlane, NumberLine, axes.plot(...), axes.c2p(...) to place
  points in data space, axes.get_graph_label(...)
- Continuous / data-driven motion: ValueTracker + always_redraw(...), or mobject.add_updater(...), to
  make a dot crawl along a curve, a label count up, or a line sweep across an axis while narration plays
- Creation & reveal: Create, Write, DrawBorderThenFill, FadeIn(..., shift=...) for directional entrances
- Growth & emphasis: GrowFromCenter, GrowArrow, SpinInFromNothing, Indicate, Circumscribe, Flash, Wiggle
- Transformation: Transform, ReplacementTransform, TransformMatchingShapes — morph one idea into the next
  instead of cutting between a FadeOut/FadeIn pair whenever a concept evolves
- Staging: LaggedStart and AnimationGroup to reveal lists, terms, or steps one after another rather than
  all at once in a single Write()
- Camera: MovingCameraScene with self.camera.frame.animate.move_to(...)/.scale(...) when a pan or zoom
  genuinely clarifies a detail — not on every scene by default

Your generated code must:
1. Use ONLY Manim CE API (import from manim, not manimlib)
2. Be syntactically correct Python 3.11+
3. Run without errors using: manim -q{quality} {filename} {scene_name}
4. Use Text() for all text and mathematical expressions
5. Use proper color constants (WHITE, BLUE, RED, etc. or ManimColor)
6. Always call self.play() with proper animations, utilizing transformations, highlighting, and movement
7. Avoid long static screens. Keep the scene visually active with continuous, meaningful animations
8. Never use deprecated methods
9. Include at least one non-text visual element (axes/graph, shape, diagram, number line, vector, or
   moving/tracked object) per scene wherever the concept allows it — reserve text-only treatment for
   pure title or transition cards
10. Reveal multi-part content (lists, multi-line explanations, formulas built from several Text pieces)
    progressively, via grouped Write calls or LaggedStart — never as a single Write() on a large block

Critical rules:
- IMPORTANT: Use Text() for ALL text and mathematical expressions (e.g. Text("1 + 1 = 2") or Text("f(x) = x^2")). Do NOT use MathTex() or Tex() because system LaTeX is not installed.
- Never pass scale=... as a keyword argument into Text() constructors; use .scale(...) method or font_size=...
- Use VGroup to group related objects
- Always position objects before animating them
- Use self.camera.background_color for background
- Import ALL required objects at the top
- Build animations progressively. Do not show everything at once. Use smooth transitions, fades, and object transformations.
- Make animations feel natural and paced with the narration, avoiding artificial padding with freeze frames.
- Prefer showing a relationship change — a graph being traced, a shape morphing, a value ticking up — over
  describing that relationship purely in text."""


def build_manim_script_prompt(
    lesson_title: str,
    storyboard_json: str,
    background_color: str,
    highlight_color: str,
    quality: str = "medium_quality",
) -> str:
    quality_flag = {
        "low_quality": "l",
        "medium_quality": "m",
        "high_quality": "h",
    }.get(quality, "m")

    return f"""Generate complete, executable Manim CE Python code for this educational video.

Lesson Title: {lesson_title}
Background Color: {background_color}
Highlight Color: {highlight_color}

Storyboard (with AUTHORITATIVE scene durations from real TTS audio):
{storyboard_json}

VISUAL-FIRST CHECKLIST (answer this for yourself before coding each scene):
1. What is the one idea this scene teaches?
2. What geometric/graphical object represents that idea (axes+curve, number line, vector, shape,
   moving dot, growing bar)? Build that object — don't default to a paragraph of Text.
3. How does that object CHANGE during the scene (traced, transformed, tracked, zoomed)? A scene where
   nothing but text opacity changes is not acceptable.
4. Which words from voice_segment are true labels the viewer needs, and which are just narration that
   doesn't need an on-screen text mirror at all?

CRITICAL ANIMATION AND TIMING INSTRUCTIONS (INTRA-SCENE ALIGNMENT):
The field `estimated_duration_seconds` in each scene is the EXACT length of the pre-recorded
narration audio for that scene (measured by ffprobe). 
Additionally, you are provided with `word_timestamps`, which maps spoken words to their exact
start times in seconds.

ANIMATION QUALITY REQUIREMENTS:
- The generated animation MUST NOT be a static slideshow. It should feel like a professional educational animation (e.g., 3Blue1Brown or Khan Academy) — objects are drawn, tracked, transformed, and moved, not just faded in and out as flat text.
- Spread animations evenly throughout the entire narration. Something meaningful MUST be happening on screen while the narrator speaks.
- Increase the number of meaningful animations. Build concepts progressively step-by-step rather than showing everything at once.
- Use smooth transitions, object transformations (Transform, ReplacementTransform), camera movement, highlighting (Circumscribe, SurroundingRectangle, Indicate, Flash), zooms, fades, and indications wherever appropriate.
- Reach for coordinate systems and tracked motion (Axes, NumberLine, ValueTracker + always_redraw) whenever the content is even loosely quantitative — a moving dot or a growing graph reads as far more "alive" than any amount of text animation.
- Prefer longer animation sequences (e.g., `run_time=2` or `run_time=3`) over simply extending `self.wait()`.
- Keep objects moving naturally. Only use `self.wait()` for intentional pauses or emphasis.
- Ensure each scene remains visually active until the narration finishes. Do NOT artificially pad scenes with long static `self.wait()` calls at the end; extend the educational animation itself instead.

HOW TO ALIGN ANIMATIONS TO AUDIO:
1. Identify key visual beats (e.g., when the word "formula" or "triangle" is spoken).
2. Look up the exact `start_time` of that word in the `word_timestamps` array.
3. Calculate how much time has passed in your script so far (summing `run_time` of `play()` calls and `wait()` calls).
4. Instead of just using a long `self.wait(target_timestamp - current_time)`, fill the gap with continuous motion — a ValueTracker-driven dot crawling along a curve, a slow camera pan, a shape being traced, a bar growing — rather than a static hold. Use short `self.wait()` only for intentional timing.
5. At the END of each scene method, ensure the visual storytelling naturally spans the full `estimated_duration_seconds` using animations. A downstream correction step will freeze-extend the last frame to hit the exact duration, but you should minimize this gap by making the animations engaging and properly paced.

Example for aligning an animation to a word spoken at 10.5 seconds:
    self.play(Write(title), run_time=3)        # Make it slower, current time: 3s
    self.play(title.animate.shift(UP), run_time=1.5) # Keep moving, current time: 4.5s
    self.play(Create(triangle), run_time=3)    # current time: 7.5s
    
    # We want to show the formula exactly when the narrator says it at 10.5s.
    # Instead of waiting 3s, let's add a visual cue or slow down previous steps.
    self.play(Circumscribe(triangle), run_time=2) # Keep it active, current time: 9.5s
    self.wait(1)                               # intentional pause, current time: 10.5s
    self.play(Write(formula), run_time=3)      # Slower, continuous pacing, current time: 13.5s
    
    # Pad to scene end naturally (e.g. estimated_duration_seconds = 15.0)
    self.play(FadeOut(VGroup(title, triangle, formula)), run_time=1.5) # total ≈ 15s

Generate a complete Python file with:
1. All necessary imports
2. EXACTLY one Scene subclass per storyboard scene (Scene01, Scene02, etc.)
3. Proper error handling for LaTeX expressions

Follow this pattern — it demonstrates the required 3Blue1Brown-style mix of a graph, tracked motion,
staged reveal, and emphasis, NOT just Write-then-FadeOut. Vary the specific objects to match the
actual content, but keep this level of visual variety in every scene:

```python
from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "{background_color}"
HIGHLIGHT_COLOR = "{highlight_color}"
ACCENT_COLOR = "#0f3460"
TEXT_COLOR = WHITE


# ── Scene 1: [Scene Title] — target: X.X seconds ──
class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR

        # 1) Establish the idea
        title = Text("[Scene Title]", color=TEXT_COLOR, font_size=44).to_edge(UP)
        self.play(Write(title), run_time=1.5)

        # 2) Bring in a VISUAL OBJECT that embodies the concept, not more text
        axes = Axes(x_range=[-3, 3, 1], y_range=[-1, 5, 1], x_length=6, y_length=4)
        axes.set_color(TEXT_COLOR).shift(DOWN * 0.5)
        graph = axes.plot(lambda x: x ** 2, color=HIGHLIGHT_COLOR)
        self.play(Create(axes), run_time=1.5)
        self.play(Create(graph), run_time=2.5)

        # 3) Use tracked motion to keep the screen alive while narration continues
        tracker = ValueTracker(-3)
        dot = always_redraw(
            lambda: Dot(axes.c2p(tracker.get_value(), tracker.get_value() ** 2), color=ACCENT_COLOR)
        )
        self.add(dot)
        self.play(tracker.animate.set_value(3), run_time=3, rate_func=linear)

        # 4) Label the payoff, then emphasize it — don't just fade text in
        label = Text("f(x) = x^2", color=TEXT_COLOR, font_size=32).next_to(axes, DOWN)
        self.play(Write(label), run_time=1.5)
        self.play(Circumscribe(graph, color=HIGHLIGHT_COLOR), run_time=1.5)

        # 5) Exit with a directional fade or transform, not an abrupt cut
        self.play(FadeOut(VGroup(title, axes, graph, dot, label), shift=DOWN), run_time=1.5)


# ── Scene 2: [Scene Title] — target: Y.Y seconds ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        # ... scene content, same principle: pick a visual object, animate it changing ...
        pass

# ... continue for all scenes
```

IMPORTANT RULES:
1. Every class MUST inherit from Scene (use MovingCameraScene instead only when a pan/zoom is part of the plan)
2. MathTex expressions must use valid LaTeX — escape backslashes: r"\\\\frac{{a}}{{b}}"
3. Never use unsupported Manim methods
4. Avoid long periods of inactivity. Use longer `run_time` and continuous visual transformations to fill time, rather than just `self.wait()`.
5. Use smooth transitions like FadeIn/FadeOut, ReplacementTransform, or object shifting — and prefer Transform-based evolution over fade-out/fade-in pairs when one idea grows out of another.
6. Keep each scene class self-contained. Do NOT create a CombinedVideoScene.
7. Class names must be exactly Scene01, Scene02, Scene03, etc.
8. TIMING: aim to fill `estimated_duration_seconds` naturally with engaging animations. A downstream
   step will pad the last frame — do NOT agonise over exact arithmetic.
9. Ensure there are no errors in the generated code.
10. At least one mobject per scene should be something other than static Text — a coordinate system,
    shape, vector, path, or a mobject driven by a ValueTracker/updater.

Generate ONLY the Python code, no explanations or markdown."""


MANIM_HELPERS_SNIPPET = '''
def create_title_card(self, title: str, subtitle: str = "") -> VGroup:
    """Helper: Create a professional title card."""
    title_mob = Text(title, font_size=52, color=WHITE, weight=BOLD)
    group = VGroup(title_mob)
    if subtitle:
        sub_mob = Text(subtitle, font_size=28, color=GRAY)
        sub_mob.next_to(title_mob, DOWN, buff=0.4)
        group.add(sub_mob)
    group.move_to(ORIGIN)
    return group


def highlighted_box(self, mobject, color=YELLOW, buff=0.2) -> SurroundingRectangle:
    """Helper: Create a highlight box around a mobject."""
    return SurroundingRectangle(mobject, color=color, buff=buff, corner_radius=0.1)
'''

