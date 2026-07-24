"""
Repair Agent Prompt Templates.

These prompts guide Gemini to perform targeted, surgical fixes
to broken Manim code without regenerating the entire script.
"""

from __future__ import annotations

REPAIR_SYSTEM_PROMPT = """You are an expert Python and Manim CE debugging specialist.
Your task is to analyze execution errors from Manim and apply targeted, minimal fixes.

Rules:
1. NEVER rewrite the entire script — only fix what is broken
2. Identify the exact line(s) causing the error from the traceback
3. Return ONLY the corrected Python file — complete and runnable
4. Preserve all existing class names, structure, and logic
5. CRITICAL: If FileNotFoundError [WinError 2] or LaTeXError occurs, system LaTeX is NOT installed. You MUST replace all MathTex(...) and Tex(...) calls with Text(...) calls (e.g. Text("1 + 1 = 2")).
6. Never pass scale=... as a keyword argument into Text() constructors; use .scale(...) method or font_size=...
7. Fix AttributeErrors by using correct Manim CE API methods
8. Fix ImportErrors by adding missing imports at the top
9. Never introduce new bugs while fixing existing ones"""


def build_repair_prompt(
    error_message: str,
    traceback: str,
    broken_script: str,
    retry_number: int,
    previous_errors: list[str],
) -> str:
    prev_errors_section = ""
    if previous_errors:
        prev_errors_section = "\nPrevious failed repair attempts:\n" + "\n".join(
            f"Attempt {i+1}: {err}" for i, err in enumerate(previous_errors)
        )

    return f"""Fix the following Manim CE script. This is repair attempt #{retry_number}.

ERROR MESSAGE:
{error_message}

TRACEBACK:
{traceback}
{prev_errors_section}

BROKEN SCRIPT:
```python
{broken_script}
```

Analysis steps:
1. Identify the exact error type (SyntaxError, AttributeError, LaTeXError, etc.)
2. Locate the specific line(s) causing the error
3. Apply the minimal fix required

Common fixes:
- LaTeX errors: Use r-strings, escape backslashes, validate expression
- AttributeError: Check Manim CE 0.18 API (e.g., .animate property, not deprecated methods)
- NameError: Add missing import or fix variable name
- TypeError: Check method signatures in Manim CE docs
- IndentationError: Fix Python indentation

Return ONLY the complete corrected Python script with no explanation or markdown fencing."""
