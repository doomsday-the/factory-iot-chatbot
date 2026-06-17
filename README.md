# IoT Factory ChatBot Dashboard

A factory chat dashboard using Streamlit for UI, FastAPI as the backend server, and Gemini 2.5 Flash to generate SELECT-only queries securely and query data from a PostgreSQL database containing factory metrics.

## Architecture

```
User
 ↓
Streamlit UI
 ↓
FastAPI Backend
 ↓ (Gemini parses question -> SQL)
PostgreSQL
 ↓ (Run SELECT queries safely)
FastAPI Backend
 ↓ (Gemini parses DB results -> Friendly text)
Streamlit UI (Answer)
```

## Folder Structure
```
├── backend/
│   ├── main.py        # FastAPI API
│   ├── database.py    # PostgreSQL connection & query validation
│   └── llm.py         # Gemini LLM integration
├── frontend/
│   └── app.py         # Streamlit Application
├── .env               # Local Env Config (git-ignored)
└── requirements.txt   # Dependencies
```

## Setup & Running Locally

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables in `.env`:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=iot_dashboard
   DB_USER=user
   DB_PASSWORD=password
   GEMINI_API_KEY=your_gemini_api_key
   ```

3. Run the Application:
   You can easily start both the FastAPI backend and Streamlit frontend using the provided run script:
   ```bash
   python run.py
   ```
   *This will automatically launch the backend on port 8000 and the frontend on port 8501.*

   Alternatively, you can run them separately:
   ```bash
   # Terminal 1: Backend
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

   # Terminal 2: Frontend
   streamlit run frontend/app.py
   ```

## Render Deployment

### 1. Backend Service (FastAPI Web Service)
- **Repository Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `DATABASE_URL`: Your PostgreSQL external connection URI (or individual `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` variables).
  - `GEMINI_API_KEY`: Your Gemini API Key.

### 2. Frontend Service (Streamlit Web Service)
- **Repository Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0`
- **Environment Variables**:
  - `BACKEND_URL`: The URL of your deployed backend service (e.g. `https://chatbot-backend.onrender.com`).
