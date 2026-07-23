# Developer Guide

## System Requirements
- Python 3.12+
- Node.js 20+
- FFmpeg (must be in system PATH)
- Manim CE (Community Edition) + its dependencies (LaTeX, Cairo, Pango). See [Manim Docs](https://docs.manim.community/en/stable/installation.html)
- Tesseract OCR (for image processing). See [Tesseract Docs](https://github.com/tesseract-ocr/tesseract)

## Local Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables
Copy `backend/.env.example` to `backend/.env` and fill in the required values:
- `GEMINI_API_KEY`: Get from Google AI Studio.
- Firebase Admin SDK JSON: Place your service account JSON file in the project and point `FIREBASE_CREDENTIALS_PATH` to it.

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Start the Frontend
```bash
cd frontend
npm run dev
```
The React app will be available at `http://localhost:5173`.

## LangGraph State Management
The core of the pipeline is `backend/app/graph/builder.py`. State is maintained using a custom `FirebaseCheckpointer` which allows the application to pause and resume, or recover from crashes without losing context.

To debug graph state, look at the `checkpoints` collection in your Firebase Firestore database.
