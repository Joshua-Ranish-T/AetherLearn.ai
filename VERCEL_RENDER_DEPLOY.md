# ⚡ Vercel & Render Deployment Guide (Turnkey Setup)

This guide explains the exact, step-by-step process for deploying the **EduVideo AI Platform** using **Render** for the backend engine and **Vercel** for the frontend SPA.

We have already modified and configured your codebase so that deploying to both platforms works **right out of the box** without port binding errors or 404 page routing issues!

---

## 🛠️ Codebase Modifications Applied

1. **[render.yaml](file:///d:/MathTutor/render.yaml)**: Created a Blueprint definition in your project root. When you connect your repository to Render, it automatically sets up the Docker Web Service, selects the `backend/` root directory, and configures health checks.
2. **[backend/run_prod.py](file:///d:/MathTutor/backend/run_prod.py)** & **[backend/Dockerfile](file:///d:/MathTutor/backend/Dockerfile)**: Updated the server startup command to dynamically read Render's `$PORT` environment variable (`os.environ.get("PORT", 8000)`). This prevents "Port binding failed" and health check timeout errors on Render.
3. **[frontend/vercel.json](file:///d:/MathTutor/frontend/vercel.json)**: Added client-side rewrite rules for Vercel. When users refresh or bookmark `/workspace`, `/progress`, or `/projects`, Vercel serves the Vite SPA index instead of returning a 404 error.

---

## 🚀 Phase 1: Deploy Backend to Render (3 Clicks via Blueprint)

Render natively supports Docker builds and will automatically compile Python 3.11, LaTeX, Cairo, Pango, and FFmpeg from our Dockerfile.

### Step 1: Push Your Code to GitHub
Commit all recent changes and push your branch to GitHub:
```bash
git add .
git commit -m "Configure turnkey deployment for Render and Vercel"
git push origin main
```

### Step 2: Connect to Render via Blueprint
1. Log into your [Render Dashboard](https://dashboard.render.com/).
2. Click the **New +** button in the top right and select **Blueprint**.
3. Connect your GitHub repository (`EduVideo` or your repo name).
4. Render will automatically detect the [render.yaml](file:///d:/MathTutor/render.yaml) file and show the `eduvideo-backend` service!
5. Click **Apply Blueprint**.

### Step 3: Configure Required Environment Variables on Render
During or after setup, go to **Dashboard -> eduvideo-backend -> Environment**, and fill in these 4 secrets:

| Variable Name | Value / Example |
| :--- | :--- |
| `GEMINI_API_KEY` | `AIzaSyYourGeminiApiKeyHere...` |
| `FIREBASE_PROJECT_ID` | `manimvideogeneration` |
| `FIREBASE_STORAGE_BUCKET` | `manimvideogeneration.firebasestorage.app` |
| `FIREBASE_CREDENTIALS_JSON` | *(See PowerShell command below to get the single-line string)* |

> [!TIP]
> **How to get your `FIREBASE_CREDENTIALS_JSON` string:**
> Open PowerShell in your IDE and run this command:
> ```powershell
> Get-Content -Raw backend\firebase-credentials.json | ConvertFrom-Json | ConvertTo-Json -Compress
> ```
> Copy the entire output string and paste it directly into Render's `FIREBASE_CREDENTIALS_JSON` field!

### Step 4: Select Instance Type & Wait for Build
* Under **Settings -> Instance Type**, select at least **Standard (2 GB RAM / 1 CPU)** or higher.
  * *Why?* Manim CE renders high-definition mathematical videos and compiles LaTeX equations, which requires more memory than Render's 512MB Free tier provides.
* Once deployed, Render will generate your live API URL:
  👉 `https://eduvideo-backend-xxxxx.onrender.com`

---

## 🌐 Phase 2: Deploy Frontend to Vercel

Vercel is the fastest CDN platform for hosting Vite React single-page applications.

### Step 1: Import Project in Vercel
1. Log into your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New -> Project** and import your GitHub repository.
3. In the **Configure Project** screen, edit the settings:
   * **Root Directory**: Click *Edit* and select `frontend`.
   * **Framework Preset**: Notice Vercel automatically selects **Vite**.
   * **Build Command**: `npm run build` (default).
   * **Output Directory**: `dist` (default).

### Step 2: Add Frontend Environment Variables in Vercel
Before clicking Deploy, expand the **Environment Variables** section and add:

| Variable Name | Value / Example |
| :--- | :--- |
| `VITE_API_URL` | **Paste your live Render URL here** (e.g. `https://eduvideo-backend-xxxxx.onrender.com`) |
| `VITE_REQUIRE_AUTH` | `true` |
| `VITE_FIREBASE_API_KEY` | `AIzaSy...` *(From your frontend/.env)* |
| `VITE_FIREBASE_AUTH_DOMAIN` | `manimvideogeneration.firebaseapp.com` |
| `VITE_FIREBASE_PROJECT_ID` | `manimvideogeneration` |
| `VITE_FIREBASE_STORAGE_BUCKET` | `manimvideogeneration.firebasestorage.app` |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | `3922...` |
| `VITE_FIREBASE_APP_ID` | `1:3922...` |

### Step 3: Click Deploy!
Vercel will build your React application in ~30 seconds and provide your live frontend URL:
👉 `https://eduvideo-app.vercel.app`

---

## 🔗 Phase 3: Connect CORS & Verify

1. Copy your live Vercel domain (e.g., `https://eduvideo-app.vercel.app`).
2. Go back to your Render Dashboard -> **eduvideo-backend -> Environment**.
3. Edit the `CORS_ORIGINS` variable to whitelist your Vercel frontend:
   ```json
   ["https://eduvideo-app.vercel.app"]
   ```
4. Click **Save Changes** (Render will automatically restart the backend in 5 seconds).

### 🎉 You are now live in production!
Visit your Vercel URL, log in with Google, and test creating an animated video lesson! Your live terminal progress logs will stream in real time from Render directly to your Vercel frontend.
