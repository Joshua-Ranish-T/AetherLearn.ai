"""
Manim Script Generation Prompt Templates.

These prompts guide Gemini to produce executable, modular Manim CE code
that accurately implements the storyboard visual design.
"""

from __future__ import annotations

MANIM_SYSTEM_PROMPT = """You are a senior Manim Community Edition developer with deep expertise in:
- Manim CE 0.18+ API (NOT ManimGL — use Community Edition only)
- Mathematical animation best practices (similar to 3Blue1Brown)
- Clean, modular Python code architecture
- Educational video production with continuous visual engagement

Your generated code must:
1. Use ONLY Manim CE API (import from manim, not manimlib)
2. Be syntactically correct Python 3.11+
3. Run without errors using: manim -q{quality} {filename} {scene_name}
4. Use Text() for all text and mathematical expressions
5. Use proper color constants (WHITE, BLUE, RED, etc. or ManimColor)
6. Always call self.play() with proper animations, utilizing transformations, highlighting, and movement
7. Avoid long static screens. Keep the scene visually active with continuous, meaningful animations
8. Never use deprecated methods

Critical rules:
- IMPORTANT: Use Text() for ALL text and mathematical expressions (e.g. Text("1 + 1 = 2") or Text("f(x) = x^2")). Do NOT use MathTex() or Tex() because system LaTeX is not installed.
- Never pass scale=... as a keyword argument into Text() constructors; use .scale(...) method or font_size=...
- Use VGroup to group related objects
- Always position objects before animating them
- Use self.camera.background_color for background
- Import ALL required objects at the top
- Build animations progressively. Do not show everything at once. Use smooth transitions, fades, and object transformations.
- Make animations feel natural and paced with the narration, avoiding artificial padding with freeze frames."""


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

CRITICAL ANIMATION AND TIMING INSTRUCTIONS (INTRA-SCENE ALIGNMENT):
The field `estimated_duration_seconds` in each scene is the EXACT length of the pre-recorded
narration audio for that scene (measured by ffprobe). 
Additionally, you are provided with `word_timestamps`, which maps spoken words to their exact
start times in seconds.

ANIMATION QUALITY REQUIREMENTS:
- The generated animation MUST NOT be a static slideshow. It should feel like a professional educational animation (e.g., 3Blue1Brown or Khan Academy).
- Spread animations evenly throughout the entire narration. Something meaningful MUST be happening on screen while the narrator speaks.
- Increase the number of meaningful animations. Build concepts progressively step-by-step rather than showing everything at once.
- Use smooth transitions, object transformations (Transform, ReplacementTransform), camera movement, highlighting (Circumscribe, SurroundingRectangle), zooms, fades, and indications wherever appropriate.
- Prefer longer animation sequences (e.g., `run_time=2` or `run_time=3`) over simply extending `self.wait()`.
- Keep objects moving naturally. Only use `self.wait()` for intentional pauses or emphasis.
- Ensure each scene remains visually active until the narration finishes. Do NOT artificially pad scenes with long static `self.wait()` calls at the end; extend the educational animation itself instead.

HOW TO ALIGN ANIMATIONS TO AUDIO:
1. Identify key visual beats (e.g., when the word "formula" or "triangle" is spoken).
2. Look up the exact `start_time` of that word in the `word_timestamps` array.
3. Calculate how much time has passed in your script so far (summing `run_time` of `play()` calls and `wait()` calls).
4. Instead of just using a long `self.wait(target_timestamp - current_time)`, fill the gap with slow, continuous animations (like drawing, panning, or highlighting) or use longer `run_time` for the preceding animations to keep the scene active. Use short `self.wait()` only for intentional timing.
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

Follow this exact structure:

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
        
        # Create objects
        title = Text("[Scene Title]", color=TEXT_COLOR, font_size=48)
        
        # Animate progressively with natural, engaging pacing
        self.play(Write(title), run_time=2.5)
        self.play(title.animate.scale(1.1).set_color(HIGHLIGHT_COLOR), run_time=1.5)
        
        # Continue with meaningful animations throughout the scene
        # ...
        
        # Transition smoothly instead of abrupt cuts or long waits
        self.play(FadeOut(title, shift=DOWN), run_time=2)


# ── Scene 2: [Scene Title] — target: Y.Y seconds ──
class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        # ... scene content ...
        pass

# ... continue for all scenes
```

IMPORTANT RULES:
1. Every class MUST inherit from Scene (not MovingCameraScene unless camera movement is needed)
2. MathTex expressions must use valid LaTeX — escape backslashes: r"\\\\frac{{a}}{{b}}"
3. Never use unsupported Manim methods
4. Avoid long periods of inactivity. Use longer `run_time` and continuous visual transformations to fill time, rather than just `self.wait()`.
5. Use smooth transitions like FadeIn/FadeOut, ReplacementTransform, or object shifting.
6. Keep each scene class self-contained. Do NOT create a CombinedVideoScene.
7. Class names must be exactly Scene01, Scene02, Scene03, etc.
8. TIMING: aim to fill `estimated_duration_seconds` naturally with engaging animations. A downstream
   step will pad the last frame — do NOT agonise over exact arithmetic.
9. Ensure there are no errors in the generated code.

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
