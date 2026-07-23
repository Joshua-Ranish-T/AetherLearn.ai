# EduVideo Platform — AI Educational Video Generator

The EduVideo Platform is a complete, production-ready system that leverages Google's Gemini 1.5 Pro to automatically convert raw educational content (like text, PDFs, or handwritten notes) into high-quality, fully animated, and narrated Manim videos.

This is a modern, modular rewrite of the previous monolithic AI Tutor project, adopting standard software engineering practices.

## Key Features
- **Multi-Modal Input:** Upload text, topics, PDFs, images, or handwritten notes.
- **AI Multi-Agent Pipeline:** Built with **LangGraph**, separating tasks into Supervisor, OCR, Content Generation, Manim Scripting, Repair, and Narration agents.
- **Robust Error Recovery:** Features an LLM-driven Repair Agent that surgically fixes Manim compilation errors based on traceback logs.
- **FastAPI Backend:** Fully typed, asynchronous REST API.
- **Firebase Persistence:** Uses Firestore for database state (projects, jobs, videos, checkpointing) and Firebase Storage for assets.
- **Modern React Frontend:** React 19, Vite, TailwindCSS with a premium glassmorphism dark-mode UI.

## Project Structure
```text
.
├── backend/
│   ├── app/
│   │   ├── api/        # FastAPI routers
│   │   ├── agents/     # LangGraph AI agents (Gemini)
│   │   ├── core/       # Config, logging, exceptions, Firebase init
│   │   ├── database/   # Firestore repositories
│   │   ├── graph/      # LangGraph state definition & checkpointer
│   │   ├── prompts/    # Structured LLM prompt templates
│   │   ├── schemas/    # Pydantic data models
│   │   └── services/   # OCR, TTS, Manim Execution, Sync services
│   ├── main.py         # Application entry point
│   ├── pyproject.toml
│   └── .env
└── frontend/
    ├── src/
    │   ├── components/ # React components & layouts
    │   ├── hooks/      # TanStack Query & SSE hooks
    │   ├── pages/      # Route pages
    │   ├── services/   # Axios API client
    │   └── types/      # TypeScript interfaces
    ├── package.json
    ├── tailwind.config.js
    └── index.html
```

## Getting Started

See the documentation in the `docs/` directory for detailed information:
- [Developer Guide](docs/developer-guide.md)
- [Architecture Details](docs/architecture.md)
- [API Reference](docs/api.md)
