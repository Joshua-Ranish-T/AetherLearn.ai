# E2B Sandbox Custom Template for AetherLearn.ai Manim Rendering
#
# To build and push this custom template to E2B:
# 1. Install E2B CLI: npm i -g @e2b/cli
# 2. Login to E2B: e2b auth login
# 3. Build template: e2b template build -d backend/e2b.Dockerfile --name aetherlearn-manim
#
# Once built, configure E2B_API_KEY in your Render environment variables.

FROM e2b/code-interpreter:latest

# Install system dependencies required for Manim (LaTeX, Cairo, Pango) and FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    texlive \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-science \
    tipa \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Manim CE and required Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir manim scipy numpy sympy pillow

WORKDIR /root
