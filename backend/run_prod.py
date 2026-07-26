#!/usr/bin/env python3
"""Production Uvicorn server runner that respects PORT environment variable (for Render/Cloud deployments)."""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
