# AetherLearn.ai Platform — Backend Engine

FastAPI backend and LangGraph multi-agent AI pipeline for automated educational Manim video generation.

## Key Technologies
- **Python 3.11+**
- **FastAPI**: Fully typed, asynchronous REST API.
- **LangGraph & LangChain**: Multi-agent orchestration (Supervisor, OCR, Content Generation, Manim Scripting, Repair, Narration).
- **Manim CE**: Mathematical animation rendering engine.
- **Google Gemini API**: AI reasoning, code generation, and error repair.
- **Firebase Admin SDK**: Firestore persistence and Cloud Storage asset management.

## Running Locally
```bash
# Start development server with auto-reload (ignores render directory changes)
python run_dev.py
```
or via Uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude "renders/*" --reload-exclude "data/*" --reload-exclude "uploads/*"
```
