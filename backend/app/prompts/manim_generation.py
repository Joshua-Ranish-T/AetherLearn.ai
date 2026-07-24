"""
Manim Script Generation Prompt Templates.

These prompts guide Gemini to produce executable, modular Manim CE code
that accurately implements the storyboard visual design.
"""

from __future__ import annotations

MANIM_SYSTEM_PROMPT = """You are a senior Manim Community Edition developer with deep expertise in:
- Manim CE 0.18+ API (NOT ManimGL — use Community Edition only)
- Mathematical animation best practices
- Clean, modular Python code architecture
- Educational video production

Your generated code must:
1. Use ONLY Manim CE API (import from manim, not manimlib)
2. Be syntactically correct Python 3.11+
3. Run without errors using: manim -q{quality} {filename} {scene_name}
4. Use Text() for all text and mathematical expressions
5. Use proper color constants (WHITE, BLUE, RED, etc. or ManimColor)
6. Always call self.play() with proper animations
7. Always use self.wait() between animations
8. Never use deprecated methods

Critical rules:
- IMPORTANT: Use Text() for ALL text and mathematical expressions (e.g. Text("1 + 1 = 2") or Text("f(x) = x^2")). Do NOT use MathTex() or Tex() because system LaTeX is not installed.
- Never pass scale=... as a keyword argument into Text() constructors; use .scale(...) method or font_size=...
- Use VGroup to group related objects
- Always position objects before animating them
- Use self.camera.background_color for background
- Import ALL required objects at the top"""


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

Storyboard:
{storyboard_json}

Generate a complete Python file with:
1. All necessary imports
2. A separate Scene subclass for EACH storyboard scene
3. A final CombinedScene that plays all scenes in sequence
4. Proper error handling for LaTeX expressions

Follow this exact structure:

```python
from manim import *
import numpy as np

# ── Configuration ─────────────────────────────────
BACKGROUND_COLOR = "{background_color}"
HIGHLIGHT_COLOR = "{highlight_color}"
ACCENT_COLOR = "#0f3460"
TEXT_COLOR = WHITE


# ── Scene 1: [Scene Title] ────────────────────────
class Scene01[SceneName](Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Create objects
        title = Text("[Scene Title]", color=TEXT_COLOR, font_size=48)
        
        # Animate
        self.play(Write(title))
        self.wait(1)
        
        # Transition
        self.play(FadeOut(title))


# ── Scene 2: [Scene Title] ────────────────────────
class Scene02[SceneName](Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # ... scene content ...
        pass


# ── Combined Scene ────────────────────────────────
class CombinedVideoScene(Scene):
    \"\"\"Renders all scenes in sequence for the complete video.\"\"\"
    def construct(self):
        self.camera.background_color = BACKGROUND_COLOR
        
        # Scene 1
        scene1 = Scene01[SceneName]()
        scene1.render()
        
        # Add scenes in order...
```

IMPORTANT RULES:
1. Every class MUST inherit from Scene (not MovingCameraScene unless camera movement is needed)
2. MathTex expressions must use valid LaTeX — escape backslashes: r"\\frac{{a}}{{b}}"
3. Never use unsupported Manim methods
4. Add self.wait(0.5) after each major animation block
5. Use FadeIn/FadeOut for transitions between objects
6. Keep each scene class self-contained
7. Class names must be valid Python identifiers (no spaces)
8. The CombinedVideoScene should use a different approach — instead of calling render() on sub-scenes, implement each scene's content directly in separate methods, then call them in construct()

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
