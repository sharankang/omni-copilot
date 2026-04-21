# Omni Copilot

Omni Copilot is an advanced AI-powered desktop assistant designed to seamlessly integrate with your favorite tools and streamline your workflows. Built with a modern Next.js frontend and a resilient FastAPI Python backend, it harnesses the Groq AI model to act as a unified interface for your digital workspace.

## Features & Integrations
- **Groq AI**: Lightning-fast intelligent reasoning using Groq LLM model.
- **Google Workspace**: Integrated Google Drive, Calendar, and Gmail features.
- **Slack**: Direct interaction and message handling via bot integrations.
- **Notion**: Database sync and workspace management.
- **Discord**: Easy webhook connections and alerting.
- **Modern UI**: Clean "Bento Box" UI styling, dark mode support, using TailwindCSS and Framer Motion.

## Architecture
- **Frontend**: Next.js 16+, React 19, Tailwind CSS v4, Framer Motion
- **Backend**: Python (FastAPI), SQLite (aiosqlite), Groq API LLM Client

## Getting Started

### Prerequisites
- Node.js (v20+)
- Python (3.10+)
- Relevant API Keys for integrations (see Environment Variables below)

### 1. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows (Command Prompt):
   venv\Scripts\activate
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the Environment Variables by copying the given example file and filling in your credentials:
   ```bash
   cp .env.example .env
   ```
5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```
   *(Running locally on `http://localhost:8000`)*

### 2. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
   *(Running locally on `http://localhost:3000`)*

## Configuration & Environment Variables

Most configurations live in the `backend/.env` file. I have provided a `.env.example` in the backend folder that lists all the needed keys:
- **Groq API**: Needs `GROQ_API_KEY` for LLM integrations.
- **Google APIs**: Require `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
- **Other Platforms**: Make sure to gather `SLACK_BOT_TOKEN`, `NOTION_API_KEY`, etc. if you wish to use those native plugins.
