# Use Python 3.11 slim as the base image
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# Install system dependencies required for Manim (LaTeX, Cairo, Pango), FFmpeg, EasyOCR, and PyTesseract
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    tesseract-ocr \
    texlive \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-science \
    tipa \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency definitions and application package
COPY pyproject.toml README.md ./
COPY app ./app

# Upgrade pip and install application and dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy remaining files (main.py, etc.)
COPY . .

# Ensure storage, rendering, and upload directories exist
RUN mkdir -p /app/renders /app/data/storage /app/uploads

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI server using dynamic production runner
CMD ["python", "run_prod.py"]

