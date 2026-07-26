# 🚀 Production Hosting Guide: EduVideo AI Platform

This guide explains how to deploy the **EduVideo AI Platform** (FastAPI backend + React/Vite frontend) to production.

---

## 🏗️ Architecture & Requirements

### 1. Why the Backend Requires Docker Containerization
Your FastAPI backend uses **Manim CE** for mathematical animation rendering, **FFmpeg** for audio/video synchronization, and **Tesseract/EasyOCR** for document processing. 
Standard serverless Python runtimes (such as Vercel Python Functions, basic AWS Lambda, or simple Heroku Python buildpacks) **will fail** because they lack essential Linux system packages (`texlive`, `libcairo2`, `libpango1.0`, and `ffmpeg`).

To solve this, we have generated a production-ready Docker container setup:
* [backend/Dockerfile](file:///d:/MathTutor/backend/Dockerfile): Pre-installs Python 3.11, LaTeX (TeX Live), Cairo, Pango, FFmpeg, and Tesseract OCR.
* [backend/.dockerignore](file:///d:/MathTutor/backend/.dockerignore): Keeps container image size optimized by excluding local cache and virtual environments.
* [docker-compose.yml](file:///d:/MathTutor/docker-compose.yml): For one-command deployment on VPS or local testing.

### 2. Frontend SPA Architecture
The frontend is a React + TypeScript + Vite Single Page Application (SPA). When built (`npm run build`), it generates static HTML, CSS, and JS assets in `frontend/dist`. It should be hosted on a global CDN such as **Vercel**, **Netlify**, or **Firebase Hosting**.

---

## 🌟 Option 1: Recommended Cloud Stack (Google Cloud Run + Vercel)

This is the most scalable and cost-effective stack for production. **Google Cloud Run** runs your Docker container serverlessly (scaling down to zero when idle so you don't pay for unused compute), while **Vercel** serves the frontend with global CDN speed.

### Step 1: Deploy the Backend to Google Cloud Run
1. Install the [Google Cloud SDK](https://cloud.google.com/sdk) and authenticate:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_GCP_PROJECT_ID
   ```
2. Enable necessary Google Cloud APIs:
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
   ```
3. Deploy directly from the `backend/` directory using Cloud Build:
   ```bash
   cd backend
   gcloud run deploy eduvideo-backend \
     --source . \
     --region us-central1 \
     --platform managed \
     --allow-unauthenticated \
     --memory 4Gi \
     --cpu 2 \
     --timeout 600
   ```
   > [!NOTE]
   > We allocate **4GB RAM and 2 CPUs** with a **600-second timeout** because rendering Manim video animations and compiling LaTeX equations is CPU-intensive and can take 1–3 minutes per video.

4. Once deployed, Cloud Run will provide your live backend URL (e.g., `https://eduvideo-backend-xyz-uc.a.run.app`).

### Step 2: Configure Backend Environment Variables on Cloud Run
In the Google Cloud Console (under **Cloud Run -> eduvideo-backend -> Edit & Deploy New Revision -> Variables & Secrets**), add:
```env
APP_ENV=production
USE_FIREBASE=true
REQUIRE_AUTH=true
GEMINI_API_KEY=AIzaSyYourGeminiApiKey...
FIREBASE_PROJECT_ID=manimvideogeneration
FIREBASE_STORAGE_BUCKET=manimvideogeneration.firebasestorage.app
CORS_ORIGINS=["https://your-frontend-app.vercel.app"]

# Paste your compacted Firebase service account JSON here:
FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"manimvideogeneration",...}
```

### Step 3: Deploy the Frontend to Vercel
1. Push your project to GitHub.
2. Log into [Vercel](https://vercel.com) and import your repository.
3. Configure the Project Settings:
   * **Root Directory**: `frontend`
   * **Framework Preset**: `Vite`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
4. Add Environment Variables in Vercel:
   ```env
   VITE_API_URL=https://eduvideo-backend-xyz-uc.a.run.app
   VITE_REQUIRE_AUTH=true
   VITE_FIREBASE_API_KEY=AIzaSy...
   VITE_FIREBASE_AUTH_DOMAIN=manimvideogeneration.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=manimvideogeneration
   VITE_FIREBASE_STORAGE_BUCKET=manimvideogeneration.firebasestorage.app
   VITE_FIREBASE_MESSAGING_SENDER_ID=3922...
   VITE_FIREBASE_APP_ID=1:3922...
   ```
5. Click **Deploy**!

---

## ⚡ Option 2: All-in-One Deployment on Render.com

If you prefer managing both frontend and backend on a single dashboard, **Render** supports Docker services and static SPAs.

### Step 1: Deploy Backend as a Docker Web Service
1. In Render Dashboard, click **New -> Web Service** and connect your GitHub repository.
2. Set the following options:
   * **Root Directory**: `backend`
   * **Environment**: `Docker`
   * **Dockerfile Path**: `./Dockerfile`
   * **Instance Type**: Select at least **Standard (2GB RAM / 1 CPU)** or higher (Manim animation rendering will run out of memory on 512MB Free instances).
3. Add Environment Variables under the Environment tab (same as Cloud Run above).

### Step 2: Deploy Frontend as a Static Site
1. In Render Dashboard, click **New -> Static Site** and connect your GitHub repo.
2. Set the following options:
   * **Root Directory**: `frontend`
   * **Build Command**: `npm install && npm run build`
   * **Publish Directory**: `dist`
3. Add your `VITE_*` environment variables (pointing `VITE_API_URL` to your Render Web Service URL).

---

## 🖥️ Option 3: VPS / Dedicated Server (AWS EC2, DigitalOcean, Linode)

If you have an Ubuntu/Debian VPS or AWS EC2 instance, you can use our pre-configured [docker-compose.yml](file:///d:/MathTutor/docker-compose.yml) to spin up the backend.

### Step 1: Install Docker & Git on your VPS
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git nginx
sudo systemctl enable --now docker
```

### Step 2: Clone & Configure Environment
```bash
git clone https://github.com/yourusername/EduVideo.git
cd EduVideo
```
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=AIzaSy...
FIREBASE_PROJECT_ID=manimvideogeneration
FIREBASE_STORAGE_BUCKET=manimvideogeneration.firebasestorage.app
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
CORS_ORIGINS=["https://yourdomain.com"]
```

### Step 3: Start the Backend Container
```bash
sudo docker compose up -d --build
```
The FastAPI backend will now be running and restarting automatically on port `8000`. You can configure Nginx or Caddy as a reverse proxy with Let's Encrypt SSL to route `api.yourdomain.com` to `localhost:8000`.

---

## 🔑 How to Prepare `FIREBASE_CREDENTIALS_JSON`

For cloud deployments, you do not need to upload your `firebase-credentials.json` file. Instead, compact the JSON into a single line string or Base64 string:

### Option A: Compact JSON (PowerShell on Windows)
Run this command in your IDE terminal where `firebase-credentials.json` is located:
```powershell
Get-Content -Raw backend\firebase-credentials.json | ConvertFrom-Json | ConvertTo-Json -Compress
```
Copy the single-line output and paste it directly into your hosting platform's `FIREBASE_CREDENTIALS_JSON` environment variable!

### Option B: Base64 String (Linux / Mac / Git Bash)
```bash
cat backend/firebase-credentials.json | base64 -w 0
```
Our backend initialization code automatically detects and decodes Base64 or raw JSON strings!

---

## ✅ Post-Deployment Verification Checklist

Once deployed, run these quick checks to ensure 100% functionality:
1. **Health Check**: Visit `https://your-backend-url.com/health` -> should return `{"status": "ok"}`.
2. **Auth Verification**: Log into the frontend SPA with Google OAuth -> check console network tab to confirm ID tokens are successfully passed to `/api/v1/projects`.
3. **Video Generation**: Start a test project -> verify in logs that Manim renders the MP4 without syntax or LaTeX errors and uploads it cleanly to your Firebase Storage bucket (`manimvideogeneration.firebasestorage.app`).
