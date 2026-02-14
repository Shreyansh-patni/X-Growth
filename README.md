# X Growth Automation System (MVP)

A comprehensive automation system for growing X (Twitter) accounts using AI-generated replies and intelligent monitoring.

## Features

-   **Smart Monitoring**: Tracks Home Timeline and User Lists for relevant tweets.
-   **AI Reply Generation**: Uses LLMs (OpenAI/Gemini) to generate context-aware replies.
-   **Safety First**: Built-in safety classifiers and rate limiting (Token Bucket) to prevent bans.
-   **Approval Dashboard**: Web interface to review, edit, and approve replies before they are posted.
-   **Analytics**: Track growth stats and system activity.

## Project Structure

-   `backend/`: FastAPI application (Python) handling core logic, database, and background services.
-   `frontend/`: Next.js application (React) for the dashboard and settings.

## Prerequisites

-   Python 3.10+
-   Node.js 18+
-   PostgreSQL (Supabase or Local)
-   X API Credentials (Basic or Pro tier recommended)

## Getting Started

### 1. Configuration
Ensure your `backend/.env` file is set up with:
-   `DATABASE_URL`
-   `OPENAI_API_KEY` or `GEMINI_API_KEY`
-   `X_API_KEY`, `X_API_SECRET` (Consumer Keys)
-   `X_USERNAME`, `X_PASSWORD` (For fallback automation)

### 2. Run the Application
We have provided a helper script to start both Backend and Frontend:

```powershell
./start_app.ps1
```

Or manually:

**Backend:**
```bash
cd backend
python -m uvicorn app.main:app --port 8001
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### 3. Access the Dashboard
Open [http://localhost:3000](http://localhost:3000) in your browser.

## Tech Stack
-   **Backend**: FastAPI, SQLAlchemy, Alembic, Playwright
-   **Frontend**: Next.js, TailwindCSS, Shadcn UI
-   **Database**: PostgreSQL
-   **AI**: OpenAI GPT-4o / Gemini Pro
