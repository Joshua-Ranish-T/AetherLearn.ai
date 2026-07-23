"""
Content Generation Prompt Templates.

These templates are used by ContentGenerationAgent to produce structured
lesson plans and storyboards from extracted educational content.
"""

from __future__ import annotations

LESSON_PLAN_SYSTEM_PROMPT = """You are an expert educational content designer and instructional technologist.
Your role is to transform raw educational content into structured, visually-rich lesson plans
optimized for animated video production using Manim Community Edition.

You must produce clear, accurate, pedagogically sound educational content that:
- Builds understanding progressively (scaffolded learning)
- Uses concrete examples before abstract concepts
- Includes mathematical precision where required
- Is optimized for visual animation (not just text narration)
- Sounds natural when spoken aloud as narration

Always return valid JSON that strictly conforms to the requested schema."""


def build_lesson_plan_prompt(
    extracted_text: str,
    subject_domain: str,
    equations: list[str],
    code_blocks: list[str],
    input_type: str,
) -> str:
    """Build the user prompt for lesson plan and storyboard generation."""

    equations_section = ""
    if equations:
        eqs = "\n".join(f"  - {eq}" for eq in equations[:10])
        equations_section = f"\nDetected Mathematical Expressions:\n{eqs}\n"

    code_section = ""
    if code_blocks:
        code_preview = code_blocks[0][:500] if code_blocks else ""
        code_section = f"\nDetected Code:\n```\n{code_preview}\n```\n"

    return f"""Analyze the following educational content and generate a complete lesson plan with storyboard.

Input Type: {input_type}
Subject Domain: {subject_domain}
{equations_section}{code_section}

Educational Content:
---
{extracted_text[:6000]}
---

Generate a comprehensive lesson plan in the following JSON format. Be thorough, educational, and precise.
Every scene should have detailed animation descriptions that a Manim developer can implement.

{{
  "title": "Descriptive lesson title",
  "subject": "{subject_domain}",
  "difficulty_level": "beginner | intermediate | advanced",
  "target_audience": "Description of target learners",
  "learning_objectives": ["objective 1", "objective 2", "objective 3"],
  "prerequisite_knowledge": ["prereq 1", "prereq 2"],
  "key_concepts": ["concept 1", "concept 2", "concept 3"],
  "explanation": "Full markdown explanation of the concept step by step...",
  "summary": "Concise 2-3 sentence summary",
  "keywords": ["keyword1", "keyword2"],
  "estimated_video_duration_seconds": 120,
  "full_narration_script": "Complete narration for the entire video...",
  "animation_plan": {{
    "total_scenes": 4,
    "estimated_total_duration_seconds": 120,
    "visual_theme": "Dark background with vibrant colors for mathematical clarity",
    "background_color": "#1a1a2e",
    "highlight_color": "#e94560",
    "accent_color": "#0f3460",
    "camera_movements": ["pan left", "zoom in on equation"],
    "special_effects": ["particle effects on key reveal", "highlight box"],
    "notes": "Use consistent color scheme throughout"
  }},
  "storyboard": [
    {{
      "scene_number": 1,
      "scene_title": "Introduction",
      "learning_objective": "What viewer learns in this scene",
      "animation_description": "Detailed description of what animates on screen",
      "voice_segment": "Exact narration text for this scene",
      "estimated_duration_seconds": 15,
      "background_color": "#1a1a2e",
      "transition": "FadeIn",
      "mathematical_expressions": ["\\\\frac{{d}}{{dx}}[f(x)]"],
      "code_snippet": "",
      "objects": [
        {{
          "object_type": "text",
          "content": "Display text here",
          "position": "CENTER",
          "color": "WHITE",
          "scale": 1.0
        }},
        {{
          "object_type": "equation",
          "content": "\\\\frac{{d}}{{dx}}[f(x)] = f'(x)",
          "position": "DOWN",
          "color": "#e94560",
          "scale": 1.2
        }}
      ],
      "animations": [
        {{
          "animation_type": "Write",
          "target_object": "title text",
          "duration": 1.5,
          "parameters": {{"run_time": "1.5"}}
        }},
        {{
          "animation_type": "FadeIn",
          "target_object": "equation",
          "duration": 1.0,
          "parameters": {{}}
        }}
      ]
    }}
  ]
}}

Requirements:
- Generate 4-8 scenes based on content complexity
- Each scene should be 10-30 seconds
- Objects list must include ALL visual elements for the scene
- Animations list must correspond to objects
- voice_segment must sound like an experienced teacher speaking naturally
- Use LaTeX notation for all math (double-escaped for JSON: \\\\frac, \\\\int, etc.)
- mathematical_expressions must be valid LaTeX
- Return ONLY the JSON object, no markdown wrapping"""


STORYBOARD_REFINEMENT_PROMPT = """Review this storyboard and ensure:
1. Each scene flows naturally from the previous
2. Mathematical expressions are valid LaTeX
3. Voice segments are natural and educational
4. Animation descriptions are specific enough for a Manim developer
5. Timing is realistic (no scene shorter than 8 seconds)

Return the refined storyboard JSON."""
