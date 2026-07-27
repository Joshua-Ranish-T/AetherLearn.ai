# API Reference

The backend exposes a REST API built with FastAPI. Complete interactive documentation is available at `http://localhost:8000/docs` when the server is running.

## Base URL
`/api/v1`

## Endpoints

### Projects
- `POST /projects` — Create a project from text/topic.
- `POST /projects/upload` — Create a project from an uploaded file (PDF/Image). Expects `multipart/form-data`.
- `GET /projects` — List all projects (supports pagination `limit` & `offset`).
- `GET /projects/{id}` — Get project metadata.
- `DELETE /projects/{id}` — Delete project and associated jobs.

### Generation & Jobs
- `POST /generate` — Start the video generation pipeline for a project. Returns a `Job` ID immediately.
  - Body: `{ "project_id": "string", "quality": "low_quality", "force_regenerate": boolean }`
- `GET /jobs/{id}` — Get the current status of a generation job.
- `GET /jobs/{id}/stream` — Server-Sent Events (SSE) endpoint for real-time progress updates and pipeline logs.

### Videos
- `GET /videos` — List all completed videos.
- `GET /video/{id}` — Get video metadata (including signed Firebase Storage URLs for assets).
- `GET /project/{id}/videos` — Get all videos associated with a specific project.
- `GET /video/{id}/download` — Redirects to the MP4 file download URL.

### Rendering
- `POST /render` — Manually trigger a re-render starting from a specific pipeline stage (e.g., after manually editing the generated Manim script).
